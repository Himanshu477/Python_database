import os.path

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('compat',parent_package,top_path)
    return config

if __name__ == '__main__':
