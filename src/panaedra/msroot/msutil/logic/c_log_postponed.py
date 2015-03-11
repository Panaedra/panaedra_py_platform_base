import datetime
import json
import re

from collections import OrderedDict


class c_log_postponed(object): 
  
  def __init__(self):

    self.oRegexMatchDigit  = re.compile(r'\d+') 
    self.cDatetimeFormat   = '{:<21}'
    self.tStatusLn         = []
  
  def GetFormattedDatetime(self):
    
    return self.cDatetimeFormat.format(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
  
  
  def GetJsonAsOrderedDict(self, cJsonIP): 

    return json.loads(cJsonIP, object_pairs_hook=OrderedDict)
  
  
  def SetColumnProperties(self, cColumnPropertiesAsJsonIP): 
    
    self.tColumnProperties = self.GetJsonAsOrderedDict(cColumnPropertiesAsJsonIP)
    
  
  def GetStatusDictAsString(self, tStatusDictIP):
 
    cStatusLn = ''
    if self.tColumnProperties is None: 
      for cStatusDictKey in tStatusDictIP.iterkeys(): 
        cStatusLn = '{0} {1}'.format(cStatusLn, tStatusDictIP[cStatusDictKey])
    else:   
      for cColumnTitle in self.tColumnProperties.keys(): 
        tOneColumnProperty = self.tColumnProperties[cColumnTitle]
        if isinstance(tOneColumnProperty, (dict)) and \
           tOneColumnProperty.has_key('format')   and \
           tStatusDictIP.has_key(cColumnTitle): 
          cColumnLn = tStatusDictIP[cColumnTitle]
        else: 
          cColumnLn = '' 
        cStatusLn += tOneColumnProperty['format'].format(cColumnLn)
        
    return cStatusLn 
   
   
  def WriteStatusColumnHeaders(self): 
    if not self.tColumnProperties is None: 
      cColumnHeaderLine = ''
      for cColumnTitle in self.tColumnProperties.iterkeys(): 
        tOneColumnProperty = self.tColumnProperties[cColumnTitle]
        if isinstance(tOneColumnProperty, (dict)) and tOneColumnProperty.has_key('format'): 
          cColumnHeaderLine += tOneColumnProperty['format'].format(cColumnTitle)  
      self.WriteStatusLn(cColumnHeaderLine, bDatetimeStamp=False)  
      self.WriteStatusLn(self.WriteHeaderSeparatorLines(), bDatetimeStamp=False)  

    
  def WriteHeaderSeparatorLines(self): 
    cColumnHeaderLine = ''
    for cColumnTitle in self.tColumnProperties.iterkeys(): 
      cColumnHeaderLine += '{s:{c}^{n}}'.format(s='',n=self.oRegexMatchDigit.search(self.tColumnProperties[cColumnTitle]['format']).group(0),c='-')
    return cColumnHeaderLine
  
  
  def WriteDictToStatusLn(self, tStatusDictIP): 
    
    if isinstance(tStatusDictIP, (dict)): 
      self.WriteStatusLn(self.GetStatusDictAsString(tStatusDictIP))
    else: 
      raise TypeError('The input to WriteStatusArrayToLn is not a dictionary {}')


  def WriteStatusLn(self, cStatusLnIP, bDatetimeStamp=True):
    
    if bDatetimeStamp:
      self.tStatusLn.append(self.GetFormattedDatetime() + cStatusLnIP)
    else: 
      self.tStatusLn.append(self.cDatetimeFormat.format('') + cStatusLnIP)
  
  def WriteStatusEmptyLn(self):
    
    self.tStatusLn.append('') 

  
  def ToString(self): 
      
    cLogAsMemory = '' 
    for cStatusLn in self.tStatusLn: 
      cLogAsMemory += '{}\n'.format(cStatusLn)
    return cLogAsMemory 
    
    
if __name__ == '__main__':
  """
  oLog = c_log_postponed()
  oLog.WriteStatusLn("test test test")
  oLog.WriteStatusEmptyLn()
  oLog.SetColumnProperties('''{
                                "column1" : {
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
  oLog.WriteDictToStatusLn({'column1': 4321, 'column2': 'test sentence' })
  oLog.WriteDictToStatusLn({'column1': 3, 'column2': 'etst' })
  oLog.WriteDictToStatusLn({'column1': 7, 'column3': 'test tset' })
 
  print oLog.ToString()
  """
# EOF   