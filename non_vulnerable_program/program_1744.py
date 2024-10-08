from numpy import hstack
import types

def fftshift(x,axes=None):
    """ fftshift(x, axes=None) -> y

    Shift zero-frequency component to center of spectrum.

    This function swaps half-spaces for all axes listed (defaults to all).

    Notes:
      If len(x) is even then the Nyquist component is y[0].
    """
    tmp = asarray(x)
    ndim = len(tmp.shape)
    if axes is None:
        axes = range(ndim)
    y = tmp
    for k in axes:
        n = tmp.shape[k]
        p2 = (n+1)/2
        mylist = concatenate((arange(p2,n),arange(p2)))
        y = take(y,mylist,k)
    return y


def ifftshift(x,axes=None):
    """ ifftshift(x,axes=None) - > y

    Inverse of fftshift.
    """
    tmp = asarray(x)
    ndim = len(tmp.shape)
    if axes is None:
        axes = range(ndim)
    y = tmp
    for k in axes:
        n = tmp.shape[k]
        p2 = n-(n+1)/2
        mylist = concatenate((arange(p2,n),arange(p2)))
        y = take(y,mylist,k)
    return y

def fftfreq(n,d=1.0):
    """ fftfreq(n, d=1.0) -> f

    DFT sample frequencies

    The returned float array contains the frequency bins in
    cycles/unit (with zero at the start) given a window length n and a
    sample spacing d:

      f = [0,1,...,n/2-1,-n/2,...,-1]/(d*n)         if n is even
      f = [0,1,...,(n-1)/2,-(n-1)/2,...,-1]/(d*n)   if n is odd
    """
    assert isinstance(n,types.IntType) or isinstance(n, integer)
    return hstack((arange(0,(n-1)/2 + 1), arange(-(n/2),0))) / (n*d)


#!/usr/bin/env python
"""
Defines FortranAnalyzer.

Permission to use, modify, and distribute this software is given under the
terms of the NumPy License. See http://scipy.org.
NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.

Author: Pearu Peterson <pearu@cens.ioc.ee>
Created: June 2006
"""

