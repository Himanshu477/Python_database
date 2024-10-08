from cpuinfo import cpu
from fcompiler import FCompiler, dummy_fortran_file
from exec_command import find_executable

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
        'compiler_f77' : [fc_exe,"-FI","-w90","-w95"],
        'compiler_fix' : [fc_exe,"-FI","-72"],
        'compiler_f90' : [fc_exe],
        'linker_so'    : [fc_exe,"-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    def get_flags(self):
        opt = ["-KPIC","-cm"]
        return opt

    def get_flags_opt(self):
        return ['-O3','-unroll']

    def get_flags_arch(self):
        opt = []
        if cpu.has_fdiv_bug():
            opt.append('-fdiv_check')
        if cpu.has_f00f_bug():
            opt.append('-0f_check')
        if cpu.is_PentiumPro() or cpu.is_PentiumII():
            opt.extend(['-tpp6','-xi'])
        elif cpu.is_PentiumIII():
            opt.append('-tpp6')
        elif cpu.is_Pentium():
            opt.append('-tpp5')
        elif cpu.is_PentiumIV():
            opt.extend(['-tpp7','-xW'])
        if cpu.has_mmx():
            opt.append('-xM')
        return opt

    def get_flags_linker_so(self):
        opt = FCompiler.get_flags_linker_so(self)
        v = self.get_version()
        if v and v >= '8.0':
            opt.append('-nofor_main')
        return opt

class IntelVisualFCompiler(FCompiler):

    compiler_type = 'intelv'
    version_pattern = r'Intel\(R\) Fortran Compiler for 32-bit applications, '\
                      'Version (?P<version>[^\s*]*)'

    ar_exe = 'lib.exe'
    fc_exe = 'ifl'
    if sys.platform=='win32':
