class sc_path(object):

  cSharedIniDir    = ''
  cIniDir          = ''
  cLogDir          = ''
  cLogverboseDir   = ''
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
    cls.cLogverboseDir   = tData['cLogverboseDir'    ]
    cls.cWorkDir         = tData['cWorkDir'          ]
    cls.cTempDir         = tData['cTempDir'          ]
    cls.cDataExchangeDir = tData['cDataExchangeDir'  ]
    cls.cDataRecoveryDir = tData['cDataRecoveryDir'  ]
    cls.cOtaPath         = tData['cOtaPath'          ]
    cls.cWorkPath        = tData['cWorkPath'         ]

#EOF'
