import os.path
import datetime
import json
import re

from panaedra.msroot.msutil.logic.sc_path import sc_path
from panaedra.msroot.msflux.logic_xu.sc_msflux_shutdownrequest_xu import sc_environment
from panaedra.msroot.msutil.logic.sc_date_timestamp import sc_date_timestamp
from panaedra.msroot.msutil.logic.c_log_postponed import c_log_postponed
from collections import OrderedDict

class sc_log(object):
  '''Factory class
  '''
  @classmethod
  def GetLogger(cls, cLognameIP, cSublogdirIP=None):
    oRet = c_mslog(cLognameIP, cSublogdirIP)
    return oRet
  
  @classmethod
  def GetLoggerPostponed(cls):
    '''get a (new) logging object'''
    return c_log_postponed()


class c_mslog(object):
  '''A log object that logs to file. From a bridge (especially from a fifo thread), use snapshot logfiles only.
  '''
  
  def __init__(self, cLognameIP, cSublogdirIP=None):
    '''Constructor
    '''
    self.cLogname                  =  cLognameIP
    self.cSublogdir                = cSublogdirIP
    self._cSnapshotLogFileNamePrev = None 
    self._cSnapshotSuffix          = None
    self.bIncludeTimeStamp         = True
    self.tColumnProperties         = None
    self.oRegexMatchDigit          = re.compile(r'\d+') 
    self.cDatetimeFormat           = '{:<21}'
    self.tStatusLn                 = []  
      
    '''Set this property to add an own header to the status log, 
       the normal header will be placed underneath this one'''
    self.cOwnHeader = None
    '''direct errors to the log-manager '''
    self.bErrorOnLogManager = None 
    '''error log file name'''
    self.cErrorLogFileName  = None 
    '''status log file name'''
    self.cStatusLogFileName = None 
    '''timestamp toevoegen aan WriteStatusLn regels'''
    self.bIncludeTimeStamp = None 
    ''' timestamp'''
    self.cTimeStamp = None 
    '''for WriteStatusLnBuf calls, automatically do a WriteStatusHeader if 
    * something else was written in between. Also at day switch.'''
    self.bAutoHeaders = None 
    
    if False:
      '''BoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3'''
      self.cLogname                  = ''
      self.cSublogdir                = ''
      self._cSnapshotLogFileNamePrev = '' 
      self._cSnapshotSuffix          = ''   
      '''EoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3''' 
  
  
  def cLogFileName(self): 
    
    if sc_environment.bLiveEnv == True: 
      cEnv = 'live' 
    else: 
      cEnv = 'nonlive' 
    
    cRet = '{0[dir]}/{0[subdir]}{0[logname]}_{0[env]}_{0[stamp]}_{0[sfx]}.log'.format(
      {'dir'         : sc_environment.cLogDir,
       'subdir'      : '' if (self.cSublogdir is None or len(self.cSublogdir) == 0) else self.cSublogdir + '/',
       'logname'     : self.cLogname,
       'env'         : cEnv,
       'stamp'       : sc_date_timestamp.cTimeStamp_Short_Date(),
       'sfx'         : '' if (self._cSnapshotSuffix is None or len(self._cSnapshotSuffix) == 0) else self._cSnapshotSuffix.lower() + '_',
       })
     
    return os.path.normpath(cRet)

  
  def cSnapshotLogFileName(self):
    
    cRet = '{0[dir]}/{0[subdir]}{0[logname]}_{0[env]}_{0[stamp]}_{0[sfx]}snapshot.log'.format(
      {'dir'         : sc_path.cLogverboseDir,
       'subdir'      : '' if (self.cSublogdir is None or len(self.cSublogdir) == 0) else self.cSublogdir + '/',
       'logname'     : self.cLogname,
       'env'         : sc_environment.cEnv.lower(),
       'stamp'       : sc_date_timestamp.cTimeStamp_Short_Date(),
       'sfx'         : '' if (self._cSnapshotSuffix is None or len(self._cSnapshotSuffix) == 0) else self._cSnapshotSuffix.lower() + '_',
       })
     
    cRet = os.path.normpath(cRet)
    
    if self._cSnapshotLogFileNamePrev <> cRet:
      self._cSnapshotLogFileNamePrev = cRet
      with open(cRet,'ab') as f:
        f.write('\n')
      # ShouldHave: correct file rights, like in abl
    return cRet  


  def SnapshotStatus(self, cSuffixIP, cMessageIP):
    ''' Write a snapshot file. 
       The separate snapshot file will be overwritten with each call.'''
    self._cSnapshotSuffix = cSuffixIP
    
    ''' write message to snapshot log '''
    with open(self.cSnapshotLogFileName(),'wb') as f:
      if self.bIncludeTimeStamp:
        f.write('{0:<20}'.format(sc_date_timestamp.cTimeOnly_Long_WithPeriods()))
      f.write('{0}\n'.format(cMessageIP))

    
  def WriteStatus(self, cMessageIP): 
    
    with open(self.cLogFileName(), "a") as oFile:
      oFile.write(cMessageIP)

  
  def WriteStatusLn(self, cMessageIP): 
    
    self.WriteStatus('{0}\n'.format(cMessageIP))
  
  
  def WriteStatusEmptyLn(self): 
    
    self.WriteStatus('{0}\n'.format(''))
    
   
  def GetFormattedDatetime(self):
    
    return self.cDatetimeFormat.format(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
  
  
  def GetJsonAsOrderedDict(self, cJsonIP): 

    return json.loads(cJsonIP, object_pairs_hook=OrderedDict)
  
  
  def SetColumnProperties(self, cColumnPropertiesAsJsonIP): 
    
    self.tColumnProperties = self.GetJsonAsOrderedDict(cColumnPropertiesAsJsonIP)
    
  
  def GetStatusDictAsString(self, tStatusDictIP):
 
    cStatusLn = ''
    if self.tColumnProperties is None: 
      for cStatusDictKey in tStatusDictIP.iterkeys(): 
        cStatusLn = '{0} {1}'.format(cStatusLn, tStatusDictIP[cStatusDictKey])
    else:   
      for cColumnTitle in self.tColumnProperties.keys(): 
        tOneColumnProperty = self.tColumnProperties[cColumnTitle]
        if isinstance(tOneColumnProperty, (dict)) and \
           tOneColumnProperty.has_key('format')   and \
           tStatusDictIP.has_key(cColumnTitle): 
          cColumnLn = tStatusDictIP[cColumnTitle]
        else: 
          cColumnLn = '' 
        cStatusLn += tOneColumnProperty['format'].format(cColumnLn)
        
    return cStatusLn 
   
   
  def WriteStatusColumnHeaders(self): 
    if not self.tColumnProperties is None: 
      cColumnHeaderLine = ''
      for cColumnTitle in self.tColumnProperties.iterkeys(): 
        tOneColumnProperty = self.tColumnProperties[cColumnTitle]
        if isinstance(tOneColumnProperty, (dict)) and tOneColumnProperty.has_key('format'): 
          cColumnHeaderLine += tOneColumnProperty['format'].format(cColumnTitle)  
      self.WriteStatusLn(cColumnHeaderLine, bDatetimeStamp=False)  
      self.WriteStatusLn(self.WriteHeaderSeparatorLines(), bDatetimeStamp=False)  

    
  def WriteHeaderSeparatorLines(self): 
    cColumnHeaderLine = ''
    for cColumnTitle in self.tColumnProperties.iterkeys(): 
      cColumnHeaderLine += '{s:{c}^{n}}'.format(s='',n=self.oRegexMatchDigit.search(self.tColumnProperties[cColumnTitle]['format']).group(0),c='-')
    return cColumnHeaderLine
  
  
  def WriteStatusDictToLn(self, tStatusDictIP): 
    
    if isinstance(tStatusDictIP, (dict)): 
      self.WriteStatus('{0}\n'.format(self.GetStatusDictAsString(tStatusDictIP)))
    else: 
      raise TypeError('The input to WriteStatusArrayToLn is not a dictionary {}')
 
    
  def WriteStatusInit(self, hBufferReportIP): 
    '''formatted with columns with buffer/query , field-handles possible''' 
    pass 
  
 
  def SnapshotStatusLnBuf(self, cSuffixIP):
    '''write a snapshot file with header. the separate snapshot file will be overwritten with each call'''
    pass 
  
  
  def OpenStatusStream(self):
    pass
  

  def CloseStatusStream(self): 
    pass 
  
  
  # Write error messages 
  def WriteError(self, cMessage):
    pass 

  
  def WriteErrorLn(self, cMessage):
    pass 
  
  
  def WriteException(self, oExepctionIP, cExtraTextIP): 
    pass 
    
  
  def WriteMissingData(self, hBufferIP, cSvKeyValuesIP): 
    pass 
  
 
  def Dispose(self): 
    '''signal the end of the logging'''
    pass 

if __name__ == '__main__':
  
  '''
  sc_environment.cLogDir = 'e:/'
  oLog1 = c_mslog('test1', '')
  oLog1.WriteStatusLn('test')
  oLog1.WriteStatusDictToLn({ 'a': 1, 'b' : 2})

  oLog2 = c_mslog('test2', '')
  oLog2.WriteStatusLn('test')
  oLog2.WriteStatusDictToLn({ 'a': 1, 'b' : 2})
  
  oLog3 = c_mslog('test3', '')
  oLog3.WriteStatusLn('test')
  oLog3.WriteStatusDictToLn({ 'a': 1, 'b' : 2})
  '''
#EOF
