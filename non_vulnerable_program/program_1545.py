import timeit
N = [1000,100]
t1 = timeit.Timer('a=N.zeros(shape,type)','import numpy as N; shape=%s;type=float'%N)
t2 = timeit.Timer('a=N.zeros(shape,type)','import Numeric as N; shape=%s;type=N.Float'%N)
t3 = timeit.Timer('a=N.zeros(shape,type)',"import numarray as N; shape=%s;type=N.Float"%N)
print "shape = ", N
print "NumPy: ", t1.repeat(3,100)
print "Numeric: ", t2.repeat(3,100)
print "Numarray: ", t3.repeat(3,100)


#!/usr/bin/env python
"""
A setup.py script to use setuptools, which gives egg goodness, etc.
"""

