from cPickle import dump, dumps

# functions that are now methods

def take(a, indices, axis=0):
    a = asarray(a)
    return a.take(indices, axis)

def reshape(a, newshape):
    """Change the shape of a to newshape.  Return a new view object.
    """
    return asarray(a).reshape(newshape)

def choose(a, choices):
    a = asarray(a)
    return a.choose(choices)

def repeat(a, repeats, axis=0):
    """repeat elements of a repeats times along axis
       repeats is a sequence of length a.shape[axis]
       telling how many times to repeat each element.
       If repeats is an integer, it is interpreted as
       a tuple of length a.shape[axis] containing repeats.
       The argument a can be anything array(a) will accept.
    """
    a = array(a, copy=0)
    return a.repeat(repeats, axis)

def put (a, ind, v):
    """put(a, ind, v) results in a[n] = v[n] for all n in ind
       If v is shorter than mask it will be repeated as necessary.
       In particular v can be a scalar or length 1 array.
       The routine put is the equivalent of the following (although the loop   
       is in C for speed): 

           ind = array(indices, copy=0) 
           v = array(values, copy=0).astype(a, a.dtype) 
           for i in ind: a.flat[i] = v[i] 
       a must be a contiguous Numeric array.
    """
    a = array(a,copy=0)
    v = array(v,copy=0)
    return a.put(a, ind, v.astype(a.dtype))

def putmask (a, mask, v):
    """putmask(a, mask, v) results in a = v for all places mask is true.
       If v is shorter than mask it will be repeated as necessary.
       In particular v can be a scalar or length 1 array.
    """
    return a.putmask(mask, v)

def swapaxes(a, axis1, axis2):
    """swapaxes(a, axis1, axis2) returns array a with axis1 and axis2
    interchanged.
    """
    a = array(a, copy=0)
    return a.swapaxes(axis1, axis2)

def transpose(a, axes=None):
    """transpose(a, axes=None) returns array with dimensions permuted
    according to axes.  If axes is None (default) returns array with
    dimensions reversed.
    """
    a = array(a,copy=0)
    return a.transpose(axes)

def sort(a, axis=-1):
    """sort(a,axis=-1) returns array with elements sorted along given axis.
    """
    a = array(a, copy=0)
    return a.sort(axis)

def argsort(a, axis=-1):
    """argsort(a,axis=-1) return the indices into a of the sorted array
    along the given axis, so that take(a,result,axis) is the sorted array.
    """
    a = array(a, copy=0)
    return a.argsort(axis)

def argmax(a, axis=-1):
    """argmax(a,axis=-1) returns the indices to the maximum value of the
    1-D arrays along the given axis.    
    """
    a = array(a, copy=0)
    return a.argmax(axis)

def argmin(a, axis=-1):
    """argmin(a,axis=-1) returns the indices to the minimum value of the
    1-D arrays along the given axis.    
    """
    a = array(a,copy=0)
    return a.argmin(axis)

def searchsorted(a, v):
    """searchsorted(a, v)
    """
    a = array(a,copy=0)
    return a.searchsorted(v)

def resize(a, new_shape):
    """resize(a,new_shape) returns a new array with the specified shape.
    The original array's total size can be any size. It
    fills the new array with repeated copies of a.
    """

    a = ravel(a)
    Na = len(a)
    if not Na: return zeros(new_shape, a.dtypechar)
    total_size = up.multiply.reduce(new_shape)
    n_copies = pyint(total_size / Na)
    extra = total_size % Na

    if extra != 0: 
        n_copies = n_copies+1
        extra = Na-extra

    a = concatenate( (a,)*n_copies)
    if extra > 0:
        a = a[:-extra]

    return reshape(a, new_shape)


def diagonal(a, offset=0, axis1=0, axis2=1):
    """diagonal(a, offset=0, axis1=0, axis2=1) returns the given diagonals
    defined by the last two dimensions of the array.
    """
    return asarray(a).diagonal(offset, axis1, axis2)
##    a = asarray(a)
##    nd = len(a.shape)
##    new_axes = range(nd)
##    if (axis1 < 0): axis1 += nd
##    if (axis2 < 0): axis2 += nd
##    try: 
##        new_axes.remove(axis1)  
##        new_axes.remove(axis2)  
##    except ValueError: 
##            raise ValueError, "axis1(=%d) and axis2(=%d) must be different and within range." % (axis1, axis2) 
##    new_axes = new_axes + [axis1, axis2] ### insert at the end, not the beginning
##    a = transpose(a, new_axes)
##    s = a.shape
##    rank = len(s) 
##    if rank == 2:
##        n1 = s[0]
##        n2 = s[1]
##        n = n1 * n2
##        s = (n,)
##        a = reshape(a, s)
##        if offset < 0:
##            return take(a, range(- n2 * offset, min(n2, n1+offset) *
##                                      (n2+1) - n2 * offset, n2+1), axis=0)
##        else:
##            return take(a, range(offset, min(n1, n2-offset) *
##                                 (n2+1) + offset, n2+1), axis=0)
##    else:
##        my_diagonal = []
##        for i in range(s[0]):
##            my_diagonal.append(diagonal(a[i], offset, rank-3, rank-2)) ###
##        return array(my_diagonal)
    

def trace(a, offset=0, axis1=0, axis2=1, rtype=None):
    """trace(a,offset=0, axis1=0, axis2=1) returns the sum along diagonals
    (defined by the last two dimenions) of the array.
    """
    return asarray(a).trace(offset, axis1, axis2, rtype)

def ravel(m):
    """ravel(m) returns a 1d array corresponding to all the elements of it's
    argument.
    """
    return asarray(m).ravel()

def nonzero(a):
    """nonzero(a) returns the indices of the elements of a which are not zero,
    a must be 1d
    """
    return asarray(a).nonzero()
##  return repeat(arange(len(a)), not_equal(a, 0))

def shape(a):
    """shape(a) returns the shape of a (as a function call which
       also works on nested sequences).
    """
    return asarray(a).shape

def compress(condition, m, axis=-1):
    """compress(condition, x, axis=-1) = those elements of x corresponding 
    to those elements of condition that are "true".  condition must be the
    same size as the given dimension of x."""
    return asarray(m).compress(condition, axis)

def clip(m, m_min, m_max):
    """clip(m, m_min, m_max) = every entry in m that is less than m_min is
    replaced by m_min, and every entry greater than m_max is replaced by
    m_max.
    """
    return asarray(m).clip(m_min, m_max)
##    selector = less(m, m_min)+2*greater(m, m_max)
##    return choose(selector, (m, m_min, m_max))

def sum (x, axis=0, rtype=None):
    """Sum the array over the given axis.
    """
    return asarray(x).sum(axis, rtype)

def product (x, axis=0, rtype=None):
    """Product of the array elements over the given axis."""
    return asarray(x).prod(axis, rtype)

def sometrue (x, axis=0):
    """Perform a logical_or over the given axis."""
    return asarray(x).any(axis)

def alltrue (x, axis=0):
    """Perform a logical_and over the given axis."""
    return asarray(x).all(axis)

def any(x,axis=None):
    """Return true if any elements of x are true:  sometrue(ravel(x))
    """
    return ravel(x).any(axis)

def all(x,axis=None):
    """Return true if all elements of x are true:  alltrue(ravel(x))
    """
    return ravel(x).all(axis)

def cumsum (x, axis=0, rtype=None):
    """Sum the array over the given axis."""
    return asarray(x).cumsum(axis, rtype)

def cumproduct (x, axis=0, rtype=None):
    """Sum the array over the given axis."""
    return asarray(x).cumprod(axis, rtype)

def around(m, decimals=0):
    """around(m, decimals=0) \
    Round in the same way as standard python performs rounding. Returns 
    always a float.
    """
    return asarray(m).round(decimals)
##    m = asarray(m)
##    s = sign(m)
##    if decimals:
##        m = absolute(m*10.**decimals)
##    else:
##        m = absolute(m)
##    rem = m-asarray(m).astype(intp)
##    m = where(less(rem,0.5), floor(m), ceil(m))
##    # convert back
##    if decimals:
##        m = m*s/(10.**decimals)
##    else:
##        m = m*s
##    return m
    
def sign(m):
    """sign(m) gives an array with shape of m with elements defined by sign
    function:  where m is less than 0 return -1, where m greater than 0, a=1,
    elsewhere a=0.
    """
    return asarray(m).sign()
##    m = asarray(m)
##    return zeros(shape(m))-less(m,0)+greater(m,0)

def ndim(a):
    try:
        return a.ndim
    except AttributeError:
        return asarray(a).ndim

def rank (a):
    """Get the rank of sequence a (the number of dimensions, not a matrix rank)
       The rank of a scalar is zero.
    """
    try:
        return a.ndim
    except:
        return asarray(a).ndim

def shape (a):
    "Get the shape of sequence a"
    try:
        return a.shape
    except:
        return asarray(a).shape

def size (a, axis=None):
    "Get the number of elements in sequence a, or along a certain axis."
    a = asarray(a)
    if axis is None:
        return a.size
    else:
        return a.shape[axis]


""" Machine limits for Float32 and Float64.
"""

__all__ = ['float_epsilon','float_tiny','float_min',
           'float_max','float_precision','float_resolution',
           'single_epsilon','single_tiny','single_min','single_max',
           'single_precision','single_resolution',
           'longfloat_epsilon','longfloat_tiny','longfloat_min','longfloat_max',
           'longfloat_precision','longfloat_resolution']
           

