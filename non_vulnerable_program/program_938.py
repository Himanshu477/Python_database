import doctest
def test_suite(level=1):
    return doctest.DocTestSuite()

if __name__ == "__main__":
    ScipyTest().run()


"""
>>> import scipy.base as nx
>>> from scipy.base.polynomial import poly1d

>>> p = poly1d([1.,2,3])
>>> p
poly1d([ 1.,  2.,  3.])
>>> print p
   2
1 x + 2 x + 3
>>> q = poly1d([3.,2,1])
>>> q
poly1d([ 3.,  2.,  1.])
>>> print q
   2
3 x + 2 x + 1

>>> p(0)
3.0
>>> p(5)
38.0
>>> q(0)
1.0
>>> q(5)
86.0

>>> p * q
poly1d([  3.,   8.,  14.,   8.,   3.])
>>> p / q
[poly1d([ 0.33333333]), poly1d([ 1.33333333,  2.66666667])]
>>> p + q
poly1d([ 4.,  4.,  4.])
>>> p - q
poly1d([-2.,  0.,  2.])
>>> p ** 4
poly1d([   1.,    8.,   36.,  104.,  214.,  312.,  324.,  216.,   81.])

>>> p(q)
poly1d([  9.,  12.,  16.,   8.,   6.])
>>> q(p)
poly1d([  3.,  12.,  32.,  40.,  34.])

>>> nx.asarray(p)
array([ 1.,  2.,  3.])
>>> len(p)
2

>>> p[0], p[1], p[2], p[3]
(3.0, 2.0, 1.0, 0)

>>> p.integ()
poly1d([ 0.33333333,  1.        ,  3.        ,  0.        ])
>>> p.integ(1)
poly1d([ 0.33333333,  1.        ,  3.        ,  0.        ])
>>> p.integ(5)
poly1d([ 0.00039683,  0.00277778,  0.025     ,  0.        ,  0.        ,
        0.        ,  0.        ,  0.        ])
>>> p.deriv()
poly1d([ 2.,  2.])
>>> p.deriv(2)
poly1d([ 2.])
"""

