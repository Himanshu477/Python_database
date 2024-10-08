    from numpy.distutils.core import setup
    setup(configuration=configuration)


#!/usr/bin/env python

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('distutils',parent_package,top_path)
    config.add_subpackage('command')
    config.add_subpackage('fcompiler')
    config.add_data_dir('tests')
    config.add_data_files('site.cfg')
    config.make_config_py()
    return config

if __name__ == '__main__':
