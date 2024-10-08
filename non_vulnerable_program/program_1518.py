import types

try:
    _gentype = types.GeneratorType
except AttributeError:
    _gentype = types.NoneType

# save away Python sum
_sum_ = sum

# functions that are now methods
def _wrapit(obj, method, *args, **kwds):
    try:
        wrap = obj.__array_wrap__
    except AttributeError:
        wrap = None
    result = getattr(asarray(obj),method)(*args, **kwds)
    if wrap and isinstance(result, mu.ndarray):
    if not isinstance(result, mu.ndarray):
            result = asarray(result)
        result = wrap(result)
    return result

def take(a, indices, axis=0):
    try:
        take = a.take
    except AttributeError:
        return _wrapit(a, 'take', indices, axis)
    return take(indices, axis)

# not deprecated --- copy if necessary, view otherwise
def reshape(a, newshape, order='C'):
    """Change the shape of a to newshape.  Return a new view object if possible
    otherwise return a copy.
    """
    try:
        reshape = a.reshape
    except AttributeError:
        return _wrapit(a, 'reshape', newshape, order=order)
    return reshape(newshape, order=order)

def choose(a, choices):
    try:
        choose = a.choose
    except AttributeError:
        return _wrapit(a, 'choose', choices)
    return choose(choices)

def repeat(a, repeats, axis=0):
    """repeat elements of a repeats times along axis
       repeats is a sequence of length a.shape[axis]
       telling how many times to repeat each element.
       If repeats is an integer, it is interpreted as
       a tuple of length a.shape[axis] containing repeats.
       The argument a can be anything array(a) will accept.
    """
    try:
        repeat = a.repeat
    except AttributeError:
        return _wrapit(a, 'repeat', repeats, axis)
    return repeat(repeats, axis)

def put (a, ind, v):
    """put(a, ind, v) results in a[n] = v[n] for all n in ind
       If v is shorter than mask it will be repeated as necessary.
       In particular v can be a scalar or length 1 array.
       The routine put is the equivalent of the following (although the loop
       is in C for speed):

           ind = array(indices, copy=False)
           v = array(values, copy=False).astype(a.dtype)
           for i in ind: a.flat[i] = v[i]
       a must be a contiguous numpy array.
    """
    return a.put(v,ind)

def putmask (a, mask, v):
    """putmask(a, mask, v) results in a = v for all places mask is true.
       If v is shorter than mask it will be repeated as necessary.
       In particular v can be a scalar or length 1 array.
    """
    return a.putmask(v, mask)

def swapaxes(a, axis1, axis2):
    """swapaxes(a, axis1, axis2) returns array a with axis1 and axis2
    interchanged.
    """
    try:
        swapaxes = a.swapaxes
    except AttributeError:
        return _wrapit(a, 'swapaxes', axis1, axis2)
    return swapaxes(axis1, axis2)

def transpose(a, axes=None):
    """transpose(a, axes=None) returns a view of the array with
    dimensions permuted according to axes.  If axes is None
    (default) returns array with dimensions reversed.
    """
    try:
        transpose = a.transpose
    except AttributeError:
        return _wrapit(a, 'transpose', axes)
    return transpose(axes)

def sort(a, axis=-1):
    """sort(a,axis=-1) returns array with elements sorted along given axis.
    """
    a = asanyarray(a).copy()
    a.sort(axis)
    return a

def argsort(a, axis=-1):
    """argsort(a,axis=-1) return the indices into a of the sorted array
    along the given axis, so that take(a,result,axis) is the sorted array.
    """
    try:
        argsort = a.argsort
    except AttributeError:
        return _wrapit(a, 'argsort', axis)
    return argsort(axis)

def argmax(a, axis=-1):
    """argmax(a,axis=-1) returns the indices to the maximum value of the
    1-D arrays along the given axis.
    """
    try:
        argmax = a.argmax
    except AttributeError:
        return _wrapit(a, 'argmax', axis)
    return argmax(axis)

def argmin(a, axis=-1):
    """argmin(a,axis=-1) returns the indices to the minimum value of the
    1-D arrays along the given axis.
    """
    try:
        argmin = a.argmin
    except AttributeError:
        return _wrapit(a, 'argmin', axis)
    return argmin(axis)
    
def searchsorted(a, v):
    """searchsorted(a, v)
    """
    try:
        searchsorted = a.searchsorted
    except AttributeError:
        return _wrapit(a, 'searchsorted', v)
    return searchsorted(v)

def resize(a, new_shape):
    """resize(a,new_shape) returns a new array with the specified shape.
    The original array's total size can be any size. It
    fills the new array with repeated copies of a.

    Note that a.resize(new_shape) will fill array with 0's
    beyond current definition of a.
    """

    if isinstance(new_shape, (int, nt.integer)):
        new_shape = (new_shape,)
    a = ravel(a)
    Na = len(a)
    if not Na: return mu.zeros(new_shape, a.dtype.char)
    total_size = um.multiply.reduce(new_shape)
    n_copies = int(total_size / Na)
    extra = total_size % Na

    if total_size == 0:
        return a[:0]

    if extra != 0:
        n_copies = n_copies+1
        extra = Na-extra

    a = concatenate( (a,)*n_copies)
    if extra > 0:
        a = a[:-extra]

    return reshape(a, new_shape)

def squeeze(a):
    "Returns a with any ones from the shape of a removed"
    try:
        squeeze = a.squeeze
    except AttributeError:
        return _wrapit(a, 'squeeze')
    return squeeze()

def diagonal(a, offset=0, axis1=0, axis2=1):
    """diagonal(a, offset=0, axis1=0, axis2=1) returns the given diagonals
    defined by the last two dimensions of the array.
    """
    return asarray(a).diagonal(offset, axis1, axis2)

def trace(a, offset=0, axis1=0, axis2=1, dtype=None):
    """trace(a,offset=0, axis1=0, axis2=1) returns the sum along diagonals
    (defined by the last two dimenions) of the array.
    """
    return asarray(a).trace(offset, axis1, axis2, dtype)

# not deprecated --- always returns a 1-d array.  Copy-if-necessary.
def ravel(m,order='C'):
    """ravel(m) returns a 1d array corresponding to all the elements of it's
    argument.  The new array is a view of m if possible, otherwise it is
    a copy.
    """
    a = asarray(m)
    return a.ravel(order)

def nonzero(a):
    """nonzero(a) returns the indices of the elements of a which are not zero,
    a must be 1d
    """
    try:
        nonzero = a.nonzero
    except AttributeError:
        res = _wrapit(a, 'nonzero')
    else:
        res = nonzero()

    if len(res) == 1:
        return res[0]
    else:
        raise ValueError, "Input argument must be 1d"
    

def shape(a):
    """shape(a) returns the shape of a (as a function call which
       also works on nested sequences).
    """
    try:
        result = a.shape
    except AttributeError:
        result = asarray(a).shape
    return result

def compress(condition, m, axis=-1):
    """compress(condition, x, axis=-1) = those elements of x corresponding
    to those elements of condition that are "true".  condition must be the
    same size as the given dimension of x."""
    try:
        compress = m.compress
    except AttributeError:
        return _wrapit(m, 'compress', condition, axis)
    return compress(condition, axis)

def clip(m, m_min, m_max):
    """clip(m, m_min, m_max) = every entry in m that is less than m_min is
    replaced by m_min, and every entry greater than m_max is replaced by
    m_max.
    """
    try:
        clip = m.clip
    except AttributeError:
        return _wrapit(m, 'clip', m_min, m_max)
    return clip(m_min, m_max)

def sum(x, axis=0, dtype=None):
    """Sum the array over the given axis.  The optional dtype argument
    is the data type for intermediate calculations.

    The default is to upcast (promote) smaller integer types to the
    platform-dependent Int.  For example, on 32-bit platforms:

        x.dtype                         default sum() dtype
        ---------------------------------------------------
        bool, Int8, Int16, Int32        Int32

    Examples:
    >>> sum([0.5, 1.5])
    2.0
    >>> sum([0.5, 1.5], dtype=Int32)
    1
    >>> sum([[0, 1], [0, 5]])
    array([0, 6])
    >>> sum([[0, 1], [0, 5]], axis=1)
    array([1, 5])
    """
    if isinstance(x, _gentype):
        return _sum_(x)
    try:
        sum = x.sum
    except AttributeError:
        return _wrapit(x, 'sum', axis, dtype)
    return sum(axis, dtype)

def product (x, axis=0, dtype=None):
    """Product of the array elements over the given axis."""
    try:
        prod = x.prod
    except AttributeError:
        return _wrapit(x, 'prod', axis, dtype)
    return prod(axis, dtype)

def sometrue (x, axis=0):
    """Perform a logical_or over the given axis."""
    try:
        any = x.any
    except AttributeError:
        return _wrapit(x, 'any', axis)
    return any(axis)

def alltrue (x, axis=0):
    """Perform a logical_and over the given axis."""
    try:
        all = x.all
    except AttributeError:
        return _wrapit(x, 'all', axis)
    return all(axis)

def any(x,axis=None):
    """Return true if any elements of x are true:  
    """
    try:
        any = x.any
    except AttributeError:
        return _wrapit(x, 'any', axis)
    return any(axis)

def all(x,axis=None):
    """Return true if all elements of x are true:  
    """
    try:
        all = x.all
    except AttributeError:
        return _wrapit(x, 'all', axis)
    return all(axis)

def cumsum (x, axis=0, dtype=None):
    """Sum the array over the given axis."""
    try:
        cumsum = x.cumsum
    except AttributeError:
        return _wrapit(x, 'cumsum', axis, dtype)
    return cumsum(axis, dtype)

def cumproduct (x, axis=0, dtype=None):
    """Sum the array over the given axis."""
    try:
        cumprod = x.cumprod
    except AttributeError:
        return _wrapit(x, 'cumprod', axis, dtype)
    return cumprod(axis, dtype)

def ptp(a, axis=0):
    """Return maximum - minimum along the the given dimension
    """
    try:
        ptp = a.ptp
    except AttributeError:
        return _wrapit(a, 'ptp', axis)
    return ptp(axis)

def amax(a, axis=0):
    """Return the maximum of 'a' along dimension axis.
    """
    try:
        max = a.max
    except AttributeError:
        return _wrapit(a, 'max', axis)
    return max(axis)

def amin(a, axis=0):
    """Return the minimum of a along dimension axis.
    """
    try:
        min = a.min
    except AttributeError:
        return _wrapit(a, 'min', axis)
    return min(axis)

def alen(a):
    """Return the length of a Python object interpreted as an array
    of at least 1 dimension.
    """
    try:
        return len(a)
    except TypeError:
        return len(array(a,ndmin=1))

def prod(a, axis=0, dtype=None):
    """Return the product of the elements along the given axis
    """
    try:
        prod = a.prod
    except AttributeError:
        return _wrapit(a, 'prod', axis, dtype)
    return prod(axis, dtype)

def cumprod(a, axis=0, dtype=None):
    """Return the cumulative product of the elments along the given axis
    """
    try:
        cumprod = a.cumprod
    except AttributeError:
        return _wrapit(a, 'cumprod', axis, dtype)
    return cumprod(axis, dtype)

def ndim(a):
    try:
        return a.ndim
    except AttributeError:
        return asarray(a).ndim

def rank(a):
    """Get the rank of sequence a (the number of dimensions, not a matrix rank)
       The rank of a scalar is zero.
    """
    try:
        return a.ndim
    except AttributeError:
        return asarray(a).ndim

def size (a, axis=None):
    "Get the number of elements in sequence a, or along a certain axis."
    if axis is None:
        try:
            return a.size
        except AttributeError:
            return asarray(a).size
    else:
        try:
            return a.shape[axis]
        except AttributeError:
            return asarray(a).shape[axis]

def round_(a, decimals=0):
    """Round 'a' to the given number of decimal places.  Rounding
    behaviour is equivalent to Python.

    Return 'a' if the array is not floating point.  Round both the real
    and imaginary parts separately if the array is complex.
    """
    try:
        round = a.round
    except AttributeError:
        return _wrapit(a, 'round', decimals)
    return round(decimals)

around = round_

def mean(a, axis=0, dtype=None):
    try:
        mean = a.mean
    except AttributeError:
        return _wrapit(a, 'mean', axis, dtype)
    return mean(axis, dtype)    

def std(a, axis=0, dtype=None):
    try:
        std = a.std
    except AttributeError:
        return _wrapit(a, 'std', axis, dtype)
    return std(axis, dtype)

def var(a, axis=0, dtype=None):
    try:
        var = a.var
    except AttributeError:
        return _wrapit(a, 'var', axis, dtype)
    return var(axis, dtype)


# Compatibility module containing deprecated names

__all__ = ['NewAxis',
           'UFuncType', 'UfuncType', 'ArrayType', 'arraytype',
           'LittleEndian', 'Bool',
           'Character', 'UnsignedInt8', 'UnsignedInt16', 'UnsignedInt', 'UInt',
           'UInt8','UInt16','UInt32', 'UnsignedInt32', 'UnsignedInteger',
           # UnsignedInt64 and Unsigned128 added below if possible
           # same for Int64 and Int128, Float128, and Complex128
           'Int8', 'Int16', 'Int32',
           'Int0', 'Int', 'Float0', 'Float', 'Complex0', 'Complex',
           'PyObject', 'Float32', 'Float64', 'Float16', 'Float8',
           'Complex32', 'Complex64', 'Complex8', 'Complex16',
           'sarray', 'arrayrange', 'cross_correlate',
           'matrixmultiply', 'outerproduct', 'innerproduct',
           'cross_product', 'array_constructor',
           'DumpArray', 'LoadArray', 'multiarray', 'divide_safe',
           # from cPickle
           'dump', 'dumps'
          ]

