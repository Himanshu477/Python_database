from numpy.distutils.from_template import process_file as process_f_file
from numpy.distutils.conv_template import process_file as process_c_file
from numpy.distutils.extension import Extension
from numpy.distutils.system_info import get_info, dict_append

class build_src(build_ext.build_ext):

    description = "build sources from SWIG, F2PY files or a function"

    user_options = [
        ('build-src=', 'd', "directory to \"build\" sources to"),
        ('f2pyflags=', None, "additonal flags to f2py"),
        ('swigflags=', None, "additional flags to swig"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ('inplace', 'i',
         "ignore build-lib and put compiled extensions into the source " +
         "directory alongside your pure Python modules"),
        ]

    boolean_options = ['force','inplace']

    help_options = []

    def initialize_options(self):
        self.extensions = None
        self.package = None
        self.py_modules = None
        self.build_src = None
        self.build_lib = None
        self.build_base = None
        self.force = None
        self.inplace = None
        self.package_dir = None
        self.f2pyflags = None
        self.swigflags = None
        return

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))
        if self.package is None:
            self.package = self.distribution.ext_package
        self.extensions = self.distribution.ext_modules
        self.libraries = self.distribution.libraries or []
        self.py_modules = self.distribution.py_modules
        if self.build_src is None:
            self.build_src = os.path.join(self.build_base, 'src')
        if self.inplace is None:
            build_ext = self.get_finalized_command('build_ext')
            self.inplace = build_ext.inplace

        # py_modules is used in build_py.find_package_modules
        self.py_modules = {}

        if self.f2pyflags is None:
            self.f2pyflags = []
        else:
            self.f2pyflags = self.f2pyflags.split() # XXX spaces??

        if self.swigflags is None:
            self.swigflags = []
        else:
            self.swigflags = self.swigflags.split() # XXX spaces??
        return

    def run(self):
        if not (self.extensions or self.libraries):
            return
        self.build_sources()

        return
        
    def build_sources(self):

        for libname_info in self.libraries:
            self.build_library_sources(*libname_info)

        if self.extensions:
            self.check_extensions_list(self.extensions)

            for ext in self.extensions:
                self.build_extension_sources(ext)

        return

    def build_library_sources(self, lib_name, build_info):
        sources = list(build_info.get('sources',[]))

        if not sources:
            return

        log.info('building library "%s" sources' % (lib_name))

        sources = self.generate_sources(sources, (lib_name, build_info))

        sources = self.template_sources(sources, (lib_name, build_info))

        sources, h_files = self.filter_h_files(sources)

        if h_files:
            print self.package,'- nothing done with h_files=',h_files

        #for f in h_files:
        #    self.distribution.headers.append((lib_name,f))

        build_info['sources'] = sources
        return

    def build_extension_sources(self, ext):

        sources = list(ext.sources)

        log.info('building extension "%s" sources' % (ext.name))

        fullname = self.get_ext_fullname(ext.name)

        modpath = fullname.split('.')
        package = '.'.join(modpath[0:-1])


        if self.inplace:
            build_py = self.get_finalized_command('build_py')
            self.ext_target_dir = build_py.get_package_dir(package)


        sources = self.generate_sources(sources, ext)

        sources = self.template_sources(sources, ext)
        
        sources = self.swig_sources(sources, ext)

        sources = self.f2py_sources(sources, ext)

        sources, py_files = self.filter_py_files(sources)

        if not self.py_modules.has_key(package):
            self.py_modules[package] = []
        modules = []
        for f in py_files:
            module = os.path.splitext(os.path.basename(f))[0]
            modules.append((package, module, f))
        self.py_modules[package] += modules

        sources, h_files = self.filter_h_files(sources)

        if h_files:
            print package,'- nothing done with h_files=',h_files
        #for f in h_files:
        #    self.distribution.headers.append((package,f))

        ext.sources = sources

        return

    def generate_sources(self, sources, extension):
        new_sources = []
        func_sources = []
        for source in sources:
            if type(source) is type(''):
                new_sources.append(source)
            else:
                func_sources.append(source)
        if not func_sources:
            return new_sources
        if self.inplace:
            build_dir = self.ext_target_dir
        else:
            if type(extension) is type(()):
                name = extension[0]
            #    if not extension[1].has_key('include_dirs'):
            #        extension[1]['include_dirs'] = []
            #    incl_dirs = extension[1]['include_dirs']
            else:
                name = extension.name
            #    incl_dirs = extension.include_dirs
            #if self.build_src not in incl_dirs:
            #    incl_dirs.append(self.build_src)
            build_dir = os.path.join(*([self.build_src]\
                                       +name.split('.')[:-1]))
        self.mkpath(build_dir)
        for func in func_sources:
            source = func(extension, build_dir)
            if not source:
                continue
            if type(source) is type([]):
                [log.info("  adding '%s' to sources." % (s)) for s in source]
                new_sources.extend(source)
            else:
                log.info("  adding '%s' to sources." % (source))
                new_sources.append(source)

        return new_sources

    def filter_py_files(self, sources):
        return self.filter_files(sources,['.py'])

    def filter_h_files(self, sources):
        return self.filter_files(sources,['.h','.hpp','.inc'])

    def filter_files(self, sources, exts = []):
        new_sources = []
        files = []
        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext in exts:        
                files.append(source)
            else:
                new_sources.append(source)
        return new_sources, files

    def template_sources(self, sources, extension):
        new_sources = []
        if type(extension) is type(()):
            depends = extension[1].get('depends')
            include_dirs = extension[1].get('include_dirs')
        else:        
            depends = extension.depends
            include_dirs = extension.include_dirs
        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == '.src':  # Template file
                if self.inplace:
                    target_dir = os.path.dirname(base)
                else:
                    target_dir = appendpath(self.build_src, os.path.dirname(base))
                self.mkpath(target_dir)
                target_file = os.path.join(target_dir,os.path.basename(base))
                if (self.force or newer_group([source] + depends, target_file)):
                    if _f_pyf_ext_match(base):
                        log.info("from_template:> %s" % (target_file))
                        outstr = process_f_file(source)
                    else:
                        log.info("conv_template:> %s" % (target_file))
                        outstr = process_c_file(source)
                    fid = open(target_file,'w')
                    fid.write(outstr)
                    fid.close()
                if _header_ext_match(target_file):
                    d = os.path.dirname(target_file)
                    if d not in include_dirs:
                        log.info("  adding '%s' to include_dirs." % (d))
                        include_dirs.append(d)
                new_sources.append(target_file)
            else:
                new_sources.append(source)
        return new_sources            
        
    def f2py_sources(self, sources, extension):
        new_sources = []
        f2py_sources = []
        f_sources = []
        f2py_targets = {}
        target_dirs = []
        ext_name = extension.name.split('.')[-1]
        skip_f2py = 0

        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == '.pyf': # F2PY interface file
                if self.inplace:
                    target_dir = os.path.dirname(base)
                else:
                    target_dir = appendpath(self.build_src, os.path.dirname(base))
                if os.path.isfile(source):
                    name = get_f2py_modulename(source)
                    assert name==ext_name,'mismatch of extension names: '\
                           +source+' provides'\
                           ' '+`name`+' but expected '+`ext_name`
                    target_file = os.path.join(target_dir,name+'module.c')
                else:
                    log.debug('  source %s does not exist: skipping f2py\'ing.' \
                              % (source))
                    name = ext_name
                    skip_f2py = 1
                    target_file = os.path.join(target_dir,name+'module.c')
                    if not os.path.isfile(target_file):
                        log.debug('  target %s does not exist:\n   '\
                                  'Assuming %smodule.c was generated with '\
                                  '"build_src --inplace" command.' \
                                  % (target_file, name))
                        target_dir = os.path.dirname(base)
                        target_file = os.path.join(target_dir,name+'module.c')
                        assert os.path.isfile(target_file),`target_file`+' missing'
                        log.debug('   Yes! Using %s as up-to-date target.' \
                                  % (target_file))
                target_dirs.append(target_dir)
                f2py_sources.append(source)
                f2py_targets[source] = target_file
                new_sources.append(target_file)
            elif fortran_ext_match(ext):
                f_sources.append(source)
            else:
                new_sources.append(source)

        if not (f2py_sources or f_sources):
            return new_sources

        map(self.mkpath, target_dirs)

        f2py_options = extension.f2py_options + self.f2pyflags

        if self.distribution.libraries:
            for name,build_info in self.distribution.libraries:
                if name in extension.libraries:
                    f2py_options.extend(build_info.get('f2py_options',[]))

        log.info("f2py options: %s" % (f2py_options))

        if f2py_sources:
            assert len(f2py_sources)==1,\
                   'only one .pyf file is allowed per extension module but got'\
                   ' more:'+`f2py_sources`
            source = f2py_sources[0]
            target_file = f2py_targets[source]
            target_dir = os.path.dirname(target_file) or '.'
            depends = [source] + extension.depends
            if (self.force or newer_group(depends, target_file,'newer')) \
                   and not skip_f2py:
                log.info("f2py: %s" % (source))
                import numpy.f2py as f2py2e
                f2py2e.run_main(f2py_options + ['--build-dir',target_dir,source])
            else:
                log.debug("  skipping '%s' f2py interface (up-to-date)" % (source))
        else:
            #XXX TODO: --inplace support for sdist command
            if type(extension) is type(()): name = extension[0]
            else: name = extension.name
            target_dir = os.path.join(*([self.build_src]\
                                        +name.split('.')[:-1]))
            target_file = os.path.join(target_dir,ext_name + 'module.c')
            new_sources.append(target_file)
            depends = f_sources + extension.depends
            if (self.force or newer_group(depends, target_file, 'newer')) \
                   and not skip_f2py:
                import numpy.f2py as f2py2e
                log.info("f2py:> %s" % (target_file))
                self.mkpath(target_dir)
                f2py2e.run_main(f2py_options + ['--lower',
                                                '--build-dir',target_dir]+\
                                ['-m',ext_name]+f_sources)
            else:
                log.debug("  skipping f2py fortran files for '%s' (up-to-date)"\
                          % (target_file))

        assert os.path.isfile(target_file),`target_file`+' missing'

        target_c = os.path.join(self.build_src,'fortranobject.c')
        target_h = os.path.join(self.build_src,'fortranobject.h')
        log.info("  adding '%s' to sources." % (target_c))
        new_sources.append(target_c)
        if self.build_src not in extension.include_dirs:
            log.info("  adding '%s' to include_dirs." \
                     % (self.build_src))
            extension.include_dirs.append(self.build_src)

        if not skip_f2py:
            import numpy.f2py as f2py2e
            d = os.path.dirname(f2py2e.__file__)
            source_c = os.path.join(d,'src','fortranobject.c')
            source_h = os.path.join(d,'src','fortranobject.h')
            if newer(source_c,target_c) or newer(source_h,target_h):
                self.mkpath(os.path.dirname(target_c))
                self.copy_file(source_c,target_c)
                self.copy_file(source_h,target_h)
        else:
            assert os.path.isfile(target_c),`target_c` + ' missing'
            assert os.path.isfile(target_h),`target_h` + ' missing'
   
        for name_ext in ['-f2pywrappers.f','-f2pywrappers2.f90']:
            filename = os.path.join(target_dir,ext_name + name_ext)
            if os.path.isfile(filename):
                log.info("  adding '%s' to sources." % (filename))
                f_sources.append(filename)

        return new_sources + f_sources

    def swig_sources(self, sources, extension):
        # Assuming SWIG 1.3.14 or later. See compatibility note in
        #   http://www.swig.org/Doc1.3/Python.html#Python_nn6

        new_sources = []
        swig_sources = []
        swig_targets = {}
        target_dirs = []
        py_files = []     # swig generated .py files
        target_ext = '.c'
        typ = None
        is_cpp = 0
        skip_swig = 0
        ext_name = extension.name.split('.')[-1]

        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == '.i': # SWIG interface file
                if self.inplace:
                    target_dir = os.path.dirname(base)
                    py_target_dir = self.ext_target_dir
                else:
                    target_dir = appendpath(self.build_src, os.path.dirname(base))
                    py_target_dir = target_dir
                if os.path.isfile(source):
                    name = get_swig_modulename(source)
                    assert name==ext_name[1:],'mismatch of extension names: '\
                           +source+' provides'\
                           ' '+`name`+' but expected '+`ext_name[1:]`
                    if typ is None:
                        typ = get_swig_target(source)
                        is_cpp = typ=='c++'
                        if is_cpp:
                            target_ext = '.cpp'
                    else:
                        assert typ == get_swig_target(source),`typ`
                    target_file = os.path.join(target_dir,'%s_wrap%s' \
                                               % (name, target_ext))
                else:
                    log.debug('  source %s does not exist: skipping swig\'ing.' \
                             % (source))
                    name = ext_name[1:]
                    skip_swig = 1
                    target_file = _find_swig_target(target_dir, name)
                    if not os.path.isfile(target_file):
                        log.debug('  target %s does not exist:\n   '\
                                  'Assuming %s_wrap.{c,cpp} was generated with '\
                                  '"build_src --inplace" command.' \
                                 % (target_file, name))
                        target_dir = os.path.dirname(base)
                        target_file = _find_swig_target(target_dir, name)
                        assert os.path.isfile(target_file),`target_file`+' missing'
                        log.debug('   Yes! Using %s as up-to-date target.' \
                                  % (target_file))
                target_dirs.append(target_dir)
                new_sources.append(target_file)
                py_files.append(os.path.join(py_target_dir, name+'.py'))
                swig_sources.append(source)
                swig_targets[source] = new_sources[-1]
            else:
                new_sources.append(source)

        if not swig_sources:
            return new_sources

        if skip_swig:
            return new_sources + py_files

        map(self.mkpath, target_dirs)
        swig = self.find_swig()
        swig_cmd = [swig, "-python"]
        if is_cpp:
            swig_cmd.append('-c++')
        for d in extension.include_dirs:
            swig_cmd.append('-I'+d)
        for source in swig_sources:
            target = swig_targets[source]
            depends = [source] + extension.depends
            if self.force or newer_group(depends, target, 'newer'):
                log.info("%s: %s" % (os.path.basename(swig) \
                                     + (is_cpp and '++' or ''), source))
                self.spawn(swig_cmd + self.swigflags \
                           + ["-o", target, '-outdir', py_target_dir, source])
            else:
                log.debug("  skipping '%s' swig interface (up-to-date)" \
                         % (source))

        return new_sources + py_files

_f_pyf_ext_match = re.compile(r'.*[.](f90|f95|f77|for|ftn|f|pyf)\Z',re.I).match
_header_ext_match = re.compile(r'.*[.](inc|h|hpp)\Z',re.I).match

#### SWIG related auxiliary functions ####
_swig_module_name_match = re.compile(r'\s*%module\s*(?P<name>[\w_]+)',
                                     re.I).match
_has_c_header = re.compile(r'-[*]-\s*c\s*-[*]-',re.I).search
_has_cpp_header = re.compile(r'-[*]-\s*c[+][+]\s*-[*]-',re.I).search

def get_swig_target(source):
    f = open(source,'r')
    result = 'c'
    line = f.readline()
    if _has_cpp_header(line):
        result = 'c++'
    if _has_c_header(line):
        result = 'c'
    f.close()
    return result

def get_swig_modulename(source):
    f = open(source,'r')
    f_readlines = getattr(f,'xreadlines',f.readlines)
    for line in f_readlines():
        m = _swig_module_name_match(line)
        if m:
            name = m.group('name')
            break
    f.close()
    return name

def _find_swig_target(target_dir,name):
    for ext in ['.cpp','.c']:
        target = os.path.join(target_dir,'%s_wrap%s' % (name, ext))
        if os.path.isfile(target):
            break
    return target

#### F2PY related auxiliary functions ####

_f2py_module_name_match = re.compile(r'\s*python\s*module\s*(?P<name>[\w_]+)',
                                re.I).match
_f2py_user_module_name_match = re.compile(r'\s*python\s*module\s*(?P<name>[\w_]*?'\
                                     '__user__[\w_]*)',re.I).match

def get_f2py_modulename(source):
    name = None
    f = open(source)
    f_readlines = getattr(f,'xreadlines',f.readlines)
    for line in f_readlines():
        m = _f2py_module_name_match(line)
        if m:
            if _f2py_user_module_name_match(line): # skip *__user__* names
                continue
            name = m.group('name')
            break
    f.close()
    return name

##########################################


# Added Fortran compiler support to config. Currently useful only for
# try_compile call. try_run works but is untested for most of Fortran
# compilers (they must define linker_exe first).
# Pearu Peterson

