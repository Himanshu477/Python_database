import time
import numpy

##
# 03.11.2005, c
def ediff1d( ar1, toEnd = None, toBegin = None ):
    """Array difference with prefixed and/or appended value."""
    dar1 = ar1[1:] - ar1[:-1]
    if toEnd and toBegin:
        shape = (ar1.shape[0] + 1,) + ar1.shape[1:]
        ed = numpy.empty( shape, dtype = ar1.dtype )
        ed[0], ed[-1] = toBegin, toEnd
        ed[1:-1] = dar1
    elif toEnd:
        ed = numpy.empty( ar1.shape, dtype = ar1.dtype )
        ed[-1] = toEnd
        ed[:-1] = dar1
    elif toBegin:
        ed = numpy.empty( ar1.shape, dtype = ar1.dtype )
        ed[0] = toBegin
        ed[1:] = dar1
    else:
        ed = dar1

    return ed


##
# 01.11.2005, c
# 02.11.2005
def unique1d( ar1, retIndx = False ):
    """Unique elements of 1D array. When retIndx is True, return also the
    indices indx such that ar1[indx] is the resulting array of unique
    elements."""
    ar = numpy.array( ar1 ).ravel()
    if retIndx:
        perm = numpy.argsort( ar )
        aux = numpy.take( ar, perm )
        flag = ediff1d( aux, 1 ) != 0
        return numpy.compress( flag, perm ), numpy.compress( flag, aux )
    else:
        aux = numpy.sort( ar )
        return numpy.compress( ediff1d( aux, 1 ) != 0, aux ) 

##
# 01.11.2005, c
def intersect1d( ar1, ar2 ):
    """Intersection of 1D arrays with unique elements."""
    aux = numpy.sort( numpy.concatenate( (ar1, ar2 ) ) )
    return numpy.compress( (aux[1:] - aux[:-1]) == 0, aux )

##
# 01.11.2005, c
def intersect1d_nu( ar1, ar2 ):
    """Intersection of 1D arrays with any elements."""
    # Might be faster then unique1d( intersect1d( ar1, ar2 ) )?
    aux = numpy.sort( numpy.concatenate( (unique1d( ar1 ),
                                          unique1d( ar2  )) ) )
    return numpy.compress( (aux[1:] - aux[:-1]) == 0, aux )

##
# 01.11.2005, c
def setxor1d( ar1, ar2 ):
    """Set exclusive-or of 1D arrays with unique elements."""
    aux = numpy.sort( numpy.concatenate( (ar1, ar2 ) ) )
    flag = ediff1d( aux, toEnd = 1, toBegin = 1 ) == 0
    flag2 = ediff1d( flag, 0 ) == 0
    return numpy.compress( flag2, aux )

##
# 03.11.2005, c
# 05.01.2006
def setmember1d( ar1, ar2 ):
    """Return an array of shape of ar1 containing 1 where the elements of
    ar1 are in ar2 and 0 otherwise."""
    ar = numpy.concatenate( (ar1, ar2 ) )
    tt = numpy.concatenate( (numpy.zeros_like( ar1 ),
                             numpy.zeros_like( ar2 ) + 1) )
    perm = numpy.argsort( ar )
    aux = numpy.take( ar, perm )
    aux2 = numpy.take( tt, perm )
    flag = ediff1d( aux, 1 ) == 0

    ii = numpy.where( flag * aux2 )
    aux = perm[ii+1]
    perm[ii+1] = perm[ii]
    perm[ii] = aux

    indx = numpy.argsort( perm )[:len( ar1 )]

    return numpy.take( flag, indx )

##
# 03.11.2005, c
def union1d( ar1, ar2 ):
    """Union of 1D arrays with unique elements."""
    return unique1d( numpy.concatenate( (ar1, ar2) ) )

##
# 03.11.2005, c
def setdiff1d( ar1, ar2 ):
    """Set difference of 1D arrays with unique elements."""
    aux = setmember1d( ar1, ar2 )
    return numpy.compress( aux == 0, ar1 )

##
# 02.11.2005, c
def test_unique1d_speed( plotResults = False ):
#    exponents = numpy.linspace( 2, 7, 9 )
    exponents = numpy.linspace( 2, 6, 9 )
    ratios = []
    nItems = []
    dt1s = []
    dt2s = []
    for ii in exponents:

        nItem = 10 ** ii
        print 'using %d items:' % nItem
        a = numpy.fix( nItem / 10 * numpy.random.random( nItem ) )

        print 'dictionary:'
        tt = time.clock() 
        b = numpy.unique( a )
        dt1 = time.clock() - tt
        print dt1

        print 'array:'
        tt = time.clock() 
        c = unique1d( a )
        dt2 = time.clock() - tt
        print dt2


        if dt1 < 1e-8:
            ratio = 'ND'
        else:
            ratio = dt2 / dt1
        print 'ratio:', ratio
        print 'nUnique: %d == %d\n' % (len( b ), len( c ))

        nItems.append( nItem )
        ratios.append( ratio )
        dt1s.append( dt1 )
        dt2s.append( dt2 )

        assert numpy.alltrue( b == c )


    print nItems
    print dt1s
    print dt2s
    print ratios

    if plotResults:
