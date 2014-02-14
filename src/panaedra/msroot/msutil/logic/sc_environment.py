import ast
import sys
import os
import subprocess

class sc_environment:
  """Cross-platform environment and session information"""

  _bInitialized=False
  cEnv='(not-set)'
  bLiveEnv=False
  cUserID=''
  cUiMode=''            
  cAsMode=''        
  cLayer=''
  cLang=''
  cUserID=''
  cOsUserID=''
  cLogDir=''         
  cSharedIniDir=''      
  cSessionGuid=''
  cSessionGuidShort=''
  cSessionGuidRemote=''
  cOtaPath=''          
  cWorkPath=''
  cDevIP=''   
  cDevToken=''

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
  
  @classmethod
  def _InheritAblEnvironmentSettings(cls,cDataIP):
    """Called from Bridge"""
    tData = ast.literal_eval(cDataIP)
    cls.cEnv               = tData['cEnv'              ]
    cls.bLiveEnv           = tData['bLiveEnv'          ]
    cls.cUserID            = tData['cUserID'           ]
    cls.cUiMode            = tData['cUiMode'           ]
    cls.cAsMode            = tData['cAsMode'           ]
    cls.cLayer             = tData['cLayer'            ]
    cls.cLang              = tData['cLang'             ]
    cls.cUserID            = tData['cUserID'           ]
    cls.cOsUserID          = tData['cOsUserID'         ]
    cls.cLogDir            = tData['cLogDir'           ]
    cls.cSharedIniDir      = tData['cSharedIniDir'     ]
    cls.cSessionGuid       = tData['cSessionGuid'      ]
    cls.cSessionGuidShort  = tData['cSessionGuidShort' ]
    cls.cSessionGuidRemote = tData['cSessionGuidRemote']
    cls.cOtaPath           = tData['cOtaPath'          ]
    cls.cWorkPath          = tData['cWorkPath'         ]
    cls.cDevIP             = tData['cDevIP'            ]
    cls.cDevToken          = tData['cDevToken'         ]
    return 'Setting environment to: %s, workpath to: %s, devtoken to: %s' % (repr(cls.cEnv),repr(cls.cWorkPath),repr(cls.cDevToken))

#EOF
