import gc
import sys
import inspect
import threading

class sc_mspysys(object):
  
  @classmethod
  def MicroSleep(cls, cMillisecondsIP):
    '''Called by bridge. Does the same as time.sleep(), but enables responding to signals like kill -2 (SIGINT) '''
    iMillisecondsIP = int(cMillisecondsIP)
    dummy_event = threading.Event()
    dummy_event.wait(timeout=iMillisecondsIP / 1000.0)
    return ''
    
  @classmethod
  def Sleep(cls, seconds):
    '''Python called only. Does the same as time.sleep(), but enables responding to signals like kill -2 (SIGINT). Note: In python 3, time.sleep is implemented as interruptable. 
    @type seconds: float
    '''
    dummy_event = threading.Event()
    dummy_event.wait(timeout=seconds)
    return ''
  
  @classmethod
  def AllObjectsToTrash(cls, cDataIP):
    '''Called by bridge. 
       Does a 'del' on all class objects. 
       Prevents core dumps at the end of an ABL session. 
       For manual investigation: use DumpAllObjects()
    '''
    tObjects=gc.get_objects()
    for o in tObjects:
      if getattr(o, "__class__", None):
        del o
    return ''

  @classmethod
  def DumpAllObjects(cls,tFindFilter=[],oStream=None):
    '''For example, call:
       # with open('/mydir/mydump.log','wb') as f:
       #   sc_mspysys.DumpAllObjects(tFindFilter=['edis','sc_', 'c_clients', 'Connection', 'Lock', 'Thread', 'Queue', 'Event',],oStream=f)
    '''
    exclude = [
        "function",
        "type",
        "list",
        "dict",
        "tuple",
        "wrapper_descriptor",
        "module",
        "method_descriptor",
        "member_descriptor",
        "instancemethod",
        "builtin_function_or_method",
        "frame",
        "classmethod",
        "classmethod_descriptor",
        "_Environ",
        "MemoryError",
        "_Printer",
        "_Helper",
        "getset_descriptor",
        ]
    gc.collect()
    oo = gc.get_objects()
    if oStream is None: oStream = sys.stdout
    for o in oo:
      try:
        if getattr(o, "__class__", None):
          name = o.__class__.__name__
          if name not in exclude:
            filename = ''
            try:
              filename = inspect.getabsfile(o.__class__)
            except:            
              filename = repr(o.__class__)
            bFiltered=False
            if len(tFindFilter) > 0:
              bFiltered=True
              for item in tFindFilter:
                if name.find(item) >= 0:
                  bFiltered=False
                  break 
            if not bFiltered:
              oStream.write("Object of class: {0} ... defined in file: {1}\n".format(name,filename))
              oStream.flush()
      except:
        pass         
    
#EOF
