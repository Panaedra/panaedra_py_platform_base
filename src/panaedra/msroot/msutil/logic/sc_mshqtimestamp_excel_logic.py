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
    
    tHeadings = ['Line', 'Time', 'ProcID', 'Proc', 'Delta', 'LoopStart', 'LoopDelta', 'Var']  
    tData=[[],[],[],[],[],[],[],[]]
    fFirstTime=None
    iLoopProcID=None
    tProcID={}
    iProcID=1
    iTotalLines=0
    with open(cFileIP) as f:
      for i,cLine in enumerate(f):
        iTotalLines+=1
        tData[0].append(i)
        cTime,cRemainder=cLine.rstrip().split(':')
        cRemainder=cRemainder.lstrip()
        fTime=float(cTime)
        if fFirstTime is None: fFirstTime=fTime
        fTime-=fFirstTime
        cProc,cProcseq,cVar=cRemainder.split('\x03')
        tData[1].append(fTime)
        if not (cProc,cProcseq) in tProcID.keys():
          tProcID[(cProc,cProcseq)]=[iProcID,i,fTime]
          iProcID+=1
        else:
          if iLoopProcID is None:
            # This is a repetition; indicate as looppoint
            iLoopProcID=tProcID[(cProc,cProcseq)][0]
            # Set first looppoint to True as well
            tData[5][tProcID[(cProc,cProcseq)][1]]=True
        tData[2].append(tProcID[(cProc,cProcseq)][0])
        tData[3].append('{}_{}'.format(cProc,cProcseq))
        if i==0:
          tData[4].append(0.0)
        else:
          fDelta = tData[1][-1] - tData[1][-2]  
          tData[4].append(fDelta)
        if (not iLoopProcID is None) and (iLoopProcID==tProcID[(cProc,cProcseq)][0]):
          tData[5].append(True)
        else:
          tData[5].append(False)
        tData[6].append(None)  
        tData[7].append(cVar)
    
    # Calculate the loop delta's
    fTimePrev=None
    for i in range(iTotalLines):
      if not tData[5][i]:
        tData[6][i] = 0
      else:
        tData[6][i] = 0
        if fTimePrev!=None:
          tData[6][i] = tData[1][i] - fTimePrev
        fTimePrev=tData[1][i]
    
    oWorksheet.set_column(0,0, 80)  # Column width (of summary)
    cls.AddToSummary(oWorksheet, oFixedfont, 'Delta total: {} seconds'.format(fTime))
    
    iDataStartRow=1
    iDataStartCol=1
   
    oNanoFormat = oWorkbook.add_format()
    oNanoFormat.set_num_format('0.000000000')
    oWorksheet.set_column(iDataStartCol+1,iDataStartCol+1,cell_format=oNanoFormat)
    oWorksheet.set_column(iDataStartCol+4,iDataStartCol+4,cell_format=oNanoFormat)
    
    oWorksheet.set_column(iDataStartCol,iDataStartCol, 10)  # Column width
    oWorksheet.set_column(iDataStartCol+1,iDataStartCol+1, 15)
    oWorksheet.set_column(iDataStartCol+2,iDataStartCol+2, 10)
    oWorksheet.set_column(iDataStartCol+3,iDataStartCol+3, 90)
    oWorksheet.set_column(iDataStartCol+4,iDataStartCol+4, 15)
    oWorksheet.set_column(iDataStartCol+5,iDataStartCol+5, 10)
    oWorksheet.set_column(iDataStartCol+6,iDataStartCol+6, 15)
    oWorksheet.set_column(iDataStartCol+7,iDataStartCol+7, 50)
    
    oWorksheet.write_row(iDataStartRow-1, iDataStartCol, tHeadings, oBold)
    oWorksheet.write_column(iDataStartRow, iDataStartCol,  tData[0])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+1, tData[1])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+2, tData[2])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+3, tData[3])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+4, tData[4])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+5, tData[5])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+6, tData[6])
    oWorksheet.write_column(iDataStartRow, iDataStartCol+7, tData[7])
    
    oWorkbook.close()
  
  @classmethod
  def AddToSummary(cls, oWorksheetIP, oFixedfontIP, cSummaryLineIP):
    print cSummaryLineIP
    oWorksheetIP.write_string(cls.iSummaryRow + 1,0,cSummaryLineIP, oFixedfontIP)
    cls.iSummaryRow+=1
    
if __name__ == '__main__':
  sc_mshqtimestamp_excel_logic.TimestampFileToExcel(r'T:\ota\systeemtst\dataexchange\fluxdumpbig__dwan_idetest.txt')

#EOF
