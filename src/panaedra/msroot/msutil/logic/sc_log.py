import os.path

from panaedra.msroot.msutil.logic.sc_path import sc_path
from panaedra.msroot.msflux.logic_xu.sc_msflux_shutdownrequest_xu import sc_environment
from panaedra.msroot.msutil.logic.sc_date_timestamp import sc_date_timestamp

class sc_log(object):
  '''Factory class
  '''
  @classmethod
  def GetLogger(cls, cSourcenameIP, cLognameIP, cSublogdirIP=None):
    oRet = c_mslog(cSourcenameIP, cLognameIP, cSublogdirIP)
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
      self.cSourcename               = '' 
      self.cLogname                  = ''
      self.cSublogdir                = ''
      self._cSnapshotLogFileNamePrev = '' 
      self._cSnapshotSuffix          = ''   
      '''EoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3''' 
      
  def cSnapshotLogFileName(self):
    
    cRet = '{0[dir]}/{0[subdir]}{0[src]}_{0[env]}_{0[stamp]}_{0[sfx]}snapshot.log'.format(
      {'dir'         : sc_path.cLogverboseDir,
       'subdir'      : '' if (self.cSublogdir is None or len(self.cSublogdir) == 0) else self.cSublogdir + '/',
       'src'         : self.cSourcename,
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
        f.write('{0:<20}'.format(sc_date_timestamp.cTimeOnly_Short_WithPeriods()))
      f.write('{0}\n'.format(cMessageIP))

#EOF
