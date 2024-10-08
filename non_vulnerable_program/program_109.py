import os
from glob import glob
from scipy_distutils.misc_util import get_path, default_config_dict

def configuration(parent_package=''):
    parent_path = parent_package
    if parent_package:
        parent_package += '.'
    local_path = get_path(__name__)

    config = default_config_dict()
    config['packages'].append(parent_package+'compiler')
    config['packages'].append(parent_package+'compiler.tests') 
    config['package_dir']['compiler'] = local_path
    test_path = os.path.join(local_path,'tests')
    config['package_dir']['compiler.tests'] = test_path
    
    scxx_files = glob(os.path.join(local_path,'scxx','*.h'))
    install_path = os.path.join(parent_path,'compiler','scxx')
    config['data_files'].extend( [(install_path,scxx_files)])

    cxx_files = glob(os.path.join(local_path,'CXX','*.*'))
    install_path = os.path.join(parent_path,'compiler','CXX')
    config['data_files'].extend( [(install_path,cxx_files)])
    
    blitz_files = glob(os.path.join(local_path,'blitz-20001213','blitz','*.*'))
    install_path = os.path.join(parent_path,'compiler','blitz-20001213',
                                'blitz')
    config['data_files'].extend( [(install_path,blitz_files)])
    
    array_files = glob(os.path.join(local_path,'blitz-20001213','blitz',
                                    'array','*.*'))
    install_path = os.path.join(parent_path,'compiler','blitz-20001213',
                                'blitz','array')
    config['data_files'].extend( [(install_path,array_files)])
    
    meta_files = glob(os.path.join(local_path,'blitz-20001213','blitz',
                                    'meta','*.*'))
    install_path = os.path.join(parent_path,'compiler','blitz-20001213',
                                'blitz','meta')
    config['data_files'].extend( [(install_path,meta_files)])

    swig_files = glob(os.path.join(local_path,'swig','*.c'))
    install_path = os.path.join(parent_path,'compiler','swig')
    config['data_files'].extend( [(install_path,swig_files)])

    doc_files = glob(os.path.join(local_path,'doc','*.html'))
    install_path = os.path.join(parent_path,'compiler','doc')
    config['data_files'].extend( [(install_path,doc_files)])

    example_files = glob(os.path.join(local_path,'examples','*.py'))
    install_path = os.path.join(parent_path,'compiler','examples')
    config['data_files'].extend( [(install_path,example_files)])
    
    return config


