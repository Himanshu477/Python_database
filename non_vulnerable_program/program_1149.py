import umath
import oldnumeric
import function_base
from numeric import e, pi, newaxis, ndarray, inf
from oldnumeric import typecodes, amax, amin
from numerictypes import *
import numeric

    
MaskType=bool_
divide_tolerance = 1.e-35

class MAError (Exception):
    def __init__ (self, args=None):
        "Create an exception"
        self.args = args
    def __str__(self):
        "Calculate the string representation"
        return str(self.args)
    __repr__ = __str__

class _MaskedPrintOption:
    "One instance of this class, masked_print_option, is created."
    def __init__ (self, display):
        "Create the masked print option object."
        self.set_display(display)
        self._enabled = 1

    def display (self):
        "Show what prints for masked values."
        return self._display

    def set_display (self, s):
        "set_display(s) sets what prints for masked values."
        self._display = s

    def enabled (self):
        "Is the use of the display value enabled?"
        return self._enabled

    def enable(self, flag=1):
        "Set the enabling flag to flag."
        self._enabled = flag

    def __str__ (self):
        return str(self._display)

#if you single index into a masked location you get this object.
masked_print_option = _MaskedPrintOption('--')

# Use single element arrays or scalars.
default_real_fill_value = 1.e20
default_complex_fill_value = 1.e20 + 0.0j
default_character_fill_value = '-'
default_integer_fill_value = 999999
default_object_fill_value = '?'

def default_fill_value (obj):
    "Function to calculate default fill value for an object."
    if isinstance(obj, types.FloatType):
        return default_real_fill_value
    elif isinstance(obj, types.IntType) or isinstance(obj, types.LongType):
            return default_integer_fill_value
    elif isinstance(obj, types.StringType):
            return default_character_fill_value
    elif isinstance(obj, types.ComplexType):
            return default_complex_fill_value
    elif isinstance(obj, MaskedArray) or isinstance(obj, ndarray):
        x = obj.dtypechar
        if x in typecodes['Float']:
            return default_real_fill_value
        if x in typecodes['Integer']:
            return default_integer_fill_value
        if x in typecodes['Complex']:
            return default_complex_fill_value
        if x in typecodes['Character']:
            return default_character_fill_value
        if x in typecodes['UnsignedInteger']:
            return umath.absolute(default_integer_fill_value)
        return default_object_fill_value
    else:
        return default_object_fill_value

def minimum_fill_value (obj):
    "Function to calculate default fill value suitable for taking minima."
    if isinstance(obj, types.FloatType):
        return numeric.inf
    elif isinstance(obj, types.IntType) or isinstance(obj, types.LongType):
        return sys.maxint
    elif isinstance(obj, MaskedArray) or isinstance(obj, ndarray):
        x = obj.dtypechar
        if x in typecodes['Float']:
            return numeric.inf
        if x in typecodes['Integer']:
            return sys.maxint
        if x in typecodes['UnsignedInteger']:
            return sys.maxint
    else:
        raise TypeError, 'Unsuitable type for calculating minimum.'

def maximum_fill_value (obj):
    "Function to calculate default fill value suitable for taking maxima."
    if isinstance(obj, types.FloatType):
        return -inf
    elif isinstance(obj, types.IntType) or isinstance(obj, types.LongType):
            return -sys.maxint
    elif isinstance(obj, MaskedArray) or isinstance(obj, ndarray):
        x = obj.dtypechar
        if x in typecodes['Float']:
            return -inf
        if x in typecodes['Integer']:
            return -sys.maxint
        if x in typecodes['UnsignedInteger']:
            return 0
    else:
        raise TypeError, 'Unsuitable type for calculating maximum.'

def set_fill_value (a, fill_value):
    "Set fill value of a if it is a masked array."
    if isMaskedArray(a):
        a.set_fill_value (fill_value)

def getmask (a):
    """Mask of values in a; could be None.
       Returns None if a is not a masked array.
       To get an array for sure use getmaskarray."""
    if isinstance(a, MaskedArray):
        return a.raw_mask()
    else:
        return None

def getmaskarray (a):
    """Mask of values in a; an array of zeros if mask is None
     or not a masked array, and is a byte-sized integer.
     Do not try to add up entries, for example.
    """
    m = getmask(a)
    if m is None:
        return make_mask_none(shape(a))
    else:
        return m

def is_mask (m):
    """Is m a legal mask? Does not check contents, only type.
    """
    if m is None or (isinstance(m, ndarray) and \
                     m.dtype is MaskType):
        return 1
    else:
        return 0

def make_mask (m, copy=0, flag=0):
    """make_mask(m, copy=0, flag=0)
       return m as a mask, creating a copy if necessary or requested.
       Can accept any sequence of integers or None. Does not check
       that contents must be 0s and 1s.
       if flag, return None if m contains no true elements.
    """
    if m is None:
        return None
    elif isinstance(m, ndarray):
        if m.dtype is MaskType:
            if copy:
                result = numeric.array(m, dtype=MaskType, copy=copy)
            else:
                result = m
        else:
            result = m.astype(MaskType)
    else:
        result = filled(m,True).astype(MaskType)

    if flag and not oldnumeric.sometrue(oldnumeric.ravel(result)):
        return None
    else:
        return result

def make_mask_none (s):
    "Return a mask of all zeros of shape s."
    result = numeric.zeros(s, dtype=MaskType)
    result.shape = s
    return result

def mask_or (m1, m2):
    """Logical or of the mask candidates m1 and m2, treating None as false.
       Result may equal m1 or m2 if the other is None.
     """
    if m1 is None: return make_mask(m2)
    if m2 is None: return make_mask(m1)
    if m1 is m2 and is_mask(m1): return m1
    return make_mask(umath.logical_or(m1, m2))

def filled (a, value = None):
    """a as a contiguous numeric array with any masked areas replaced by value
    if value is None or the special element "masked", get_fill_value(a)
    is used instead.

    If a is already a contiguous numeric array, a itself is returned.

    filled(a) can be used to be sure that the result is numeric when
    passing an object a to other software ignorant of MA, in particular to
    numeric itself.
    """
    if isinstance(a, MaskedArray):
        return a.filled(value)
    elif isinstance(a, ndarray) and a.flags['CONTIGUOUS']:
        return a
    elif isinstance(a, types.DictType):
        return numeric.array(a, 'O')
    else:
        return numeric.array(a)

def get_fill_value (a):
    """
    The fill value of a, if it has one; otherwise, the default fill value
    for that type.
    """
    if isMaskedArray(a):
        result = a.fill_value()
    else:
        result = default_fill_value(a)
    return result

def common_fill_value (a, b):
    "The common fill_value of a and b, if there is one, or None"
    t1 = get_fill_value(a)
    t2 = get_fill_value(b)
    if t1 == t2: return t1
    return None

# Domain functions return 1 where the argument(s) are not in the domain.
class domain_check_interval:
    "domain_check_interval(a,b)(x) = true where x < a or y > b"
    def __init__(self, y1, y2):
        "domain_check_interval(a,b)(x) = true where x < a or y > b"
        self.y1 = y1
        self.y2 = y2

    def __call__ (self, x):
        "Execute the call behavior."
        return umath.logical_or(umath.greater (x, self.y2),
                                   umath.less(x, self.y1)
                                  )

class domain_tan:
    "domain_tan(eps) = true where abs(cos(x)) < eps)"
    def __init__(self, eps):
        "domain_tan(eps) = true where abs(cos(x)) < eps)"
        self.eps = eps

    def __call__ (self, x):
        "Execute the call behavior."
        return umath.less(umath.absolute(umath.cos(x)), self.eps)

class domain_greater:
    "domain_greater(v)(x) = true where x <= v"
    def __init__(self, critical_value):
        "domain_greater(v)(x) = true where x <= v"
        self.critical_value = critical_value

    def __call__ (self, x):
        "Execute the call behavior."
        return umath.less_equal (x, self.critical_value)

class domain_greater_equal:
    "domain_greater_equal(v)(x) = true where x < v"
    def __init__(self, critical_value):
        "domain_greater_equal(v)(x) = true where x < v"
        self.critical_value = critical_value

    def __call__ (self, x):
        "Execute the call behavior."
        return umath.less (x, self.critical_value)

class masked_unary_operation:
    def __init__ (self, aufunc, fill=0, domain=None):
        """ masked_unary_operation(aufunc, fill=0, domain=None)
            aufunc(fill) must be defined
            self(x) returns aufunc(x)
            with masked values where domain(x) is true or getmask(x) is true.
        """
        self.f = aufunc
        self.fill = fill
        self.domain = domain
        self.__doc__ = getattr(aufunc, "__doc__", str(aufunc))

    def __call__ (self, a, *args, **kwargs):
        "Execute the call behavior."
# numeric tries to return scalars rather than arrays when given scalars.
        m = getmask(a)
        d1 = filled(a, self.fill)
        if self.domain is not None:
            m = mask_or(m, self.domain(d1))
        if m is None:
            result = self.f(d1, *args, **kwargs)
            if type(result) is ndarray:
                return masked_array (result)
            else:
                return result
        else:
            dx = masked_array(d1, m)
            result = self.f(filled(dx, self.fill), *args, **kwargs)
            if type(result) is ndarray:
                return masked_array(result, m)
            elif m[...]:
                return masked
            else:
                return result

    def __str__ (self):
        return "Masked version of " + str(self.f)


class domain_safe_divide:
    def __init__ (self, tolerance=divide_tolerance):
        self.tolerance = tolerance
    def __call__ (self, a, b):
        return umath.absolute(a) * self.tolerance >= umath.absolute(b)

class domained_binary_operation:
    """Binary operations that have a domain, like divide. These are complicated so they
       are a separate class. They have no reduce, outer or accumulate.
    """
    def __init__ (self, abfunc, domain, fillx=0, filly=0):
        """abfunc(fillx, filly) must be defined.
           abfunc(x, filly) = x for all x to enable reduce.
        """
        self.f = abfunc
        self.domain = domain
        self.fillx = fillx
        self.filly = filly
        self.__doc__ = getattr(abfunc, "__doc__", str(abfunc))

    def __call__(self, a, b):
        "Execute the call behavior."
        ma = getmask(a)
        mb = getmask(b)
        d1 = filled(a, self.fillx)
        d2 = filled(b, self.filly)
        t = self.domain(d1, d2)

        if oldnumeric.sometrue(t, None):
            d2 = where(t, self.filly, d2)
            mb = mask_or(mb, t)
        m = mask_or(ma, mb)
        if m is None:
            result =  self.f(d1, d2)
            if type(result) is ndarray:
                return masked_array(result)
            else:
                return result
        result = self.f(d1, d2)
        if type(result) is ndarray:
            if m.shape != result.shape:
                m = mask_or(getmaskarray(a), getmaskarray(b))
            return masked_array(result, m)
        elif m[...]:
            return masked
        else:
            return result
    def __str__ (self):
        return "Masked version of " + str(self.f)

class masked_binary_operation:
    def __init__ (self, abfunc, fillx=0, filly=0):
        """abfunc(fillx, filly) must be defined.
           abfunc(x, filly) = x for all x to enable reduce.
        """
        self.f = abfunc
        self.fillx = fillx
        self.filly = filly
        self.__doc__ = getattr(abfunc, "__doc__", str(abfunc))

    def __call__ (self, a, b, *args, **kwargs):
        "Execute the call behavior."
        m = mask_or(getmask(a), getmask(b))
        if m is None:
            d1 = filled(a, self.fillx)
            d2 = filled(b, self.filly)
            result =  self.f(d1, d2, *args, **kwargs)
            if type(result) is ndarray:
                return masked_array(result)
            else:
                return result
        d1 = filled(a, self.fillx)
        d2 = filled(b, self.filly)
        result = self.f(d1, d2, *args, **kwargs)
        if type(result) is ndarray:
            if m.shape != result.shape:
                m = mask_or(getmaskarray(a), getmaskarray(b))
            return masked_array(result, m)
        elif m[...]:
            return masked
        else:
            return result

    def reduce (self, target, axis=0):
        """Reduce target along the given axis with this function."""
        m = getmask(target)
        t = filled(target, self.filly)
        if t.shape == ():
            t = t.reshape(1)
            if m is not None:
               m = make_mask(m, copy=1)
               m.shape = (1,)
        if m is None:
            return masked_array (self.f.reduce (t, axis))
        else:
            t = masked_array (t, m)
            t = self.f.reduce(filled(t, self.filly), axis)
            m = umath.logical_and.reduce(m, axis)
            if isinstance(t, ndarray):
                return masked_array(t, m, get_fill_value(target))
            elif m:
                return masked
            else:
                return t

    def outer (self, a, b):
        "Return the function applied to the outer product of a and b."
        ma = getmask(a)
        mb = getmask(b)
        if ma is None and mb is None:
            m = None
        else:
            ma = getmaskarray(a)
            mb = getmaskarray(b)
            m = logical_or.outer(ma, mb)
        d = self.f.outer(filled(a, self.fillx), filled(b, self.filly))
        return masked_array(d, m)

    def accumulate (self, target, axis=0):
        """Accumulate target along axis after filling with y fill value."""
        t = filled(target, self.filly)
        return masked_array (self.f.accumulate (t, axis))
    def __str__ (self):
        return "Masked version of " + str(self.f)

sqrt = masked_unary_operation(umath.sqrt, 0.0, domain_greater_equal(0.0))
log = masked_unary_operation(umath.log, 1.0, domain_greater(0.0))
log10 = masked_unary_operation(umath.log10, 1.0, domain_greater(0.0))
exp = masked_unary_operation(umath.exp)
conjugate = masked_unary_operation(umath.conjugate)
sin = masked_unary_operation(umath.sin)
cos = masked_unary_operation(umath.cos)
tan = masked_unary_operation(umath.tan, 0.0, domain_tan(1.e-35))
arcsin = masked_unary_operation(umath.arcsin, 0.0, domain_check_interval(-1.0, 1.0))
arccos = masked_unary_operation(umath.arccos, 0.0, domain_check_interval(-1.0, 1.0))
arctan = masked_unary_operation(umath.arctan)
# Missing from numeric
arcsinh = masked_unary_operation(umath.arcsinh)
arccosh = masked_unary_operation(umath.arccosh)
arctanh = masked_unary_operation(umath.arctanh)
sinh = masked_unary_operation(umath.sinh)
cosh = masked_unary_operation(umath.cosh)
tanh = masked_unary_operation(umath.tanh)
absolute = masked_unary_operation(umath.absolute)
fabs = masked_unary_operation(umath.fabs)
negative = masked_unary_operation(umath.negative)
nonzero = masked_unary_operation(oldnumeric.nonzero)
around = masked_unary_operation(function_base.round_)
floor = masked_unary_operation(umath.floor)
ceil = masked_unary_operation(umath.ceil)
sometrue = masked_unary_operation(oldnumeric.sometrue)
alltrue = masked_unary_operation(oldnumeric.alltrue, 1)
logical_not = masked_unary_operation(umath.logical_not)

add = masked_binary_operation(umath.add)
subtract = masked_binary_operation(umath.subtract)
subtract.reduce = None
multiply = masked_binary_operation(umath.multiply, 1, 1)
divide = domained_binary_operation(umath.divide, domain_safe_divide(), 0, 1)
true_divide = domained_binary_operation(umath.true_divide, domain_safe_divide(), 0, 1)
floor_divide = domained_binary_operation(umath.floor_divide, domain_safe_divide(), 0, 1)
remainder = domained_binary_operation(umath.remainder, domain_safe_divide(), 0, 1)
fmod = domained_binary_operation(umath.fmod, domain_safe_divide(), 0, 1)
hypot = masked_binary_operation(umath.hypot)
arctan2 = masked_binary_operation(umath.arctan2, 0.0, 1.0)
arctan2.reduce = None
equal = masked_binary_operation(umath.equal)
equal.reduce = None
not_equal = masked_binary_operation(umath.not_equal)
not_equal.reduce = None
less_equal = masked_binary_operation(umath.less_equal)
less_equal.reduce = None
greater_equal = masked_binary_operation(umath.greater_equal)
greater_equal.reduce = None
less = masked_binary_operation(umath.less)
less.reduce = None
greater = masked_binary_operation(umath.greater)
greater.reduce = None
logical_and = masked_binary_operation(umath.logical_and)
logical_or = masked_binary_operation(umath.logical_or)
logical_xor = masked_binary_operation(umath.logical_xor)
bitwise_and = masked_binary_operation(umath.bitwise_and)
bitwise_or = masked_binary_operation(umath.bitwise_or)
bitwise_xor = masked_binary_operation(umath.bitwise_xor)

def rank (object):
    return oldnumeric.rank(filled(object))

def shape (object):
    return oldnumeric.shape(filled(object))

def size (object, axis=None):
    return oldnumeric.size(filled(object), axis)

class MaskedArray (object):
    """Arrays with possibly masked values.
       Masked values of 1 exclude the corresponding element from 
       any computation.

       Construction:
           x = array(data, dtype=None, copy=True, fortran=False,
                     mask = None, fill_value=None)

       If copy=False, every effort is made not to copy the data:
           If data is a MaskedArray, and argument mask=None,
           then the candidate data is data.data and the
           mask used is data.mask. If data is a numeric array,
           it is used as the candidate raw data.
           If dtypechar is not None and
           is != data.dtypechar then a data copy is required.
           Otherwise, the candidate is used.

       If a data copy is required, raw data stored is the result of:
       numeric.array(data, dtype=dtypechar, copy=copy)

       If mask is None there are no masked values. Otherwise mask must
       be convertible to an array of booleans with the same shape as x.

       fill_value is used to fill in masked values when necessary,
       such as when printing and in method/function filled().
       The fill_value is not used for computation within this module.
    """
    def __init__(self, data, dtype=None, copy=True, fortran=False, 
                 mask=None, fill_value=None):
        """array(data, dtype=None, copy=True, fortran=False, mask=None, fill_value=None)
           If data already a numeric array, its dtype becomes the default value of dtype.
        """
        tc = dtype
        need_data_copied = copy
        if isinstance(data, MaskedArray):
            c = data.data
            ctc = c.dtypechar
            if tc is None:
                tc = ctc
            elif dtype2char(tc) != ctc:
                need_data_copied = True
            if mask is None:
                mask = data.mask
            elif mask is not None: #attempting to change the mask
                need_data_copied = True

        elif isinstance(data, ndarray):
            c = data
            ctc = c.dtypechar
            if tc is None:
                tc = ctc
            elif dtype2char(tc) != ctc:
                need_data_copied = True
        else:
            need_data_copied = False #because I'll do it now
            c = numeric.array(data, dtype=tc, copy=True, fortran=fortran)

        if need_data_copied:
            if tc == ctc:
                self._data = numeric.array(c, dtype=tc, copy=True, fortran=fortran)
            else:
                self._data = c.astype(tc)
        else:
            self._data = c

        if mask is None:
            self._mask = None
            self._shared_mask = 0
        else:
            self._mask = make_mask (mask)
            if self._mask is None:
                self._shared_mask = 0
            else:
                self._shared_mask = (self._mask is mask)
                nm = size(self._mask)
                nd = size(self._data)
                if nm != nd:
                    if nm == 1:
                        self._mask = oldnumeric.resize(self._mask, self._data.shape)
                        self._shared_mask = 0
                    elif nd == 1:
                        self._data = oldnumeric.resize(self._data, self._mask.shape)
                        self._data.shape = self._mask.shape
                    else:
                        raise MAError, "Mask and data not compatible."
                elif nm == 1 and shape(self._mask) != shape(self._data):
                    self.unshare_mask()
                    self._mask.shape = self._data.shape

        self.set_fill_value(fill_value)

    def __array__ (self, t = None):
        "Special hook for numeric. Converts to numeric if possible."
        if self._mask is not None:
            if oldnumeric.ravel(self._mask).any():
                raise MAError, \
                """Cannot automatically convert masked array to numeric because data
                   is masked in one or more locations.
                """
            else:  # Mask is all false
                   # Optimize to avoid future invocations of this section.
                self._mask = None
                self._shared_mask = 0
        if t:
            return self._data.astype(t)
        else:
            return self._data

    def _get_shape(self):
        "Return the current shape."
        return self._data.shape

    def _set_shape (self, newshape):
        "Set the array's shape."
        self._data.shape = newshape
        if self._mask is not None:
            self._mask = self._mask.copy()
            self._mask.shape = newshape

    def _get_flat(self):
        """Calculate the flat value.
        """
        if self._mask is None:
            return masked_array(self._data.ravel(), mask=None,
                                fill_value = self.fill_value())
        else:
            return masked_array(self._data.ravel(),
                                mask=self._mask.ravel(),
                                fill_value = self.fill_value())

    def _set_flat (self, value):
        "x.flat = value"
        y = self.ravel()
        y[:] = value

    def _get_real(self):
        "Get the real part of a complex array."
        if self._mask is None:
            return masked_array(self._data.real, mask=None,
                            fill_value = self.fill_value())
        else:
            return masked_array(self._data.real, mask=self._mask.ravel(),
                            fill_value = self.fill_value())

    def _set_real (self, value):
        "x.real = value"
        y = self.real
        y[...] = value

    def _get_imaginary(self):
        "Get the imaginary part of a complex array."
        if self._mask is None:
            return masked_array(self._data.imag, mask=None,
                            fill_value = self.fill_value())
        else:
            return masked_array(self._data.imag, mask=self._mask.ravel(),
                            fill_value = self.fill_value())

    def _set_imaginary (self, value):
        "x.imaginary = value"
        y = self.imaginary
        y[...] = value

    def __str__(self):
        """Calculate the str representation, using masked for fill if
           it is enabled. Otherwise fill with fill value.
        """
        if masked_print_option.enabled():
            f = masked_print_option
        else:
            f = self.fill_value()
        res = self.filled(f)
        return str(res)

    def __repr__(self):
        """Calculate the repr representation, using masked for fill if
           it is enabled. Otherwise fill with fill value.
        """
        with_mask = """\
array(data =
 %(data)s,
      mask =
 %(mask)s,
      fill_value=%(fill)s)
"""
        with_mask1 = """\
array(data = %(data)s,
      mask = %(mask)s,
      fill_value=%(fill)s)
"""
        without_mask = """array(
 %(data)s)"""
        without_mask1 = """array(%(data)s)"""

        n = len(self.shape)
        if self._mask is None:
            if n <=1:
                return without_mask1 % {'data':str(self.filled())}
            return without_mask % {'data':str(self.filled())}
        else:
            if n <=1:
                return with_mask % {
                    'data': str(self.filled()),
                    'mask': str(self._mask),
                    'fill': str(self.fill_value())
                    }
            return with_mask % {
                'data': str(self.filled()),
                'mask': str(self._mask),
                'fill': str(self.fill_value())
                }
        without_mask1 = """array(%(data)s)"""
        if self._mask is None:
            return without_mask % {'data':str(self.filled())}
        else:
            return with_mask % {
                'data': str(self.filled()),
                'mask': str(self._mask),
                'fill': str(self.fill_value())
                }

    def __float__(self):
        "Convert self to float."
        self.unmask()
        if self._mask is not None:
            raise MAError, 'Cannot convert masked element to a Python float.'
        return float(self.data.item())

    def __int__(self):
        "Convert self to int."
        self.unmask()
        if self._mask is not None:
            raise MAError, 'Cannot convert masked element to a Python int.'
        return int(self.data.item())

    def __getitem__(self, i):
        "Get item described by i. Not a copy as in previous versions."
        self.unshare_mask()
        m = self._mask
        dout = self._data[i]
        if m is None:
            return dout
        mi = m[i]
        if mi.size == 1:
            if mi: 
                return masked
            else:
                return dout
        else:
            return masked_array(dout, mi, fill_value=self._fill_value)

    def __getslice__(self, i, j):
        "Get slice described by i, j"
        self.unshare_mask()
        m = self._mask
        dout = self._data[i:j]
        if m is None:
            return masked_array(dout, fill_value=self._fill_value)
        else:
            return masked_array(dout, mask = m[i:j], fill_value=self._fill_value)

# --------
# setitem and setslice notes
# note that if value is masked, it means to mask those locations.
# setting a value changes the mask to match the value in those locations.

    def __setitem__(self, index, value):
        "Set item described by index. If value is masked, mask those locations."
        d = self._data
        if self is masked:
            raise MAError, 'Cannot alter the masked element.'
        if value is masked:
            if self._mask is None:
                self._mask = make_mask_none(d.shape)
                self._shared_mask = False
            else:
                self.unshare_mask()
            self._mask[index] = True
            return
        m = getmask(value)
        value = filled(value).astype(d.dtype)
        d[index] = value
        if m is None:
            if self._mask is not None:
                self.unshare_mask()
                self._mask[index] = False
        else:
            if self._mask is None:
                self._mask = make_mask_none(d.shape)
                self._shared_mask = True
            else:
                self.unshare_mask()
            self._mask[index] = m

    def __setslice__(self, i, j, value):
        "Set slice i:j; if value is masked, mask those locations."
        d = self._data
        if self is masked:
            raise MAError, "Cannot alter the 'masked' object."
        if value is masked:
            if self._mask is None:
                self._mask = make_mask_none(d.shape)
                self._shared_mask = False
            self._mask[i:j] = True
            return
        m = getmask(value)
        value = filled(value).astype(d.dtype)
        d[i:j] = value
        if m is None:
            if self._mask is not None:
                self.unshare_mask()
                self._mask[i:j] = False
        else:
            if self._mask is None:
                self._mask = make_mask_none(self._data.shape)
                self._shared_mask = False
            self._mask[i:j] = m

    def __len__ (self):
        """Return length of first dimension. This is weird but Python's
         slicing behavior depends on it."""
        return len(self._data)

    def __and__(self, other):
        "Return bitwise_and"
        return bitwise_and(self, other)

    def __or__(self, other):
        "Return bitwise_or"
        return bitwise_or(self, other)

    def __xor__(self, other):
        "Return bitwise_xor"
        return bitwise_xor(self, other)

    __rand__ = __and__
    __ror__ = __or__
    __rxor__ = __xor__

    def __abs__(self):
        "Return absolute(self)"
        return absolute(self)

    def __neg__(self):
        "Return negative(self)"
        return negative(self)

    def __pos__(self):
        "Return array(self)"
        return array(self)

    def __add__(self, other):
        "Return add(self, other)"
        return add(self, other)

    __radd__ = __add__

    def __mod__ (self, other):
        "Return remainder(self, other)"
        return remainder(self, other)

    def __rmod__ (self, other):
        "Return remainder(other, self)"
        return remainder(other, self)

    def __lshift__ (self, n):
        return left_shift(self, n)

    def __rshift__ (self, n):
        return right_shift(self, n)

    def __sub__(self, other):
        "Return subtract(self, other)"
        return subtract(self, other)

    def __rsub__(self, other):
        "Return subtract(other, self)"
        return subtract(other, self)

    def __mul__(self, other):
        "Return multiply(self, other)"
        return multiply(self, other)

    __rmul__ = __mul__

    def __div__(self, other):
        "Return divide(self, other)"
        return divide(self, other)

    def __rdiv__(self, other):
        "Return divide(other, self)"
        return divide(other, self)

    def __truediv__(self, other):
        "Return divide(self, other)"
        return true_divide(self, other)

    def __rtruediv__(self, other):
        "Return divide(other, self)"
        return true_divide(other, self)

    def __floordiv__(self, other):
        "Return divide(self, other)"
        return floor_divide(self, other)

    def __rfloordiv__(self, other):
        "Return divide(other, self)"
        return floor_divide(other, self)

    def __pow__(self,other, third=None):
        "Return power(self, other, third)"
        return power(self, other, third)

    def __sqrt__(self):
        "Return sqrt(self)"
        return sqrt(self)

    def __iadd__(self, other):
        "Add other to self in place."
        t = self._data.dtypechar
        f = filled(other,0)
        t1 = f.dtypechar
        if t == t1:
            pass
        elif t in typecodes['Integer']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Float']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Complex']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            elif t1 in typecodes['Complex']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        else:
            raise TypeError, 'Incorrect type for in-place operation.'

        if self._mask is None:
            self._data += f
            m = getmask(other)
            self._mask = m
            self._shared_mask = m is not None
        else:
            result = add(self, masked_array(f, mask=getmask(other)))
            self._data = result.data
            self._mask = result.mask
            self._shared_mask = 1
        return self

    def __imul__(self, other):
        "Add other to self in place."
        t = self._data.dtypechar
        f = filled(other,0)
        t1 = f.dtypechar
        if t == t1:
            pass
        elif t in typecodes['Integer']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Float']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Complex']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            elif t1 in typecodes['Complex']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        else:
            raise TypeError, 'Incorrect type for in-place operation.'

        if self._mask is None:
            self._data *= f
            m = getmask(other)
            self._mask = m
            self._shared_mask = m is not None
        else:
            result = multiply(self, masked_array(f, mask=getmask(other)))
            self._data = result.data
            self._mask = result.mask
            self._shared_mask = 1
        return self

    def __isub__(self, other):
        "Subtract other from self in place."
        t = self._data.dtypechar
        f = filled(other,0)
        t1 = f.dtypechar
        if t == t1:
            pass
        elif t in typecodes['Integer']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Float']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Complex']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            elif t1 in typecodes['Complex']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        else:
            raise TypeError, 'Incorrect type for in-place operation.'

        if self._mask is None:
            self._data -= f
            m = getmask(other)
            self._mask = m
            self._shared_mask = m is not None
        else:
            result = subtract(self, masked_array(f, mask=getmask(other)))
            self._data = result.data
            self._mask = result.mask
            self._shared_mask = 1
        return self



    def __idiv__(self, other):
        "Divide self by other in place."
        t = self._data.dtypechar
        f = filled(other,0)
        t1 = f.dtypechar
        if t == t1:
            pass
        elif t in typecodes['Integer']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Float']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        elif t in typecodes['Complex']:
            if t1 in typecodes['Integer']:
                f = f.astype(t)
            elif t1 in typecodes['Float']:
                f = f.astype(t)
            elif t1 in typecodes['Complex']:
                f = f.astype(t)
            else:
                raise TypeError, 'Incorrect type for in-place operation.'
        else:
            raise TypeError, 'Incorrect type for in-place operation.'
        mo = getmask(other)
        result = divide(self, masked_array(f, mask=mo))
        self._data = result.data
        dm = result.raw_mask()
        if dm is not self._mask:
            self._mask = dm
            self._shared_mask = 1
        return self

    def __eq__(self,other):
        return equal(self,other)

    def __ne__(self,other):
        return not_equal(self,other)

    def __lt__(self,other):
        return less(self,other)

    def __le__(self,other):
        return less_equal(self,other)

    def __gt__(self,other):
        return greater(self,other)

    def __ge__(self,other):
        return greater_equal(self,other)

    def astype (self, tc):
        "return self as array of given type."
        d = self._data.astype(tc)
        return array(d, mask=self._mask)

    def byte_swapped(self):
        """Returns the raw data field, byte_swapped. Included for consistency
         with numeric but doesn't make sense in this context.
        """
        return self._data.byte_swapped()

    def compressed (self):
        "A 1-D array of all the non-masked data."
        d = oldnumeric.ravel(self._data)
        if self._mask is None:
            return array(d)
        else:
            m = 1 - oldnumeric.ravel(self._mask)
            c = oldnumeric.compress(m, d)
            return array(c, copy=0)

    def count (self, axis = None):
        "Count of the non-masked elements in a, or along a certain axis."
        m = self._mask
        s = self._data.shape
        ls = len(s)
        if m is None:
            if ls == 0:
                return 1
            if ls == 1:
                return s[0]
            if axis is None:
                return reduce(lambda x,y:x*y, s)
            else:
                n = s[axis]
                t = list(s)
                del t[axis]
                return ones(t) * n
        if axis is None:
            w = oldnumeric.ravel(m).astype(int)  
            n1 = size(w)
            if n1 == 1:
                 n2 = w[0]
            else:
                 n2 = umath.add.reduce(w)
            return n1 - n2
        else:
            n1 = size(m, axis)
            n2 = sum(m.astype(int), axis)
            return n1 - n2

    def dot (self, other):
        "s.dot(other) = innerproduct(s, other)"
        return innerproduct(self, other)

    def fill_value(self):
        "Get the current fill value."
        return self._fill_value

    def filled (self, fill_value=None):
        """A numeric array with masked values filled. If fill_value is None,
           use self.fill_value().

           If mask is None, copy data only if not contiguous.
           Result is always a contiguous, numeric array.
# Is contiguous really necessary now?
        """
        d = self._data
        m = self._mask
        if m is None:
            if d.flags['CONTIGUOUS']:
                return d
            else:
                return d.copy()
        else:
            if fill_value is None:
                value = self._fill_value
            else:
                value = fill_value

            if self is masked:
                result = numeric.array(value).reshape(*d.shape)
            else:
                try:
                    result = numeric.array(d, dtype=d.dtype, copy=1)
                    result[m] = value
                except:
                    #ok, can't put that value in here
                    value = numeric.array(value, dtype=object)
                    d = d.astype(object)
                    result = oldnumeric.choose(m, (d, value))
            return result

    def ids (self):
        """Return the ids of the data and mask areas"""
        return (id(self._data), id(self._mask))

    def iscontiguous (self):
        "Is the data contiguous?"
        return self._data.flags['CONTIGUOUS']

    def itemsize(self):
        "Item size of each data item."
        return self._data.itemsize


    def outer(self, other):
        "s.outer(other) = outerproduct(s, other)"
        return outerproduct(self, other)

    def put (self, values):
        """Set the non-masked entries of self to filled(values).
           No change to mask
        """
        iota = numeric.arange(self.size)
        d = self._data
        if self._mask is None:
            ind = iota
        else:
            ind = oldnumeric.compress(1 - self._mask, iota)
        d[ind] =  filled(values).astype(d.dtype)

    def putmask (self, values):
        """Set the masked entries of self to filled(values).
           Mask changed to None.
        """
        d = self._data
        if self._mask is not None:
            d[self._mask] = filled(values).astype(d.dtype)
            self._shared_mask = 0
            self._mask = None

    def ravel (self):
        """Return a 1-D view of self."""
        if self._mask is None:
            return masked_array(self._data.ravel())
        else:
            return masked_array(self._data.ravel(), self._mask.ravel())

    def raw_data (self):
        """ Obsolete; use data property instead.
            The raw data; portions may be meaningless.
            May be noncontiguous. Expert use only."""
        return self._data
    data = property(fget=raw_data, 
           doc="The data, but values at masked locations are meaningless.")

    def raw_mask (self):
        """ Obsolete; use mask property instead.
            May be noncontiguous. Expert use only.
        """
        return self._mask
    mask = property(fget=raw_mask, 
           doc="The mask, may be None. Values where mask true are meaningless.")

    def reshape (self, *s):
        """This array reshaped to shape s"""
        d = self._data.reshape(*s)
        if self._mask is None:
            return masked_array(d)
        else:
            m = self._mask.reshape(*s)
        return masked_array(d, m)

    def set_fill_value (self, v=None):
        "Set the fill value to v. Omit v to restore default."
        if v is None:
            v = default_fill_value (self.raw_data())
        self._fill_value = v

    def _get_size (self):
        return self._data.size
    size = property(fget=_get_size, doc="Number of elements in the array.")
## CHECK THIS: signature of numeric.array.size?
    
    def _get_dtypechar(self):
        return self._data.dtypechar
    dtypechar = property(fget=_get_dtypechar, doc="type character of the array.")

    def _get_dtype(self):
        return self._data.dtype
    dtype = property(fget=_get_dtype, doc="type of the array elements.")

    def item(self):
        "Return Python scalar if possible."
        if self._mask is not None:
            m = oldnumeric.ravel(self._mask)
            try:
                if m[0]:
                    return masked
            except IndexError:
                return masked
        return self._data.item()

    def tolist(self, fill_value=None):
        "Convert to list"
        return self.filled(fill_value).tolist()

    def tostring(self, fill_value=None):
        "Convert to string"
        return self.filled(fill_value).tostring()

    def unmask (self):
        "Replace the mask by None if possible."
        if self._mask is None: return
        m = make_mask(self._mask, flag=1)
        if m is None:
            self._mask = None
            self._shared_mask = 0

    def unshare_mask (self):
        "If currently sharing mask, make a copy."
        if self._shared_mask:
            self._mask = make_mask (self._mask, copy=1, flag=0)
            self._shared_mask = 0

    shape = property(_get_shape, _set_shape,
           doc = 'tuple giving the shape of the array')

    flat = property(_get_flat, _set_flat,
           doc = 'Access array in flat form.')

    real = property(_get_real, _set_real,
           doc = 'Access the real part of the array')

    imaginary = property(_get_imaginary, _set_imaginary,
           doc = 'Access the imaginary part of the array')

    imag = imaginary

#end class MaskedArray

array = MaskedArray

def isMaskedArray (x):
    "Is x a masked array, that is, an instance of MaskedArray?"
    return isinstance(x, MaskedArray)

isarray = isMaskedArray
isMA = isMaskedArray  #backward compatibility

def allclose (a, b, fill_value=1, rtol=1.e-5, atol=1.e-8):
    """ Returns true if all components of a and b are equal
        subject to given tolerances.
        If fill_value is 1, masked values considered equal.
        If fill_value is 0, masked values considered unequal.
        The relative error rtol should be positive and << 1.0
        The absolute error atol comes into play for those elements
        of b that are very small or zero; it says how small a must be also.
    """
    m = mask_or(getmask(a), getmask(b))
    d1 = filled(a)
    d2 = filled(b)
    x = filled(array(d1, copy=0, mask=m), fill_value).astype(float)
    y = filled(array(d2, copy=0, mask=m), 1).astype(float)
    d = umath.less_equal(umath.absolute(x-y), atol + rtol * umath.absolute(y))
    return oldnumeric.alltrue(oldnumeric.ravel(d))

def allequal (a, b, fill_value=1):
    """
        True if all entries of  a and b are equal, using
        fill_value as a truth value where either or both are masked.
    """
    m = mask_or(getmask(a), getmask(b))
    if m is None:
        x = filled(a)
        y = filled(b)
        d = umath.equal(x, y)
        return oldnumeric.alltrue(oldnumeric.ravel(d))
    elif fill_value:
        x = filled(a)
        y = filled(b)
        d = umath.equal(x, y)
        dm = array(d, mask=m, copy=0)
        return oldnumeric.alltrue(oldnumeric.ravel(filled(dm, 1)))
    else:
        return 0

def masked_values (data, value, rtol=1.e-5, atol=1.e-8, copy=1):
    """
       masked_values(data, value, rtol=1.e-5, atol=1.e-8)
       Create a masked array; mask is None if possible.
       If copy==0, and otherwise possible, result
       may share data values with original array.
       Let d = filled(data, value). Returns d
       masked where abs(data-value)<= atol + rtol * abs(value)
       if d is of a floating point type. Otherwise returns
       masked_object(d, value, copy)
    """
    abs = umath.absolute
    d = filled(data, value)
    if issubclass(d.dtype, numeric.floating):
        m = umath.less_equal(abs(d-value), atol+rtol*abs(value))
        m = make_mask(m, flag=1)
        return array(d, mask = m, copy=copy,
                      fill_value=value)
    else:
        return masked_object(d, value, copy=copy)

def masked_object (data, value, copy=1):
    "Create array masked where exactly data equal to value"
    d = filled(data, value)
    dm = make_mask(umath.equal(d, value), flag=1)
    return array(d, mask=dm, copy=copy, fill_value=value)

def arrayrange(start, stop=None, step=1, dtype=None):
    """Just like range() except it returns a array whose type can be specified
    by the keyword argument dtypechar.
    """
    return array(numeric.arrayrange(start, stop, step, dtype))

arange = arrayrange

def fromstring (s, t):
    "Construct a masked array from a string. Result will have no mask."
    return masked_array(numeric.fromstring(s, t))

def left_shift (a, n):
    "Left shift n bits"
    m = getmask(a)
    if m is None:
        d = umath.left_shift(filled(a), n)
        return masked_array(d)
    else:
        d = umath.left_shift(filled(a,0), n)
        return masked_array(d, m)

def right_shift (a, n):
    "Right shift n bits"
    m = getmask(a)
    if m is None:
        d = umath.right_shift(filled(a), n)
        return masked_array(d)
    else:
        d = umath.right_shift(filled(a,0), n)
        return masked_array(d, m)

def resize (a, new_shape):
    """resize(a, new_shape) returns a new array with the specified shape.
    The original array's total size can be any size."""
    m = getmask(a)
    if m is not None:
        m = oldnumeric.resize(m, new_shape)
    result = array(oldnumeric.resize(filled(a), new_shape), mask=m)
    result.set_fill_value(get_fill_value(a))
    return result

def repeat(a, repeats, axis=0):
    """repeat elements of a repeats times along axis
       repeats is a sequence of length a.shape[axis]
       telling how many times to repeat each element.
    """
    af = filled(a)
    if isinstance(repeats, types.IntType):
        repeats = tuple([repeats]*(shape(af)[axis]))

    m = getmask(a)
    if m is not None:
        m = oldnumeric.repeat(m, repeats, axis)
    d = oldnumeric.repeat(af, repeats, axis)
    result = masked_array(d, m)
    result.set_fill_value(get_fill_value(a))
    return result

def identity(n):
    """identity(n) returns the identity matrix of shape n x n.
    """
    return array(numeric.identity(n))

def indices (dimensions, dtype=None):
    """indices(dimensions,dtype=None) returns an array representing a grid
    of indices with row-only, and column-only variation.
    """
    return array(numeric.indices(dimensions, dtype))

def zeros (shape, dtype=int):
    """zeros(n, dtype=int) =
     an array of all zeros of the given length or shape."""
    return array(numeric.zeros(shape, dtype))

def ones (shape, dtype=int):
    """ones(n, dtype=int) =
     an array of all ones of the given length or shape."""
    return array(numeric.ones(shape, dtype))


def count (a, axis = None):
    "Count of the non-masked elements in a, or along a certain axis."
    a = masked_array(a)
    return a.count(axis)

def power (a, b, third=None):
    "a**b"
    if third is not None:
        raise MAError, "3-argument power not supported."
    ma = getmask(a)
    mb = getmask(b)
    m = mask_or(ma, mb)
    fa = filled(a, 1)
    fb = filled(b, 1)
    if fb.dtypechar in typecodes["Integer"]:
        return masked_array(umath.power(fa, fb), m)
    md = make_mask(umath.less_equal (fa, 0), flag=1)
    m = mask_or(m, md)
    if m is None:
        return masked_array(umath.power(fa, fb))
    else:
        fa = numeric.where(m, 1, fa)
        return masked_array(umath.power(fa, fb), m)

def masked_array (a, mask=None, fill_value=None):
    """masked_array(a, mask=None) =
       array(a, mask=mask, copy=0, fill_value=fill_value)
    """
    return array(a, mask=mask, copy=0, fill_value=fill_value)

sum = add.reduce
product = multiply.reduce

def average (a, axis=0, weights=None, returned = 0):
    """average(a, axis=0, weights=None)
       Computes average along indicated axis.
       If axis is None, average over the entire array
       Inputs can be integer or floating types; result is of type float.

       If weights are given, result is sum(a*weights)/(sum(weights)*1.0)
       weights must have a's shape or be the 1-d with length the size
       of a in the given axis.

       If returned, return a tuple: the result and the sum of the weights
       or count of values. Results will have the same shape.

       masked values in the weights will be set to 0.0
    """
    a = masked_array(a)
    mask = a.mask
    ash = a.shape
    if ash == ():
        ash = (1,)
    if axis is None:
        if mask is None:
            if weights is None:
                n = add.reduce(a.raw_data().ravel())
                d = reduce(lambda x, y: x * y, ash, 1.0)
            else:
                w = filled(weights, 0.0).ravel()
                n = umath.add.reduce(a.raw_data().ravel() * w)
                d = umath.add.reduce(w)
                del w
        else:
            if weights is None:
                n = add.reduce(a.ravel())
                w = oldnumeric.choose(mask, (1.0,0.0)).ravel()
                d = umath.add.reduce(w)
                del w
            else:
                w = array(filled(weights, 0.0), float, mask=mask).ravel()
                n = add.reduce(a.ravel() * w)
                d = add.reduce(w)
                del w
    else:
        if mask is None:
            if weights is None:
                d = ash[axis] * 1.0
                n = umath.add.reduce(a.raw_data(), axis)
            else:
                w = filled(weights, 0.0)
                wsh = w.shape
                if wsh == ():
                    wsh = (1,)
                if wsh == ash:
                    w = numeric.array(w, float, copy=0)
                    n = add.reduce(a*w, axis)
                    d = add.reduce(w, axis)
                    del w
                elif wsh == (ash[axis],):
                    ni = ash[axis]
                    r = [newaxis]*len(ash)
                    r[axis] = slice(None,None,1)
                    w = eval ("w["+ repr(tuple(r)) + "] * ones(ash, float)")
                    n = add.reduce(a*w, axis)
                    d = add.reduce(w, axis)
                    del w, r
                else:
                    raise ValueError, 'average: weights wrong shape.'
        else:
            if weights is None:
                n = add.reduce(a, axis)
                w = numeric.choose(mask, (1.0, 0.0))
                d = umath.add.reduce(w, axis)
                del w
            else:
                w = filled(weights, 0.0)
                wsh = w.shape
                if wsh == ():
                    wsh = (1,)
                if wsh == ash:
                    w = array(w, float, mask=mask, copy=0)
                    n = add.reduce(a*w, axis)
                    d = add.reduce(w, axis)
                elif wsh == (ash[axis],):
                    ni = ash[axis]
                    r = [newaxis]*len(ash)
                    r[axis] = slice(None,None,1)
                    w = eval ("w["+ repr(tuple(r)) + "] * masked_array(ones(ash, float), mask)")
                    n = add.reduce(a*w, axis)
                    d = add.reduce(w, axis)
                else:
                    raise ValueError, 'average: weights wrong shape.'
                del w
    #print n, d, repr(mask), repr(weights)
    if n is masked or d is masked: return masked
    result = divide (n, d)
    del n

    if isinstance(result, MaskedArray):
        result.unmask()
        if returned:
            if not isinstance(d, MaskedArray):
                d = masked_array(d)
            if not d.shape == result.shape:
                d = ones(result.shape, float) * d
            d.unmask()
    if returned:
        return result, d
    else:
        return result

def where (condition, x, y):
    """where(condition, x, y) is x where condition is nonzero, y otherwise.
       condition must be convertible to an integer array.
       Answer is always the shape of condition.
       The type depends on x and y. It is integer if both x and y are
       the value masked.
    """
    fc = filled(not_equal(condition,0), 0)
    if x is masked:
        xv = 0
        xm = 1
    else:
        xv = filled(x)
        xm = getmask(x)
        if xm is None: xm = 0
    if y is masked:
        yv = 0
        ym = 1
    else:
        yv = filled(y)
        ym = getmask(y)
        if ym is None: ym = 0
    d = numeric.choose(fc, (yv, xv))
    md = numeric.choose(fc, (ym, xm))
    m = getmask(condition)
    m = make_mask(mask_or(m, md), copy=0, flag=1)
    return masked_array(d, m)

def choose (indices, t):
    "Returns array shaped like indices with elements chosen from t"
    def fmask (x):
        if x is masked: return 1
        return filled(x)
    def nmask (x):
        if x is masked: return 1
        m = getmask(x)
        if m is None: return 0
        return m
    c = filled(indices,0)
    masks = [nmask(x) for x in t]
    a = [fmask(x) for x in t]
    d = numeric.choose(c, a)
    m = numeric.choose(c, masks)
    m = make_mask(mask_or(m, getmask(indices)), copy=0, flag=1)
    return masked_array(d, m)

def masked_where(condition, x, copy=1):
    """Return x as an array masked where condition is true.
       Also masked where x or condition masked.
    """
    cm = filled(condition,1)
    m = mask_or(getmask(x), cm)
    return array(filled(x), copy=copy, mask=m)

def masked_greater(x, value, copy=1):
    "masked_greater(x, value) = x masked where x > value"
    return masked_where(greater(x, value), x, copy)

def masked_greater_equal(x, value, copy=1):
    "masked_greater_equal(x, value) = x masked where x >= value"
    return masked_where(greater_equal(x, value), x, copy)

def masked_less(x, value, copy=1):
    "masked_less(x, value) = x masked where x < value"
    return masked_where(less(x, value), x, copy)

def masked_less_equal(x, value, copy=1):
    "masked_less_equal(x, value) = x masked where x <= value"
    return masked_where(less_equal(x, value), x, copy)

def masked_not_equal(x, value, copy=1):
    "masked_not_equal(x, value) = x masked where x != value"
    d = filled(x,0)
    c = umath.not_equal(d, value)
    m = mask_or(c, getmask(x))
    return array(d, mask=m, copy=copy)

def masked_equal(x, value, copy=1):
    """masked_equal(x, value) = x masked where x == value
       For floating point consider masked_values(x, value) instead.
    """
    d = filled(x,0)
    c = umath.equal(d, value)
    m = mask_or(c, getmask(x))
    return array(d, mask=m, copy=copy)

def masked_inside(x, v1, v2, copy=1):
    """x with mask of all values of x that are inside [v1,v2]
       v1 and v2 can be given in either order.
    """
    if v2 < v1:
        t = v2
        v2 = v1
        v1 = t
    d=filled(x, 0)
    c = umath.logical_and(umath.less_equal(d, v2), umath.greater_equal(d, v1))
    m = mask_or(c, getmask(x))
    return array(d, mask = m, copy=copy)

def masked_outside(x, v1, v2, copy=1):
    """x with mask of all values of x that are outside [v1,v2]
       v1 and v2 can be given in either order.
    """
    if v2 < v1:
        t = v2
        v2 = v1
        v1 = t
    d = filled(x,0)
    c = umath.logical_or(umath.less(d, v1), umath.greater(d, v2))
    m = mask_or(c, getmask(x))
    return array(d, mask = m, copy=copy)

def reshape (a, *newshape):
    "Copy of a with a new shape."
    m = getmask(a)
    d = filled(a).reshape(*newshape)
    if m is None:
        return masked_array(d)
    else:
        return masked_array(d, mask=numeric.reshape(m, *newshape))

def ravel (a):
    "a as one-dimensional, may share data and mask"
    m = getmask(a)
    d = oldnumeric.ravel(filled(a))
    if m is None:
        return masked_array(d)
    else:
        return masked_array(d, mask=numeric.ravel(m))

def concatenate (arrays, axis=0):
    "Concatenate the arrays along the given axis"
    d = []
    for x in arrays:
        d.append(filled(x))
    d = numeric.concatenate(d, axis)
    for x in arrays:
        if getmask(x) is not None: break
    else:
        return masked_array(d)
    dm = []
    for x in arrays:
        dm.append(getmaskarray(x))
    dm = numeric.concatenate(dm, axis)
    return masked_array(d, mask=dm)

def take (a, indices, axis=0):
    "take(a, indices, axis=0) returns selection of items from a."
    m = getmask(a)
    d = masked_array(a).raw_data()
    if m is None:
        return masked_array(numeric.take(d, indices, axis))
    else:
        return masked_array(numeric.take(d, indices, axis),
                     mask = numeric.take(m, indices, axis))

def transpose(a, axes=None):
    "transpose(a, axes=None) reorder dimensions per tuple axes"
    m = getmask(a)
    d = filled(a)
    if m is None:
        return masked_array(numeric.transpose(d, axes))
    else:
        return masked_array(numeric.transpose(d, axes),
                     mask = numeric.transpose(m, axes))


def put(a, indices, values):
    """put(a, indices, values) sets storage-indexed locations to corresponding values.

    Values and indices are filled if necessary.

    """
    d = a.raw_data()
    ind = filled(indices)
    v = filled(values)
    numeric.put (d, ind, v)
    m = getmask(a)
    if m is not None:
        a.unshare_mask()
        numeric.put(a.raw_mask(), ind, 0)

def putmask(a, mask, values):
    "putmask(a, mask, values) sets a where mask is true."
    if mask is None:
        return
    numeric.putmask(a.raw_data(), mask, values)
    m = getmask(a)
    if m is None: return
    a.unshare_mask()
    numeric.putmask(a.raw_mask(), mask, 0)

def innerproduct(a,b):
    """innerproduct(a,b) returns the dot product of two arrays, which has
    shape a.shape[:-1] + b.shape[:-1] with elements computed by summing the
    product of the elements from the last dimensions of a and b.
    Masked elements are replace by zeros.
    """
    fa = filled(a, 0)
    fb = filled(b, 0)
    if len(fa.shape) == 0: fa.shape = (1,)
    if len(fb.shape) == 0: fb.shape = (1,)
    return masked_array(numeric.innerproduct(fa, fb))

def outerproduct(a, b):
    """outerproduct(a,b) = {a[i]*b[j]}, has shape (len(a),len(b))"""
    fa = filled(a,0).ravel()
    fb = filled(b,0).ravel()
    d = numeric.outerproduct(fa, fb)
    ma = getmask(a)
    mb = getmask(b)
    if ma is None and mb is None:
        return masked_array(d)
    ma = getmaskarray(a)
    mb = getmaskarray(b)
    m = make_mask(1-numeric.outerproduct(1-ma,1-mb), copy=0)
    return masked_array(d, m)

def dot(a, b):
    """dot(a,b) returns matrix-multiplication between a and b.  The product-sum
    is over the last dimension of a and the second-to-last dimension of b.
    Masked values are replaced by zeros. See also innerproduct.
    """
    return innerproduct(filled(a,0), numeric.swapaxes(filled(b,0), -1, -2))

def compress(condition, x, dimension=-1):
    """Select those parts of x for which condition is true.
       Masked values in condition are considered false.
    """
    c = filled(condition, 0)
    m = getmask(x)
    if m is not None:
        m=numeric.compress(c, m, dimension)
    d = numeric.compress(c, filled(x), dimension)
    return masked_array(d, m)

class _minimum_operation:
    "Object to calculate minima"
    def __init__ (self):
        """minimum(a, b) or minimum(a)
           In one argument case returns the scalar minimum.
        """
        pass

    def __call__ (self, a, b=None):
        "Execute the call behavior."
        if b is None:
            m = getmask(a)
            if m is None:
                d = amin(filled(a).ravel())
                return d
            ac = a.compressed()
            if len(ac) == 0:
                return masked
            else:
                return amin(ac.raw_data())
        else:
            return where(less(a, b), a, b)[...]

    def reduce (self, target, axis=0):
        """Reduce target along the given axis."""
        m = getmask(target)
        if m is None:
            t = filled(target)
            return masked_array (umath.minimum.reduce (t, axis))
        else:
            t = umath.minimum.reduce(filled(target, minimum_fill_value(target)), axis)
            m = umath.logical_and.reduce(m, axis)
            return masked_array(t, m, get_fill_value(target))

    def outer (self, a, b):
        "Return the function applied to the outer product of a and b."
        ma = getmask(a)
        mb = getmask(b)
        if ma is None and mb is None:
            m = None
        else:
            ma = getmaskarray(a)
            mb = getmaskarray(b)
            m = logical_or.outer(ma, mb)
        d = umath.minimum.outer(filled(a), filled(b))
        return masked_array(d, m)

minimum = _minimum_operation ()

class _maximum_operation:
    "Object to calculate maxima"
    def __init__ (self):
        """maximum(a, b) or maximum(a)
           In one argument case returns the scalar maximum.
        """
        pass

    def __call__ (self, a, b=None):
        "Execute the call behavior."
        if b is None:
            m = getmask(a)
            if m is None:
                d = amax(filled(a).ravel())
                return d
            ac = a.compressed()
            if len(ac) == 0:
                return masked
            else:
                return amax(ac.raw_data())
        else:
            return where(greater(a, b), a, b)[...]

    def reduce (self, target, axis=0):
        """Reduce target along the given axis."""
        m = getmask(target)
        if m is None:
            t = filled(target)
            return masked_array (umath.maximum.reduce (t, axis))
        else:
            t = umath.maximum.reduce(filled(target, maximum_fill_value(target)), axis)
            m = umath.logical_and.reduce(m, axis)
            return masked_array(t, m, get_fill_value(target))

    def outer (self, a, b):
        "Return the function applied to the outer product of a and b."
        ma = getmask(a)
        mb = getmask(b)
        if ma is None and mb is None:
            m = None
        else:
            ma = getmaskarray(a)
            mb = getmaskarray(b)
            m = logical_or.outer(ma, mb)
        d = umath.maximum.outer(filled(a), filled(b))
        return masked_array(d, m)

maximum = _maximum_operation ()

def sort (x, axis = -1, fill_value=None):
    """If x does not have a mask, return a masked array formed from the
       result of numeric.sort(x, axis).
       Otherwise, fill x with fill_value. Sort it.
       Set a mask where the result is equal to fill_value.
       Note that this may have unintended consequences if the data contains the
       fill value at a non-masked site.

       If fill_value is not given the default fill value for x's type will be
       used.
    """
    if fill_value is None:
        fill_value = default_fill_value (x)
    d = filled(x, fill_value)
    s = oldnumeric.sort(d, axis)
    if getmask(x) is None:
        return masked_array(s)
    return masked_values(s, fill_value, copy=0)

def diagonal(a, k = 0, axis1=0, axis2=1):
    """diagonal(a,k=0,axis1=0, axis2=1) = the k'th diagonal of a"""
    d = oldnumeric.diagonal(filled(a), k, axis1, axis2)
    m = getmask(a)
    if m is None:
        return masked_array(d, m)
    else:
        return masked_array(d, oldnumeric.diagonal(m, k, axis1, axis2))

def argsort (x, axis = -1, fill_value=None):
    """Treating masked values as if they have the value fill_value,
       return sort indices for sorting along given axis.
       if fill_value is None, use get_fill_value(x)
       Returns a numpy array.
    """
    d = filled(x, fill_value)
    return oldnumeric.argsort(d, axis)

def argmin (x, axis = -1, fill_value=None):
    """Treating masked values as if they have the value fill_value,
       return indices for minimum values along given axis.
       if fill_value is None, use get_fill_value(x).
       Returns a numpy array if x has more than one dimension.
       Otherwise, returns a scalar index.
    """
    d = filled(x, fill_value)
    return oldnumeric.argmin(d, axis)

def argmax (x, axis = -1, fill_value=None):
    """Treating masked values as if they have the value fill_value,
       return sort indices for maximum along given axis.
       if fill_value is None, use -get_fill_value(x) if it exists.
       Returns a numpy array if x has more than one dimension.
       Otherwise, returns a scalar index.
    """
    if fill_value is None:
        fill_value = default_fill_value (x)
        try:
            fill_value = - fill_value
        except:
            pass
    d = filled(x, fill_value)
    return oldnumeric.argmax(d, axis)

def fromfunction (f, s):
    """apply f to s to create array as in umath."""
    return masked_array(numeric.fromfunction(f,s))

def asarray(data, dtype=None):
    """asarray(data, dtype) = array(data, dtype, copy=0)
    """
    if isinstance(data, MaskedArray) and \
        (dtype is None or dtype == data.dtype):
        return data
    return array(data, dtype=dtype, copy=0)

masked = MaskedArray([0], int, mask=[1])[0:0]
masked = masked[0:0]



__all__ = ['matrix', 'bmat', 'mat', 'asmatrix']

