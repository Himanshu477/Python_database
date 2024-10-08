from UserList import UserList

class test_sequence_base(unittest.TestCase):
    seq_type = None

    def check_conversion(self):
        a = self.seq_type([])
        before = sys.getrefcount(a)
        import weave
        weave.inline("",['a'])
        #print 'first:',before
        # first call is goofing up refcount.
        before = sys.getrefcount(a)        
        weave.inline("",['a'])
        after = sys.getrefcount(a)        
        #print '2nd,3rd:', before, after
        assert(after == before)

    def check_in(self):
        """ Test the "in" method for lists.  We'll assume
            it works for sequences if it works here.
        """
        a = self.seq_type([1,2,'alpha',3.1416])

        item = 1
        code = "return_val = a.in(item);"
        res = inline_tools.inline(code,['a','item'])
        assert res == 1
        item = 0
        res = inline_tools.inline(code,['a','item'])
        assert res == 0
        
        # check overloaded in(int val) method
        code = "return_val = a.in(1);"
        res = inline_tools.inline(code,['a'])
        assert res == 1
        code = "return_val = a.in(0);"
        res = inline_tools.inline(code,['a'])
        assert res == 0
        
        # check overloaded in(double val) method
        code = "return_val = a.in(3.1416);"
        res = inline_tools.inline(code,['a'])
        assert res == 1
        code = "return_val = a.in(3.1417);"
        res = inline_tools.inline(code,['a'])
        assert res == 0
        
        # check overloaded in(char* val) method        
        code = 'return_val = a.in("alpha");'
        res = inline_tools.inline(code,['a'])
        assert res == 1
        code = 'return_val = a.in("beta");'
        res = inline_tools.inline(code,['a'])
        assert res == 0
        
        # check overloaded in(std::string val) method
        code = """
               std::string val = std::string("alpha");
               return_val = a.in(val);
               """
        res = inline_tools.inline(code,['a'])
        assert res == 1
        code = """
               std::string val = std::string("beta");
               return_val = a.in(val);
               """
        res = inline_tools.inline(code,['a'])
        assert res == 0

    def check_count(self):
        """ Test the "count" method for lists.  We'll assume
            it works for sequences if it works hre.
        """
        a = self.seq_type([1,2,'alpha',3.1416])

        item = 1
        code = "return_val = a.count(item);"
        res = inline_tools.inline(code,['a','item'])
        assert res == 1
        
        # check overloaded count(int val) method
        code = "return_val = a.count(1);"
        res = inline_tools.inline(code,['a'])
        assert res == 1
        
        # check overloaded count(double val) method
        code = "return_val = a.count(3.1416);"
        res = inline_tools.inline(code,['a'])
        assert res == 1
        
        # check overloaded count(char* val) method        
        code = 'return_val = a.count("alpha");'
        res = inline_tools.inline(code,['a'])
        assert res == 1
        
        # check overloaded count(std::string val) method
        code = """
               std::string alpha = std::string("alpha");
               return_val = a.count(alpha);
               """
        res = inline_tools.inline(code,['a'])
        assert res == 1
        
    def check_access_speed(self):
        N = 1000000
        print '%s access -- val = a[i] for N =', (self.seq_type, N)
        a = self.seq_type([0]) * N
        val = 0
        t1 = time.time()
        for i in xrange(N):
            val = a[i]
        t2 = time.time()
        print 'python1:', t2 - t1
        t1 = time.time()
        for i in a:
            val = i
        t2 = time.time()
        print 'python2:', t2 - t1
        
        code = """
               const int N = a.length();
               py::object val;
               for(int i=0; i < N; i++)
                   val = a[i];
               """
        # compile not included in timing       
        inline_tools.inline(code,['a'])           
        t1 = time.time()
        inline_tools.inline(code,['a'])           
        t2 = time.time()
        print 'weave:', t2 - t1

    def check_access_set_speed(self):
        N = 1000000
        print '%s access/set -- b[i] = a[i] for N =', (self.seq_type,N)
        a = self.seq_type([0]) * N
        # b is always a list so we can assign to it.
        b = [1] * N
        t1 = time.time()
        for i in xrange(N):
            b[i] = a[i]
        t2 = time.time()
        print 'python:', t2 - t1
        
        a = self.seq_type([0]) * N
        b = [1] * N     
        code = """
               const int N = a.length();
               for(int i=0; i < N; i++)
                   b[i] = a[i];       
               """
        # compile not included in timing
        inline_tools.inline(code,['a','b'])           
        t1 = time.time()
        inline_tools.inline(code,['a','b'])           
        t2 = time.time()
        print 'weave:', t2 - t1
        assert list(b) == list(a)   

class test_tuple(test_sequence_base):
    seq_type = tuple

    def check_set_item_operator_equal_fail(self):
        # Tuples should only allow setting of variables 
        # immediately after creation.
        a = (1,2,3)            
        try:
            inline_tools.inline("a[1] = 1234;",['a'])
        except TypeError:
            pass    
    def check_set_item_operator_equal(self):     
        code = """
               py::tuple a(3);
               a[0] = 1;
               a[1] = 2;
               a[2] = 3;
               return_val = a;
               """
        a = inline_tools.inline(code)
        assert a == (1,2,3)
        # returned value should only have a single refcount
        assert sys.getrefcount(a) == 2

    def check_set_item_index_error(self):     
        code = """
               py::tuple a(3);
               a[4] = 1;
               return_val = a;
               """
        try:
            a = inline_tools.inline(code)
            assert 0
        except IndexError:
            pass    
    def check_get_item_operator_index_error(self):
        code = """
               py::tuple a(3);
               py::object b = a[4]; // should fail.
               """
        try:
            a = inline_tools.inline(code)
            assert 0
        except IndexError:
            pass
                
class test_list(test_sequence_base):
    seq_type = list
    def check_append_passed_item(self):
        a = []
        item = 1
        
        # temporary refcount fix until I understand why it incs by one.
        inline_tools.inline("a.append(item);",['a','item'])
        del a[0]                
        
        before1 = sys.getrefcount(a)
        before2 = sys.getrefcount(item)
        inline_tools.inline("a.append(item);",['a','item'])
        assert a[0] is item
        del a[0]                
        after1 = sys.getrefcount(a)
        after2 = sys.getrefcount(item)
        assert after1 == before1
        assert after2 == before2    
    def check_append(self):
        a = []
        # temporary refcount fix until I understand why it incs by one.
        inline_tools.inline("a.append(1);",['a'])
        del a[0]                
        
        before1 = sys.getrefcount(a)
        
        # check overloaded append(int val) method
        inline_tools.inline("a.append(1234);",['a'])        
        assert sys.getrefcount(a[0]) == 2                
        assert a[0] == 1234
        del a[0]                

        # check overloaded append(double val) method
        inline_tools.inline("a.append(123.0);",['a'])
        assert sys.getrefcount(a[0]) == 2       
        assert a[0] == 123.0
        del a[0]                
        
        # check overloaded append(char* val) method        
        inline_tools.inline('a.append("bubba");',['a'])
        assert sys.getrefcount(a[0]) == 2       
        assert a[0] == 'bubba'
        del a[0]                
        
        # check overloaded append(std::string val) method
        inline_tools.inline('a.append(std::string("sissy"));',['a'])
        assert sys.getrefcount(a[0]) == 2       
        assert a[0] == 'sissy'
        del a[0]                
                
        after1 = sys.getrefcount(a)
        assert after1 == before1
    def check_insert(self):
        a = [1,2,3]
    
        a.insert(1,234)
        del a[1]
        
        # temporary refcount fix until I understand why it incs by one.
        inline_tools.inline("a.insert(1,1234);",['a'])
        del a[1]                
        
        before1 = sys.getrefcount(a)
        
        # check overloaded insert(int ndx, int val) method
        inline_tools.inline("a.insert(1,1234);",['a'])        
        assert sys.getrefcount(a[1]) == 2                
        assert a[1] == 1234
        del a[1]                

        # check overloaded insert(int ndx, double val) method
        inline_tools.inline("a.insert(1,123.0);",['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 123.0
        del a[1]                
        
        # check overloaded insert(int ndx, char* val) method        
        inline_tools.inline('a.insert(1,"bubba");',['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 'bubba'
        del a[1]                
        
        # check overloaded insert(int ndx, std::string val) method
        inline_tools.inline('a.insert(1,std::string("sissy"));',['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 'sissy'
        del a[0]                
                
        after1 = sys.getrefcount(a)
        assert after1 == before1

    def check_set_item_operator_equal(self):
        a = self.seq_type([1,2,3])            
        # temporary refcount fix until I understand why it incs by one.
        inline_tools.inline("a[1] = 1234;",['a'])
        before1 = sys.getrefcount(a)
        
        # check overloaded insert(int ndx, int val) method
        inline_tools.inline("a[1] = 1234;",['a'])        
        assert sys.getrefcount(a[1]) == 2                
        assert a[1] == 1234

        # check overloaded insert(int ndx, double val) method
        inline_tools.inline("a[1] = 123.0;",['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 123.0
        
        # check overloaded insert(int ndx, char* val) method        
        inline_tools.inline('a[1] = "bubba";',['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 'bubba'
        
        # check overloaded insert(int ndx, std::string val) method
        code = """
               std::string val = std::string("sissy");
               a[1] = val;
               """
        inline_tools.inline(code,['a'])
        assert sys.getrefcount(a[1]) == 2       
        assert a[1] == 'sissy'
                
        after1 = sys.getrefcount(a)
        assert after1 == before1
    def check_set_item_operator_equal_created(self):     
        code = """
               py::list a(3);
               a[0] = 1;
               a[1] = 2;
               a[2] = 3;
               return_val = a;
               """
        a = inline_tools.inline(code)
        assert a == [1,2,3]
        # returned value should only have a single refcount
        assert sys.getrefcount(a) == 2
    def check_set_item_index_error(self):     
        code = """
               py::list a(3);
               a[4] = 1;
               """
        try:
            a = inline_tools.inline(code)
            assert 0
        except IndexError:
            pass
    def check_get_item_index_error(self):     
        code = """
               py::list a(3);
               py::object o = a[4];
               """
        try:
            a = inline_tools.inline(code)
            assert 0
        except IndexError:
            pass

    def check_string_add_speed(self):
        N = 1000000
        print 'string add -- b[i] = a[i] + "blah" for N =', N        
        a = ["blah"] * N
        desired = [1] * N
        t1 = time.time()
        for i in xrange(N):
            desired[i] = a[i] + 'blah'
        t2 = time.time()
        print 'python:', t2 - t1
        
        a = ["blah"] * N
        b = [1] * N     
        code = """
               const int N = a.length();
               std::string blah = std::string("blah");
               for(int i=0; i < N; i++)
                   b[i] = (std::string)a[i] + blah;       
               """
        # compile not included in timing
        inline_tools.inline(code,['a','b'])           
        t1 = time.time()
        inline_tools.inline(code,['a','b'])           
        t2 = time.time()
        print 'weave:', t2 - t1
        assert b == desired   
    def check_int_add_speed(self):
        N = 1000000
        print 'int add -- b[i] = a[i] + 1 for N =', N        
        a = [0] * N
        desired = [1] * N
        t1 = time.time()
        for i in xrange(N):
            desired[i] = a[i] + 1
        t2 = time.time()
        print 'python:', t2 - t1
        
        a = [0] * N
        b = [0] * N     
        code = """
               const int N = a.length();
               for(int i=0; i < N; i++)
                   b[i] = (int)a[i] + 1;       
               """
        # compile not included in timing
        inline_tools.inline(code,['a','b'])           
        t1 = time.time()
        inline_tools.inline(code,['a','b'])           
        t2 = time.time()
        print 'weave:', t2 - t1
        assert b == desired   

def test_suite(level=1):
    from unittest import makeSuite
    suites = []    
    if level >= 5:
        #suites.append( makeSuite(test_list,'check_'))
        suites.append( makeSuite(test_tuple,'check_'))
    total_suite = unittest.TestSuite(suites)
    return total_suite

def test(level=10,verbose=2):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


""" Implements a fast replacement for calling DrawLines with an array as an
    argument.  It uses weave, so you'll need that installed.

    Copyright:   Space Telescope Science Institute
    License:     BSD Style
    Designed by: Enthought, Inc.
    Author:      Eric Jones eric@enthought.com

    I wrote this because I was seeing very bad performance for DrawLines when
    called with a large number of points -- 5000-30000. Now, I have found the
    performance is sometimes OK, and sometimes very poor.  Drawing to a
    MemoryDC seems to be worse than drawing to the screen.  My first cut of the
    routine just called PolyLine directly, but I got lousy performance for this
    also.  After noticing the slowdown as the array length grew was much worse
    than linear, I tried the following "chunking" algorithm.  It is much more
    efficient (sometimes by 2 orders of magnitude, but usually only a factor
    of 3).  There is a slight drawback in that it will draw end caps for each
    chunk of the array which is not strictly correct.  I don't imagine this is
    a major issue, but remains an open issue.

"""
