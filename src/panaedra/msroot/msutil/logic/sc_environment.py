import os
import ast
import sys
import json
import subprocess
import traceback

from panaedra.msroot.msutil.logic.sc_path import sc_path

class sc_environment:
  """Cross-platform environment and session information"""

  _bInitialized=False
  cEnv='(not-set)'
  bLiveEnv=False
  cUserID=''
  cUserPasswordHash=''
  cUiMode=''            
  cAsMode=''        
  cLayer=''
  cLang=''
  cUserID=''
  cOsUserID=''
  cLogDir=''         
  cSharedIniDir=''      
  cSessionPid=''
  cSessionHostname=''
  cSessionGuid=''
  cSessionGuidShort=''
  cSessionGuidRemote=''
  cOtaPath=''          
  cWorkPath=''
  cDevIP=''   
  cDevToken=''
  oLog=None

  @classmethod
  def _Initialize(cls):
    if not cls._bInitialized:
      cls._bInitialized = True

  @classmethod
  def SessionLog(cls):
    if cls.oLog is None:
      from panaedra.msroot.msutil.logic.sc_log import sc_log
      cls.oLog = sc_log.GetLogger('session%s' % sc_environment.cSessionPid, '')
    return cls.oLog
    
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
    cRet = ''
    try:
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
      cls.cSessionPid        = tData['cSessionPid'       ]
      cls.cSessionHostname   = tData['cSessionHostname'  ]
      cls.cSessionGuid       = tData['cSessionGuid'      ]
      cls.cSessionGuidShort  = tData['cSessionGuidShort' ]
      cls.cSessionGuidRemote = tData['cSessionGuidRemote']
      cls.cOtaPath           = tData['cOtaPath'          ]
      cls.cWorkPath          = tData['cWorkPath'         ]
      cls.cDevIP             = tData['cDevIP'            ]
      cls.cDevToken          = tData['cDevToken'         ]
      cls.cLogverboseDir     = tData['cLogverboseDir'    ]
      sc_path._InheritAblEnvironmentSettings(tData)
      cRet = 'Set environment to: %s, workpath to: %s, devtoken to: %s' % (repr(cls.cEnv),repr(cls.cWorkPath),repr(cls.cDevToken)) 
    except:
      cRet=traceback.format_exc()
      sys.stderr.write('{0}\n'.format(cRet))
    return cRet

  @classmethod
  def GetEnvironmentSettings(cls,cDataIP=None):
    """Called from Bridge (optional)"""
    tRet={}
    for item in dir(cls):
      o=getattr(cls,item)
      if (not item.startswith('_') 
        and (type(o) in (str,bool,int,float)) 
        and len(str(o)) > 0):
        tRet[item]=o
    return json.dumps(tRet,indent=0)

if __name__ == '__main__':
  sc_environment.cEnv='JustTesting'
  print sc_environment.GetEnvironmentSettings()
  
#EOF
