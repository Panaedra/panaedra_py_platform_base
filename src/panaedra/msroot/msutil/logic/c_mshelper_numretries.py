import os, sys
from panaedra.msroot.msutil.logic.sc_mspysys import sc_mspysys

class c_mshelper_numretries(object):
  '''Helper object. Retry a certain action a fixed number of times. 
     Retry time can be increased for each retry iteration.
   
   Example:
     from panaedra.msroot.msutil.logic.c_mshelper_numretries import num_retries
     @num_retries(max_tries=3, exc_types=[TypeError,ZeroDivisionError])
     def i_will_fail():
       cTypeError = '%s' % (1,2,3) 
       iOtherError = 1 / 0 
       print "This won't be reached: %s %s" % (cTypeError, iOtherError)
     
  '''
  
  @staticmethod
  def _decorator(*args,**kwargs):
    def wrap(func):
      kwargs['func']=func
      return c_mshelper_numretries(**kwargs).execute()
    return wrap
  
  def __init__(self, 
    func=None, func_args=(), func_kwargs={}, 
    max_tries=5, retry_seconds=[0.3, 1.0, 2.5, 5.0], 
    exc_types=[TypeError,ValueError], 
    retry_func=[None], retry_args=(), retry_kwargs={}):
    ''' Constructor
    
    :param    func:           The function to be called
    :type     func:           function 
    :param    func_args:      list of arguments for the function to be called
    :type     func_args:      list 
    :param    func_kwargs:    dict of keyword arguments for the function to be called
    :type     func_kwargs:    dict 
    :param    max_tries:      An exception is raised after max_tries is reached. max_tries=1 does not retry. max_tries=0 does nothing at all.
    :type     max_tries:      int 
    :param    retry_seconds:  Can be 1 float, or a list of floats. I.E.: [0.5, 1.0, 5.0] will wait 0.5 seconds after the first fail, 1.0 seconds after the second fail, 5.0 seconds after fail three to N. 
    :type     retry_seconds:  list 
    :param    exc_types:      If any thrown exception is not in this list, no retries will be done and the exception will be raised as normal. If the list is [Exception], any exception will be retried. 
    :type     exc_types:      list 
    :param    retry_func:     Can be 1 function pointer, or a list of function pointers. Entries with None are handled as no-ops. Called if except, post-pause. len(list) should be one less than max_retries, rest is ignored. I.E.: [onfirst, onrest] will execute onfirst on the first iteration, and onrest on all other iterations 
    :type     retry_func:     list 
    :param    retry_args:     list of arguments for all (!) retry functions
    :type     retry_args:     list 
    :param    retry_kwargs:   dict of keyword arguments for all (!) retry functions
    :type     retry_kwargs:   dict 
    
    :rtype:   c_mshelper_numretries
    :returns: a reusable object for retry loops
    '''
    self.aFunc=func
    self.tFuncArgs=func_args
    self.tFuncKwArgs=func_kwargs
    self.iMaxTries=max_tries
    self.tRetrySeconds=retry_seconds
    self.tExcTypes=exc_types
    self.tRetryFunc=retry_func
    self.tRetryArgs=retry_args
    self.tRetryKwArgs=retry_kwargs
    
    # To avoid lingering circular references at exceptions within exceptions,
    # local variables should not be used. We use data members here for all 
    # calls to sys.exc_info().
    self._nolingr_oExcType=None
    self._nolingr_oExcObj=None
    self._nolingr_oExcTb=None
  
  def execute(self):
    iRetry = 0
    while iRetry < self.iMaxTries:
      iRetry += 1
      try:
        self.aFunc(*self.tFuncArgs,**self.tFuncKwArgs)
        break
      except:
        self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb = sys.exc_info()
        if not self._nolingr_oExcType in self.tExcTypes:
          # Avoid lingering circular references
          del(self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb)
          raise
        fname = os.path.split(self._nolingr_oExcTb.tb_frame.f_code.co_filename)[1]
        print iRetry, repr(self._nolingr_oExcType), fname, self._nolingr_oExcTb.tb_lineno
        # Avoid lingering circular references
        del(self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb)
        if iRetry == self.iMaxTries: 
          raise
      fPause = self.tRetrySeconds if not hasattr(self.tRetrySeconds, '__iter__') else self.tRetrySeconds[min(len(self.tRetrySeconds), iRetry) - 1]  
      sc_mspysys.Sleep(fPause)
      aRetry = self.tRetryFunc if not hasattr(self.tRetryFunc, '__iter__') else self.tRetryFunc[min(len(self.tRetryFunc), iRetry) - 1]
      if not aRetry is None:
        aRetry(*self.tRetryArgs, **self.tRetryKwArgs)

# to be used as decorator:
num_retries=c_mshelper_numretries._decorator

#EOF
