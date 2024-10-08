from numerictypes import obj2dtype

__all__ = ['issubclass_', 'get_numpy_include', 'issubdtype']

def issubclass_(arg1, arg2):
    try:
        return issubclass(arg1, arg2)
    except TypeError:
        return False

def issubdtype(arg1, arg2):
    return issubclass(obj2dtype(arg1), obj2dtype(arg2))
    
def get_numpy_include():
    """Return the directory in the package that contains the numpy/*.h header 
    files.
    
    Extension modules that need to compile against numpy.base should use this
    function to locate the appropriate include directory. Using distutils:
    
      import numpy
      Extension('extension_name', ...
                include_dirs=[numpy.get_numpy_include()])
    """
    from numpy.distutils.misc_util import get_numpy_include_dirs
    include_dirs = get_numpy_include_dirs()
    assert len(include_dirs)==1,`include_dirs`
    return include_dirs[0]


# To get sub-modules
