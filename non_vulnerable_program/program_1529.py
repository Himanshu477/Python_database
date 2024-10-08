from os.path import join

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('numarray',parent_package,top_path)

    config.add_data_files('include/numarray/*.h')

    # Configure fftpack_lite
    config.add_extension('_capi',
                         sources=['_capi.c']
                         )

    return config

if __name__ == '__main__':
