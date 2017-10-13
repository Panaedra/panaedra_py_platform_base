import os
import traceback
import json

from datetime import datetime
from influxdb.client import InfluxDBClient
from panaedra.msroot.msutil.logic.sc_msjson_logic import outputJSON, inputJSON

class c_influxdbclient_bulk(InfluxDBClient):
  '''
  Collect some (metrics) data, and write in bulk
  '''
  def __init__(self, *args, **kwargs):
    self.tPoints = [] 
    self.oTimestamp = None  
    self.cDatabase = None
    self.cWorkfile = None
    self.oLog = None
    self.cRetentionPolicy = kwargs.pop('cRetentionPolicy')
    super(c_influxdbclient_bulk, self).__init__(*args, **kwargs)
  
  def set_workfile(self, cWorkdirIP): 
    self.cWorkfile = os.path.join(cWorkdirIP, 'measurements.dat')
    if os.path.exists(self.cWorkfile + '.working'):
      raise IOError('Detected \'{}\'. Remove or rename this file to \'{}\' and restart this process.'.format(self.cWorkfile + '.working', self.cWorkfile))
      
  def set_logger(self, oLogIP):
    self.oLog = oLogIP
  
  def set_timestamp(self, dtTimestampIP=None):
    self.oTimestamp = datetime.utcnow() if dtTimestampIP is None else dtTimestampIP
    
  def add_point(self, cMeasurementIP, oFieldIP=None, tFieldsIP=None, tTagsIP=None, oTimestampIP=None): 
    tPoint = { 
      'measurement': cMeasurementIP, 
      'time'       : self.oTimestamp if oTimestampIP is None else oTimestampIP, # The timestamp is converted on the client-side. 
      'fields'     : { 'value': oFieldIP } if not oFieldIP is None else tFieldsIP,
      'tags'       : tTagsIP
    }
    self.tPoints.append(tPoint)
    return tPoint
  
  def write_points_bulk(self): 
    bOk = False
    try:
      bOk = self.write_points(self.tPoints, retention_policy=self.cRetentionPolicy)
    except:
      if (self.oLog and self.cWorkfile):
        self.oLog.error('Failed to write measurement points to %s:%s.\n%s' % (self._host, self._port, traceback.format_exc()))
      else: 
        raise
    if (not bOk) and self.cWorkfile:
      with open(self.cWorkfile, 'ab') as oFile:
        oFile.write(json.dumps(self.tPoints, default=outputJSON) + '\n')
        if self.oLog: self.oLog.info('Measurements points are stored in {} until the connection is restored.'.format(self.cWorkfile))
    elif (self.cWorkfile is not None) and os.path.exists(self.cWorkfile) and os.stat(self.cWorkfile).st_size:
      os.rename(self.cWorkfile, self.cWorkfile + '.working')
      with open(self.cWorkfile, 'wb') as oFile, open(self.cWorkfile + '.working', 'rb') as oTemp: 
        bOk = True
        for cLine in oTemp:
          tPoints = json.loads(cLine, object_hook=inputJSON)
          try:
            if bOk:
              bOk = self.write_points(tPoints, retention_policy=self.cRetentionPolicy)
          except:
            bOk = False
          if not bOk:
            oFile.write(cLine)
      os.remove(self.cWorkfile + '.working')
    self.tPoints = []
    return bOk

#EOF
