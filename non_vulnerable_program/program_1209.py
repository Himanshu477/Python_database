from numpy.distutils.cpuinfo import cpu
from numpy.distutils.fcompiler import FCompiler

class CompaqFCompiler(FCompiler):

    compiler_type = 'compaq'
    version_pattern = r'Compaq Fortran (?P<version>[^\s]*).*'

    if sys.platform[:5]=='linux':
        fc_exe = 'fort'
    else:
        fc_exe = 'f90'

    executables = {
        'version_cmd'  : [fc_exe, "-version"],
        'compiler_f77' : [fc_exe, "-f77rtl","-fixed"],
        'compiler_fix' : [fc_exe, "-fixed"],
        'compiler_f90' : [fc_exe],
        'linker_so'    : [fc_exe],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    module_dir_switch = '-module ' # not tested
    module_include_switch = '-I'

    def get_flags(self):
        return ['-assume no2underscore','-nomixed_str_len_arg']
    def get_flags_debug(self):
        return ['-g','-check bounds']
    def get_flags_opt(self):
        return ['-O4','-align dcommons','-assume bigarrays',
                '-assume nozsize','-math_library fast']
    def get_flags_arch(self):
        return ['-arch host', '-tune host']
    def get_flags_linker_so(self):
        if sys.platform[:5]=='linux':
            return ['-shared']
        return ['-shared','-Wl,-expect_unresolved,*']

class CompaqVisualFCompiler(FCompiler):

    compiler_type = 'compaqv'
    version_pattern = r'(DIGITAL|Compaq) Visual Fortran Optimizing Compiler'\
                      ' Version (?P<version>[^\s]*).*'

    compile_switch = '/compile_only'
    object_switch = '/object:'
    library_switch = '/OUT:'      #No space after /OUT:!

    static_lib_extension = ".lib"
    static_lib_format = "%s%s"
    module_dir_switch = '/module:'
    module_include_switch = '/I'

    ar_exe = 'lib.exe'
    fc_exe = 'DF'
    if sys.platform=='win32':
