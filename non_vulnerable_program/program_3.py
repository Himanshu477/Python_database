import os, string
from glob import glob
from types import *
from distutils.core import Command
from distutils.errors import *
from distutils.sysconfig import customize_compiler


def show_compilers ():
    from distutils.ccompiler import show_compilers
    show_compilers()

def get_headers(directory_list):
    # get *.h files from list of directories
    headers = []
    for dir in directory_list:
        head = glob(os.path.join(dir,"*.h"))
        headers.extend(head)

    return headers

def get_directories(list_of_sources):
    # get unique directories from list of sources.
    direcs = []
    for file in list_of_sources:
        dir = os.path.split(file)
        if dir[0] != '' and not dir[0] in direcs:
            direcs.append(dir[0])

    return direcs


class build_clib (Command):

    description = "build C/C++ libraries used by Python extensions"

    user_options = [
        ('build-clib', 'b',
         "directory to build C/C++ libraries to"),
        ('build-temp', 't',
         "directory to put temporary build by-products"),
        ('debug', 'g',
         "compile with debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', None,
         "list available compilers", show_compilers),
        ]

    def initialize_options (self):
        self.build_clib = None
        self.build_temp = None

        # List of libraries to build
        self.libraries = None

        # Compilation options for all libraries
        self.include_dirs = None
        self.define = None
        self.undef = None
        self.debug = None
        self.force = 0
        self.compiler = None

    # initialize_options()


    def finalize_options (self):

        # This might be confusing: both build-clib and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.
        self.set_undefined_options('build',
                                   ('build_temp', 'build_clib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))

        self.libraries = self.distribution.libraries
        if self.libraries:
            self.check_library_list(self.libraries)

        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        if type(self.include_dirs) is StringType:
            self.include_dirs = string.split(self.include_dirs,
                                             os.pathsep)

        # XXX same as for build_ext -- what about 'self.define' and
        # 'self.undef' ?

    # finalize_options()


    def run (self):

        if not self.libraries:
            return

        # Yech -- this is cut 'n pasted from build_ext.py!
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     verbose=self.verbose,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name,value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)

        self.build_libraries(self.libraries)

    # run()


    def check_library_list (self, libraries):
        """Ensure that the list of libraries (presumably provided as a
           command option 'libraries') is valid, i.e. it is a list of
           2-tuples, where the tuples are (library_name, build_info_dict).
           Raise DistutilsSetupError if the structure is invalid anywhere;
           just returns otherwise."""

        # Yechh, blecch, ackk: this is ripped straight out of build_ext.py,
        # with only names changed to protect the innocent!

        if type(libraries) is not ListType:
            raise DistutilsSetupError, \
                  "'libraries' option must be a list of tuples"

        for lib in libraries:
            if type(lib) is not TupleType and len(lib) != 2:
                raise DistutilsSetupError, \
                      "each element of 'libraries' must a 2-tuple"

            if type(lib[0]) is not StringType:
                raise DistutilsSetupError, \
                      "first element of each tuple in 'libraries' " + \
                      "must be a string (the library name)"
            if '/' in lib[0] or (os.sep != '/' and os.sep in lib[0]):
                raise DistutilsSetupError, \
                      ("bad library name '%s': " + 
                       "may not contain directory separators") % \
                      lib[0]

            if type(lib[1]) is not DictionaryType:
                raise DistutilsSetupError, \
                      "second element of each tuple in 'libraries' " + \
                      "must be a dictionary (build info)"
        # for lib

    # check_library_list ()


    def get_library_names (self):
        # Assume the library list is valid -- 'check_library_list()' is
        # called from 'finalize_options()', so it should be!

        if not self.libraries:
            return None

        lib_names = []
        for (lib_name, build_info) in self.libraries:
            lib_names.append(lib_name)
        return lib_names

    # get_library_names ()


    def get_source_files (self):
        self.check_library_list(self.libraries)
        filenames = []

        # Gets source files specified and any "*.h" header files in
        # those directories.        
        for ext in self.libraries:
            filenames.extend(ext[1]['sources'])
            filenames.extend(get_headers(get_directories(ext[1]['sources'])))

        return filenames

    def build_libraries (self, libraries):

        compiler = self.compiler

        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or type(sources) not in (ListType, TupleType):
                raise DistutilsSetupError, \
                      ("in 'libraries' option (library '%s'), " +
                       "'sources' must be present and must be " +
                       "a list of source filenames") % lib_name
            sources = list(sources)

            self.announce("building '%s' library" % lib_name)

            # First, compile the source code to object files in the library
            # directory.  (This should probably change to putting object
            # files in a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            debug=self.debug)

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)

        # for libraries

    # build_libraries ()

# class build_lib


""" Modified version of build_ext that handles fortran source files and f2py 

    The f2py_sources() method is pretty much a copy of the swig_sources()
    method in the standard build_ext class , but modified to use f2py.  It
    also.
    
    slightly_modified_standard_build_extension() is a verbatim copy of
    the standard build_extension() method with a single line changed so that
    preprocess_sources() is called instead of just swig_sources().  This new
    function is a nice place to stick any source code preprocessing functions
    needed.
    
    build_extension() handles building any needed static fortran libraries
    first and then calls our slightly_modified_..._extenstion() to do the
    rest of the processing in the (mostly) standard way.    
"""

