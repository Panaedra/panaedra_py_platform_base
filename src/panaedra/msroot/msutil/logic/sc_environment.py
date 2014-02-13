import sys
import os
import subprocess

class sc_environment:
  """Cross-platform environment and session information"""

  _bInitialized=False
  cEnv = "pub"

  @classmethod
  def _Initialize(cls):
    if not cls._bInitialized:
      cls._bInitialized = True

  @classmethod
  def GetHostName(cls):
    if not cls._bInitialized:
      cls._Initialize()
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
  
  # for use from the pythonbridge
  @classmethod
  def GetEnvironment(cls,cDataIP):
    return cls.cEnv

  @classmethod
  def SetEnvironment(cls,cDataIP):
    cls.cEnv = cDataIP
    print "Setting environment to: %s" % cDataIP
    return ''


#EOF
