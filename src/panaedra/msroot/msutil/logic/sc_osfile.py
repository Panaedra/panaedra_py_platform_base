class sc_osfile(object):
  
  @classmethod
  def StripInvalidChars(cls, cFilepathIP, cReplaceExtraCharsIP=None):

    '''Strip characters that are invalid for filenames. 
       Pass slash+backslash if you want path separators stripped as well.
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


if __name__ == '__main__':
  '''
  print sc_osfile.StripInvalidChars('jkhadsfkjh sdfhsk/ljh Ikj\sdhf *&**@# sadflskj', '/\\')
  '''

#EOF
