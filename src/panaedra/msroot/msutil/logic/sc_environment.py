import sys
import os
import subprocess

class sc_environment:
  """Cross-platform environment and session information"""

  _bInitialized=False

  @staticmethod
  def _Initialize():
    if not sc_environment._bInitialized:
      sc_environment._bInitialized = True
    pass

  @staticmethod
  def GetHostName():
    if not sc_environment._bInitialized:
      sc_environment._Initialize()
    cRet = ""
    try:
      if sys.platform in ('unix','aix7'):
        cRet = subprocess.check_output(
          ["_TOOLING_"], 
          shell=True,
          stderr=subprocess.STDOUT).strip() 
      elif sys.platform == 'win32':
        cRet = os.environ.get('COMPUTERNAME', 'UNKNOWN') 
      else:
        cRet = "Unsupported platform '%s' for GetHostName()" % sys.platform 
    except subprocess.CalledProcessError, e:
      cRet = "GetHostName() error: %s" % e
    return cRet

#EOF
