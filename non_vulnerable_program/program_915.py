import sys
from scipy.test.testing import *
from scipy.distutils.command.build_src import appendpath
from os.path import join

class test_appendpath(ScipyTestCase):

    def check_1(self):
        assert_equal(appendpath('prefix','name'),join('prefix','name'))
        assert_equal(appendpath('/prefix','name'),join('/prefix','name'))
        assert_equal(appendpath('/prefix','/name'),join('/prefix','name'))
        assert_equal(appendpath('prefix','/name'),join('prefix','name'))

    def check_2(self):
        assert_equal(appendpath('prefix/sub','name'),
                     join('prefix','sub','name'))
        assert_equal(appendpath('prefix/sub','sup/name'),
                     join('prefix','sub','sup','name'))
        assert_equal(appendpath('/prefix/sub','/prefix/name'),
                     join('/prefix','sub','name'))

    def check_3(self):
        assert_equal(appendpath('/prefix/sub','/prefix/sup/name'),
                     join('/prefix','sub','sup','name'))
        assert_equal(appendpath('/prefix/sub/sub2','/prefix/sup/sup2/name'),
                     join('/prefix','sub','sub2','sup','sup2','name'))
        assert_equal(appendpath('/prefix/sub/sub2','/prefix/sub/sup/name'),
                     join('/prefix','sub','sub2','sup','name'))

if __name__ == "__main__":
    ScipyTest().run()


# This module is a lite version of LinAlg.py module which contains
# high-level Python interface to the LAPACK library.  The lite version
# only accesses the following LAPACK functions: dgesv, zgesv, dgeev,
# zgeev, dgesdd, zgesdd, dgelsd, zgelsd, dsyevd, zheevd, dgetrf, dpotrf.

