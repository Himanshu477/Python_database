import numpy
from numpy.lib.arraysetops import *
restore_path()

##################################################

class test_aso( ScipyTestCase ):
    ##
    # 03.11.2005, c
    def check_unique1d( self ):

        a = numpy.array( [5, 7, 1, 2, 1, 5, 7] )

        ec = numpy.array( [1, 2, 5, 7] )
        c = unique1d( a )
        assert_array_equal( c, ec )

    ##
    # 03.11.2005, c
    def check_intersect1d( self ):

        a = numpy.array( [5, 7, 1, 2] )
        b = numpy.array( [2, 4, 3, 1, 5] )

        ec = numpy.array( [1, 2, 5] )
        c = intersect1d( a, b )
        assert_array_equal( c, ec )

    ##
    # 03.11.2005, c
    def check_intersect1d_nu( self ):

        a = numpy.array( [5, 5, 7, 1, 2] )
        b = numpy.array( [2, 1, 4, 3, 3, 1, 5] )

        ec = numpy.array( [1, 2, 5] )
        c = intersect1d_nu( a, b )
        assert_array_equal( c, ec )

    ##
    # 03.11.2005, c
    def check_setxor1d( self ):

        a = numpy.array( [5, 7, 1, 2] )
        b = numpy.array( [2, 4, 3, 1, 5] )

        ec = numpy.array( [3, 4, 7] )
        c = setxor1d( a, b )
        assert_array_equal( c, ec )

        a = numpy.array( [1, 2, 3] )
        b = numpy.array( [6, 5, 4] )

        ec = numpy.array( [1, 2, 3, 4, 5, 6] )
        c = setxor1d( a, b )
        assert_array_equal( c, ec )

        a = numpy.array( [1, 8, 2, 3] )
        b = numpy.array( [6, 5, 4, 8] )

        ec = numpy.array( [1, 2, 3, 4, 5, 6] )
        c = setxor1d( a, b )
        assert_array_equal( c, ec )


    ##
    # 03.11.2005, c
    def check_setmember1d( self ):

        a = numpy.array( [5, 7, 1, 2] )
        b = numpy.array( [2, 4, 3, 1, 5] )

        ec = numpy.array( [True, False, True, True] )
        c = setmember1d( a, b )
        assert_array_equal( c, ec )

        a[0] = 8
        ec = numpy.array( [False, False, True, True] )
        c = setmember1d( a, b )
        assert_array_equal( c, ec )

        a[0], a[3] = 4, 8
        ec = numpy.array( [True, False, True, False] )
        c = setmember1d( a, b )
        assert_array_equal( c, ec )

    ##
    # 03.11.2005, c
    def check_union1d( self ):

        a = numpy.array( [5, 4, 7, 1, 2] )
        b = numpy.array( [2, 4, 3, 3, 2, 1, 5] )

        ec = numpy.array( [1, 2, 3, 4, 5, 7] )
        c = union1d( a, b )
        assert_array_equal( c, ec )

    ##
    # 03.11.2005, c
    # 09.01.2006
    def check_setdiff1d( self ):

        a = numpy.array( [6, 5, 4, 7, 1, 2] )
        b = numpy.array( [2, 4, 3, 3, 2, 1, 5] )

        ec = numpy.array( [6, 7] )
        c = setdiff1d( a, b )
        assert_array_equal( c, ec )

        a = numpy.arange( 21 )
        b = numpy.arange( 19 )
        ec = numpy.array( [19, 20] )
        c = setdiff1d( a, b )
        assert_array_equal( c, ec )


    ##
    # 03.11.2005, c
    def check_manyways( self ):

        nItem = 100
        a = numpy.fix( nItem / 10 * numpy.random.random( nItem ) )
        b = numpy.fix( nItem / 10 * numpy.random.random( nItem ) )

        c1 = intersect1d_nu( a, b )
        c2 = unique1d( intersect1d( a, b ) )    
        assert_array_equal( c1, c2 )

        a = numpy.array( [5, 7, 1, 2, 8] )
        b = numpy.array( [9, 8, 2, 4, 3, 1, 5] )

        c1 = setxor1d( a, b )
        aux1 = intersect1d( a, b )
        aux2 = union1d( a, b )
        c2 = setdiff1d( aux2, aux1 )
        assert_array_equal( c1, c2 )

if __name__ == "__main__":
    ScipyTest().run()


"""Fortran to Python Interface Generator.

"""

postpone_import = True


"""
Enhanced distutils with Fortran compilers support and more.
"""

postpone_import = True


