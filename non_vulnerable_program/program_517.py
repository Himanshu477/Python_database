import re
cxx_ext_re = re.compile(r'.*[.](cpp|cxx|cc)\Z',re.I).match
fortran_pyf_ext_re = re.compile(r'.*[.](f90|f95|f77|for|ftn|f|pyf)\Z',re.I).match

class Extension(old_Extension):
    def __init__ (self, name, sources,
                  include_dirs=None,
                  define_macros=None,
                  undef_macros=None,
                  library_dirs=None,
                  libraries=None,
                  runtime_library_dirs=None,
                  extra_objects=None,
                  extra_compile_args=None,
                  extra_link_args=None,
                  export_symbols=None,
                  swig_opts=None,
                  depends=None,
                  language=None,
                  f2py_options=None,
                  module_dirs=None,
                 ):
        old_Extension.__init__(self,name, [],
                               include_dirs,
                               define_macros,
                               undef_macros,
                               library_dirs,
                               libraries,
                               runtime_library_dirs,
                               extra_objects,
                               extra_compile_args,
                               extra_link_args,
                               export_symbols)
        # Avoid assert statements checking that sources contains strings:
        self.sources = sources

        # Python 2.4 distutils new features
        self.swig_opts = swig_opts or []

        # Python 2.3 distutils new features
        self.depends = depends or []
        self.language = language

        # scipy_distutils features
        self.f2py_options = f2py_options or []
        self.module_dirs = module_dirs or []

        return

    def has_cxx_sources(self):
        for source in self.sources:
            if cxx_ext_re(str(source)):
                return True
        return False

    def has_f2py_sources(self):
        for source in self.sources:
            if fortran_pyf_ext_re(source):
                return True
        return False

# class Extension


"""scipy.distutils.fcompiler

Contains FCompiler, an abstract base class that defines the interface
for the scipy.distutils Fortran compiler abstraction model.
"""

__all__ = ['FCompiler','new_fcompiler','show_fcompilers',
           'dummy_fortran_file']

