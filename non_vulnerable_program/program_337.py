from cpuinfo import cpu
from fcompiler import FCompiler

class ForteFCompiler(FCompiler):

    compiler_type = 'forte'
    version_pattern = r'(f90|f95): Forte Developer 7 Fortran 95 (?P<version>[^\s]+).*'

    executables = {
        'version_cmd'  : ["f90", "-V"],
        'compiler_f77' : ["f90", "-f77", "-ftrap=%none"],
        'compiler_fix' : ["f90", "-fixed"],
        'compiler_f90' : ["f90"],
        'linker_so'    : ["f90","-Bdynamic","-G"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    def get_flags(self):
        return ['-xcode=pic32']
    def get_opt(self):
        return ['-fast','-dalign']
    def get_arch(self):
        return ['-xtarget=generic']
    def get_libraries(self):
        opt = FCompiler.get_libraries(self)
        opt.extend(['fsu','sunmath','mvec','f77compat'])
        return opt

if __name__ == '__main__':
