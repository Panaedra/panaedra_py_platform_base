import ast
import json
from collections import OrderedDict
import os

class sc_mshqtimestamp_logic(object):
  
  @classmethod
  def StaticMain(cls,cDataIP):
    """Called from Bridge.
    
    :param cDataIP: An ast literal_eval string, dictionary.
    :type  cDataIP: str 
    
    :rtype:   str
    :returns: Feedback: formatted json with indent 0.
    :raises:  

    """
    try:
      tParam = ast.literal_eval(cDataIP)
    except ValueError:
      raise ValueError('Malformed input %r' % cDataIP)
    
    if tParam['mode'] == 'init':
      cls.cself = sc_mshqtimestamp_logic()
      cls.cself.tRet=OrderedDict()
    
    elif tParam['mode'] == 'PyAppendTimestampsWithDict':
      cls.cself.tRet=OrderedDict()
      cls.cself.PyAppendTimestampsWithDict(tParam['cHqtFile'])
    
    tRet=cls.cself.tRet
    cls.cself.tRet=None
    
    return json.dumps(tRet,indent=0)

  def __init__(self):
    self.tRet = None
    
  def PyAppendTimestampsWithDict(self, cHqtFileIP):
    tHqtNewFile=os.path.splitext(cHqtFileIP)
    cHqtNewFile=tHqtNewFile[0] + '_new' + tHqtNewFile[1]
    tDict={}
    with open(cHqtFileIP,'rb') as f_in, open(cHqtNewFile,'wb') as f_out:
      for cLine in f_in:
        tLine=cLine.partition(':')
        tLineData=tLine[2].lstrip().split('\x03')
        cSourceLineComment=''
        if not (tLineData[2], tLineData[3], ) in tDict.keys():
          with open(tLineData[2],'rb') as f_sourcecode:
            for i,cSourceLine in enumerate(f_sourcecode):
              if (i + 1 == tLineData[3]):
                cSourceLineComment=cSourceLine.partition('/*')[2][0:-4]
                tDict[(tLineData[2], tLineData[3], )] = cSourceLineComment.strip()
                break
        f_out.write('{}{}\n'.format(cLine.rstrip(),cSourceLineComment))

#EOF