import threading

class sc_mspysys(object):
  
  @classmethod
  def MicroSleep(cls, cMillisecondsIP):
    '''Called by bridge. Does the same as time.sleep(), but enables responding to signals like kill -2 (SIGINT) '''
    iMillisecondsIP = int(cMillisecondsIP)
    dummy_event = threading.Event()
    dummy_event.wait(timeout=iMillisecondsIP / 1000.0)
    return ''
    
  @classmethod
  def Sleep(cls, seconds):
    '''Python called only. Does the same as time.sleep(), but enables responding to signals like kill -2 (SIGINT). Note: In python 3, time.sleep is implemented as interruptable. 
    @type seconds: float
    '''
    dummy_event = threading.Event()
    dummy_event.wait(timeout=seconds)
    return ''
    
#EOF
