from numpy.distutils.cpuinfo import cpu
from numpy.distutils.fcompiler import FCompiler, dummy_fortran_file
from numpy.distutils.exec_command import find_executable

class IntelFCompiler(FCompiler):

    compiler_type = 'intel'
    version_pattern = r'Intel\(R\) Fortran Compiler for 32-bit '\
                      'applications, Version (?P<version>[^\s*]*)'

    for fc_exe in map(find_executable,['ifort','ifc']):
        if os.path.isfile(fc_exe):
            break

    executables = {
        'version_cmd'  : [fc_exe, "-FI -V -c %(fname)s.f -o %(fname)s.o" \
                          % {'fname':dummy_fortran_file()}],
        'compiler_f77' : [fc_exe,"-72","-w90","-w95"],
        'compiler_fix' : [fc_exe,"-FI"],
        'compiler_f90' : [fc_exe],
        'linker_so'    : [fc_exe,"-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    pic_flags = ['-KPIC']
    module_dir_switch = '-module ' # Don't remove ending space!
    module_include_switch = '-I'

    def get_flags(self):
        opt = self.pic_flags + ["-cm"]
        return opt

    def get_flags_free(self):
        return ["-FR"]

    def get_flags_opt(self):
        return ['-O3','-unroll']

    def get_flags_arch(self):
        opt = []
        if cpu.has_fdiv_bug():
            opt.append('-fdiv_check')
        if cpu.has_f00f_bug():
            opt.append('-0f_check')
        if cpu.is_PentiumPro() or cpu.is_PentiumII() or cpu.is_PentiumIII():
            opt.extend(['-tpp6'])
        elif cpu.is_PentiumM():
            opt.extend(['-tpp7','-xB'])
        elif cpu.is_Pentium():
            opt.append('-tpp5')
        elif cpu.is_PentiumIV() or cpu.is_Xeon():
            opt.extend(['-tpp7','-xW'])
        if cpu.has_mmx() and not cpu.is_Xeon():
            opt.append('-xM')
        if cpu.has_sse2():
            opt.append('-arch SSE2')
        elif cpu.has_sse():
            opt.append('-arch SSE')
        return opt

    def get_flags_linker_so(self):
        opt = FCompiler.get_flags_linker_so(self)
        v = self.get_version()
        if v and v >= '8.0':
            opt.append('-nofor_main')
        opt.extend(self.get_flags_arch())
        return opt

class IntelItaniumFCompiler(IntelFCompiler):
    compiler_type = 'intele'
    version_pattern = r'Intel\(R\) Fortran 90 Compiler Itanium\(TM\) Compiler'\
                      ' for the Itanium\(TM\)-based applications,'\
                      ' Version (?P<version>[^\s*]*)'

    for fc_exe in map(find_executable,['ifort','efort','efc']):
        if os.path.isfile(fc_exe):
            break

    executables = {
        'version_cmd'  : [fc_exe, "-FI -V -c %(fname)s.f -o %(fname)s.o" \
                          % {'fname':dummy_fortran_file()}],
        'compiler_f77' : [fc_exe,"-FI","-w90","-w95"],
        'compiler_fix' : [fc_exe,"-FI"],
        'compiler_f90' : [fc_exe],
        'linker_so'    : [fc_exe,"-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

class IntelEM64TFCompiler(IntelFCompiler):
    compiler_type = 'intelem'

    version_pattern = r'Intel\(R\) Fortran Compiler for Intel\(R\) EM64T-based '\
                      'applications, Version (?P<version>[^\s*]*)'

    for fc_exe in map(find_executable,['ifort','efort','efc']):
        if os.path.isfile(fc_exe):
            break

    executables = {
        'version_cmd'  : [fc_exe, "-FI -V -c %(fname)s.f -o %(fname)s.o" \
                          % {'fname':dummy_fortran_file()}],
        'compiler_f77' : [fc_exe,"-FI","-w90","-w95"],
        'compiler_fix' : [fc_exe,"-FI"],
        'compiler_f90' : [fc_exe],
        'linker_so'    : [fc_exe,"-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    def get_flags_arch(self):
        opt = []
        if cpu.is_PentiumIV() or cpu.is_Xeon():
            opt.extend(['-tpp7', '-xW'])
        return opt

class IntelVisualFCompiler(FCompiler):

    compiler_type = 'intelv'
    version_pattern = r'Intel\(R\) Fortran Compiler for 32-bit applications, '\
                      'Version (?P<version>[^\s*]*)'

    ar_exe = 'lib.exe'
    fc_exe = 'ifl'
    if sys.platform=='win32':
