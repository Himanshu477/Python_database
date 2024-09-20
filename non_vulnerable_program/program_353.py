from cpuinfo import cpu
from fcompiler import FCompiler

class MipsFCompiler(FCompiler):

    compiler_type = 'mips'
    version_pattern =  r'MIPSpro Compilers: Version (?P<version>[^\s*,]*)'

    executables = {
        'version_cmd'  : ["f90", "-version"],
        'compiler_f77' : ["f77", "-f77"],
        'compiler_fix' : ["f90", "-fixedform"],
        'compiler_f90' : ["f90"],
        'linker_so'    : ["f90","-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : None
        }

    def get_flags(self):
        return ['-KPIC','-n32']
    def get_flags_opt(self):
        return ['-O3']
    def get_flags_arch(self):
        opt = []
        for a in '19 20 21 22_4k 22_5k 24 25 26 27 28 30 32_5k 32_10k'.split():
            if getattr(cpu,'is_IP%s'%a)():
                opt.append('-TARG:platform=IP%s' % a)
                break
        return opt
    def get_flags_arch_f77(self):
        r = None
        if cpu.is_r10000(): r = 10000
        elif cpu.is_r12000(): r = 12000
        elif cpu.is_r8000(): r = 8000
        elif cpu.is_r5000(): r = 5000
        elif cpu.is_r4000(): r = 4000
        if r is not None:
            return ['r%s' % (r)]
        return []
    def get_flags_arch_f90(self):
        r = self.get_flags_arch_f77()
        if r:
            r[0] = '-' + r[0]
        return r

if __name__ == '__main__':
