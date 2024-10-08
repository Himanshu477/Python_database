from cpuinfo import cpu
from fcompiler import FCompiler

class NAGFCompiler(FCompiler):

    compiler_type = 'nag'
    version_pattern =  r'NAGWare Fortran 95 compiler Release (?P<version>[^\s]*)'

    executables = {
        'version_cmd'  : ["f95", "-V"],
        'compiler_f77' : ["f95", "-fixed"],
        'compiler_fix' : ["f95", "-fixed"],
        'compiler_f90' : ["f95"],
        'linker_so'    : ["f95","-Wl,shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    def get_flags_opt(self):
        return ['-O4']
    def get_flags_arch(self):
        return ['-target=native']
    def get_flags_debug(self):
        return ['-g','-gline','-g90','-nan','-C']

if __name__ == '__main__':
