    from numpy.distutils.core import setup
    setup(configuration=configuration)


#!/usr/bin/env python

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('testing',parent_package,top_path)
    return config

if __name__ == '__main__':
