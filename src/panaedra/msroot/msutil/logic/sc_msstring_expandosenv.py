import os
import re

class sc_msstring_expandosenv:
  """Expand windows and unix environment variables"""
  _bInitialized = False
  _oCompiledRe  = None
  
  @staticmethod  
  def _Initialize():
    if not sc_msstring_expandosenv._bInitialized:
      sc_msstring_expandosenv._oCompiledRe = re.compile(r'%(\w+)(#?)%')
    
  @staticmethod  
  def ExpandString(cStrIP):
    """Expand windows and unix environment variables"""
    if not sc_msstring_expandosenv._bInitialized:
      sc_msstring_expandosenv._Initialize()
    return sc_msstring_expandosenv._oCompiledRe.sub(sc_msstring_expandosenv._mExpandWinOsenvSub, cStrIP)  

  @staticmethod  
  def _mExpandWinOsenvSub(mo):
    return os.environ.get(mo.group()[1:-1], 'UNKNOWN')

#EOF
