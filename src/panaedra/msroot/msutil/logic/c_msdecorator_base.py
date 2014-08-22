import sys

_DEBUG_DECORATOR=False

class _runfallback(object):
  '''
  Fallback class. You should roll your own. 
  
  Argument/parameter support is trivial, and not implemented in this fallback.
  
  Pay attention to 'firstparam', which you can rename, but should be 
  kept *first* because of positional parameters.
  
  '''
  def __init__(self, firstparam=None, callobject=None):
    self.aFunc=firstparam
    self.oCallObject=callobject
    self.oCallSelf=None
    self.tFuncArgs=[]
    self.tFuncKwArgs={}
  def execute(self, oCallSelf=None):
    self.oCallSelf=oCallSelf
    if self.oCallSelf is None:  
      return self.aFunc(*self.tFuncArgs, **self.tFuncKwArgs)
    else:
      return self.aFunc(self.oCallSelf, *self.tFuncArgs, **self.tFuncKwArgs)
    
class decoratorbase(object):
  '''
  Decorator base. Works for functions as well as methods.
  
  Parenthesis are mandatory, like this: 
    @num_retries()
  You can use any parameters of the constructor in the linked object, like this: 
    @num_retries(max_tries=4,retry_seconds=[1.0,2.0],exc_types=[TimeoutError])
  '''
  
  def __init__(self, *iargs, **ikwargs):
    '''If there are decorator arguments, the function
       to be decorated is *not* passed to the constructor.'''
    self._iargs = iargs
    self._ikwargs = ikwargs
    self._cargs = None
    self._fargs = None
    self._fkwargs = None
    if len(iargs) > 0:
      '''If parameters are omitted, no object pointer is passed in case of object methods. 
         To avoid confusion, we make parenthesis mandatory, even for non-OO.'''
      raise ImportError('This decorator requires parameters, like this: @num_retries()')
    if _DEBUG_DECORATOR:
      sys.stderr.write('INIT phase: %s %s\n' % (repr(self._iargs),repr(self._ikwargs)))

  def __call__(self, *cargs):
    '''If there are decorator arguments, __call__() is only
       called once, as part of the decoration process.'''
    self._cargs = cargs
    if _DEBUG_DECORATOR:
      sys.stderr.write('SETUP phase %s %s %s %s %s\n' % (repr(self._iargs),repr(self._ikwargs),repr(self._cargs),repr(self._fargs),repr(self._fkwargs)))
    def wrapped_f(*fargs,**fkwargs):
      self._fargs=fargs
      self._fkwargs=fkwargs
      if _DEBUG_DECORATOR:
        sys.stderr.write('WRAP phase: _iargs=%s | _ikwargs=%s | _cargs=%s | _fargs=%s | _fkwargs=%s\n' % (repr(self._iargs),repr(self._ikwargs),repr(self._cargs),repr(self._fargs),repr(self._fkwargs)))
      if len(self._cargs) >= 1:
        if _DEBUG_DECORATOR:
          sys.stderr.write('RUN phase: start.\n')
        oRet=self.runphase()  
        if _DEBUG_DECORATOR:
          sys.stderr.write('RUN phase: done.\n')
        return oRet
    return wrapped_f

  def runphase(self, *cargs):
    '''You should completely override this method. abstract / example.'''
    oFallback = _runfallback(*self._cargs, **self._ikwargs)
    if len(self._fargs) > 0:
      oFallback.oCallSelf = self._fargs[0] 
      oFallback.tFuncArgs = self._fargs[1:] if len(self._fargs) > 1 else []  
    if len(self._fkwargs) > 0:
      oFallback.tFuncKwArgs = self._fkwargs  
    return oFallback.execute(oFallback.oCallSelf)

#EOF
