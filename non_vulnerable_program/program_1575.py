from numpy.core.defmatrix import matrix, asmatrix
from numpy import ndarray, array
import numpy as N

def empty(shape, dtype=None, order='C'):
    """return an empty matrix of the given shape
    """
    return ndarray.__new__(matrix, shape, dtype, order=order)
        
def ones(shape, dtype=None, order='C'):
    """return a matrix initialized to all ones
    """
    a = ndarray.__new__(matrix, shape, dtype, order=order)
    a.fill(1)
    return a

def zeros(shape, dtype=None, order='C'):
    """return a matrix initialized to all zeros
    """
    a = ndarray.__new__(matrix, shape, dtype, order=order)    
    a.fill(0)
    return a

def identity(n,dtype=None):
    """identity(n) returns the identity matrix of shape n x n.
    """
    a = array([1]+n*[0],dtype=dtype)
    b = empty((n,n),dtype=dtype)
    b.flat = a
    return b

def eye(N,M=None, k=0, dtype=float):
    return asmatrix(N.eye(N,M,k,dtype))

def rand(*args):
    return asmatrix(N.rand(*args))

def randn(*args):
    return asmatrix(N.rand(*args))


