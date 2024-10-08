import unittest
from scipy_base.testing import assert_array_equal, assert_equal
from scipy_base.testing import assert_almost_equal, assert_array_almost_equal
from scipy_base import *

class test_grid(unittest.TestCase):
    def check_basic(self):
        a = mgrid[-1:1:10j]
        b = mgrid[-1:1:0.1]
        assert(a.shape == (10,))
        assert(b.shape == (20,))
        assert(a[0] == -1)
        assert_almost_equal(a[-1],1)
        assert(b[0] == -1)
        assert_almost_equal(b[1]-b[0],0.1,11)
        assert_almost_equal(b[-1],b[0]+19*0.1,11)
        assert_almost_equal(a[1]-a[0],2.0/9.0,11)

    def check_nd(self):
        c = mgrid[-1:1:10j,-2:2:10j]
        d = mgrid[-1:1:0.1,-2:2:0.2]
        assert(c.shape == (2,10,10))
        assert(d.shape == (2,20,20))
        assert_array_equal(c[0][0,:],-ones(10,'d'))
        assert_array_equal(c[1][:,0],-2*ones(10,'d'))
        assert_array_almost_equal(c[0][-1,:],ones(10,'d'),11)
        assert_array_almost_equal(c[1][:,-1],2*ones(10,'d'),11)
        assert_array_almost_equal(d[0,1,:]-d[0,0,:], 0.1*ones(20,'d'),11)
        assert_array_almost_equal(d[1,:,1]-d[1,:,0], 0.2*ones(20,'d'),11)

class test_concatenator(unittest.TestCase):
    def check_1d(self):
        assert_array_equal(r_[1,2,3,4,5,6],array([1,2,3,4,5,6]))
        b = ones(5)
        c = r_[b,0,0,b]
        assert_array_equal(c,[1,1,1,1,1,0,0,1,1,1,1,1])
        c = c_[b,0,0,b]
        assert_array_equal(c,[1,1,1,1,1,0,0,1,1,1,1,1])

    def check_2d(self):
        b = rand(5,5)
        c = rand(5,5)
        d = c_[b,c]  # append columns
        assert(d.shape == (5,10))
        assert_array_equal(d[:,:5],b)
        assert_array_equal(d[:,5:],c)
        d = r_[b,c]
        assert(d.shape == (10,5))
        assert_array_equal(d[:5,:],b)
        assert_array_equal(d[5:,:],c)

#-----------------------------------------------------------------------------

def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append( unittest.makeSuite(test_grid,'check_') )
        suites.append( unittest.makeSuite(test_concatenator,'check_') )
    
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner


if __name__ == "__main__":
    test()

""" Test functions for limits module.

    Currently empty -- not sure how to test these values
    and routines as they are machine dependent.  Suggestions?
"""

