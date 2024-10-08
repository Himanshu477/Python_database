import os,sys

opts = sys.argv[1:]
if not opts:
    opts = ['10','--quiet']

NUMARRAY = "-DNUMARRAY" in sys.argv

test_f77_files = [\
  'f77/return_integer.py',
  'f77/return_logical.py',
  'f77/return_real.py',
  'f77/return_complex.py',
  'f77/callback.py',
  ]

if not NUMARRAY:  # no support for character yet in numarray
    test_f77_files.append('f77/return_character.py')

test_f90_files = [\
  'f90/return_integer.py',
  'f90/return_logical.py',
  'f90/return_real.py',
  'f90/return_complex.py',
  'f90/return_character.py',
  'mixed/run.py',
  ]

test_files = test_f77_files

if NUMARRAY:
    print >>sys.stderr,"NOTE: f2py for numarray does not support"\
          " f90 or character arrays."
else:
    test_files += test_f90_files

py_path = os.environ.get('PYTHONPATH')
if py_path is None:
    py_path = '.'
else:
    py_path = os.pathsep.join(['.',py_path])
os.environ['PYTHONPATH'] = py_path

for f in test_files:
    print "**********************************************"
    ff = os.path.join(sys.path[0],f)
    args = [sys.executable,ff]+opts
    print "Running",' '.join(args)
    status = os.spawnve(os.P_WAIT,sys.executable,args,os.environ)
    if status:
        print 'TEST FAILURE (status=%s)' % (status)
        if f=='f90/return_integer.py':
            sys.exit()


#!/usr/bin/env python
"""

Build 'use others module data' mechanism for f2py2e.

Unfinished.

Copyright 2000 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>          
Permission to use, modify, and distribute this software is given under the
terms of the LGPL.  See http://www.fsf.org

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2000/09/10 12:35:43 $
Pearu Peterson
"""

__version__ = "$Revision: 1.3 $"[10:-1]

f2py_version='See `f2py -v`'

