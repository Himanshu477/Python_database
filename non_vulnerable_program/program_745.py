import cbfoo
from Numeric import *
def fun(x):
    return x
i=0
while i<15000:
    i=i+1
    cbfoo.foo(fun,i,(2,))
print "ok"





#!/usr/bin/env python
"""

Copyright 2000 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>          
Permission to use, modify, and distribute this software is given under the
terms of the LGPL.  See http://www.fsf.org

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2000/09/10 12:35:44 $
Pearu Peterson
"""

__version__ = "$Revision: 1.2 $"[10:-1]

tests=[]
all = 1
skip = 1
################################################################
if 0 or all:
    test={}
    test['name']='Argument passing to Fortran function(character)'
    test['depends']=['fncall']
    test['f']="""\
      function f(a)
      integer f
      character a
      if (a .eq. 'w') then
          f = 3
      else
          write(*,*) "Fortran: expected 'w' but got '",a,"'"
          f = 4
      end if
      end
"""
    test['py']="""\
