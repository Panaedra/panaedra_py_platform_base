import os, sys
import json
from copy import deepcopy

from panaedra.msroot.msutil.logic.sc_mspysys import sc_mspysys
from panaedra.msroot.msutil.logic.sc_date_timestamp import sc_date_timestamp
from panaedra.msroot.msutil.logic.c_msdecorator_base import decoratorbase

class c_mshelper_numretries(object):
  '''
  Helper object. Retry a certain action a fixed number of times. 
  Retry time can be increased for each retry iteration.
  
  You can use this class standalone, or as a decorator (see below).   
   
  Example:
    from panaedra.msroot.msutil.logic.c_mshelper_numretries import num_retries
    @num_retries(max_tries=3, exc_types=[TypeError,ZeroDivisionError])
    def i_will_fail():
      cTypeError = '%s' % (1,2,3) 
      iOtherError = 1 / 0 
      print "This won't be reached: %s %s" % (cTypeError, iOtherError)
     
  '''
  
  def __init__(self,  
    func=None, callobject=None, func_args=(), func_kwargs={}, 
    max_tries=5, retry_seconds=[0.3, 1.0, 5.0], 
    exc_types=[ZeroDivisionError], stderr_feedback=True,
    retry_func=[None], retry_args=(), retry_kwargs={}):
    ''' Constructor
    
    :param    callobject:      If OO, the OO object to be used for 'self' or 'cls', else None
    :type     callobject:      object 
    :param    func:            The function to be called
    :type     func:            function 
    :param    func_args:       list of arguments for the function to be called
    :type     func_args:       list 
    :param    func_kwargs:     dict of keyword arguments for the function to be called
    :type     func_kwargs:     dict 
    :param    stderr_feedback: Set to False if no feedback report is to be written to stderr on final fail/raise
    :type     stderr_feedback: bool
    :param    max_tries:       An exception is raised after max_tries is reached. max_tries=1 does not retry. max_tries=0 does nothing at all.
    :type     max_tries:       int 
    :param    retry_seconds:   Can be 1 float, or a list of floats. I.E.: [0.5, 1.0, 5.0] will wait 0.5 seconds after the first fail, 1.0 seconds after the second fail, 5.0 seconds after fail three to N. 
    :type     retry_seconds:   list 
    :param    exc_types:       If any thrown exception is not in this list, no retries will be done and the exception will be raised as normal. If the list is [Exception], any exception will be retried. 
    :type     exc_types:       list 
    :param    retry_func:      Can be 1 function pointer, or a list of function pointers. Use retry_args=['self'] Entries with None are handled as no-ops. Called if except, post-pause. len(list) should be one less than max_retries, rest is ignored. I.E.: [onfirst, onrest] will execute onfirst on the first iteration, and onrest on all other iterations 
    :type     retry_func:      list 
    :param    retry_args:      list of arguments for all (!) retry functions. Use retry_args=['self'] for object methods, it will be substituted with the self handle.
    :type     retry_args:      list 
    :param    retry_kwargs:    dict of keyword arguments for all (!) retry functions
    :type     retry_kwargs:    dict 
    
    :rtype:   c_mshelper_numretries
    :returns: a reusable object for retry loops
    '''
    self.oCallSelf=callobject
    self.aFunc=func
    self.tFuncArgs=func_args
    self.tFuncKwArgs=func_kwargs
    self.iMaxTries=max_tries
    self.tRetrySeconds=retry_seconds
    self.tExcTypes=exc_types
    self.tRetryFunc=retry_func
    self.tRetryArgs=retry_args
    self.tRetryKwArgs=retry_kwargs
    self.bStderrFeedback=stderr_feedback
    self.tFeedback=[]
    self._tArgsMod=None
    
    # To avoid lingering circular references at exceptions within exceptions,
    # local variables should not be used. We use data members here for all 
    # calls to sys.exc_info().
    self._nolingr_oExcType=None
    self._nolingr_oExcObj=None
    self._nolingr_oExcTb=None
  
  def execute(self, oCallSelf=None):
    iRetry=0
    while iRetry < self.iMaxTries:
      iRetry += 1
      try:
        if self.oCallSelf is None:
          return self.aFunc(*self.tFuncArgs,**self.tFuncKwArgs)
        else:
          if self._tArgsMod is None:
            self._tArgsMod=list(self.tFuncArgs) 
            self._tArgsMod.insert(0, self.oCallSelf)  
          return self.aFunc(*self._tArgsMod,**self.tFuncKwArgs)
        break
      except:
        self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb = sys.exc_info()
        if not self._nolingr_oExcType in self.tExcTypes:
          # Avoid lingering circular references
          del(self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb)
          raise
        fname = os.path.split(self._nolingr_oExcTb.tb_frame.f_code.co_filename)[1]
        if self.bStderrFeedback:
          self.tFeedback.append((
            sc_date_timestamp.cTimeOnly_Long_WithPeriods(),
            deepcopy(self._nolingr_oExcType.__name__), 
            "{0}:{1}".format(fname,self._nolingr_oExcTb.tb_lineno),))
        # Avoid lingering circular references
        del(self._nolingr_oExcType, self._nolingr_oExcObj, self._nolingr_oExcTb)
        if iRetry == self.iMaxTries:
          if self.bStderrFeedback:
            sys.stderr.write(json.dumps(self.tFeedback,indent=2))
            sys.stderr.write('\n')
            sys.stderr.flush()
          raise
      fPause = self.tRetrySeconds if not hasattr(self.tRetrySeconds, '__iter__') else self.tRetrySeconds[min(len(self.tRetrySeconds), iRetry) - 1]
      if fPause > 0.0:  
        sc_mspysys.Sleep(fPause)
      aRetry = self.tRetryFunc if not hasattr(self.tRetryFunc, '__iter__') else self.tRetryFunc[min(len(self.tRetryFunc), iRetry) - 1]
      if not aRetry is None:
        if self.tRetryArgs is None: self.tRetryArgs = []
        elif 'self' in self.tRetryArgs:
          self.tRetryArgs[self.tRetryArgs.index('self')] = oCallSelf 
        if self.tRetryKwArgs is None: self.tRetryKwArgs = {}
        aRetry(*self.tRetryArgs, **self.tRetryKwArgs)

class num_retries(decoratorbase):
  '''
  Decorator. Works for functions as well as methods.
  
  Parenthesis are mandatory, like this: 
    @num_retries()
  You can use any parameters of the c_mshelper_numretries constructor, like this: 
    @num_retries(max_tries=4,retry_seconds=[1.0,2.0],exc_types=[TimeoutError])
  '''
  def runphase(self, *cargs):
    oNumRetries = c_mshelper_numretries(*self._cargs, **self._ikwargs)
    if len(self._fargs) > 0:
      oNumRetries.oCallSelf = self._fargs[0] 
      oNumRetries.tFuncArgs = self._fargs[1:] if len(self._fargs) > 1 else []  
    if len(self._fkwargs) > 0:
      oNumRetries.tFuncKwArgs = self._fkwargs  
    return oNumRetries.execute(oNumRetries.oCallSelf)

#EOF
