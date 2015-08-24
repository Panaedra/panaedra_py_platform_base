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
      Line        , \
      Time        , \
      ProcID      , \
      Proc        , \
      Delta       , \
      LoopStart   , \
      LoopDelta   , \
      Var         , \
      LoopNo      , \
      LoopAt      , \
      LoopDeltaX  = range(len(tHeadings))
    
    tData=[]
    for i in range(len(sHeading.tHeadings)):  
      tData.append([])
      
    fFirstTime=None
    iLoopProcID=None
    tProcID={}
    iProcID=1
    iTotalLines=0
    
    # Collect all data into tData
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
    iPrev=0
    tLoop=[]
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
          tLoop.append([iPrev,i])
        fTimePrev=tData[sHeading.Time][i]
        iPrev=i
    
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
    SetColumn_NanoFormat(sHeading.LoopDelta);
    
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
    
    cls.AddToSummary(oWorksheet, oFixedfont, 'Loop count: {}'.format(len(tData[sHeading.LoopDeltaX])))
    
    # Chart: all
    
    oChartAll = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartAll.add_series(
      {
        'values':     ['Sheet1', 1, sHeading.LoopDeltaX + 1, len(tData[sHeading.LoopDeltaX]), sHeading.LoopDeltaX + 1],
        'line':       {'color': 'gray'},
      }
    )
    
    oChartAll.set_legend({'none': True})    
    oChartAll.set_size({'width': 565, 'height': 300})
    oChartAll.set_y_axis({'reverse': True})
    
    cls.AddToSummary(oWorksheet, oFixedfont, 'Chart: All loops, delta in seconds')
    
    # Insert the chart into the worksheet.
    oWorksheet.insert_chart(cls.iSummaryRow + 1, 0, oChartAll)
    cls.iSummaryRow+=15
    
    fDeltaMin=min(tData[sHeading.LoopDeltaX])
    # 1-based
    tDeltaMin=[i + 1 for i, j in enumerate(tData[sHeading.LoopDeltaX]) if j == fDeltaMin]
    
    fDeltaMax=max(tData[sHeading.LoopDeltaX])
    # 1-based
    tDeltaMax=[i + 1 for i, j in enumerate(tData[sHeading.LoopDeltaX]) if j == fDeltaMax]
    
    cls.AddToSummary(oWorksheet, oFixedfont, 'Fastest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMin),fDeltaMin))
    cls.AddToSummary(oWorksheet, oFixedfont, 'Slowest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMax),fDeltaMax))
    cls.AddToSummary(oWorksheet, oFixedfont, 'Slowest / faster ratio:       (1 to {:>-17.9f})'.format(fDeltaMax / fDeltaMin))

    # Chart: slowest

    oChartSlowest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartSlowest.add_series(
      {
        'values':     ['Sheet1', tLoop[tDeltaMax[0]][0] + 1, sHeading.Time + 1, tLoop[tDeltaMax[0]][1] + 1, sHeading.Time + 1],
        'line':       {'color': 'gray'},
      }
    )
    
    oChartSlowest.set_legend({'none': True})    
    oChartSlowest.set_size({'width': 565, 'height': 300})
    oChartSlowest.set_y_axis({'reverse': True})
    
    cls.AddToSummary(oWorksheet, oFixedfont, 'Chart: Slowest loop, zoomed in, line {} to {}'.format(tLoop[tDeltaMax[0]][0], tLoop[tDeltaMax[0]][1]))
    
    # Insert the chart into the worksheet.
    oWorksheet.insert_chart(cls.iSummaryRow + 1, 0, oChartSlowest)
    cls.iSummaryRow+=15
    
    # Chart: fastest

    oChartFastest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartFastest.add_series(
      {
        'values':     ['Sheet1', tLoop[tDeltaMin[0]][0] + 1, sHeading.Time + 1, tLoop[tDeltaMin[0]][1] + 1, sHeading.Time + 1],
        'line':       {'color': 'gray'},
      }
    )
    
    oChartFastest.set_legend({'none': True})    
    oChartFastest.set_size({'width': 565, 'height': 300})
    oChartFastest.set_y_axis({'reverse': True})
    
    cls.AddToSummary(oWorksheet, oFixedfont, 'Chart: Fastest loop, zoomed in, line {} to {}'.format(tLoop[tDeltaMin[0]][0], tLoop[tDeltaMin[0]][1]))
    
    # Insert the chart into the worksheet.
    oWorksheet.insert_chart(cls.iSummaryRow + 1, 0, oChartFastest)
    cls.iSummaryRow+=15
    
    oWorkbook.close()
  
  @classmethod
  def AddToSummary(cls, oWorksheetIP, oFixedfontIP, cSummaryLineIP):
    print cSummaryLineIP
    oWorksheetIP.write_string(cls.iSummaryRow + 1,0,cSummaryLineIP, oFixedfontIP)
    cls.iSummaryRow+=1
    
if __name__ == '__main__':
  sc_mshqtimestamp_excel_logic.TimestampFileToExcel(r'T:\ota\systeemtst\dataexchange\fluxdumpbig__dwan_idetest.txt')

#EOF
