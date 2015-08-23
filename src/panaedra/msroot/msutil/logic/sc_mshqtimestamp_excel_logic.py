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
    
    class sHeading(object):
      tHeadings = ['Line', 'Time', 'ProcID', 'Proc', 'Delta', 'LoopStart', 'LoopDelta', 'Var', 'LoopNo', 'LoopAt', 'LoopDeltaX']
      Line       = 0 
      Time       = 1
      ProcID     = 2
      Proc       = 3
      Delta      = 4
      LoopStart  = 5
      LoopDelta  = 6
      Var        = 7 
      LoopNo     = 8 
      LoopAt     = 9
      LoopDeltaX = 10
    
    tData=[]
    for i in range(len(sHeading.tHeadings)):  
      tData.append([])
    fFirstTime=None
    iLoopProcID=None
    tProcID={}
    iProcID=1
    iTotalLines=0
    with open(cFileIP) as f:
      for i,cLine in enumerate(f):
        iTotalLines+=1
        tData[sHeading.Line].append(i)
        cTime,cRemainder=cLine.rstrip().split(':')
        cRemainder=cRemainder.lstrip()
        fTime=float(cTime)
        if fFirstTime is None: fFirstTime=fTime
        fTime-=fFirstTime
        cProc,cProcseq,cVar=cRemainder.split('\x03')
        tData[sHeading.Time].append(fTime)
        if not (cProc,cProcseq) in tProcID.keys():
          tProcID[(cProc,cProcseq)]=[iProcID,i,fTime]
          iProcID+=1
        else:
          if iLoopProcID is None:
            # This is a repetition; indicate as looppoint
            iLoopProcID=tProcID[(cProc,cProcseq)][0]
            # Set first looppoint to True as well
            tData[sHeading.LoopStart][tProcID[(cProc,cProcseq)][1]]=True
        tData[sHeading.ProcID].append(tProcID[(cProc,cProcseq)][0])
        tData[sHeading.Proc].append('{}_{}'.format(cProc,cProcseq))
        if i==0:
          tData[sHeading.Delta].append(0.0)
        else:
          fDelta = tData[sHeading.Time][-1] - tData[sHeading.Time][-2]  
          tData[sHeading.Delta].append(fDelta)
        if (not iLoopProcID is None) and (iLoopProcID==tProcID[(cProc,cProcseq)][0]):
          tData[sHeading.LoopStart].append(True)
        else:
          tData[sHeading.LoopStart].append(None)
        tData[sHeading.LoopDelta].append(None)
        tData[sHeading.Var].append(cVar)
    
    # Calculate the loop delta's
    fTimePrev=None
    iLoop=0
    for i in range(iTotalLines):
      if not tData[sHeading.LoopStart][i] == True:
        tData[sHeading.LoopDelta][i] = None
      else:
        tData[sHeading.LoopDelta][i] = None
        if fTimePrev!=None:
          iLoop+=1
          fLoopDelta=tData[sHeading.Time][i] - fTimePrev
          tData[sHeading.LoopDelta][i] = fLoopDelta
          tData[sHeading.LoopNo].append(iLoop)
          tData[sHeading.LoopAt].append(tData[sHeading.Time][i])
          tData[sHeading.LoopDeltaX].append(fLoopDelta)
        fTimePrev=tData[sHeading.Time][i]
    
    oWorksheet.set_column(0,0, 80)  # Column width (of summary)
    cls.AddToSummary(oWorksheet, oFixedfont, 'Delta total: {} seconds'.format(fTime))
    
    iDataStartRow=1
    iDataStartCol=1
   
    oNanoFormat = oWorkbook.add_format()
    oNanoFormat.set_num_format('0.000000000')
    
    def SetColumn_NanoFormat(iCol):
      oWorksheet.set_column(iDataStartCol+iCol,iDataStartCol+iCol,cell_format=oNanoFormat)
    
    SetColumn_NanoFormat(sHeading.Time);
    SetColumn_NanoFormat(sHeading.Delta);
    
    def SetColumn_Width(iCol, iWidthIP):
      oWorksheet.set_column(iDataStartCol+iCol,iDataStartCol+iCol, iWidthIP)
    
    SetColumn_Width(sHeading.Line, 10)
    SetColumn_Width(sHeading.Time, 12)
    SetColumn_Width(sHeading.ProcID, 8)
    SetColumn_Width(sHeading.Proc, 90)
    SetColumn_Width(sHeading.Delta, 12)
    SetColumn_Width(sHeading.LoopStart, 8)
    SetColumn_Width(sHeading.LoopDelta, 12)
    SetColumn_Width(sHeading.Var, 50)
    SetColumn_Width(sHeading.LoopNo, 8)
    SetColumn_Width(sHeading.LoopAt, 12)
    SetColumn_Width(sHeading.LoopDeltaX, 12)
    
    oWorksheet.write_row(iDataStartRow-1, iDataStartCol, sHeading.tHeadings, oBold)
    
    for i in range(len(sHeading.tHeadings)):
      oWorksheet.write_column(iDataStartRow, iDataStartCol + i,  tData[i])
    
    # Charts
    
    oChart = oWorkbook.add_chart({'type': 'bar'})
    
    #     [sheetname, first_row, first_col, last_row, last_col]
    oChart.add_series(
      {
        'values':     ['Sheet1', 1, sHeading.LoopDeltaX + 1, len(tData[sHeading.LoopDeltaX]), sHeading.LoopDeltaX + 1],
        'line':       {'color': 'gray'},
      }
    )
        
    # Insert the chart into the worksheet.
    oWorksheet.insert_chart('A3', oChart)
    
    oWorkbook.close()
  
  @classmethod
  def AddToSummary(cls, oWorksheetIP, oFixedfontIP, cSummaryLineIP):
    print cSummaryLineIP
    oWorksheetIP.write_string(cls.iSummaryRow + 1,0,cSummaryLineIP, oFixedfontIP)
    cls.iSummaryRow+=1
    
if __name__ == '__main__':
  sc_mshqtimestamp_excel_logic.TimestampFileToExcel(r'T:\ota\systeemtst\dataexchange\fluxdumpbig__dwan_idetest.txt')

#EOF
