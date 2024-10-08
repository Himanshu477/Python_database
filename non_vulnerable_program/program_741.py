    import ctest
    print ctest.foo.__doc__
    print ctest.foo(f,g)
    return 1

if __name__ == "__main__":
    sys.argv.extend(string.split('build --build-platlib .'))
    main()


!%f90 -*- f90 -*-
python module foo__user__routines 
    interface foo_user_interface 
        subroutine cb_f(x,a,m,n) ! in :cb:test.f:foo:unknown_interface
            real*8 dimension(m),intent(out) :: x
            real*8 dimension(m,n),intent(in) :: a
            integer optional,check(shape(a,1)==m),depend(a) :: m=shape(a,1)
            integer optional,check(shape(a,0)==n),depend(a) :: n=shape(a,0)
        end subroutine cb_f
    end interface foo_user_interface
end python module foo__user__routines
python module cb ! in 
    interface  ! in :cb
        subroutine foo(cb_f,a,m,n) ! in :cb:test.f
            use foo__user__routines
            external cb_f
            real*8 dimension(m,n) :: a
            integer optional,check(shape(a,1)==m),depend(a) :: m=shape(a,1)
            integer optional,check(shape(a,0)==n),depend(a) :: n=shape(a,0)
        end subroutine foo
    end interface 
end python module cb

! This file was auto-generated with f2py (version:2.312).
! See http://cens.ioc.ee/projects/f2py2e/


#! /usr/local/Python/bin/python

