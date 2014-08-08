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
  
  def __init__(self, cLognameIP, cSublogdirIP=None):
    '''Constructor
    '''
    self.cLogname = cLognameIP
    self.cSublogdir = cSublogdirIP
    self._cSnapshotLogFileNamePrev = None 
    self._cSnapshotSuffix = None
    
    if False:
      '''BoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3''' 
      self.cLogname = ''
      self.cSublogdir = ''
      self._cSnapshotLogFileNamePrev = '' 
      self._cSnapshotSuffix = ''   
      '''EoB: Pydev type hinting, epydoc, sphinx or assert implementations not working. 2014Q3''' 

#EOF
