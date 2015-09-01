import xlsxwriter
import os
import ast

_PRETTIFY_WITH_TABLES=True

class sc_mshqtimestamp_excel_logic(object):
  
  iSummaryRow=0
  
  @classmethod
  def TimestampFileToExcel(cls, cFileIP, bPrettifyWithTablesIP=_PRETTIFY_WITH_TABLES):
    cFilepath,cFilename = os.path.split(cFileIP)
    cFilebase,dummy=os.path.splitext(cFilename)
    oWorkbook = xlsxwriter.Workbook(os.path.join(cFilepath, '{}.xlsx'.format(cFilebase)))
    oWorksheetTms = oWorkbook.add_worksheet('Timestamps')
    oWorksheetTms.set_tab_color('#11FF22')
    oWorksheetSfl = oWorkbook.add_worksheet('Sourcefiles')
    oWorksheetSfl.set_tab_color('#AA3366')
    oBold = oWorkbook.add_format({'bold': 1})
    oFixedfont = oWorkbook.add_format({'bold': 0})
    oFixedfont.set_font_name('Consolas')
    oFixedfont.set_font_size(10)
    
    class sHeading(object):
      tHeadings = ('Line', 'Time', 'ProcSeq', 'Proc', 'Delta', 'LoopStart', 'LoopDelta', 'LoopDeltaA', 'LoopDeltaB', 'VarA', 'VarB', 'Comment', 'LoopNo', 'LoopAt', 'LoopDeltaX', )
      LoopDeltaAB = [None,None]
      Line           , \
      Time           , \
      ProcSeq         , \
      Proc           , \
      Delta          , \
      LoopStart      , \
      LoopDelta      , \
      LoopDeltaAB[0] , \
      LoopDeltaAB[1] , \
      VarA           , \
      VarB           , \
      Comment        , \
      LoopNo         , \
      LoopAt         , \
      LoopDeltaX     = range(len(tHeadings))
    
    tData=[]
    for i in range(len(sHeading.tHeadings)):  
      tData.append([])
      
    fFirstTime=None
    iLoopProcSeq=None
    tProcSeq={}
    iProcSeq=1
    iTotalLines=0
    
    tSourceDicts={}
    
    # Collect all data into tData
    with open(cFileIP) as f:
      for i,cLine in enumerate(f):
        iTotalLines+=1
        tData[sHeading.Line].append(i)
        cTime,cRemainder=cLine.rstrip().partition(':')[0::2]
        cRemainder=cRemainder.lstrip()
        fTime=float(cTime)
        if fFirstTime is None: fFirstTime=fTime
        fTime-=fFirstTime
        tRemainder=cRemainder.split('\x03')
        cProc,cProcseq=tRemainder[0:2]
        cVarA,cVarB=tRemainder[5:7]
        tData[sHeading.Time].append(fTime)
        if not (cProc,cProcseq) in tProcSeq.keys():
          tProcSeq[(cProc,cProcseq)]=[iProcSeq,i,fTime]
          iProcSeq+=1
        else:
          if iLoopProcSeq is None:
            # This is a repetition; indicate as looppoint
            iLoopProcSeq=tProcSeq[(cProc,cProcseq)][0]
            # Set first looppoint to True as well
            tData[sHeading.LoopStart][tProcSeq[(cProc,cProcseq)][1]]=True
        tData[sHeading.ProcSeq].append(tProcSeq[(cProc,cProcseq)][0])
        tData[sHeading.Proc].append('{}_{}'.format(cProc,cProcseq))
        if i==0:
          tData[sHeading.Delta].append(0.0)
        else:
          fDelta = tData[sHeading.Time][-1] - tData[sHeading.Time][-2]  
          tData[sHeading.Delta].append(fDelta)
        if (not iLoopProcSeq is None) and (iLoopProcSeq==tProcSeq[(cProc,cProcseq)][0]):
          tData[sHeading.LoopStart].append(True)
        else:
          tData[sHeading.LoopStart].append(None)
        tData[sHeading.LoopDelta].append(None)
        tData[sHeading.VarA].append(cVarA)
        tData[sHeading.VarB].append(cVarB)
        cComment=''
        if not tSourceDicts.has_key((cProc,cProcseq,)):
          tEval=ast.literal_eval(tRemainder[-1]) if len(tRemainder[-1]) > 0 else None
          tSourceDicts[(cProc,cProcseq,)]=tEval
          if not tEval is None and tEval.has_key('summary'):
            cls.AddToSummary(oWorksheetTms, oFixedfont, tEval['summary'])
        else:
          tEval=tSourceDicts[(cProc,cProcseq,)]
        if not tEval is None and tEval.has_key('comment'):
          cComment= tEval['comment']
        tData[sHeading.Comment].append(cComment)
    
    # Calculate the loop delta's
    fTimePrev=None
    iLoop=0
    iPrev=0
    tLoop=[]
    for i in range(iTotalLines):
      tData[sHeading.LoopDeltaAB[(iLoop + 1) % 2]].append(None)
      tData[sHeading.LoopDeltaAB[iLoop % 2]].append(0.0)
      if not tData[sHeading.LoopStart][i] == True:
        tData[sHeading.LoopDelta][i] = None
        fZoomDelta=tData[sHeading.Time][i] - (0.0 if fTimePrev is None else fTimePrev)
        tData[sHeading.LoopDeltaAB[iLoop % 2]][i]=fZoomDelta
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
          tData[sHeading.LoopDeltaAB[iLoop % 2]][i]=0.0
          tData[sHeading.LoopDeltaAB[(iLoop + 1) % 2]][i]=fLoopDelta
        fTimePrev=tData[sHeading.Time][i]
        iPrev=i
    
    oWorksheetTms.set_column(0,0, 180)  # Column width (of summary)
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Delta total: {} seconds'.format(fTime))
    
    iDataStartRow=1
    iDataStartCol=1
   
    oNanoFormat = oWorkbook.add_format()
    oNanoFormat.set_num_format('0.000000000')
    
    def SetColumn_NanoFormat(iCol):
      oWorksheetTms.set_column(iDataStartCol+iCol,iDataStartCol+iCol,cell_format=oNanoFormat)
    
    SetColumn_NanoFormat(sHeading.Time);
    SetColumn_NanoFormat(sHeading.Delta);
    SetColumn_NanoFormat(sHeading.LoopDelta);
    
    def SetColumn_Width(iCol, iWidthIP):
      oWorksheetTms.set_column(iDataStartCol+iCol,iDataStartCol+iCol, iWidthIP)
    
    SetColumn_Width(sHeading.Line, 10)
    SetColumn_Width(sHeading.Time, 12)
    SetColumn_Width(sHeading.ProcSeq, 10)
    SetColumn_Width(sHeading.Proc, 90)
    SetColumn_Width(sHeading.Delta, 12)
    SetColumn_Width(sHeading.LoopStart, 8)
    SetColumn_Width(sHeading.LoopDelta, 12)
    SetColumn_Width(sHeading.VarA, 50)
    SetColumn_Width(sHeading.VarB, 50)
    SetColumn_Width(sHeading.Comment, 50)
    SetColumn_Width(sHeading.LoopNo, 8)
    SetColumn_Width(sHeading.LoopAt, 12)
    SetColumn_Width(sHeading.LoopDeltaX, 12)
    
    SetColumn_Width(sHeading.LoopDeltaAB[0], 14)
    SetColumn_Width(sHeading.LoopDeltaAB[1], 14)
    
    oWorksheetTms.write_row(iDataStartRow-1, iDataStartCol, sHeading.tHeadings, oBold)
    
    if bPrettifyWithTablesIP:
      
      # Optional. Gives pretty formatting and auto filters.

      # Give some columns a bit more room, because of the auto filter
      SetColumn_Width(sHeading.LoopStart, 11)
      SetColumn_Width(sHeading.LoopNo, 11)
      SetColumn_Width(sHeading.LoopDeltaX, 14)
      
      # Excel table for all data
      oWorksheetTms.add_table(0, sHeading.Line + 1, len(tData[sHeading.Line]), sHeading.Comment + 1,
        {'name': 'AllData',
         'style': 'Table Style Light 9',
         'total_row': False,
         'columns': [ {'header' : sHeading.tHeadings[x]} for x in range(sHeading.Line,sHeading.Comment + 1) ],
         })
      
      # Excel table for 'all' loops
      oWorksheetTms.add_table(0, sHeading.LoopNo + 1, len(tData[sHeading.LoopNo]), sHeading.LoopDeltaX + 1,
        {'name': 'AllLoops',
         'style': 'Table Style Light 11',
         'total_row': False,
         'columns': [ {'header' : sHeading.tHeadings[x]} for x in range(sHeading.LoopNo,sHeading.LoopDeltaX + 1) ],
         })
    
    for i in range(len(sHeading.tHeadings)):
      oWorksheetTms.write_column(iDataStartRow, iDataStartCol + i,  tData[i])
    
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Loop count: {}'.format(len(tData[sHeading.LoopDeltaX])))
    
    # Chart: all
    
    oChartAll = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartAll.add_series(
      {
        'values':  ['Timestamps', 1, sHeading.LoopDeltaX + 1, len(tData[sHeading.LoopDeltaX]), sHeading.LoopDeltaX + 1],
        'line'  :  {'color': 'gray'},
        'fill'  :  {'color': 'gray'},
        'gap'   :  0,
      }
    )
    
    oChartAll.set_legend({'none': True})    
    oChartAll.set_size({'width': 1266, 'height': 600})
    oChartAll.set_y_axis({'reverse': True})
    oChartAll.set_title({'none': True})
    oChartAll.set_x_axis({'num_format': '@'}) # Overrule the format of the referred cell; just use text format because the extra precision is clutter in the X axis    
    
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Chart: All loops, delta in seconds')
    
    # Insert the chart into the worksheet.
    oWorksheetTms.insert_chart(cls.iSummaryRow + 1, 0, oChartAll)
    cls.iSummaryRow+=30
    
    fDeltaMin=min(tData[sHeading.LoopDeltaX])
    # 1-based
    tDeltaMin=[i + 1 for i, j in enumerate(tData[sHeading.LoopDeltaX]) if j == fDeltaMin]
    iLoopFirstDeltaMin=tDeltaMin[0]
    
    fDeltaMax=max(tData[sHeading.LoopDeltaX])
    # 1-based
    tDeltaMax=[i + 1 for i, j in enumerate(tData[sHeading.LoopDeltaX]) if j == fDeltaMax]
    iLoopFirstDeltaMax=tDeltaMax[0]
    
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Fastest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMin),fDeltaMin))
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Slowest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMax),fDeltaMax))
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Slowest / fastest ratio:      (1 to {:>-17.9f})'.format(fDeltaMax / fDeltaMin))

    # Chart: slowest

    oChartSlowest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartSlowest.add_series(
      {
        'name'       :  'slowest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0] + 1, sHeading.Proc + 1, tLoop[iLoopFirstDeltaMax - 1][1] + 1, sHeading.Proc + 1],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0] + 1, sHeading.Time + 1, tLoop[iLoopFirstDeltaMax - 1][1] + 1, sHeading.Time + 1],
        'line'       :  {'color': 'silver'},
        'fill'       :  {'color': '#DD4433'},
        'gap'        :  0,
      }
    )
    
    oChartSlowest.set_legend({'none': True})    
    oChartSlowest.set_size({'width': 1266, 'height': 300})
    oChartSlowest.set_y_axis({'reverse': True})
    oChartSlowest.set_title({'none': True})
    oChartSlowest.set_x_axis({'num_format': '@'}) # Overrule the format of the referred cell; just use text format because the extra precision is clutter in the X axis

    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Chart: Slowest loop ({}), zoomed in, line {} to {}'.format(iLoopFirstDeltaMax,tLoop[iLoopFirstDeltaMax][0], tLoop[iLoopFirstDeltaMax][1]))
    
    # Insert the chart into the worksheet.
    oWorksheetTms.insert_chart(cls.iSummaryRow + 1, 0, oChartSlowest)
    cls.iSummaryRow+=15
    
    # Chart: fastest

    oChartFastest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartFastest.add_series(
      {
        'name'       :  'fastest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0] + 1, sHeading.Proc + 1, tLoop[iLoopFirstDeltaMin - 1][1] + 1, sHeading.Proc + 1],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0] + 1, sHeading.Time + 1, tLoop[iLoopFirstDeltaMin - 1][1] + 1, sHeading.Time + 1],
        'line'       :  {'color': 'silver'},
        'fill'       :  {'color': 'green'},
        'gap'        :  0,
      }
    )
    
    oChartFastest.set_legend({'none': True})    
    oChartFastest.set_size({'width': 1266, 'height': 300})
    oChartFastest.set_y_axis({'reverse': True})
    oChartFastest.set_title({'none': True})
    oChartFastest.set_x_axis({'num_format': '@'}) # Overrule the format of the referred cell; just use text format because the extra precision is clutter in the X axis    
    
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Chart: Fastest loop ({}), zoomed in, line {} to {}'.format(iLoopFirstDeltaMin,tLoop[iLoopFirstDeltaMin][0], tLoop[iLoopFirstDeltaMin][1]))
    
    # Insert the chart into the worksheet.
    oWorksheetTms.insert_chart(cls.iSummaryRow + 1, 0, oChartFastest)
    cls.iSummaryRow+=15
    
    # Chart: slowest and fastest

    oChartSlowAndFastest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartSlowAndFastest.add_series(
      {
        'name'       :  'slowest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0] + 1, sHeading.Proc + 1, tLoop[iLoopFirstDeltaMax - 1][1] + 1, sHeading.Proc + 1, ],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0] + 1, sHeading.LoopDeltaAB[(iLoopFirstDeltaMax - 1) % 2] + 1, tLoop[iLoopFirstDeltaMax - 1][1] + 1, sHeading.LoopDeltaAB[(iLoopFirstDeltaMax - 1) % 2] + 1, ],
        'line'       :  {'color': 'silver'},
        'fill'       :  {'color': '#DD4433'},
      }
    )
    
    oChartSlowAndFastest.add_series(
      {
        'name'      :  'fastest',
        'categories':  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0] + 1, sHeading.Proc + 1, tLoop[iLoopFirstDeltaMin - 1][1] + 1, sHeading.Proc + 1, ],
        'values'    :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0] + 1, sHeading.LoopDeltaAB[(iLoopFirstDeltaMin - 1) % 2] + 1, tLoop[iLoopFirstDeltaMin - 1][1] + 1, sHeading.LoopDeltaAB[(iLoopFirstDeltaMin - 1) % 2] + 1, ],
        'line'      :  {'color': 'silver'},
        'fill'      :  {'color': 'green'},
        'gap'       :  0,
      }
    )
    
    oChartSlowAndFastest.set_legend({'none': True})
    oChartSlowAndFastest.set_size({'width': 1266, 'height': 300})
    oChartSlowAndFastest.set_y_axis({'reverse': True})
    oChartSlowAndFastest.set_title({'none': True})
    oChartSlowAndFastest.set_x_axis({'num_format': '@'}) # Overrule the format of the referred cell; just use text format because the extra precision is clutter in the X axis    
    
    cls.AddToSummary(oWorksheetTms, oFixedfont, 'Chart: Slowest+Fastest comparison, loop {} and {}'.format(iLoopFirstDeltaMax,iLoopFirstDeltaMin))
    
    # Insert the chart into the worksheet.
    oWorksheetTms.insert_chart(cls.iSummaryRow + 1, 0, oChartSlowAndFastest)
    cls.iSummaryRow+=15
    
    # Freeze the first row.
    oWorksheetTms.freeze_panes(1, 0)
    
    # Close and save the excel workbook file
    oWorkbook.close()
  
  @classmethod
  def AddToSummary(cls, oWorksheetIP, oFixedfontIP, cSummaryLineIP):
    print cSummaryLineIP
    oWorksheetIP.write_string(cls.iSummaryRow + 1,0,cSummaryLineIP, oFixedfontIP)
    cls.iSummaryRow+=1
    
if __name__ == '__main__':
  sc_mshqtimestamp_excel_logic.TimestampFileToExcel(r'T:\ota\systeemtst\dataexchange\fluxdumpbig__dwan_idetest.txt')

#EOF
