from cpuinfo import cpu
from fcompiler import FCompiler

class G95FCompiler(FCompiler):

    compiler_type = 'g95'
    version_pattern = r'G95.*\(experimental\) \(g95!\) (?P<version>.*)\).*'

    executables = {
        'version_cmd'  : ["g95", "--version"],
        'compiler_f77' : ["g95", "-ffixed-form"],
        'compiler_fix' : ["g95", "-ffixed-form"],
        'compiler_f90' : ["g95"],
        'linker_so'    : ["g95","-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }
    pic_flags = ['-fpic']
    module_dir_switch = '-fmod='
    module_include_switch = '-I'

    def get_flags(self):
        return ['-fno-second-underscore']
    def get_flags_opt(self):
        return ['-O']
    def get_flags_debug(self):
        return ['-g']

if __name__ == '__main__':
