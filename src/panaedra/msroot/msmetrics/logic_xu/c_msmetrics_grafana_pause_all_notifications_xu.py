'''
Metrics (Grafana): Pause or unpause all Grafana notifications. 
Necessary around InfluxDB service restarts, otherwise Grafana will start spamming. 
'''

import os
import re
import logging
import json
import sys

from datetime import datetime
from grafana_api_client import GrafanaClient

def outputJSON(obj):
  '''Default JSON serializer.'''
  if isinstance(obj, datetime):
    if obj.utcoffset() is not None:
      obj = obj - obj.utcoffset()
    return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
  return str(obj)

def inputJSON(obj):
  '''Default JSON reader.'''
  newDic = {}
  for key in obj:
    try:
      newDic[str(key)] = datetime.strptime(obj[key], '%Y-%m-%d %H:%M:%S.%f')
      continue
    except (TypeError, ValueError):
      pass
    newDic[str(key)] = obj[key]  
  return newDic  

class c_msmetrics_grafana_pause_all_notifications_xu(object): 
  '''
  Pause or unpause all Grafana notifications, main class
  '''
  def __init__(self, cConfigIP, bLogToDefaultOutputIP=False): 
    self.tConfig = json.loads(open(cConfigIP).read(), object_pairs_hook=dict)  
    for cDir in (self.tConfig['logdir'], self.tConfig['workdir']):
      if not os.path.exists(cDir):
        os.makedirs(cDir)
    cLogfile = os.path.join(self.tConfig['logdir'], '{}_{}.log'.format(self.tConfig['logfile'], datetime.now().strftime('%Y-%m-%d')))
    self.oLog = logging.getLogger(cLogfile)
    oLogFormatter = logging.Formatter('[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s')
    hLogfileHandler = logging.FileHandler(cLogfile)
    hLogfileHandler.setFormatter(oLogFormatter)
    self.oLog.hLogfileHandler = hLogfileHandler
    self.oLog.addHandler(hLogfileHandler)
    self.oLog.setLevel(logging.INFO)
    if self.tConfig['log_tee_stdout']:
      oConsole = logging.StreamHandler(stream=sys.stdout)
      oConsole.setFormatter(oLogFormatter)
      oConsole.setLevel(logging.INFO)
      self.oLog.addHandler(oConsole)
    self.oGrafanaClient = GrafanaClient(( self.tConfig['grafana_user'],  self.tConfig['grafana_password']), host= self.tConfig['grafana_host'], port= self.tConfig['grafana_port'])
    
    
  def ClientStart(self):
    self.oLog.info('Started client c_msmetrics_grafana_pause_all_notifications_xu.')
    self.PauseNotifications(sys.argv[2]=='pause')
    
  def PauseNotifications(self,bPauseIP=True):
    tAlerts=self.oGrafanaClient.alerts()
    if self.tConfig['verbose_logging'] and not bPauseIP:
      self.oLog.info('pause_but_no_unpause: "{}"'.format(self.tConfig['pause_but_no_unpause']))
    for tAlert in tAlerts:
      if (not bPauseIP) and re.match(pattern=self.tConfig['pause_but_no_unpause'], string=tAlert['name']):
        if self.tConfig['verbose_logging']:
          self.oLog.info('Skipping unpause of "{}"'.format(tAlert['name']))
        continue
      iAlertId=tAlert['id']
      if self.tConfig['verbose_logging']:
        self.oLog.info('{:<10}id={:<10}{:<40}{:<40}{}'.format('Pausing:' if bPauseIP else 'Unpausing:',iAlertId,tAlert['name'],tAlert['dashboardUri'],tAlert['state']))
      tResponse=self.oGrafanaClient.alerts[iAlertId].pause.create(paused=bPauseIP)
      if self.tConfig['verbose_logging']:
        self.oLog.info('{}'.format(repr(tResponse)))
    
if __name__ == '__main__':
  '''
  Always startup with 2 parameters: the path to the config file, and 'pause' or 'unpause'.
  Example for Eclipse run config parameters:
  "${env_var:PanaedraEclipseWorkspace}panaedra_config/mymetrics/grafana_notifications/msmetrics_grafana_pause_all_notifications__influxdb-live-01.json" pause
  '''
  if len(sys.argv) < 2:
    sys.stderr.write('Missing first argument: the filepath to the json config.\n')
    sys.exit(1)
  if len(sys.argv) < 3 or sys.argv[2] not in ('pause','unpause',):
    sys.stderr.write('Missing second argument: \'pause\' or \'unpause\'.\n')
    sys.exit(1)
  if not os.path.isfile(sys.argv[1]):
    sys.stderr.write('The config file "{}" does not exist\n'.format(sys.argv[1]))
    sys.exit(1)
  cConfigpath = sys.argv[1]
  c_msmetrics_grafana_pause_all_notifications_xu(cConfigpath).ClientStart()
  
#EOF
