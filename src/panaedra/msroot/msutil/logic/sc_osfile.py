'''Note: see also sc_msosfile.py'''

import os
import fnmatch
import time
import datetime

class sc_osfile(object):
  
  @classmethod
  def StripInvalidChars(cls, cFilepathIP, cReplaceExtraCharsIP=None):

    '''Strip characters that are invalid for filenames. 
       Pass slash+backslash if you want path separators stripped as well.

    :param    cFilepathIP:           The path to a file (existing or nonexisting)
    :type     cFilepathIP:           str
    :param    cReplaceExtraCharsIP:  For example '/~\' replaces slashes and backslashes as well 
    :type     cReplaceExtraCharsIP:  str 
    
    :rtype:   str
    :returns: The modified path
    :raises:  

    '''
    
    tRet=[]
    aRet=tRet.append
    for cLett in cFilepathIP:
      if cLett=='>': cLett=')'
      elif cLett=='<': cLett='('
      elif cLett=='|': cLett='_'
      elif cLett=='?': cLett='_'
      elif cLett=='!': cLett='#'
      elif cLett=='*': cLett='_'
      elif cLett=='~': cLett='_'
      elif cLett==',': cLett=' '
      elif cLett==':': cLett='-'
      elif cLett==';': cLett='-'
      elif cLett=='\'': cLett='_'
      elif cLett=='"': cLett='_'
      elif cLett=='%': cLett='_'
      elif cLett=='[': cLett='('
      elif cLett==')': cLett=')'
      if not cReplaceExtraCharsIP==None:
        for cXlett in cReplaceExtraCharsIP:
          if cLett==cXlett: cLett='-'
      aRet(cLett)
      
    cRet=''.join(tRet)
    return cRet.replace('  ', ' ').replace('__', '_')
  
  @classmethod
  def GetFileNamesInDirectory_LastDays(cls, cDirPathIP, fNewerThanDaysIP, cFilenameMatchIP, cFilenameDontMatchIP=None):
    
    '''Get file names and timestamps of files in a directory which are modified during the last N days 

    :param    cDirPathIP:           The path
    :type     cDirPathIP:           str 
    :param    fNewerThanDaysIP:     For example '1' means 'Modified during the last 24 hours' 
    :type     fNewerThanDaysIP:     float 
    :param    cFilenameMatchIP:     File match filter, following 'fnmatch' format. Example: '*.xml'
    :type     cFilenameMatchIP:     str 
    :param    cFilenameDontMatchIP: File 'but-dont-match-these-ones' filter, applied after the previous parameter. Optional.
    :type     cFilenameDontMatchIP: str
    
    :rtype:   generator
    :returns: a list (by generator) of tuples: ( full-pathname, iso datetime file modify )
    :raises:  
    
    '''
    fNewerThanDaysIP *= 86400 # Note: convert days to seconds
    iPresent = time.time()
    for root, dummy, tFiles in os.walk(cDirPathIP, topdown=False):
      for cFile in tFiles:
        cFullPath = os.path.join(root, cFile)
        iMtime = os.path.getmtime(cFullPath)
        if (((iPresent - iMtime) <= fNewerThanDaysIP) 
               # Note: fnmatch is more expensive than the oMtime filter.
          and (fnmatch.fnmatch(cFile, cFilenameMatchIP)) 
          and (True if cFilenameDontMatchIP is None 
               else (not fnmatch.fnmatch(cFile, cFilenameDontMatchIP))
               )):
          yield (cFullPath, datetime.datetime.fromtimestamp(iMtime).isoformat())

if __name__ == '__main__':
  '''
  print sc_osfile.StripInvalidChars('jkhadsfkjh sdfhsk/ljh Ikj\sdhf *&**@# sadflskj', '/\\')
  '''

#EOF
