from type_check import isscalar
from twodim_base import diag
from shape_base import hstack, atleast_1d
from function_base import trim_zeros, sort_complex

__all__ = ['poly','roots','polyint','polyder','polyadd','polysub','polymul',
           'polydiv','polyval','poly1d']
 
def get_eigval_func():
    import scipy.linalg
    eigvals = scipy.linalg.eigvals
    return eigvals

def poly(seq_of_zeros):
    """ Return a sequence representing a polynomial given a sequence of roots.

        If the input is a matrix, return the characteristic polynomial.
    
        Example:
    
         >>> b = roots([1,3,1,5,6])
         >>> poly(b)
         array([1., 3., 1., 5., 6.])
    """
    seq_of_zeros = atleast_1d(seq_of_zeros)    
    sh = shape(seq_of_zeros)
    if len(sh) == 2 and sh[0] == sh[1]:
        eig = get_eigval_func()
        seq_of_zeros=eig(seq_of_zeros)
    elif len(sh) ==1:
        pass
    else:
        raise ValueError, "input must be 1d or square 2d array."

    if len(seq_of_zeros) == 0:
        return 1.0

    a = [1]
    for k in range(len(seq_of_zeros)):
        a = convolve(a,[1, -seq_of_zeros[k]], mode=2)
        
    if a.dtypechar in ['F','D']:
        # if complex roots are all complex conjugates, the roots are real.
        roots = asarray(seq_of_zeros,'D')
        pos_roots = sort_complex(compress(roots.imag > 0,roots))
        neg_roots = conjugate(sort_complex(compress(roots.imag < 0,roots)))
        if (len(pos_roots) == len(neg_roots) and
            alltrue(neg_roots == pos_roots)):
            a = a.real.copy()

    return a

def roots(p):
    """ Return the roots of the polynomial coefficients in p.

        The values in the rank-1 array p are coefficients of a polynomial.
        If the length of p is n+1 then the polynomial is
        p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]
    """
    # If input is scalar, this makes it an array
    eig = get_eigval_func()
    p = atleast_1d(p)
    if len(p.shape) != 1:
        raise ValueError,"Input must be a rank-1 array."
        
    # find non-zero array entries
    non_zero = nonzero(ravel(p))

    # find the number of trailing zeros -- this is the number of roots at 0.
    trailing_zeros = len(p) - non_zero[-1] - 1

    # strip leading and trailing zeros
    p = p[int(non_zero[0]):int(non_zero[-1])+1]
    
    # casting: if incoming array isn't floating point, make it floating point.
    if p.dtypechar not in ['f','d','F','D']:
        p = p.astype('d')

    N = len(p)
    if N > 1:
        # build companion matrix and find its eigenvalues (the roots)
        A = diag(ones((N-2,),p.dtypechar),-1)
        A[0,:] = -p[1:] / p[0]
        roots = eig(A)
    else:
        return array([])

    # tack any zeros onto the back of the array    
    roots = hstack((roots,zeros(trailing_zeros,roots.dtypechar)))
    return roots

def polyint(p,m=1,k=None):
    """Return the mth analytical integral of the polynomial p.

    If k is None, then zero-valued constants of integration are used.
    otherwise, k should be a list of length m (or a scalar if m=1) to
    represent the constants of integration to use for each integration
    (starting with k[0])
    """
    m = int(m)
    if m < 0:
        raise ValueError, "Order of integral must be positive (see polyder)"
    if k is None:
        k = _nx.zeros(m)
    k = atleast_1d(k)
    if len(k) == 1 and m > 1:
        k = k[0]*_nx.ones(m)
    if len(k) < m:
        raise ValueError, \
              "k must be a scalar or a rank-1 array of length 1 or >m."
    if m == 0:
        return p
    else:
        truepoly = isinstance(p,poly1d)
        p = asarray(p)
        y = _nx.zeros(len(p)+1,'d')
        y[:-1] = p*1.0/_nx.arange(len(p),0,-1)
        y[-1] = k[0]        
        val = polyint(y,m-1,k=k[1:])
        if truepoly:
            val = poly1d(val)
        return val
            
def polyder(p,m=1):
    """Return the mth derivative of the polynomial p.
    """
    m = int(m)
    truepoly = isinstance(p,poly1d)
    p = asarray(p)
    n = len(p)-1
    y = p[:-1] * _nx.arange(n,0,-1)
    if m < 0:
        raise ValueError, "Order of derivative must be positive (see polyint)"
    if m == 0:
        return p
    else:
        val = polyder(y,m-1)
        if truepoly:
            val = poly1d(val)
        return val

def polyval(p,x):
    """Evaluate the polynomial p at x.  If x is a polynomial then composition.

    Description:

      If p is of length N, this function returns the value:
      p[0]*(x**N-1) + p[1]*(x**N-2) + ... + p[N-2]*x + p[N-1]

      x can be a sequence and p(x) will be returned for all elements of x.
      or x can be another polynomial and the composite polynomial p(x) will be
      returned.
    """
    p = asarray(p)
    if isinstance(x,poly1d):
        y = 0
    else:
        x = asarray(x)
        y = _nx.zeros(x.shape,x.dtypechar)
    for i in range(len(p)):
        y = x * y + p[i]
    return y

def polyadd(a1,a2):
    """Adds two polynomials represented as lists
    """
    truepoly = (isinstance(a1,poly1d) or isinstance(a2,poly1d))
    a1,a2 = map(atleast_1d,(a1,a2))
    diff = len(a2) - len(a1)
    if diff == 0:
        return a1 + a2
    elif diff > 0:
        zr = _nx.zeros(diff)
        val = _nx.concatenate((zr,a1)) + a2
    else:
        zr = _nx.zeros(abs(diff))
        val = a1 + _nx.concatenate((zr,a2))
    if truepoly:
        val = poly1d(val)
    return val

def polysub(a1,a2):
    """Subtracts two polynomials represented as lists
    """
    truepoly = (isinstance(a1,poly1d) or isinstance(a2,poly1d))
    a1,a2 = map(atleast_1d,(a1,a2))
    diff = len(a2) - len(a1)
    if diff == 0:
        return a1 - a2
    elif diff > 0:
        zr = _nx.zeros(diff)
        val = _nx.concatenate((zr,a1)) - a2
    else:
        zr = _nx.zeros(abs(diff))
        val = a1 - _nx.concatenate((zr,a2))
    if truepoly:
        val = poly1d(val)
    return val


def polymul(a1,a2):
    """Multiplies two polynomials represented as lists.
    """
    truepoly = (isinstance(a1,poly1d) or isinstance(a2,poly1d))
    val = _nx.convolve(a1,a2)
    if truepoly:
        val = poly1d(val)
    return val

def polydiv(a1,a2):
    """Computes q and r polynomials so that a1(s) = q(s)*a2(s) + r(s)
    """
    truepoly = (isinstance(a1,poly1d) or isinstance(a2,poly1d))
    q, r = deconvolve(a1,a2)
    while _nx.allclose(r[0], 0, rtol=1e-14) and (r.shape[-1] > 1):
        r = r[1:]
    if truepoly:
        q, r = map(poly1d,(q,r))
    return q, r

def deconvolve(signal, divisor):
    """Deconvolves divisor out of signal.
    """
    try:
        import scipy.signal
    except:
        print "You need scipy.signal to use this function."
    num = atleast_1d(signal)
    den = atleast_1d(divisor)
    N = len(num)
    D = len(den)
    if D > N:
        quot = [];
        rem = num;
    else:
        input = _nx.ones(N-D+1,_nx.Float)
        input[1:] = 0
        quot = scipy.signal.lfilter(num, den, input)
        rem = num - _nx.convolve(den,quot,mode=2)
    return quot, rem

