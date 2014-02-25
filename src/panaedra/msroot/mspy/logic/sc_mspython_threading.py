import threading
import json

from copy import deepcopy

class sc_mspython_threading:
  """Get _TERM_UNDISCLOSED_/threading session information from the python (sub-)environment. Also inter-thread control."""
  
  tThreadInfo = {}
  tRegisteredThreads = []
  oLock = threading.RLock()

  @classmethod
  def PyRegisterThread(cls, oEventIP):
    """Called from Python only"""
    with cls.oLock:
      if not oEventIP in cls.tRegisteredThreads:
        cls.tRegisteredThreads += (oEventIP,)
  
  @classmethod
  def PyUnregisterThread(cls, oEventIP):
    """Called from Python only"""
    with cls.oLock:
      cls.tRegisteredThreads.remove(oEventIP)
  
  @classmethod
  def GetThreadInfo(cls,cDataIP):
    """Called from Bridge"""
    with cls.oLock:
      tThreadInfoCpy = deepcopy(cls.tThreadInfo)
    return json.dumps(tThreadInfoCpy,indent=0)
  
  @classmethod
  def ClearThreadInfo(cls,cDataIP):
    """Called from Bridge"""
    with cls.oLock:
      cls.tThreadInfo = {}
    return ''

  @classmethod
  def GetNextThreadEndLock(cls):
    """Called from Python only"""
    oThreadEndLockOP = None  
    with cls.oLock:
      if len(cls.tRegisteredThreads) > 0:
        oThreadEndLockOP = cls.tRegisteredThreads[0]
    return oThreadEndLockOP

  @classmethod
  def WaitAllThreadsCompleted(cls,cDataIP):
    """Called from Bridge"""
    cRet = ''
    iThreadCount = threading.active_count() # Including main thread
    if iThreadCount > 1:
      cRet += 'Active thread count: %s\n' % iThreadCount
    oThreadEndLock = cls.GetNextThreadEndLock()
    while not oThreadEndLock is None:
      cRet += 'Waiting on thread: %s\n' % repr(oThreadEndLock)
      oThreadEndLock.wait()
      oThreadEndLock = cls.GetNextThreadEndLock()
    return cRet

#EOF
