import threading

class sc_mspysys(object):
  
  @classmethod
  def MicroSleep(cls, cMillisecondsIP):
    '''Does the same as time.sleep(), but enables responding to signals like kill -2 (SIGINT) '''
    iMillisecondsIP = int(cMillisecondsIP)
    dummy_event = threading.Event()
    dummy_event.wait(timeout=iMillisecondsIP / 1000.0)
    return ''
    
#EOF
