class sc_path(object):

  cSharedIniDir    = ''
  cIniDir          = ''
  cLogDir          = ''
  cLogVerboseDir   = ''
  cWorkDir         = ''
  cTempDir         = ''
  cDataExchangeDir = ''
  cDataRecoveryDir = ''
  cOtaPath         = ''
  cWorkPath        = ''

  @classmethod
  def _InheritAblEnvironmentSettings(cls,tData):
    """Called from sc_environment.py"""
    cls.cSharedIniDir    = tData['cSharedIniDir'     ]
    cls.cIniDir          = tData['cIniDir'           ]
    cls.cLogDir          = tData['cLogDir'           ]
    cls.cLogVerboseDir   = tData['cLogVerboseDir'    ]
    cls.cWorkDir         = tData['cWorkDir'          ]
    cls.cTempDir         = tData['cTempDir'          ]
    cls.cDataExchangeDir = tData['cDataExchangeDir'  ]
    cls.cDataRecoveryDir = tData['cDataRecoveryDir'  ]
    cls.cOtaPath         = tData['cOtaPath'          ]
    cls.cWorkPath        = tData['cWorkPath'         ]
  
  @classmethod
  def Full2PartialPath(cls,cFullPath,cPath,cDelimiter):
    tPath=cPath.split(cDelimiter)
    for cEntry in tPath:
      if cFullPath.startswith(cEntry):
        return cFullPath[len(cEntry):].lstrip('/\\')
    return cFullPath

if __name__ == '__main__':
  '''
  cls=sc_path
  print cls.Full2PartialPath('/root/test/namespace/one.cls', '/root/dummy,/root/test,/root/devshelve', ',')
  '''
  
#EOF'
