    from numpy.distutils.core import setup
    setup(configuration=configuration)


#!/usr/bin/env python
def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('swig_ext',parent_package,top_path)
    config.add_extension('_example',
                         ['src/example.i','src/example.c']
                         )
    config.add_extension('_example2',
                         ['src/zoo.i','src/zoo.cc'],
                         depends=['src/zoo.h'],
                         include_dirs=['src']
                         )
    config.add_data_dir('tests')
    return config

if __name__ == "__main__":
