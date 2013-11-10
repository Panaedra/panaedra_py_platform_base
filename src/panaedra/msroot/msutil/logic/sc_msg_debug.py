import sys

class sc_msg_debug(object):
  """Debug messages"""
  @classmethod
  def Msg(cls,cMsgIP,cEolIP='\n'):
    """
    Can be used from python interpreter in a progress session, even from 
    a separate python thread in a TTY session. 
    Ofcourse result is ugly somewhere in the screen, but still useful 
    for debugging.
    """
    sys.stdout.write("%s%s" % (cMsgIP,cEolIP))
    sys.stdout.flush()

#EOF
