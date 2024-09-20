import os
from scipy.distutils.core import setup, Extension

ext = Extension('f2py_ext.fib2',['src/fib2.pyf','src/fib1.f'])

setup(
    name = 'f2py_ext',
    ext_modules = [ext],
    packages = ['f2py_ext.tests','f2py_ext'],
    package_dir = {'f2py_ext':'.'})



!    -*- f90 -*-
python module fib2
    interface
        subroutine fib(a,n)
            real*8 dimension(n),intent(out),depend(n) :: a
            integer intent(in) :: n
        end subroutine fib
    end interface 
end python module fib2


