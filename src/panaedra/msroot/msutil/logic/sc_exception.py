import sys
import traceback

class sc_exception:
  """Cross-platform environment and session information"""

  _bInitialized=False

  @staticmethod
  def _Initialize():
    if not sc_exception._bInitialized:
      sc_exception._bInitialized = True
    pass

  @staticmethod
  def ExceptionToString(oExceptionIP):
    '''Not working yet... tw 20130629'''
    if not sc_exception._bInitialized:
      sc_exception._Initialize()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    cReturn = 'NOTWORKINGYET... %s\n' % (type(oExceptionIP).__name__)
    try:
      lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
      cException = type(oExceptionIP).__name__ + " " + str(oExceptionIP) + '\n'.join('!! ' + line.rstrip() for line in lines)  # Log it or whatever here
      cReturn += cException
    except Exception as e:
      cReturn += str(e)
    return cReturn
#EOF
