from panaedra.msroot.msutil.logic.sc_path import sc_path
import os.path
from panaedra.msroot.msflux.logic_xu.sc_msflux_shutdownrequest_xu import sc_environment
from panaedra.msroot.msutil.logic.sc_date_timestamp import sc_date_timestamp

class sc_log(object):
  '''Factory class
  '''
  @classmethod
  def GetLogger(cLognameIP, cSublogdirIP=None):
    oRet = c_mslog(cLognameIP, cSublogdirIP)
    return oRet

class c_mslog(object):
  '''A log object that logs to file. From a bridge (especially from a fifo thread), use snapshot logfiles only.
  '''
  
  def __init__(self, cSourcenameIP, cLognameIP, cSublogdirIP=None):
    '''Constructor
    '''
    self.cSourcename = cSourcenameIP
    self.cLogname = cLognameIP
    self.cSublogdir = cSublogdirIP
    self._cSnapshotLogFileNamePrev = None 
    self._cSnapshotSuffix = None
    self.bIncludeTimeStamp = True
    
    if False:
      '''BoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3'''
      self.cSourcename = '' 
      self.cLogname = ''
      self.cSublogdir = ''
      self._cSnapshotLogFileNamePrev = '' 
      self._cSnapshotSuffix = ''   
      '''EoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3''' 
      
  def cSnapshotLogFileName(self):
    tSnapshotLogFileName = []
    aPnd = tSnapshotLogFileName.append
    if self.cSublogdirIP is None:
      aPnd(sc_path.cLogverboseDir)
    else:  
      aPnd(os.path.join(sc_path.cLogverboseDir, self.cSublogdirIP))
    aPnd(self.cSourcename)
    aPnd('_{0}_{1}_{2}snapshot.log'.format(
      sc_environment.cEnv.lower(),
      sc_date_timestamp.cTimeStamp_Short_Date(),
      self._cSnapshotSuffix.lower() + '_' if not self._cSnapshotSuffix is None and len(self._cSnapshotSuffix) > 0 else ''))
    cRet = ''.join(tSnapshotLogFileName)
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
        f.write('{0:<20}'.format(sc_date_timestamp.cTimeOnly_Short_WithPeriods()))
      f.write('{0}\n'.format(cMessageIP))

#EOF
