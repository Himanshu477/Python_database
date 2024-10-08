from numpy.core.numeric import *
import sys

def fliplr(m):
    """ returns an array m with the rows preserved and columns flipped 
        in the left/right direction.  Works on the first two dimensions of m. 
    """
    m = asarray(m)
    if m.ndim < 2:
        raise ValueError, "Input must be >= 2-d."
    return m[:, ::-1]

def flipud(m):
    """ returns an array with the columns preserved and rows flipped in
        the up/down direction.  Works on the first dimension of m.
    """
    m = asarray(m)
    if m.ndim < 1:
        raise ValueError, "Input must be >= 1-d."
    return m[::-1]

def rot90(m, k=1):
    """ returns the array found by rotating m by k*90
    degrees in the counterclockwise direction.  Works on the first two
    dimensions of m. 
    """
    m = asarray(m)
    if m.ndim < 2:
        raise ValueError, "Input must >= 2-d."
    k = k % 4
    if k == 0: return m
    elif k == 1: return fliplr(m).transpose()
    elif k == 2: return fliplr(flipud(m))
    else: return fliplr(m.transpose())  # k==3

def eye(N, M=None, k=0, dtype=int_):
    """ eye returns a N-by-M 2-d array where the  k-th diagonal is all ones, 
        and everything else is zeros.
    """
    if M is None: M = N
    m = equal(subtract.outer(arange(N), arange(M)),-k)
    return m.astype(dtype)

def diag(v, k=0):
    """ returns the k-th diagonal if v is a array or returns a array 
        with v as the k-th diagonal if v is a vector.
    """
    v = asarray(v)
    s = v.shape
    if len(s)==1:
        n = s[0]+abs(k)
        res = zeros((n,n), v.dtype)
        if (k>=0):
            i = arange(0,n-k)
            fi = i+k+i*n
        else:
            i = arange(0,n+k)
            fi = i+(i-k)*n
        res.flat[fi] = v
        return res
    elif len(s)==2:
        N1,N2 = s
        if k >= 0:
            M = min(N1,N2-k)
            i = arange(0,M)
            fi = i+k+i*N2
        else:
            M = min(N1+k,N2)
            i = arange(0,M)
            fi = i + (i-k)*N2
        return v.flat[fi]
    else:
            raise ValueError, "Input must be 1- or 2-d."


def tri(N, M=None, k=0, dtype=int_):
    """ returns a N-by-M array where all the diagonals starting from
        lower left corner up to the k-th are all ones.
    """
    if M is None: M = N
    m = greater_equal(subtract.outer(arange(N), arange(M)),-k)
    return m.astype(dtype)

def tril(m, k=0):
    """ returns the elements on and below the k-th diagonal of m.  k=0 is the
        main diagonal, k > 0 is above and k < 0 is below the main diagonal.
    """
    m = asarray(m)
    out = multiply(tri(m.shape[0], m.shape[1], k=k, dtype=m.dtype),m)
    return out

def triu(m, k=0):
    """ returns the elements on and above the k-th diagonal of m.  k=0 is the
        main diagonal, k > 0 is above and k < 0 is below the main diagonal.
    """
    m = asarray(m)
    out = multiply((1-tri(m.shape[0], m.shape[1], k-1, m.dtype)),m)
    return out


# borrowed from John Hunter and matplotlib
def vander(x, N=None):
    """
    X = vander(x,N=None)

    The Vandermonde matrix of vector x.  The i-th column of X is the
    the i-th power of x.  N is the maximum power to compute; if N is
    None it defaults to len(x).

    """
    x = asarray(x)
    if N is None: N=len(x)
    X = ones( (len(x),N), x.dtypechar)
    for i in range(N-1):
        X[:,i] = x**(N-i-1)
    return X


"""
Module of functions that are like ufuncs in acting on arrays and optionally
storing results in an output array.
"""
__all__ = ['fix', 'isneginf', 'isposinf', 'sign', 'log2']

