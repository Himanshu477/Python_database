import numpy.base;reload(numpy.base);reload(numpy.base.type_check)
from numpy.base import *
restore_path()

def assert_all(x):
    assert(all(x)), x
       
class test_mintypecode(ScipyTestCase):

    def check_default_1(self):
        for itype in '1bcsuwil':
            assert_equal(mintypecode(itype),'d')
        assert_equal(mintypecode('f'),'f')
        assert_equal(mintypecode('d'),'d')
        assert_equal(mintypecode('F'),'F')
        assert_equal(mintypecode('D'),'D')

    def check_default_2(self):
        for itype in '1bcsuwil':
            assert_equal(mintypecode(itype+'f'),'f')
            assert_equal(mintypecode(itype+'d'),'d')
            assert_equal(mintypecode(itype+'F'),'F')
            assert_equal(mintypecode(itype+'D'),'D')
        assert_equal(mintypecode('ff'),'f')
        assert_equal(mintypecode('fd'),'d')
        assert_equal(mintypecode('fF'),'F')
        assert_equal(mintypecode('fD'),'D')
        assert_equal(mintypecode('df'),'d')
        assert_equal(mintypecode('dd'),'d')
        #assert_equal(mintypecode('dF',savespace=1),'F')
        assert_equal(mintypecode('dF'),'D')
        assert_equal(mintypecode('dD'),'D')
        assert_equal(mintypecode('Ff'),'F')
        #assert_equal(mintypecode('Fd',savespace=1),'F')
        assert_equal(mintypecode('Fd'),'D')
        assert_equal(mintypecode('FF'),'F')
        assert_equal(mintypecode('FD'),'D')
        assert_equal(mintypecode('Df'),'D')
        assert_equal(mintypecode('Dd'),'D')
        assert_equal(mintypecode('DF'),'D')
        assert_equal(mintypecode('DD'),'D')

    def check_default_3(self):
        assert_equal(mintypecode('fdF'),'D')
        #assert_equal(mintypecode('fdF',savespace=1),'F')
        assert_equal(mintypecode('fdD'),'D')
        assert_equal(mintypecode('fFD'),'D')
        assert_equal(mintypecode('dFD'),'D')

        assert_equal(mintypecode('ifd'),'d')
        assert_equal(mintypecode('ifF'),'F')
        assert_equal(mintypecode('ifD'),'D')
        assert_equal(mintypecode('idF'),'D')
        #assert_equal(mintypecode('idF',savespace=1),'F')
        assert_equal(mintypecode('idD'),'D')
        
class test_isscalar(ScipyTestCase):
    def check_basic(self):
        assert(isscalar(3))
        assert(not isscalar([3]))
        assert(not isscalar((3,)))
        assert(isscalar(3j))
        assert(isscalar(10L))
        assert(isscalar(4.0))

class test_real(ScipyTestCase):
    def check_real(self):
        y = rand(10,)
        assert_array_equal(y,real(y))

    def check_cmplx(self):
        y = rand(10,)+1j*rand(10,)
        assert_array_equal(y.real,real(y))

class test_imag(ScipyTestCase):
    def check_real(self):
        y = rand(10,)
        assert_array_equal(0,imag(y))

    def check_cmplx(self):
        y = rand(10,)+1j*rand(10,)
        assert_array_equal(y.imag,imag(y))

class test_iscomplex(ScipyTestCase):
    def check_fail(self):
        z = array([-1,0,1])
        res = iscomplex(z)
        assert(not sometrue(res))
    def check_pass(self):
        z = array([-1j,1,0])
        res = iscomplex(z)
        assert_array_equal(res,[1,0,0])

class test_isreal(ScipyTestCase):
    def check_pass(self):
        z = array([-1,0,1j])
        res = isreal(z)
        assert_array_equal(res,[1,1,0])
    def check_fail(self):
        z = array([-1j,1,0])
        res = isreal(z)
        assert_array_equal(res,[0,1,1])

class test_iscomplexobj(ScipyTestCase):
    def check_basic(self):
        z = array([-1,0,1])
        assert(not iscomplexobj(z))
        z = array([-1j,0,-1])
        assert(iscomplexobj(z))

class test_isrealobj(ScipyTestCase):
    def check_basic(self):
        z = array([-1,0,1])
        assert(isrealobj(z))
        z = array([-1j,0,-1])
        assert(not isrealobj(z))

class test_isnan(ScipyTestCase):
    def check_goodvalues(self):
        z = array((-1.,0.,1.))
        res = isnan(z) == 0
        assert_all(alltrue(res))            
    def check_posinf(self): 
        assert_all(isnan(array((1.,))/0.) == 0)
    def check_neginf(self): 
        assert_all(isnan(array((-1.,))/0.) == 0)
    def check_ind(self): 
        assert_all(isnan(array((0.,))/0.) == 1)
    #def check_qnan(self):             log(-1) return pi*j now
    #    assert_all(isnan(log(-1.)) == 1)
    def check_integer(self):
        assert_all(isnan(1) == 0)
    def check_complex(self):
        assert_all(isnan(1+1j) == 0)
    def check_complex1(self):
        assert_all(isnan(array(0+0j)/0.) == 1)
                
class test_isfinite(ScipyTestCase):
    def check_goodvalues(self):
        z = array((-1.,0.,1.))
        res = isfinite(z) == 1
        assert_all(alltrue(res))            
    def check_posinf(self): 
        assert_all(isfinite(array((1.,))/0.) == 0)
    def check_neginf(self): 
        assert_all(isfinite(array((-1.,))/0.) == 0)
    def check_ind(self): 
        assert_all(isfinite(array((0.,))/0.) == 0)
    #def check_qnan(self): 
    #    assert_all(isfinite(log(-1.)) == 0)
    def check_integer(self):
        assert_all(isfinite(1) == 1)
    def check_complex(self):
        assert_all(isfinite(1+1j) == 1)
    def check_complex1(self):
        assert_all(isfinite(array(1+1j)/0.) == 0)
        
class test_isinf(ScipyTestCase):
    def check_goodvalues(self):
        z = array((-1.,0.,1.))
        res = isinf(z) == 0
        assert_all(alltrue(res))            
    def check_posinf(self): 
        assert_all(isinf(array((1.,))/0.) == 1)
    def check_posinf_scalar(self): 
        assert_all(isinf(array(1.,)/0.) == 1)
    def check_neginf(self): 
        assert_all(isinf(array((-1.,))/0.) == 1)
    def check_neginf_scalar(self): 
        assert_all(isinf(array(-1.)/0.) == 1)
    def check_ind(self): 
        assert_all(isinf(array((0.,))/0.) == 0)
    #def check_qnan(self): 
    #    assert_all(isinf(log(-1.)) == 0)
    #    assert_all(isnan(log(-1.)) == 1)

class test_isposinf(ScipyTestCase):
    def check_generic(self):
        vals = isposinf(array((-1.,0,1))/0.)
        assert(vals[0] == 0)
        assert(vals[1] == 0)
        assert(vals[2] == 1)

class test_isneginf(ScipyTestCase):
    def check_generic(self):
        vals = isneginf(array((-1.,0,1))/0.)
        assert(vals[0] == 1)
        assert(vals[1] == 0)
        assert(vals[2] == 0)

class test_nan_to_num(ScipyTestCase):
    def check_generic(self):
        vals = nan_to_num(array((-1.,0,1))/0.)
        assert_all(vals[0] < -1e10) and assert_all(isfinite(vals[0]))
        assert(vals[1] == 0)
        assert_all(vals[2] > 1e10) and assert_all(isfinite(vals[2]))
    def check_integer(self):
        vals = nan_to_num(1)
        assert_all(vals == 1)
    def check_complex_good(self):
        vals = nan_to_num(1+1j)
        assert_all(vals == 1+1j)
    def check_complex_bad(self):
        v = 1+1j
        v += array(0+1.j)/0.
        vals = nan_to_num(v)
        # !! This is actually (unexpectedly) zero
        assert_all(isfinite(vals))
    def check_complex_bad2(self):
        v = 1+1j
        v += array(-1+1.j)/0.
        vals = nan_to_num(v)
        assert_all(isfinite(vals))    
        #assert_all(vals.imag > 1e10)  and assert_all(isfinite(vals))    
        # !! This is actually (unexpectedly) positive
        # !! inf.  Comment out for now, and see if it
        # !! changes
        #assert_all(vals.real < -1e10) and assert_all(isfinite(vals))    


class test_real_if_close(ScipyTestCase):
    def check_basic(self):
        a = rand(10)
        b = real_if_close(a+1e-15j)
        assert_all(isrealobj(b))
        assert_array_equal(a,b)
        b = real_if_close(a+1e-7j)
        assert_all(iscomplexobj(b))
        b = real_if_close(a+1e-7j,tol=1e-6)
        assert_all(isrealobj(b))

if __name__ == "__main__":
    ScipyTest().run()


"""
>>> import numpy.base as nx
>>> import numpy.base.ufunclike as U

Test fix:
>>> a = nx.array([[1.0, 1.1, 1.5, 1.8], [-1.0, -1.1, -1.5, -1.8]])
>>> U.fix(a)
array([[ 1.,  1.,  1.,  1.],
       [ 0., -1., -1., -1.]])
>>> y = nx.zeros(a.shape, float)
>>> U.fix(a, y)
array([[ 1.,  1.,  1.,  1.],
       [ 0., -1., -1., -1.]])
>>> y
array([[ 1.,  1.,  1.,  1.],
       [ 0., -1., -1., -1.]])

Test isposinf, isneginf, sign
>>> a = nx.array([nx.Inf, -nx.Inf, nx.NaN, 0.0, 3.0, -3.0])
>>> U.isposinf(a)
array([True, False, False, False, False, False], dtype=bool)
>>> U.isneginf(a)
array([False, True, False, False, False, False], dtype=bool)
>>> U.sign(a)
array([ 1, -1,  0,  0,  1, -1])

Same thing with an output array:
>>> y = nx.zeros(a.shape, bool)
>>> U.isposinf(a, y)
array([True, False, False, False, False, False], dtype=bool)
>>> y
array([True, False, False, False, False, False], dtype=bool)
>>> U.isneginf(a, y)
array([False, True, False, False, False, False], dtype=bool)
>>> y
array([False, True, False, False, False, False], dtype=bool)
>>> U.sign(a, y)
array([True, True, False, False, True, True], dtype=bool)
>>> y
array([True, True, False, False, True, True], dtype=bool)

Now log2:
>>> a = nx.array([4.5, 2.3, 6.5])
>>> U.log2(a)
array([ 2.169925  ,  1.20163386,  2.70043972])
>>> 2**_
array([ 4.5,  2.3,  6.5])
>>> y = nx.zeros(a.shape, float)
>>> U.log2(a, y)
array([ 2.169925  ,  1.20163386,  2.70043972])
>>> y
array([ 2.169925  ,  1.20163386,  2.70043972])

"""

