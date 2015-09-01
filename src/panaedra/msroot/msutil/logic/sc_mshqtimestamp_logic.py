import os
import ast
import json

from collections import OrderedDict

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
      cls.cself.PyAppendTimestampsWithDict(
        tParam['cHqtFile'], 
        tParam['dedupe'], 
        True if not tParam.has_key('replace-file') else tParam['replace-file'])
    
    tRet=cls.cself.tRet
    cls.cself.tRet=None
    
    return json.dumps(tRet,indent=0)

  def __init__(self):
    self.tRet = None
    
  def PyAppendTimestampsWithDict(self, cHqtFileIP, bDedupeIP, bReplaceFileIP=True):
    
    tHqtNewFile=os.path.splitext(cHqtFileIP)
    cHqtNewFile=tHqtNewFile[0] + '_new' + tHqtNewFile[1]
    tSourceComments,tDedupeData={},{}
    
    with open(cHqtFileIP,'rb') as f_in, open(cHqtNewFile,'wb') as f_out:
      for cLine in f_in:
        tLine=cLine.partition(':')
        tLineData=tLine[2].lstrip().split('\x03')
        cSourceLineComment=''
        if (len(tLineData[3]) == 0 # No line number; just copy line as-is
            or len(tLineData[-1].rstrip()) > 0): # There is already data (a literal dict) present in this line; just copy line as-is
          f_out.write('{}{}\n'.format(cLine.rstrip(),cSourceLineComment))
        else:
          cRuntimeloc,cLocSequence,cSourcecodeFile,iSourcecodeLine,cVarA,cVarB=tLineData[0],tLineData[1],tLineData[2],int(tLineData[3]),tLineData[5],tLineData[6]
          iSourcecodeLineTell=0
          if not tSourceComments.has_key(cSourcecodeFile):
            tSourceComments=self._ParseSourcecode(cSourcecodeFile, tSourceComments)
          if tSourceComments[cSourcecodeFile].has_key(iSourcecodeLine):
            cSourceLineComment,iSourcecodeLineTell=tSourceComments[cSourcecodeFile][iSourcecodeLine]
          if (not bDedupeIP) or (not tDedupeData.has_key((cRuntimeloc,cLocSequence,))):
            tDedupeData[(cRuntimeloc,cLocSequence,)]=None
            f_out.write('{}: {}\x03{}\x03{}\x03{}\x03{}\x03{}\x03{}\x03{}\n'.format(tLine[0],cRuntimeloc,cLocSequence,cSourcecodeFile,iSourcecodeLine,iSourcecodeLineTell,cVarA,cVarB,cSourceLineComment))
          else:
            f_out.write('{}: {}\x03{}\x03\x03\x03\x03{}\x03{}\x03\n'.format(tLine[0],cRuntimeloc,cLocSequence,cVarA,cVarB))
    
    if bReplaceFileIP:
      tHqtTmpFile=os.path.splitext(cHqtFileIP)
      cHqtTmpFile=tHqtTmpFile[0] + '_tmp' + tHqtTmpFile[1]
      if os.path.isfile(cHqtTmpFile):
        raise RuntimeError('The file "{}" already exists, so rename is unsafe'.format(cHqtTmpFile))
      os.rename(cHqtFileIP, cHqtTmpFile)
      if (not os.path.isfile(cHqtTmpFile)) or os.path.isfile(cHqtFileIP):
        raise RuntimeError('The file "{}" could not be renamed to "{}"'.format(cHqtFileIP, cHqtTmpFile))
      os.rename(cHqtNewFile, cHqtFileIP)
      if (not os.path.isfile(cHqtFileIP)) or os.path.isfile(cHqtNewFile):
        raise RuntimeError('The file "{}" could not be renamed to "{}"'.format(cHqtNewFile, cHqtFileIP))
      os.remove(cHqtTmpFile)
      if os.path.isfile(cHqtTmpFile):
        raise RuntimeError('The file "{}" could not be removed'.format(cHqtTmpFile))
    
  def _ParseSourcecode(self, cSourcecodeFileIP, tSourceCommentsIOP):
    tSourceCommentsIOP[cSourcecodeFileIP]={}
    with open(cSourcecodeFileIP,'rb') as f_sourcecode:
      iBytePosPrev=0
      for i,cSourceLine in enumerate(iter(f_sourcecode.readline, '')): # Note: 'for line in f' can't work with .tell(), because of buffering.
        if ('{&hq}' in cSourceLine):
          cSourceLineComment=cSourceLine.partition('/*')[2]
          cSourceLineComment=cSourceLineComment.rpartition('*/')[0]
          tSourceCommentsIOP[cSourcecodeFileIP][i+1] = [cSourceLineComment.strip(), iBytePosPrev, ]
        iBytePosPrev=f_sourcecode.tell()
    return tSourceCommentsIOP

if __name__ == '__main__':
  '''
  cls=sc_mshqtimestamp_logic
  cls.StaticMain("{'mode':'init',}")
  cls.StaticMain(
    # replace-file to False for debugging only.
    "{'mode':'PyAppendTimestampsWithDict',"
    "'cHqtFile':'T:/ota/systeemtst/dataexchange/fluxdumpbig__dwan_idetest.txt'," # codeQok#7303
    "'dedupe': True,"
    "'replace-file': False, }"
    )
  '''
  
#EOF
