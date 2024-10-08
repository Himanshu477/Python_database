from numpy.core import *
import string

class UserArray:
    def __init__(self, data, dtype=None, copy=True):
        self.array = array(data, dtype, copy)
        self.shape = self.array.shape
        self.dtype = self.array.dtype
        self.name = string.split(str(self.__class__))[0]
        self.flags = self.array.flags
        self.itemsize = self.array.itemsize

    def __repr__(self):
        if len(self.shape) > 0:
            return self.__class__.__name__+repr(self.array)[len("array"):]
        else:
            return self.__class__.__name__+"("+repr(self.array)+")"

    def __array__(self,t=None):
        if t: return asarray(self.array,t)
        return self.array

    def __float__(self):
        return float(self.array)

    # Array as sequence
    def __len__(self): return len(self.array)

    def __getitem__(self, index):
        return self._rc(self.array[index])

    def __getslice__(self, i, j):
        return self._rc(self.array[i:j])


    def __setitem__(self, index, value):
        self.array[index] = asarray(value,self.dtype)
    def __setslice__(self, i, j, value):
        self.array[i:j] = asarray(value,self.dtype)

    def __abs__(self):
        return self._rc(absolute(self.array))
    def __neg__(self):
        return self._rc(-self.array)

    def __add__(self, other):
        return self._rc(self.array+asarray(other))
    __radd__ = __add__

    def __iadd__(self, other):
        add(self.array, other, self.array)
        return self

    def __sub__(self, other):
        return self._rc(self.array-asarray(other))
    def __rsub__(self, other):
        return self._rc(asarray(other)-self.array)
    def __isub__(self, other):
        subtract(self.array, other, self.array)
        return self

    def __mul__(self, other):
        return self._rc(multiply(self.array,asarray(other)))
    __rmul__ = __mul__
    def __imul__(self, other):
        multiply(self.array, other, self.array)
        return self

    def __div__(self, other):
        return self._rc(divide(self.array,asarray(other)))
    def __rdiv__(self, other):
        return self._rc(divide(asarray(other),self.array))
    def __idiv__(self, other):
        divide(self.array, other, self.array)
        return self

    def __mod__(self, other):
        return self._rc(remainder(self.array, other))
    def __rmod__(self, other):
        return self._rc(remainder(other, self.array))
    def __imod__(self, other):
        remainder(self.array, other, self.array)
        return self

    def __divmod__(self, other):
        return (self._rc(divide(self.array,other)),
                self._rc(remainder(self.array, other)))
    def __rdivmod__(self, other):
        return (self._rc(divide(other, self.array)),
                self._rc(remainder(other, self.array)))

    def __pow__(self,other):
        return self._rc(power(self.array,asarray(other)))
    def __rpow__(self,other):
        return self._rc(power(asarray(other),self.array))
    def __ipow__(self,other):
        power(self.array, other, self.array)
        return self

    def __lshift__(self,other):
        return self._rc(left_shift(self.array, other))
    def __rshift__(self,other):
        return self._rc(right_shift(self.array, other))
    def __rlshift__(self,other):
        return self._rc(left_shift(other, self.array))
    def __rrshift__(self,other):
        return self._rc(right_shift(other, self.array))
    def __ilshift__(self,other):
        left_shift(self.array, other, self.array)
        return self
    def __irshift__(self,other):
        right_shift(self.array, other, self.array)
        return self

    def __and__(self, other):
        return self._rc(bitwise_and(self.array, other))
    def __rand__(self, other):
        return self._rc(bitwise_and(other, self.array))
    def __iand__(self, other):
        bitwise_and(self.array, other, self.array)
        return self

    def __xor__(self, other):
        return self._rc(bitwise_xor(self.array, other))
    def __rxor__(self, other):
        return self._rc(bitwise_xor(other, self.array))
    def __ixor__(self, other):
        bitwise_xor(self.array, other, self.array)
        return self

    def __or__(self, other):
        return self._rc(bitwise_or(self.array, other))
    def __ror__(self, other):
        return self._rc(bitwise_or(other, self.array))
    def __ior__(self, other):
        bitwise_or(self.array, other, self.array)
        return self

    def __neg__(self):
        return self._rc(-self.array)
    def __pos__(self):
        return self._rc(self.array)
    def __abs__(self):
        return self._rc(abs(self.array))
    def __invert__(self):
        return self._rc(invert(self.array))

    def _scalarfunc(a, func):
        if len(a.shape) == 0:
            return func(a[0])
        else:
            raise TypeError, "only rank-0 arrays can be converted to Python scalars."

    def __complex__(self): return self._scalarfunc(complex)
    def __float__(self): return self._scalarfunc(float)
    def __int__(self): return self._scalarfunc(int)
    def __long__(self): return self._scalarfunc(long)
    def __hex__(self): return self._scalarfunc(hex)
    def __oct__(self): return self._scalarfunc(oct)

    def __lt__(self,other): return self._rc(less(self.array,other))
    def __le__(self,other): return self._rc(less_equal(self.array,other))
    def __eq__(self,other): return self._rc(equal(self.array,other))
    def __ne__(self,other): return self._rc(not_equal(self.array,other))
    def __gt__(self,other): return self._rc(greater(self.array,other))
    def __ge__(self,other): return self._rc(greater_equal(self.array,other))

    def copy(self): return self._rc(self.array.copy())

    def tostring(self): return self.array.tostring()

    def byteswap(self): return self._rc(self.array.byteswap())

    def astype(self, typecode): return self._rc(self.array.astype(typecode))

    def _rc(self, a):
        if len(shape(a)) == 0: return a
        else: return self.__class__(a)

    def __setattr__(self,attr,value):
        if attr=='shape':
            self.array.shape=value
        self.__dict__[attr]=value

    def __getattr__(self,attr):
        # for .attributes for example, and any future attributes
        if attr == 'real':
            return self._rc(self.array.real)
        elif attr == 'imag':
            return self._rc(self.array.imag)
        elif attr == 'flat':
            return self._rc(self.array.flat)
        return getattr(self.array, attr)

#############################################################
# Test of class UserArray
#############################################################
if __name__ == '__main__':
