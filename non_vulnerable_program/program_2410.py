from numpy.testing import *
from numpy import array
import util

class TestReturnCharacter(util.F2PyTest):
    def _check_function(self, t):
        tname = t.__doc__.split()[0]
        if tname in ['t0','t1','s0','s1']:
            assert t(23)=='2'
            r = t('ab');assert r=='a',`r`
            r = t(array('ab'));assert r=='a',`r`
            r = t(array(77,'u1'));assert r=='M',`r`
            #assert_raises(ValueError, t, array([77,87]))
            #assert_raises(ValueError, t, array(77))
        elif tname in ['ts','ss']:
            assert t(23)=='23        ',`t(23)`
            assert t('123456789abcdef')=='123456789a'
        elif tname in ['t5','s5']:
            assert t(23)=='23   ',`t(23)`
            assert t('ab')=='ab   ',`t('ab')`
            assert t('123456789abcdef')=='12345'
        else:
            raise NotImplementedError

class TestF77ReturnCharacter(TestReturnCharacter):
    code = """
       function t0(value)
         character value
         character t0
         t0 = value
       end
       function t1(value)
         character*1 value
         character*1 t1
         t1 = value
       end
       function t5(value)
         character*5 value
         character*5 t5
         t5 = value
       end
       function ts(value)
         character*(*) value
         character*(*) ts
         ts = value
       end

       subroutine s0(t0,value)
         character value
         character t0
cf2py    intent(out) t0
         t0 = value
       end
       subroutine s1(t1,value)
         character*1 value
         character*1 t1
cf2py    intent(out) t1
         t1 = value
       end
       subroutine s5(t5,value)
         character*5 value
         character*5 t5
cf2py    intent(out) t5
         t5 = value
       end
       subroutine ss(ts,value)
         character*(*) value
         character*10 ts
cf2py    intent(out) ts
         ts = value
       end
    """

    def test_all(self):
        for name in "t0,t1,t5,s0,s1,s5,ss".split(","):
            yield self.check_function, name

    def check_function(self, name):
        t = getattr(self.module, name)
        self._check_function(t)


class TestF90ReturnCharacter(TestReturnCharacter):
    suffix = ".f90"
    code = """
module f90_return_char
  contains
       function t0(value)
         character :: value
         character :: t0
         t0 = value
       end function t0
       function t1(value)
         character(len=1) :: value
         character(len=1) :: t1
         t1 = value
       end function t1
       function t5(value)
         character(len=5) :: value
         character(len=5) :: t5
         t5 = value
       end function t5
       function ts(value)
         character(len=*) :: value
         character(len=10) :: ts
         ts = value
       end function ts

       subroutine s0(t0,value)
         character :: value
         character :: t0
!f2py    intent(out) t0
         t0 = value
       end subroutine s0
       subroutine s1(t1,value)
         character(len=1) :: value
         character(len=1) :: t1
!f2py    intent(out) t1
         t1 = value
       end subroutine s1
       subroutine s5(t5,value)
         character(len=5) :: value
         character(len=5) :: t5
!f2py    intent(out) t5
         t5 = value
       end subroutine s5
       subroutine ss(ts,value)
         character(len=*) :: value
         character(len=10) :: ts
!f2py    intent(out) ts
         ts = value
       end subroutine ss
end module f90_return_char
    """

    def test_all(self):
        for name in "t0,t1,t5,ts,s0,s1,s5,ss".split(","):
            yield self.check_function, name

    def check_function(self, name):
        t = getattr(self.module.f90_return_char, name)
        self._check_function(t)

if __name__ == "__main__":
