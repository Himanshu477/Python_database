import numpy as np
from numpy.testing import *
from numpy.testing.noseclasses import KnownFailureTest
import nose

def test_slow():
    @dec.slow
    def slow_func(x,y,z):
        pass

    assert(slow_func.slow)

def test_setastest():
    @dec.setastest()
    def f_default(a):
        pass

    @dec.setastest(True)
    def f_istest(a):
        pass

    @dec.setastest(False)
    def f_isnottest(a):
        pass

    assert(f_default.__test__)
    assert(f_istest.__test__)
    assert(not f_isnottest.__test__)

class DidntSkipException(Exception): 
    pass

def test_skip_functions_hardcoded():
    @dec.skipif(True)
    def f1(x):
        raise DidntSkipException

    try:
        f1('a')
    except DidntSkipException:
        raise Exception('Failed to skip')
    except nose.SkipTest:
        pass

    @dec.skipif(False)
    def f2(x):
        raise DidntSkipException

    try:
        f2('a')
    except DidntSkipException:
        pass
    except nose.SkipTest:
        raise Exception('Skipped when not expected to')


def test_skip_functions_callable():
    def skip_tester():
        return skip_flag == 'skip me!'

    @dec.skipif(skip_tester)
    def f1(x):
        raise DidntSkipException

    try:
        skip_flag = 'skip me!'
        f1('a')
    except DidntSkipException:
        raise Exception('Failed to skip')
    except nose.SkipTest:
        pass

    @dec.skipif(skip_tester)
    def f2(x):
        raise DidntSkipException

    try:
        skip_flag = 'five is right out!'
        f2('a')
    except DidntSkipException:
        pass
    except nose.SkipTest:
        raise Exception('Skipped when not expected to')


def test_skip_generators_hardcoded():
    @dec.knownfailureif(True, "This test is known to fail")
    def g1(x):
        for i in xrange(x):
            yield i

    try:
        for j in g1(10):
            pass
    except KnownFailureTest:
        pass
    else:
        raise Exception('Failed to mark as known failure')


    @dec.knownfailureif(False, "This test is NOT known to fail")
    def g2(x):
        for i in xrange(x):
            yield i
        raise DidntSkipException('FAIL')

    try:
        for j in g2(10):
            pass
    except KnownFailureTest:
        raise Exception('Marked incorretly as known failure')
    except DidntSkipException:
        pass


def test_skip_generators_callable():
    def skip_tester():
        return skip_flag == 'skip me!'

    @dec.knownfailureif(skip_tester, "This test is known to fail")
    def g1(x):
        for i in xrange(x):
            yield i

    try:
        skip_flag = 'skip me!'
        for j in g1(10):
            pass
    except KnownFailureTest:
        pass
    else:
        raise Exception('Failed to mark as known failure')


    @dec.knownfailureif(skip_tester, "This test is NOT known to fail")
    def g2(x):
        for i in xrange(x):
            yield i
        raise DidntSkipException('FAIL')

    try:
        skip_flag = 'do not skip'
        for j in g2(10):
            pass
    except KnownFailureTest:
        raise Exception('Marked incorretly as known failure')
    except DidntSkipException:
        pass


if __name__ == '__main__':
    run_module_suite()






"""
=========
Constants
=========

Numpy includes several constants:

%(constant_list)s
"""
