from panaedra.msroot.msutil.logic.c_log_postponed import c_log_postponed


class sc_log_postponed(object): 
  
  @classmethod
  def GetLoggerPostponed(cls):
    '''get a (new) logging object'''
    return c_log_postponed()

   
if __name__ == '__main__':
  oLog = sc_log_postponed.GetLoggerPostponed()
  oLog.WriteStatusLn('TSTSTSTSTSTST SSSSSTTT')
  oLog.WriteEmptyLn()
  oLog.SetColumnProperties('''{
                                "column4" : {
                                  "format"      : "{:<20}"
                                },
                                "column2" : {
                                  "format"      : "{:<30}"
                                },
                                "column3" : {
                                  "format"      : "{:<30}"
                                }
                              }
                           ''') 
 
  oLog.WriteStatusColumnHeaders()
  oLog.WriteDictToStatusLn({'column1': 123, 'column2': 'test zinnetje' })
  oLog.WriteDictToStatusLn({'column1': 3, 'column2': 'spin' })
  oLog.WriteDictToStatusLn({'column1': 7, 'column3': 'testje' })
 
  print oLog.ToString()
  """
  """
# EOF   