import types
import Numeric
from Numeric import *

__all__ = ['round','any','all','logspace','linspace','fix','mod',
           'select','trim_zeros','amax','amin','ptp','cumsum',
           'prod','cumprod','diff','angle','unwrap','sort_complex']

round = Numeric.around
any = Numeric.sometrue
all = Numeric.alltrue

def logspace(start,stop,num=50,endpoint=1):
    """ Evenly spaced samples on a logarithmic scale.

        Return num evenly spaced samples from 10**start to 10**stop.  If
        endpoint=1 then last sample is 10**stop.
    """
    if endpoint:
        step = (stop-start)/float((num-1))
        y = Numeric.arange(0,num) * step + start
    else:
        step = (stop-start)/float(num)
        y = Numeric.arange(0,num) * step + start
    return Numeric.power(10.0,y)

def linspace(start,stop,num=50,endpoint=1,retstep=0):
    """ Evenly spaced samples.
    
        Return num evenly spaced samples from start to stop.  If endpoint=1 then
        last sample is stop. If retstep is 1 then return the step value used.
    """
    if endpoint:
        step = (stop-start)/float((num-1))
        y = Numeric.arange(0,num) * step + start        
    else:
        step = (stop-start)/float(num)
        y = Numeric.arange(0,num) * step + start
    if retstep:
        return y, step
    else:
        return y

def fix(x):
    """ Round x to nearest integer towards zero.
    """
    x = Numeric.asarray(x)
    y = Numeric.floor(x)
    return Numeric.where(x<0,y+1,y)

def mod(x,y):
    """ x - y*floor(x/y)
    
        For numeric arrays, x % y has the same sign as x while
        mod(x,y) has the same sign as y.
    """
    return x - y*Numeric.floor(x*1.0/y)

def select(condlist, choicelist, default=0):
    """ Returns an array comprised from different elements of choicelist
        depending on the list of conditions.

        condlist is a list of condition arrays containing ones or zeros
    
        choicelist is a list of choice matrices (of the "same" size as the
        arrays in condlist).  The result array has the "same" size as the
        arrays in choicelist.  If condlist is [c0,...,cN-1] then choicelist
        must be of length N.  The elements of the choicelist can then be
        represented as [v0,...,vN-1]. The default choice if none of the
        conditions are met is given as the default argument. 
    
        The conditions are tested in order and the first one statisfied is
        used to select the choice. In other words, the elements of the
        output array are found from the following tree (notice the order of
        the conditions matters):
    
        if c0: v0
        elif c1: v1
        elif c2: v2
        ...
        elif cN-1: vN-1
        else: default
    
        Note, that one of the condition arrays must be large enough to handle
        the largest array in the choice list.
    """
    n = len(condlist)
    n2 = len(choicelist)
    if n2 != n:
        raise ValueError, "List of cases, must be same length as the list of conditions."
    choicelist.insert(0,default)    
    S = 0
    pfac = 1
    for k in range(1,n+1):
        S += k * pfac * asarray(condlist[k-1])
        if k < n:
            pfac *= (1-asarray(condlist[k-1]))
    # handle special case of a 1-element condition but
    #  a multi-element choice
    if type(S) in ScalarType or max(asarray(S).shape)==1:
        pfac = asarray(1)
        for k in range(n2+1):
            pfac = pfac + asarray(choicelist[k])            
        S = S*ones(asarray(pfac).shape)
    return choose(S, tuple(choicelist))

# Basic operations
def amax(m,axis=-1):
    """Returns the maximum of m along dimension axis. 
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:
        m = asarray(m)
    return maximum.reduce(m,axis)

def amin(m,axis=-1):
    """Returns the minimum of m along dimension axis.
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:        
        m = asarray(m)
    return minimum.reduce(m,axis)

# Actually from Basis, but it fits in so naturally here...

def ptp(m,axis=-1):
    """Returns the maximum - minimum along the the given dimension
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:
        m = asarray(m)
    return amax(m,axis)-amin(m,axis)

def cumsum(m,axis=-1):
    """Returns the cumulative sum of the elements along the given axis
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:
        m = asarray(m)
    return add.accumulate(m,axis)

def prod(m,axis=-1):
    """Returns the product of the elements along the given axis
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:
        m = asarray(m)
    return multiply.reduce(m,axis)

def cumprod(m,axis=-1):
    """Returns the cumulative product of the elments along the given axis
    """
    if axis is None:
        m = ravel(m)
        axis = 0
    else:
        m = asarray(m)
    return multiply.accumulate(m,axis)

def diff(x, n=1,axis=-1):
    """Calculates the nth order, discrete difference along given axis.
    """
    x = asarray(x)
    nd = len(x.shape)
    slice1 = [slice(None)]*nd
    slice2 = [slice(None)]*nd
    slice1[axis] = slice(1,None)
    slice2[axis] = slice(None,-1)
    if n > 1:
        return diff(x[slice1]-x[slice2], n-1, axis=axis)
    else:
        return x[slice1]-x[slice2]

def angle(z,deg=0):
    """Return the angle of complex argument z."""
    if deg:
        fact = 180/pi
    else:
        fact = 1.0
    z = asarray(z)
    if z.typecode() in ['D','F']:
       zimag = z.imag
       zreal = z.real
    else:
       zimag = 0
       zreal = z
    return arctan2(zimag,zreal) * fact

def unwrap(p,discont=pi,axis=-1):
    """unwrap(p,discont=pi,axis=-1)

    unwraps radian phase p by changing absolute jumps greater than discont to
    their 2*pi complement along the given axis.
    """
    p = asarray(p)
    nd = len(p.shape)
    dd = diff(p,axis=axis)
    slice1 = [slice(None,None)]*nd     # full slices
    slice1[axis] = slice(1,None)
    ddmod = mod(dd+pi,2*pi)-pi
    putmask(ddmod,(ddmod==-pi) & (dd > 0),pi)
    ph_correct = ddmod - dd;
    putmask(ph_correct,abs(dd)<discont,0)
    up = array(p,copy=1,typecode='d')
    up[slice1] = p[slice1] + cumsum(ph_correct,axis)
    return up

def sort_complex(a):
    """ Doesn't currently work for integer arrays -- only float or complex.
    """
    a = asarray(a,typecode=a.typecode().upper())
    def complex_cmp(x,y):
        res = cmp(x.real,y.real)
        if res == 0:
            res = cmp(x.imag,y.imag)
        return res
    l = a.tolist()                
    l.sort(complex_cmp)
    return array(l)

def trim_zeros(filt,trim='fb'):
    """ Trim the leading and trailing zeros from a 1D array.
    
        Example:
            >>> import scipy
            >>> a = array((0,0,0,1,2,3,2,1,0))
            >>> scipy.trim_zeros(a)
            array([1, 2, 3, 2, 1])
    """
    first = 0
    if 'f' in trim or 'F' in trim:
        for i in filt:
            if i != 0.: break
            else: first = first + 1
    last = len(filt)
    if 'b' in trim or 'B' in trim:
        for i in filt[::-1]:
            if i != 0.: break
            else: last = last - 1
    return filt[first:last]

#-----------------------------------------------------------------------------
# Test Routines
#-----------------------------------------------------------------------------

def test(level=10):
    from scipy_base.testing import module_test
    module_test(__name__,__file__,level=level)

def test_suite(level=1):
    from scipy_base.testing import module_test_suite
    return module_test_suite(__name__,__file__,level=level)

if __name__ == '__main__':
    test()

"""Module ieee:  exports a few useful IEEE-754 constants and functions.

PINF    positive infinity
MINF    minus infinity
NAN     a generic quiet NaN
PZERO   positive zero
MZERO   minus zero

isnan(x)
    Return true iff x is a NaN.
"""

def _make_inf():
    x = 2.0
    x2 = x * x
    i = 0
    while i < 100 and x != x2:
        x = x2
        x2 = x * x
        i = i + 1
    if x != x2:
        raise ValueError("This machine's floats go on forever!")
    return x

# NaN-testing.
#
# The usual method (x != x) doesn't work.
# Python forces all comparisons thru a 3-outcome cmp protocol; unordered
# isn't a possible outcome.  The float cmp outcome is essentially defined
# by this C expression (combining some cross-module implementation
# details, and where px and py are pointers to C double):
#   px == py ? 0 : *px < *py ? -1 : *px > *py ? 1 : 0
# Comparing x to itself thus always yields 0 by the first clause, and so x
# != x is never true. If px and py point to distinct NaN objects, a
# strange thing happens: 1. On scrupulous 754 implementations, *px < *py
# returns false, and so
#    does *px > *py.  Python therefore returns 0, i.e. "equal"!
# 2. On Pentium HW, an unordered outcome sets an otherwise-impossible
#    combination of condition codes, including both the "less than" and
#    "equal to" flags.  Microsoft C generates naive code that accepts the
#    "less than" flag at face value, and so the *px < *py clause returns
#    true, and Python returns -1, i.e. "not equal".
# So with a proper C 754 implementation Python returns the wrong result,
# and under MS's improper 754 implementation Python yields the right
# result -- both by accident.  It's unclear who should be shot <wink>.
#
# Anyway, the point of all that was to convince you it's tricky getting
# the right answer in a portable way!

def isnan(x):
    """x -> true iff x is a NaN."""
    # multiply by 1.0 to create a distinct object (x < x *always*
    # false in Python, due to object identity forcing equality)
    if x * 1.0 < x:
        # it's a NaN and this is MS C on a Pentium
        return 1
    # Else it's non-NaN, or NaN on a non-MS+Pentium combo.
    # If it's non-NaN, then x == 1.0 and x == 2.0 can't both be true, 
    # so we return false.  If it is NaN, then assuming a good 754 C 
    # implementation Python maps both unordered outcomes to true. 
    return 1.0 == x == 2.0

PINF = _make_inf()
MINF = -PINF

NAN = PINF - PINF
if not isnan(NAN):
    raise ValueError("This machine doesn't have NaNs, "
                     "'overflows' to a finite number, "
                     "suffers a novel way of implementing C comparisons, "
                     "or is 754-conformant but is using " 
                     "a goofy rounding mode.")
PZERO = 0.0
MZERO = -PZERO

