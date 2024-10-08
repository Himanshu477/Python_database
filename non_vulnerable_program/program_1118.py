from os.path import join

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info
    config = Configuration('linalg',parent_package,top_path)

    # Configure lapack_lite
    lapack_info = get_info('lapack_opt',0)
    def get_lapack_lite_sources(ext, build_dir):
        if not lapack_info:
            print "### Warning:  Using unoptimized lapack ###"
            return ext.depends[:-1]
        else:
            return ext.depends[:1]

    config.add_extension('lapack_lite',
                         sources = [get_lapack_lite_sources],
                         depends=  ['lapack_litemodule.c',
                                   'zlapack_lite.c', 'dlapack_lite.c',
                                   'blas_lite.c', 'dlamch.c',
                                   'f2c_lite.c','f2c.h'],
                         extra_info = lapack_info
                         )
            
    return config

if __name__ == '__main__':
