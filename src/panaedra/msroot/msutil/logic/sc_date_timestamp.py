from datetime import datetime

class sc_date_timestamp(object):

  @classmethod  
  def cTimeStamp_Short_Date(cls):
    return '%s' % datetime.now().strftime('%Y%m%d')

  @classmethod  
  def cTimeOnly_Short_WithPeriods(cls):
    return '%s' % datetime.now().strftime('%H:%M:%S')
  
  @classmethod  
  def cTimeOnly_Long_WithPeriods(cls):
    return '%s' % datetime.now().strftime('%H:%M:%S.%f')

#EOF
