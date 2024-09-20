import os
import re
import sys
import imp
import copy
import types
import glob

def get_path(mod_name,parent_path=None):
    """ Return path of the module.

    Returned path is relative to parent_path when given,
    otherwise it is absolute path.
    """
    if mod_name == '__main__':
        d = os.path.abspath('.')
    elif mod_name == '__builtin__':
        #builtin if/then added by Pearu for use in core.run_setup.        
        d = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        __import__(mod_name)
        mod = sys.modules[mod_name]
        file = mod.__file__
        d = os.path.dirname(os.path.abspath(file))
    if parent_path is not None:
        pd = os.path.abspath(parent_path)
        if pd==d[:len(pd)]:
            d = d[len(pd)+1:]
    return d or '.'

# Hooks for colored terminal output.
# See also http://www.livinglogic.de/Python/ansistyle
def terminal_has_colors():
    if sys.platform=='cygwin' and not os.environ.has_key('USE_COLOR'):
        # Avoid importing curses that causes illegal operation
        # with a message:
        #  PYTHON2 caused an invalid page fault in
        #  module CYGNURSES7.DLL as 015f:18bbfc28
        # Details: Python 2.3.3 [GCC 3.3.1 (cygming special)]
        #          ssh to Win32 machine from debian
        #          curses.version is 2.2
        #          CYGWIN_98-4.10, release 1.5.7(0.109/3/2))
        return 0
    if hasattr(sys.stdout,'isatty') and sys.stdout.isatty(): 
        try:
            import curses
            curses.setupterm()
            if (curses.tigetnum("colors") >= 0
                and curses.tigetnum("pairs") >= 0
                and ((curses.tigetstr("setf") is not None 
                      and curses.tigetstr("setb") is not None) 
                     or (curses.tigetstr("setaf") is not None
                         and curses.tigetstr("setab") is not None)
                     or curses.tigetstr("scp") is not None)):
                return 1
        except Exception,msg:
            pass
    return 0

if terminal_has_colors():
    def red_text(s): return '\x1b[31m%s\x1b[0m'%s
    def green_text(s): return '\x1b[32m%s\x1b[0m'%s
    def yellow_text(s): return '\x1b[33m%s\x1b[0m'%s
    def blue_text(s): return '\x1b[34m%s\x1b[0m'%s
    def cyan_text(s): return '\x1b[35m%s\x1b[0m'%s
else:
    def red_text(s): return s
    def green_text(s): return s
    def yellow_text(s): return s
    def cyan_text(s): return s
    def blue_text(s): return s

#########################

def cyg2win32(path):
    if sys.platform=='cygwin' and path.startswith('/cygdrive'):
        path = path[10] + ':' + os.path.normcase(path[11:])
    return path

#########################

#XXX need support for .C that is also C++
cxx_ext_match = re.compile(r'.*[.](cpp|cxx|cc)\Z',re.I).match
fortran_ext_match = re.compile(r'.*[.](f90|f95|f77|for|ftn|f)\Z',re.I).match
f90_ext_match = re.compile(r'.*[.](f90|f95)\Z',re.I).match
f90_module_name_match = re.compile(r'\s*module\s*(?P<name>[\w_]+)',re.I).match
def _get_f90_modules(source):
    """ Return a list of Fortran f90 module names that
    given source file defines.
    """
    if not f90_ext_match(source):
        return []
    modules = []
    f = open(source,'r')
    f_readlines = getattr(f,'xreadlines',f.readlines)
    for line in f_readlines():
        m = f90_module_name_match(line)
        if m:
            name = m.group('name')
            modules.append(name)
            # break  # XXX can we assume that there is one module per file?
    f.close()
    return modules

def all_strings(lst):
    """ Return True if all items in lst are string objects. """
    for item in lst:
        if type(item) is not types.StringType:
            return False
    return True

def has_f_sources(sources):
    """ Return True if sources contains Fortran files """
    for source in sources:
        if fortran_ext_match(source):
            return True
    return False

def has_cxx_sources(sources):
    """ Return True if sources contains C++ files """
    for source in sources:
        if cxx_ext_match(source):
            return True
    return False

def filter_sources(sources):
    """ Return four lists of filenames containing
    C, C++, Fortran, and Fortran 90 module sources,
    respectively.
    """
    c_sources = []
    cxx_sources = []
    f_sources = []
    fmodule_sources = []
    for source in sources:
        if fortran_ext_match(source):
            modules = _get_f90_modules(source)
            if modules:
                fmodule_sources.append(source)
            else:
                f_sources.append(source)
        elif cxx_ext_match(source):
            cxx_sources.append(source)
        else:
            c_sources.append(source)            
    return c_sources, cxx_sources, f_sources, fmodule_sources


def _get_headers(directory_list):
    # get *.h files from list of directories
    headers = []
    for dir in directory_list:
        head = glob.glob(os.path.join(dir,"*.h")) #XXX: *.hpp files??
        headers.extend(head)
    return headers

def _get_directories(list_of_sources):
    # get unique directories from list of sources.
    direcs = []
    for file in list_of_sources:
        dir = os.path.split(file)
        if dir[0] != '' and not dir[0] in direcs:
            direcs.append(dir[0])
    return direcs

def get_dependencies(sources):
    #XXX scan sources for include statements
    return _get_headers(_get_directories(sources))

def is_local_src_dir(directory):
    """ Return true if directory is local directory.
    """
    abs_dir = os.path.abspath(directory)
    c = os.path.commonprefix([os.getcwd(),abs_dir])
    new_dir = abs_dir[len(c):].split(os.sep)
    if new_dir and not new_dir[0]:
        new_dir = new_dir[1:]
    if new_dir and new_dir[0]=='build':
        return False
    new_dir = os.sep.join(new_dir)
    return os.path.isdir(new_dir)

def _gsf_visit_func(filenames,dirname,names):
    if os.path.basename(dirname) in ['CVS','.svn','build']:
        names[:] = []
        return
    for name in names:
        if name[-1] in "~#":
            continue
        fullname = os.path.join(dirname,name)
        ext = os.path.splitext(fullname)[1]
        if ext and ext in ['.pyc','.o']:
            continue
        if os.path.isfile(fullname):
            filenames.append(fullname)

def get_ext_source_files(ext):
    # Get sources and any include files in the same directory.
    filenames = []
    sources = filter(lambda s:type(s) is types.StringType,ext.sources)
    filenames.extend(sources)
    filenames.extend(get_dependencies(sources))
    for d in ext.depends:
        if is_local_src_dir(d):
            os.path.walk(d,_gsf_visit_func,filenames)
        elif os.path.isfile(d):
            filenames.append(d)
    return filenames

def get_lib_source_files(lib):
    filenames = []
    sources = lib[1].get('sources',[])
    sources = filter(lambda s:type(s) is types.StringType,sources)
    filenames.extend(sources)
    filenames.extend(get_dependencies(sources))
    depends = build_info.get('depends',[])
    for d in depends:
        if is_local_src_dir(d):
            os.path.walk(d,_gsf_visit_func,filenames)
        elif os.path.isfile(d):
            filenames.append(d)
    return filenames

def get_data_files(data):
    if type(data) is types.StringType:
        return [data]
    sources = data[1]
    filenames = []
    for s in sources:
        if is_local_src_dir(s):
            os.path.walk(s,_gsf_visit_func,filenames)
        elif os.path.isfile(s):
            filenames.append(s)
    return filenames

def dot_join(*args):
    return '.'.join(filter(None,args))

def get_frame(level=0):
    try:
        return sys._getframe(level+1)
    except AttributeError:
        frame = sys.exc_info()[2].tb_frame
        for i in range(level+1):
            frame = frame.f_back
        return frame

######################

class Configuration:

    _list_keys = ['packages','ext_modules','data_files','include_dirs',
                  'libraries','headers','scripts']
    _dict_keys = ['package_dir']
    
    def __init__(self,
                 package_name=None,
                 parent_name=None,
                 top_path=None,
                 package_path=None,
                 **attrs):
        """ Construct configuration instance of a package.
        """
        self.name = dot_join(parent_name, package_name)

        caller_frame = get_frame(1)
        caller_name = eval('__name__',caller_frame.f_globals,caller_frame.f_locals)
        
        self.local_path = get_path(caller_name, top_path)
        if top_path is None:
            top_path = self.local_path
        if package_path is None:
            package_path = self.local_path
        elif os.path.isdir(os.path.join(self.local_path,package_path)):
            package_path = os.path.join(self.local_path,package_path)
        self.top_path = top_path

        self.list_keys = copy.copy(self._list_keys)
        self.dict_keys = copy.copy(self._dict_keys)

        for n in self.list_keys:
            setattr(self,n,copy.copy(attrs.get(n,[])))

        for n in self.dict_keys:
            setattr(self,n,copy.copy(attrs.get(n,{})))

        known_keys = self.list_keys + self.dict_keys
        self.extra_keys = []
        for n in attrs.keys():
            if n in known_keys:
                continue
            a = attrs[n]
            setattr(self,n,a)
            if type(a) is types.ListType:
                self.list_keys.append(n)
            elif type(a) is types.DictType:
                self.dict_keys.append(n)
            else:
                self.extra_keys.append(n)


        if os.path.exists(os.path.join(package_path,'__init__.py')):
            self.packages.append(self.name)
            self.package_dir[self.name] = package_path        
        return

    def todict(self):
        """ Return configuration distionary suitable for passing
        to distutils.core.setup() function.
        """
        d = {}
        for n in self.list_keys + self.dict_keys + self.extra_keys:
            a = getattr(self,n)
            if a:
                d[n] = a
        if self.name:
            d['name'] = self.name
        return d

    def add_subpackage(self,subpackage_name,subpackage_path=None):
        """ Add subpackage configuration.
        """
        assert '.' not in subpackage_name,`subpackage_name`
        if subpackage_path is None:
            subpackage_path = os.path.join(self.local_path,subpackage_name)
        setup_py = os.path.join(subpackage_path,'setup_%s.py' % (subpackage_name))
        if not os.path.isfile(setup_py):
            setup_py = os.path.join(subpackage_path,'setup.py')
        if not os.path.isfile(setup_py):
            print 'Assuming default configuration '\
                  '(%s/{setup_%s,setup}.py was not found)' \
                  % (os.path.dirname(setup_py),subpackage_name)
            name = dot_join(self.name, subpackage_name)        
            self.packages.append(name)
            self.package_dir[name] = subpackage_path
            return

        # In case setup_py imports local modules:
        sys.path.insert(0,os.path.dirname(setup_py))

        try:
            info = (open(setup_py),setup_py,('.py','U',1))
            setup_name = os.path.splitext(os.path.basename(setup_py))[0]
            n = dot_join(self.name,setup_name)
            setup_module = imp.load_module('_'.join(n.split('.')),*info)
            if not hasattr(setup_module,'configuration'):
                print 'Assuming default configuration '\
                      '(%s does not define configuration())' % (setup_module)
                name = dot_join(self.name, subpackage_name)        
                self.packages.append(name)
                self.package_dir[name] = subpackage_path
            else:
                args = (self.name,)
                if setup_module.configuration.func_code.co_argcount>1:
                    args = args + (self.top_path,)
                config = setup_module.configuration(*args)
                if not config:
                    print 'No configuration returned, assuming unavailable.'
                else:
                    if isinstance(config,Configuration):
                        config = config.todict()
                    self.dict_append(**config)
        finally:
            del sys.path[0]        
        return

    def add_data_dir(self,data_path):
        """ Add files under data_path to data_files list.
        """
        path = os.path.join(self.local_path,data_path)
        filenames = []
        os.path.walk(path, _gsf_visit_func,filenames)
        self.add_data_files(*filenames)
        return

    def add_data_files(self,*files):
        data_dict = {}
        for f in files:
            lf = f[len(self.local_path)+1:]
            d = os.path.dirname(lf)
            d = os.path.join(*(self.name.split('.')+[d]))
            if not data_dict.has_key(d):
                data_dict[d] = [f]
            else:
                data_dict[d].append(f)
        self.data_files.extend(data_dict.items())
        return            
        
    def add_include_dirs(self,*paths):
        self.include_dirs.extend(self._fix_paths(paths))

    def add_headers(self,*paths):
        paths = self._fix_paths(paths)
        self.headers.extend([(self.name,p) for p in paths])

    def _fix_paths(self,paths):
        new_paths = []
        for n in paths:
            if isinstance(n,str):
                if '*' in n or '?' in n:
                    p = glob.glob(n)
                    p2 = glob.glob(os.path.join(self.local_path,n))
                    if p2:
                        new_paths.extend(p2)
                    elif p:
                        new_paths.extend(p)
                    else:
                        new_paths.append(n)
                else:
                    n2 = os.path.join(self.local_path,n)
                    if os.path.exists(n2):
                        new_paths.append(n2)
                    else:
                        new_paths.append(n)
            else:
                new_paths.append(n)
        return new_paths

    def paths(self,*paths):
        return self._fix_paths(paths)

    def add_extension(self,name,sources,**kw):
        ext_args = copy.copy(kw)
        ext_args['name'] = dot_join(self.name,name)
        ext_args['sources'] = sources

        for k in ext_args.keys():
            v = ext_args[k]
            if k in ['sources','depends']:
                new_v = self._fix_paths(v)
                ext_args[k] = new_v

        from scipy.distutils.core import Extension
        ext = Extension(**ext_args)
        self.ext_modules.append(ext)
        return ext

    def add_library(self,name,sources,**build_info):
        """
        Valid keywords for build_info:
          depends
          macros
          include_dirs
          extra_compiler_args
          f2py_options
        """
        build_info = copy.copy(build_info)
        name = name + '@' + self.name
        build_info['sources'] = sources

        for k in build_info.keys():
            v = build_info[k]
            if k in ['sources','depends']:
                new_v = self._fix_paths(v)
                build_info[k] = new_v
        self.libraries.append((name,build_info))
        return

    def dict_append(self,**dict):
        for key in self.list_keys:
            a = getattr(self,key)
            a.extend(dict.get(key,[]))
        for key in self.dict_keys:
            a = getattr(self,key)
            a.update(dict.get(key,{}))
        known_keys = self.list_keys + self.dict_keys + self.extra_keys
        for key in dict.keys():
            if key not in known_keys and not hasattr(self,key):
                print 'Inheriting attribute %r from %r' \
                      % (key,dict.get('name','?'))
                setattr(self,key,dict[key])
                self.extra_keys.append(key)
        return

    def __str__(self):
        known_keys = self.list_keys + self.dict_keys + self.extra_keys
        s = '<'+5*'-' + '\n'
        s += 'Configuration of '+self.name+':\n'
        for k in known_keys:
            a = getattr(self,k,None)
            if a:
                s += '%s = %r\n' % (k,a)
        s += 5*'-' + '>'
        return s

    def get_config_cmd(self):
        cmd = get_cmd('config')
        cmd.ensure_finalized()
        cmd.dump_source = 0
        cmd.noisy = 0
        old_path = os.environ.get('PATH')
        if old_path:
            path = os.pathsep.join(['.',old_path])
            os.environ['PATH'] = path
        return cmd

    def get_build_temp_dir(self):
        cmd = get_cmd('build')
        cmd.ensure_finalized()
        return cmd.build_temp

    def have_f77c(self):
        """ Check for availability of Fortran 77 compiler.
        Use it inside source generating function to ensure that
        setup distribution instance has been initialized.
        """
        simple_fortran_subroutine = '''
        subroutine simple
        end
        '''
        config_cmd = self.get_config_cmd()
        flag = config_cmd.try_compile(simple_fortran_subroutine,lang='f77')
        return flag

    def have_f90c(self):
        """ Check for availability of Fortran 90 compiler.
        Use it inside source generating function to ensure that
        setup distribution instance has been initialized.
        """
        simple_fortran_subroutine = '''
        subroutine simple
        end
        '''
        config_cmd = self.get_config_cmd()
        flag = config_cmd.try_compile(simple_fortran_subroutine,lang='f90')
        return flag

def get_cmd(cmdname,_cache={}):
    if not _cache.has_key(cmdname):
        import distutils.core
        dist = distutils.core._setup_distribution
        if dist is None:
            from distutils.errors import DistutilsInternalError
            raise DistutilsInternalError,\
                  'setup distribution instance not initialized'
        cmd = dist.get_command_obj(cmdname)
        _cache[cmdname] = cmd
    return _cache[cmdname]

#########################

def dict_append(d,**kws):
    for k,v in kws.items():
        if d.has_key(k):
            d[k].extend(v)
        else:
            d[k] = v

def generate_config_py(extension, build_dir):
    """ Generate <package>/config.py file containing system_info
    information used during building the package.

    Usage:\
        ext = Extension(dot_join(config['name'],'config'),
                        sources=[generate_config_py])
        config['ext_modules'].append(ext)
    """
    from scipy.distutils.system_info import system_info
    from distutils.dir_util import mkpath
    target = os.path.join(*([build_dir]+extension.name.split('.'))) + '.py'
    mkpath(os.path.dirname(target))
    f = open(target,'w')
    f.write('# This file is generated by %s\n' % (os.path.abspath(sys.argv[0])))
    f.write('# It contains system_info results at the time of building this package.\n')
    f.write('__all__ = ["get_info","show"]\n\n')
    for k,i in system_info.saved_results.items():
        f.write('%s=%r\n' % (k,i))
    f.write('\ndef get_info(name): g=globals(); return g.get(name,g.get(name+"_info",{}))\n')
    f.write('''
def show():
    for name,info_dict in globals().items():
        if name[0]=="_" or type(info_dict) is not type({}): continue
        print name+":"
        if not info_dict:
            print "  NOT AVAILABLE"
        for k,v in info_dict.items():
            v = str(v)
            if k==\'sources\' and len(v)>200: v = v[:60]+\' ...\\n... \'+v[-60:]
            print \'    %s = %s\'%(k,v)
        print
    return
    ''')

    f.close()
    return target

def generate_svn_version_py(extension, build_dir):
    """ Generate __svn_version__.py file containing SVN
    revision number of a module.
    
    To use, add the following codelet to setup
    configuration(..) function

      ext = Extension(dot_join(config['name'],'__svn_version__'),
                      sources=[generate_svn_version_py])
      ext.local_path = local_path
      config['ext_modules'].append(ext)

    """
    from distutils import dep_util
    local_path = extension.local_path
    target = os.path.join(build_dir, '__svn_version__.py')
    entries = os.path.join(local_path,'.svn','entries')
    if os.path.isfile(entries):
        if not dep_util.newer(entries, target):
            return target
    elif os.path.isfile(target):
        return target

    revision = get_svn_revision(local_path)
    f = open(target,'w')
    f.write('revision=%s\n' % (revision))
    f.close()
    return target


#!/usr/bin/env python
