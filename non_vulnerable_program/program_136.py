from compiler_test_utils import *
restore_path()


class test_default_dir(unittest.TestCase):
    def check_is_writable(self):
        path = default_dir()
        name = os.path.join(path,'dummy_catalog')
        test_file = open(name,'w')
        try:
            test_file.write('making sure default location is writable\n')
        finally:
            test_file.close()
            os.remove(name)

class test_os_dependent_catalog_name(unittest.TestCase):        
    pass
    
class test_catalog_path(unittest.TestCase):        
    def check_default(self):
        in_path = default_dir()
        path = catalog_path(in_path)
        d,f = os.path.split(path)
        assert(d == in_path)
        assert(f == os_dependent_catalog_name())
    def check_current(self):
        in_path = '.'
        path = catalog_path(in_path)
        d,f = os.path.split(path)
        assert(d == os.path.abspath(in_path))     
        assert(f == os_dependent_catalog_name())   
    def check_user(path):
        if sys.platform != 'win32':
            in_path = '~'
            path = catalog_path(in_path)
            d,f = os.path.split(path)
            assert(d == os.path.expanduser(in_path))        
            assert(f == os_dependent_catalog_name())
    def check_module(self):
        # hand it a module and see if it uses the parent directory
        # of the module.
        path = catalog_path(os.__file__)
        d,f = os.path.split(os.__file__)
        d2,f = os.path.split(path)
        assert (d2 == d)
    def check_path(self):
        # use os.__file__ to get a usable directory.
        in_path,f = os.path.split(os.__file__)
        path = catalog_path(in_path)
        d,f = os.path.split(path)
        assert (d == in_path)
    def check_bad_path(self):
        # stupid_path_name
        in_path = 'stupid_path_name'
        path = catalog_path(in_path)
        assert (path is None)

class test_get_catalog(unittest.TestCase):
    """ This only tests whether new catalogs are created correctly.
        And whether non-existent return None correctly with read mode.
        Putting catalogs in the right place is all tested with
        catalog_dir tests.
    """
    def get_test_dir(self,erase = 0):
        # make sure tempdir catalog doesn't exist
        import tempfile
        temp = tempfile.gettempdir()
        pardir = os.path.join(temp,'catalog_test')
        if not os.path.exists(pardir):
            os.mkdir(pardir)
        catalog_file = os.path.join(pardir,os_dependent_catalog_name()+'.dat')
        if os.path.exists(catalog_file) and erase:
            os.remove(catalog_file)
        catalog_file = os.path.join(pardir,os_dependent_catalog_name()+'.dir')
        if os.path.exists(catalog_file) and erase:
            os.remove(catalog_file)
        catalog_file = os.path.join(pardir,os_dependent_catalog_name())
        if os.path.exists(catalog_file) and erase:
            os.remove(catalog_file)
        return pardir
    def check_nonexistent_catalog_is_none(self):
        pardir = self.get_test_dir(erase=1)
        catalog = get_catalog(pardir)
        assert(catalog is None)
    def check_create_catalog(self):
        pardir = self.get_test_dir(erase=1)
        catalog = get_catalog(pardir,'cr')
        assert(catalog is not None)

class test_catalog(unittest.TestCase):

    def clear_environ(self):
        if os.environ.has_key('PYTHONCOMPILED'):
            self.old_PYTHONCOMPILED = os.environ['PYTHONCOMPILED']
            del os.environ['PYTHONCOMPILED']
        else:    
            self.old_PYTHONCOMPILED = None
    def reset_environ(self):
        if self.old_PYTHONCOMPILED:
            os.environ['PYTHONCOMPILED'] = self.old_PYTHONCOMPILED
            self.old_PYTHONCOMPILED = None
    def setUp(self):
        self.clear_environ()        
    def tearDown(self):
        self.reset_environ()
    
    def check_set_module_directory(self):
        q = catalog.catalog()
        q.set_module_directory('bob')
        r = q.get_module_directory()
        assert (r == 'bob')
    def check_clear_module_directory(self):
        q = catalog.catalog()
        r = q.get_module_directory()
        assert (r == None)
        q.set_module_directory('bob')
        r = q.clear_module_directory()
        assert (r == None)
    def check_get_environ_path(self):
        if sys.platform == 'win32': sep = ';'
        else: sep = ':'
        os.environ['PYTHONCOMPILED'] = sep.join(('path1','path2','path3'))
        q = catalog.catalog()
        path = q.get_environ_path()                
        assert(path == ['path1','path2','path3'])
    def check_build_search_order1(self):        
        """ MODULE in search path should be replaced by module_dir.
        """                        
        q = catalog.catalog(['first','MODULE','third'])
        q.set_module_directory('second')
        order = q.build_search_order()
        assert(order == ['first','second','third',default_dir()])
    def check_build_search_order2(self):        
        """ MODULE in search path should be removed if module_dir==None.
        """                        
        q = catalog.catalog(['first','MODULE','third'])
        order = q.build_search_order()
        assert(order == ['first','third',default_dir()])        
    def check_build_search_order3(self):
        """ If MODULE is absent, module_dir shouldn't be in search path.
        """                        
        q = catalog.catalog(['first','second'])
        q.set_module_directory('third')
        order = q.build_search_order()
        assert(order == ['first','second',default_dir()])
    def check_build_search_order4(self):
        """ Make sure environment variable is getting used.
        """                        
        q = catalog.catalog(['first','second'])
        if sys.platform == 'win32': sep = ';'
        else: sep = ':'
        os.environ['PYTHONCOMPILED'] = sep.join(('MODULE','fourth','fifth'))
        q.set_module_directory('third')
        order = q.build_search_order()
        assert(order == ['first','second','third','fourth','fifth',default_dir()])
    
    def check_catalog_files1(self):
        """ Be sure we get at least one file even without specifying the path.
        """
        q = catalog.catalog()
        files = q.get_catalog_files()
        assert(len(files) == 1)

    def check_catalog_files2(self):
        """ Ignore bad paths in the path.
        """
        q = catalog.catalog()
        os.environ['PYTHONCOMPILED'] = '_some_bad_path_'
        files = q.get_catalog_files()
        assert(len(files) == 1)
    
    def check_get_existing_files1(self):
        """ Shouldn't get any files when temp doesn't exist and no path set.            
        """ 
        clear_temp_catalog()
        q = catalog.catalog()
        files = q.get_existing_files()
        restore_temp_catalog()
        assert(len(files) == 0)
    def check_get_existing_files2(self):
        """ Shouldn't get a single file from the temp dir.
        """ 
        clear_temp_catalog()
        q = catalog.catalog()
        # create a dummy file
        import os 
        q.add_function('code', os.getpid)
        del q
        q = catalog.catalog()
        files = q.get_existing_files()
        restore_temp_catalog()
        assert(len(files) == 1)
                       
    def check_access_writable_file(self):
        """ There should always be a writable file -- even if it is in temp
        """
        q = catalog.catalog()
        file = q.get_writable_file()
        try:
            f = open(file,'w')
            f.write('bob')
        finally:
            f.close()
            os.remove(file)                
    def check_writable_with_bad_path(self):
        """ There should always be a writable file -- even if search paths contain
            bad values.
        """
        if sys.platform == 'win32': sep = ';'
        else: sep = ':'        
        os.environ['PYTHONCOMPILED'] = sep.join(('_bad_path_name_'))
        q = catalog.catalog()
        file = q.get_writable_file()
        try:
            f = open(file,'w')
            f.write('bob')
        finally:
            f.close()
        os.remove(file)                
    def check_writable_dir(self):
        """ Check that we can create a file in the writable directory
        """
        q = catalog.catalog()
        d = q.get_writable_dir()
        file = os.path.join(d,'some_silly_file')
        try:
            f = open(file,'w')
            f.write('bob')
        finally:
            f.close()
            os.remove(file)
    def check_unique_module_name(self):
        """ Check that we can create a file in the writable directory
        """
        q = catalog.catalog()
        file = q.unique_module_name('bob')
        cfile1 = file+'.cpp'
        assert(not os.path.exists(cfile1))
        #make sure it is writable
        try:
            f = open(cfile1,'w')
            f.write('bob')
        finally:    
            f.close()
        # try again with same code fragment -- should get unique name
        file = q.unique_module_name('bob')
        cfile2 = file+'.cpp'
        assert(not os.path.exists(cfile2+'.cpp'))
        os.remove(cfile1)
    def check_add_function_persistent1(self):
        """ Test persisting a function in the default catalog
        """
        clear_temp_catalog()
        q = catalog.catalog()
        mod_name = q.unique_module_name('bob')
        d,f = os.path.split(mod_name)
        module_name, funcs = simple_module(d,f,'f')
        for i in funcs:
            q.add_function_persistent('code',i)
        pfuncs = q.get_cataloged_functions('code')    
        os.remove(module_name)
        # any way to clean modules???
        restore_temp_catalog()
        for i in funcs:
            assert(i in pfuncs)        
 
    def not_sure_about_this_check_add_function_persistent2(self):
        """ Test ordering of persistent functions
        """
        clear_temp_catalog()
        q = catalog.catalog()                
        
        mod_name = q.unique_module_name('bob')        
        d,f = os.path.split(mod_name)
        module_name1, funcs1 = simple_module(d,f,'f')
        for i in funcs1:
            q.add_function_persistent('code',i)
        
        d = empty_temp_dir()
        q = catalog(d)        
        mod_name = q.unique_module_name('bob')        
        d,f = os.path.split(mod_name)
        module_name2, funcs2 = simple_module(d,f,'f')
        for i in funcs2:
            q.add_function_persistent('code',i)
        pfuncs = q.get_cataloged_functions('code')    
        
        os.remove(module_name1)
        os.remove(module_name2)
        cleanup_temp_dir(d)
        restore_temp_catalog()
        # any way to clean modules???
        for i in funcs1:
            assert(i in pfuncs)        
        for i in funcs2:
            assert(i in pfuncs)
        # make sure functions occur in correct order for
        # lookup     
        all_funcs = zip(funcs1,funcs2)
        print all_funcs
        for a,b in all_funcs:
            assert(pfuncs.index(a) > pfuncs.index(b))
    
        assert(len(pfuncs) == 4)

    def check_add_function_ordered(self):
        clear_temp_catalog()
        q = catalog.catalog()
        import string
        
        q.add_function('f',string.upper)        
        q.add_function('f',string.lower)
        q.add_function('ff',string.find)        
        q.add_function('ff',string.replace)
        q.add_function('fff',string.atof)
        q.add_function('fff',string.atoi)
        del q

        # now we're gonna make a new catalog with same code
        # but different functions in a specified module directory
        env_dir = empty_temp_dir()
        r = catalog.catalog(env_dir)
        r.add_function('ff',os.abort)
        r.add_function('ff',os.chdir)
        r.add_function('fff',os.access)
        r.add_function('fff',os.open)
        del r
        # now we're gonna make a new catalog with same code
        # but different functions in a user specified directory
        user_dir = empty_temp_dir()
        s = catalog.catalog(user_dir)
        import re
        s.add_function('fff',re.match)
        s.add_function('fff',re.purge)
        del s

        # open new catalog and make sure it retreives the functions
        # from d catalog instead of the temp catalog (made by q)
        os.environ['PYTHONCOMPILED'] = env_dir
        t = catalog.catalog(user_dir)
        funcs1 = t.get_functions('f')
        funcs2 = t.get_functions('ff')
        funcs3 = t.get_functions('fff')
        restore_temp_catalog()
        # make sure everything is read back in the correct order
        assert(funcs1 == [string.lower,string.upper])
        assert(funcs2 == [os.chdir,os.abort,string.replace,string.find])
        assert(funcs3 == [re.purge,re.match,os.open,
                          os.access,string.atoi,string.atof])
        cleanup_temp_dir(user_dir)
        cleanup_temp_dir(env_dir)
        
    
def test_suite():
    suites = []
    suites.append( unittest.makeSuite(test_default_dir,'check_'))
    suites.append( unittest.makeSuite(test_os_dependent_catalog_name,'check_'))
    suites.append( unittest.makeSuite(test_catalog_path,'check_'))
    suites.append( unittest.makeSuite(test_get_catalog,'check_'))
    suites.append( unittest.makeSuite(test_catalog,'check_'))

    total_suite = unittest.TestSuite(suites)
    return total_suite

def test():
    all_tests = test_suite()
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner


if __name__ == '__main__':
    test()


