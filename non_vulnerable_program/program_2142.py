    import nose
except ImportError:
    pass

def slow(t):
    """Labels a test as 'slow'.

    The exact definition of a slow test is obviously both subjective and
    hardware-dependent, but in general any individual test that requires more
    than a second or two should be labeled as slow (the whole suite consits of
    thousands of tests, so even a second is significant)."""

    t.slow = True
    return t

def setastest(tf=True):
    ''' Signals to nose that this function is or is not a test

    Parameters
    ----------
    tf : bool
        If True specifies this is a test, not a test otherwise

    e.g
    >>> @setastest(False)
    >>> def func_with_test_in_name(arg1, arg2): pass
    ...
    >>>

    This decorator cannot use the nose namespace, because it can be
    called from a non-test module. See also istest and nottest in
    nose.tools

    '''
    def set_test(t):
        t.__test__ = tf
        return t
    return set_test

def skipif(skip_condition, msg=None):
    ''' Make function raise SkipTest exception if skip_condition is true

    Parameters
    ---------
    skip_condition : bool
        Flag to determine whether to skip test (True) or not (False)
    msg : string
        Message to give on raising a SkipTest exception

   Returns
   -------
   decorator : function
       Decorator, which, when applied to a function, causes SkipTest
       to be raised when the skip_condition was True, and the function
       to be called normally otherwise.

    Notes
    -----
    You will see from the code that we had to further decorate the
    decorator with the nose.tools.make_decorator function in order to
    transmit function name, and various other metadata.
    '''
    if msg is None:
        msg = 'Test skipped due to test condition'
    def skip_decorator(f):
        def skipper(*args, **kwargs):
            if skip_condition:
                raise nose.SkipTest, msg
            else:
                return f(*args, **kwargs)
        return nose.tools.make_decorator(f)(skipper)
    return skip_decorator

def skipknownfailure(f):
    ''' Decorator to raise SkipTest for test known to fail
    '''
    def skipper(*args, **kwargs):
        raise nose.SkipTest, 'This test is known to fail'
    return nose.tools.make_decorator(f)(skipper)


''' Nose test running

Implements test and bench functions for modules.

'''
