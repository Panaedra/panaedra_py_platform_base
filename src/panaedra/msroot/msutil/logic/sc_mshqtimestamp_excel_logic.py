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
    oWorksheetSmy = oWorkbook.add_worksheet('Summary')
    oWorksheetSmy.set_tab_color('#8888FF')
    oWorksheetTms = oWorkbook.add_worksheet('Timestamps')
    oWorksheetTms.set_tab_color('#11FF22')
    oWorksheetLps = oWorkbook.add_worksheet('Loops')
    oWorksheetLps.set_tab_color('#11F182')
    oWorksheetWat = oWorkbook.add_worksheet('Watches')
    oWorksheetWat.set_tab_color('#F1E122')
    oWorksheetSfl = oWorkbook.add_worksheet('Sourcefiles')
    oWorksheetSfl.set_tab_color('#BB77EE')
    oBold = oWorkbook.add_format({'bold': 1})
    oFixedfont = oWorkbook.add_format({'bold': 0})
    oFixedfont.set_font_name('Consolas')
    oFixedfont.set_font_size(10)
    
    class sHeadingTms(object):
      tHeadings = ('Line', 'Time', 'VarA', 'VarB', 'Comment', 'ProcUid', 'Proc', 'Delta', 'LoopStart', 'LoopDelta', 'LoopDeltaA', 'LoopDeltaB', )
      LoopDeltaAB = [None,None]
      Line           , \
      Time           , \
      VarA           , \
      VarB           , \
      Comment        , \
      ProcUid        , \
      Proc           , \
      Delta          , \
      LoopStart      , \
      LoopDelta      , \
      LoopDeltaAB[0] , \
      LoopDeltaAB[1] = range(len(tHeadings))
    
    class sHeadingLps(object):
      tHeadings = ('LoopNo', 'LoopAt', 'LoopDeltaX', )
      LoopNo         , \
      LoopAt         , \
      LoopDeltaX     = range(len(tHeadings))
    
    tDataTms=[]
    for i in range(len(sHeadingTms.tHeadings)):  
      tDataTms.append([])
      
    tDataLps=[]
    for i in range(len(sHeadingTms.tHeadings)):  
      tDataLps.append([])
      
    fFirstTime=None
    iLoopProcUid=None
    tProcUid={}
    iProcUid=1
    iTotalLines=0
    tSourceDicts={}
    
    # Collect all data into tDataTms
    with open(cFileIP) as f:
      for i,cLine in enumerate(f):
        if cLine.startswith('Hqts_Additional_Info:'):
          cEval=cLine.rstrip().partition(':')[2].lstrip()
          if cEval.startswith('{'):
            tAdditionalInfo=ast.literal_eval(cEval)
            if tAdditionalInfo.has_key('summary'):
              cls.AddToSummary(oWorksheetSmy, oFixedfont, tAdditionalInfo['summary'])
        else:
          iTotalLines+=1
          tDataTms[sHeadingTms.Line].append(i+1)
          cTime,cRemainder=cLine.rstrip().partition(':')[0::2]
          cRemainder=cRemainder.lstrip()
          fTime=float(cTime)
          if fFirstTime is None: fFirstTime=fTime
          fTime-=fFirstTime
          tRemainder=cRemainder.split('\x03')
          cProc,cProcseq=tRemainder[0:2]
          cVarA,cVarB=tRemainder[5:7]
          tDataTms[sHeadingTms.Time].append(fTime)
          if not (cProc,cProcseq) in tProcUid.keys():
            tProcUid[(cProc,cProcseq)]=[iProcUid,i,fTime]
            iProcUid+=1
          else:
            if iLoopProcUid is None:
              # This is a repetition; indicate as looppoint
              iLoopProcUid=tProcUid[(cProc,cProcseq)][0]
              # Set first looppoint to True as well
              tDataTms[sHeadingTms.LoopStart][tProcUid[(cProc,cProcseq)][1]]=True
          tDataTms[sHeadingTms.ProcUid].append(tProcUid[(cProc,cProcseq)][0])
          if iTotalLines==1:
            tDataTms[sHeadingTms.Delta].append(0.0)
          else:
            fDelta = tDataTms[sHeadingTms.Time][-1] - tDataTms[sHeadingTms.Time][-2]  
            tDataTms[sHeadingTms.Delta].append(fDelta)
          if (not iLoopProcUid is None) and (iLoopProcUid==tProcUid[(cProc,cProcseq)][0]):
            tDataTms[sHeadingTms.LoopStart].append(True)
          else:
            tDataTms[sHeadingTms.LoopStart].append(None)
          tDataTms[sHeadingTms.LoopDelta].append(None)
          tDataTms[sHeadingTms.VarA].append(cVarA)
          tDataTms[sHeadingTms.VarB].append(cVarB)
          cComment,cProcID='',''
          if not tSourceDicts.has_key((cProc,cProcseq,)):
            tEval=ast.literal_eval(tRemainder[-1]) if len(tRemainder[-1]) > 0 else None
            tSourceDicts[(cProc,cProcseq,)]=tEval
            if not tEval is None and tEval.has_key('summary'):
              cls.AddToSummary(oWorksheetSmy, oFixedfont, tEval['summary'])
          else:
            tEval=tSourceDicts[(cProc,cProcseq,)]
          if not tEval is None and tEval.has_key('comment'):
            cComment= tEval['comment']
          tDataTms[sHeadingTms.Comment].append(cComment)
          if not tEval is None and tEval.has_key('id'):
            cProcID= tEval['id']
          tDataTms[sHeadingTms.Proc].append('{}_{}{}'.format(cProc,cProcseq, '_{}'.format(cProcID) if len(cProcID) > 0 else ''))
    
    # Calculate the loop delta's
    fTimePrev=None
    iLoop=0
    iPrev=0
    tLoop=[]
    for i in range(iTotalLines):
      tDataTms[sHeadingTms.LoopDeltaAB[(iLoop + 1) % 2]].append(None)
      tDataTms[sHeadingTms.LoopDeltaAB[iLoop % 2]].append(0.0)
      if not tDataTms[sHeadingTms.LoopStart][i] == True:
        tDataTms[sHeadingTms.LoopDelta][i] = None
        fZoomDelta=tDataTms[sHeadingTms.Time][i] - (0.0 if fTimePrev is None else fTimePrev)
        tDataTms[sHeadingTms.LoopDeltaAB[iLoop % 2]][i]=fZoomDelta
      else:
        tDataTms[sHeadingTms.LoopDelta][i] = None
        if fTimePrev!=None:
          iLoop+=1
          fLoopDelta=tDataTms[sHeadingTms.Time][i] - fTimePrev
          tDataTms[sHeadingTms.LoopDelta][i] = fLoopDelta
          tDataLps[sHeadingLps.LoopNo].append(iLoop)
          tDataLps[sHeadingLps.LoopAt].append(tDataTms[sHeadingTms.Time][i])
          tDataLps[sHeadingLps.LoopDeltaX].append(fLoopDelta)
          tLoop.append([iPrev,i])
          tDataTms[sHeadingTms.LoopDeltaAB[iLoop % 2]][i]=0.0
          tDataTms[sHeadingTms.LoopDeltaAB[(iLoop + 1) % 2]][i]=fLoopDelta
        fTimePrev=tDataTms[sHeadingTms.Time][i]
        iPrev=i
    
    oWorksheetSmy.set_column(0, 0, 180)  # Column width (of summary)
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Delta total: {} seconds'.format(fTime))
    
    iDataStartRow=1
    iDataStartCol=0
   
    oNanoFormat = oWorkbook.add_format()
    oNanoFormat.set_num_format('0.000000000')
    
    def SetColumnTms_NanoFormat(iCol):
      oWorksheetTms.set_column(iDataStartCol+iCol,iDataStartCol+iCol,cell_format=oNanoFormat)
    
    SetColumnTms_NanoFormat(sHeadingTms.Time);
    SetColumnTms_NanoFormat(sHeadingTms.Delta);
    SetColumnTms_NanoFormat(sHeadingTms.LoopDelta);
    
    def SetColumnTms_Width(iCol, iWidthIP):
      oWorksheetTms.set_column(iDataStartCol+iCol,iDataStartCol+iCol, iWidthIP)
    
    SetColumnTms_Width(sHeadingTms.Line, 10)
    SetColumnTms_Width(sHeadingTms.Time, 12)
    SetColumnTms_Width(sHeadingTms.ProcUid, 10)
    SetColumnTms_Width(sHeadingTms.Proc, 90)
    SetColumnTms_Width(sHeadingTms.Delta, 12)
    SetColumnTms_Width(sHeadingTms.LoopStart, 8)
    SetColumnTms_Width(sHeadingTms.LoopDelta, 12)
    SetColumnTms_Width(sHeadingTms.VarA, 50)
    SetColumnTms_Width(sHeadingTms.VarB, 50)
    SetColumnTms_Width(sHeadingTms.Comment, 50)
    SetColumnTms_Width(sHeadingTms.LoopDeltaAB[0], 14)
    SetColumnTms_Width(sHeadingTms.LoopDeltaAB[1], 14)
    
    def SetColumnLps_Width(iCol, iWidthIP):
      oWorksheetLps.set_column(iCol,iCol, iWidthIP)
    
    SetColumnLps_Width(sHeadingLps.LoopNo, 8)
    SetColumnLps_Width(sHeadingLps.LoopAt, 12)
    SetColumnLps_Width(sHeadingLps.LoopDeltaX, 12)
    
    oWorksheetTms.write_row(iDataStartRow-1, iDataStartCol, sHeadingTms.tHeadings, oBold)
    oWorksheetLps.write_row(0, 0, sHeadingLps.tHeadings, oBold)
    
#     if bPrettifyWithTablesIP:
#       
#       # Optional. Gives pretty formatting and auto filters.
# 
#       # Give some columns a bit more room, because of the auto filter
#       SetColumn_Width(sHeadingTms.LoopStart, 11)
#       SetColumn_Width(sHeadingTms.LoopNo, 11)
#       SetColumn_Width(sHeadingTms.LoopDeltaX, 14)
#       
#       # Excel table for all data
#       oWorksheetTms.add_table(0, sHeadingTms.Line, len(tData[sHeadingTms.Line]), sHeadingTms.LoopDeltaAB[1],
#         {'name': 'AllData',
#          'style': 'Table Style Light 9',
#          'total_row': False,
#          'columns': [ {'header' : sHeadingTms.tHeadings[x]} for x in range(sHeadingTms.Line - 1,sHeadingTms.LoopDeltaAB[1]) ],
#          })
#       
#       # Excel table for 'all' loops
#       oWorksheetTms.add_table(0, sHeadingTms.LoopNo, len(tData[sHeadingTms.LoopNo]), sHeadingTms.LoopDeltaX,
#         {'name': 'AllLoops',
#          'style': 'Table Style Light 11',
#          'total_row': False,
#          'columns': [ {'header' : sHeadingTms.tHeadings[x]} for x in range(sHeadingTms.LoopNo - 1,sHeadingTms.LoopDeltaX) ],
#          })
    
    for i in range(len(sHeadingTms.tHeadings)):
      oWorksheetTms.write_column(iDataStartRow, iDataStartCol + i,  tDataTms[i])
      
    for i in range(len(sHeadingLps.tHeadings)):
      oWorksheetLps.write_column(iDataStartRow, iDataStartCol + i,  tDataLps[i])
    
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Loop count: {}'.format(len(tDataLps[sHeadingLps.LoopDeltaX])))
    
    # Chart: all
    
    oChartAll = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartAll.add_series(
      {
        'name'       :  'loops',
        'categories' :  ['Loops', 1, sHeadingLps.LoopNo, len(tDataLps[sHeadingLps.LoopNo]), sHeadingLps.LoopNo],
        'values'     :  ['Loops', 1, sHeadingLps.LoopDeltaX, len(tDataLps[sHeadingLps.LoopDeltaX]), sHeadingLps.LoopDeltaX],
        'line'       :  {'color': 'gray'},
        'fill'       :  {'color': 'gray'},
        'gap'        :  0,
      }
    )
    
    oChartAll.set_legend({'none': True})    
    oChartAll.set_size({'width': 1266, 'height': 600})
    oChartAll.set_y_axis({'reverse': True})
    oChartAll.set_title({'none': True})
    oChartAll.set_x_axis({'num_format': '@'}) # Overrule the format of the referred cell; just use text format because the extra precision is clutter in the X axis    
    
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Chart: All loops, delta in seconds')
    
    # Insert the chart into the worksheet.
    oWorksheetSmy.insert_chart(cls.iSummaryRow + 1, 0, oChartAll)
    cls.iSummaryRow+=30
    
    fDeltaMin=min(tDataLps[sHeadingLps.LoopDeltaX])
    # 1-based
    tDeltaMin=[i + 1 for i, j in enumerate(tDataLps[sHeadingLps.LoopDeltaX]) if j == fDeltaMin]
    iLoopFirstDeltaMin=tDeltaMin[0]
    
    fDeltaMax=max(tDataLps[sHeadingLps.LoopDeltaX])
    # 1-based
    tDeltaMax=[i + 1 for i, j in enumerate(tDataLps[sHeadingLps.LoopDeltaX]) if j == fDeltaMax]
    iLoopFirstDeltaMax=tDeltaMax[0]
    
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Fastest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMin),fDeltaMin))
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Slowest loop: iteration {:>10}, {:>-17.9f} seconds'.format(repr(tDeltaMax),fDeltaMax))
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Slowest / fastest ratio:      (1 to {:>-17.9f})'.format(fDeltaMax / fDeltaMin))

    # Chart: slowest

    oChartSlowest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartSlowest.add_series(
      {
        'name'       :  'slowest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0], sHeadingTms.Proc, tLoop[iLoopFirstDeltaMax - 1][1], sHeadingTms.Proc],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0], sHeadingTms.Time, tLoop[iLoopFirstDeltaMax - 1][1], sHeadingTms.Time],
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

    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Chart: Slowest loop ({}), zoomed in, line {} to {}'.format(iLoopFirstDeltaMax,tLoop[iLoopFirstDeltaMax][0], tLoop[iLoopFirstDeltaMax][1]))
    
    # Insert the chart into the worksheet.
    oWorksheetSmy.insert_chart(cls.iSummaryRow + 1, 0, oChartSlowest)
    cls.iSummaryRow+=15
    
    # Chart: fastest

    oChartFastest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartFastest.add_series(
      {
        'name'       :  'fastest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0], sHeadingTms.Proc, tLoop[iLoopFirstDeltaMin - 1][1], sHeadingTms.Proc],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0], sHeadingTms.Time, tLoop[iLoopFirstDeltaMin - 1][1], sHeadingTms.Time],
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
    
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Chart: Fastest loop ({}), zoomed in, line {} to {}'.format(iLoopFirstDeltaMin,tLoop[iLoopFirstDeltaMin][0], tLoop[iLoopFirstDeltaMin][1]))
    
    # Insert the chart into the worksheet.
    oWorksheetSmy.insert_chart(cls.iSummaryRow + 1, 0, oChartFastest)
    cls.iSummaryRow+=15
    
    # Chart: slowest and fastest

    oChartSlowAndFastest = oWorkbook.add_chart({'type': 'bar'})
    # [sheetname, first_row, first_col, last_row, last_col]
    oChartSlowAndFastest.add_series(
      {
        'name'       :  'slowest',
        'categories' :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0], sHeadingTms.Proc, tLoop[iLoopFirstDeltaMax - 1][1], sHeadingTms.Proc, ],
        'values'     :  ['Timestamps', tLoop[iLoopFirstDeltaMax - 1][0], sHeadingTms.LoopDeltaAB[(iLoopFirstDeltaMax - 1) % 2], tLoop[iLoopFirstDeltaMax - 1][1], sHeadingTms.LoopDeltaAB[(iLoopFirstDeltaMax - 1) % 2], ],
        'line'       :  {'color': 'silver'},
        'fill'       :  {'color': '#DD4433'},
      }
    )
    
    oChartSlowAndFastest.add_series(
      {
        'name'      :  'fastest',
        'categories':  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0], sHeadingTms.Proc, tLoop[iLoopFirstDeltaMin - 1][1], sHeadingTms.Proc, ],
        'values'    :  ['Timestamps', tLoop[iLoopFirstDeltaMin - 1][0], sHeadingTms.LoopDeltaAB[(iLoopFirstDeltaMin - 1) % 2], tLoop[iLoopFirstDeltaMin - 1][1], sHeadingTms.LoopDeltaAB[(iLoopFirstDeltaMin - 1) % 2], ],
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
    
    cls.AddToSummary(oWorksheetSmy, oFixedfont, 'Chart: Slowest+Fastest comparison, loop {} and {}'.format(iLoopFirstDeltaMax,iLoopFirstDeltaMin))
    
    # Insert the chart into the worksheet.
    oWorksheetSmy.insert_chart(cls.iSummaryRow + 1, 0, oChartSlowAndFastest)
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
