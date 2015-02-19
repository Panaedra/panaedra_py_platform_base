
class sc_msosfile(object):
  
  @classmethod
  def WriteStringToFile(cls, cFilepathIP, cStringIP):      
    
    with open(cFilepathIP, "w") as strFile:
      strFile.write(cStringIP)
      strFile.close

#EOF


