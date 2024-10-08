from scipy_base import *
import unittest
import scipy_base.limits



##################################################
### Test for sum

class test_float(unittest.TestCase):
    def check_nothing(self):
        pass

class test_double(unittest.TestCase):
    def check_nothing(self):
        pass

##################################################


def test_suite(level=1):
    suites = []
    if level > 0:
        suites.append( unittest.makeSuite(test_float,'check_') )
        suites.append( unittest.makeSuite(test_double,'check_') )
    
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner


if __name__ == "__main__":
    test()

""" Test functions for basic module

"""

# only for short term testing
