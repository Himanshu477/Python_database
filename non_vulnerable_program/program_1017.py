from os.path import join

def configuration(parent_package='',top_path=None):
    from scipy.distutils.misc_util import Configuration
    config = Configuration('random',parent_package,top_path)
            
    return config

if __name__ == '__main__':
