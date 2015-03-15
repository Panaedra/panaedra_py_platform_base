
class sc_msosfile(object):
  
  @classmethod
  def WriteStringToFile(cls, cFilepathIP, cStringIP):      
    
    with open(cFilepathIP, 'w') as strFile:
      strFile.write(cStringIP)
      strFile.close
      

  @classmethod  
  def GetFileSectionAsString(cls, cInputFilepathIP, iStartBytePositionIP, iFilePortionExtentIP):   
   
    with open(cInputFilepathIP, 'rb') as oInputFile:
      oInputFile.seek(iStartBytePositionIP, 0)
      return oInputFile.read(iFilePortionExtentIP)

  @classmethod 
  def CopyFileSection(cls, cInputFilepathIP, cOutputFilepathIP, iStartBytePositionIP, iFilePortionExtentIP): 

    with open(cInputFilepathIP, 'rb') as oInputFile:
      oInputFile.seek(iStartBytePositionIP, 0)
      with open(cOutputFilepathIP, 'wb') as oOutputFile:
        oOutputFile.write(oInputFile.read(iFilePortionExtentIP))


if __name__ == '__main__':
  
  sc_msosfile.CopyFileSection('E:/_CLOUD_test/aof_filesize_nonlive_20150313_.log', 'E:/_CLOUD_test/test.log', 1000, 2000)

#EOF


