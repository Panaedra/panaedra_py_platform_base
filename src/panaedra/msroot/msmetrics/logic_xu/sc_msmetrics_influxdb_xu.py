import json
import ast

from copy import deepcopy
from collections import OrderedDict

from panaedra.msroot.msmetrics.logic_xu.c_msmetrics_influxdbclient_bulk_xu import c_influxdbclient_bulk

class sc_msmetrics_influxdb_xu(object):
  
  def __init__(self,cHost,iPort,cDatabase,cRetentionPolicy):
    self.cHost=cHost
    self.iPort=iPort
    self.cDatabase=cDatabase
    self.cRetentionPolicy=cRetentionPolicy
    self.oInfluxDbCli=None
  
  def connect_to_client(self):
    if self.oInfluxDbCli is None:
      self.oInfluxDbCli=c_influxdbclient_bulk(self.cHost,self.iPort,database=self.cDatabase,cRetentionPolicy=self.cRetentionPolicy)
      
  @classmethod
  def WriteJsonToInfluxdb(cls,cDataIP):
    '''Called from Bridge.
    
    :param cDataIP: An ast literal_eval string, dictionary.
    :type  cDataIP: str 
    
    :rtype:   str
    :returns: Feedback: formatted json with indent 0.
    :raises:  

    '''
    try:
      tParam = ast.literal_eval(cDataIP)
    except ValueError:
      raise ValueError('Malformed input %r' % cDataIP)

    if tParam['mode'] == 'init':
      cls.cself = sc_msmetrics_influxdb_xu(tParam['host'],tParam['port'],tParam['database'],tParam['retentionpolicy'])
      cls.cself.tRet=OrderedDict()
      cls.cself.tRet['oInfluxDbCli'] = str(cls.cself.oInfluxDbCli)
      
    elif tParam['mode'] == 'dispose':
      cls.cself.tRet=OrderedDict()
      del cls.cself.oInfluxDbCli # 2017Q4: disconnect was not quickly found, del may or may not work, look into details when needed.
      cls.cself.oInfluxDbCli=None
      cls.cself.tRet['disposed'] = True

    elif tParam['mode'] == 'helloworld':
      cls.cself.tRet=OrderedDict()
      cls.cself.connect_to_client()
      cls.cself.oInfluxDbCli.create_database('helloworld')
      oResults=cls.cself.oInfluxDbCli.query('show databases;')
      for oResult in oResults:
        cls.cself.tRet['helloworld']=str(oResult)
        break 

    elif tParam['mode'] == 'jsonfile2influx':
      cls.cself.tRet=OrderedDict()
      cls.cself.connect_to_client()
      cJsonFile=tParam['jsonfile']
      cTagNames=tParam['tagnames']
      tTagNames=cTagNames.split(',')
      cMeasurement=tParam['measurement']
      with open(cJsonFile,'rb') as f:
        tJsonContents=json.load(f)
      cls.cself.oInfluxDbCli.set_timestamp()
      for tJsonRow in tJsonContents:
        tJsonRow=deepcopy(tJsonRow)
        tTags={}
        for cTagName in tTagNames:
          # Move field data to tag dictionary
          tTags[cTagName]=tJsonRow.pop(cTagName)
        cls.cself.oInfluxDbCli.add_point(cMeasurement, tFieldsIP=tJsonRow, tTagsIP=tTags)
        cls.cself.oInfluxDbCli.write_points_bulk()
      cls.cself.tRet['jsonfile-written']=True

    tRet=cls.cself.tRet
    cls.cself.tRet=None
    return json.dumps(tRet,indent=0)

#EOF
