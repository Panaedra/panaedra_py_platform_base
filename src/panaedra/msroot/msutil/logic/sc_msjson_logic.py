from datetime import datetime

def outputJSON(obj):
  '''Default JSON serializer.'''
  if isinstance(obj, datetime):
    if obj.utcoffset() is not None:
      obj = obj - obj.utcoffset()
    return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
  return str(obj)

def inputJSON(obj):
  '''Default JSON reader.'''
  newDic = {}
  for key in obj:
    try:
      newDic[str(key)] = datetime.strptime(obj[key], '%Y-%m-%d %H:%M:%S.%f')
      continue
    except (TypeError, ValueError):
      pass
    newDic[str(key)] = obj[key]  
  return newDic  

#EOF
