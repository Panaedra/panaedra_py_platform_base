import xlsxwriter
import os

class sc_mshqtimestamp_excel_logic(object):
  
  iSummaryRow=0  
  
  @classmethod
  def TimestampFileToExcel(cls, cFileIP):
    cFilepath,cFilename = os.path.split(cFileIP)
    cFilebase,dummy=os.path.splitext(cFilename)
    oWorkbook = xlsxwriter.Workbook(os.path.join(cFilepath, '{}.xlsx'.format(cFilebase)))
    oWorksheet = oWorkbook.add_worksheet()
    oBold = oWorkbook.add_format({'bold': 1})
    oFixedfont = oWorkbook.add_format({'bold': 0})
    oFixedfont.set_font_name('Consolas')
    oFixedfont.set_font_size(10)
    
    tHeadings = ['Line', 'Time', 'Proc', 'Var']  
    fFirstTime=None
    tData=[[],[],[],[]]
    with open(cFileIP) as f:
      for i,cLine in enumerate(f):
        #print i, cLine.rstrip()
        tData[0].append(i)
        cTime,cRemainder=cLine.rstrip().split(':')
        cRemainder=cRemainder.lstrip()
        fTime=float(cTime)
        if fFirstTime is None: fFirstTime=fTime
        fTime-=fFirstTime
        cProc,cProcseq,cVar=cRemainder.split('\x03')
        tData[1].append(fTime)
        tData[2].append('{}_{}'.format(cProc,cProcseq))
        tData[3].append(cVar)
    
    oWorksheet.set_column(0,0, 80)  # Column width (of summary)
    cls.AddToSummary(oWorksheet, oFixedfont, 'Delta total: {} seconds'.format(fTime))
    
    iDataStartRow=1
    iDataStartCol=1
   
    oWorksheet.set_column(iDataStartCol,iDataStartCol+1, 20)  # Column width
    oWorksheet.set_column(iDataStartCol+2,iDataStartCol+2, 90)
    oWorksheet.set_column(iDataStartCol+3,iDataStartCol+3, 50)
    
    oWorksheet.write_row(iDataStartRow-1, iDataStartCol, tHeadings, oBold)
    oWorksheet.write_column(iDataStartRow, iDataStartCol,  tData[0])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+1, tData[1])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+2, tData[2])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+3, tData[3])
    
    oWorkbook.close()
  
  @classmethod
  def AddToSummary(cls, oWorksheetIP, oFixedfontIP, cSummaryLineIP):
    print cSummaryLineIP
    oWorksheetIP.write_string(cls.iSummaryRow + 1,0,cSummaryLineIP, oFixedfontIP)
    cls.iSummaryRow+=1
    
if __name__ == '__main__':
  sc_mshqtimestamp_excel_logic.TimestampFileToExcel(r'T:\ota\systeemtst\dataexchange\fluxdumpbig__dwan_idetest.txt')

#EOF
