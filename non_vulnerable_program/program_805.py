import f2pytest,sys
r = 3
def g():
    global r
    r = 4
f2pytest.f(g)
if not r==4:
    sys.stderr.write('expected 4 but got %s\\n'%r)
    sys.exit()
print 'ok'
"""
    tests.append(test)



!%f90
python module minpack__user__routines 
    interface hybrd_user_interface 
        subroutine fcnd(n,x,fvec,iflag) ! in :minpack:src/hybrd.f:hybrd:unknown_interface
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            integer :: iflag
        end subroutine fcnd
        subroutine fcnd2(m,n,x,fvec,iflag) ! in :minpack:src/lmdif.f:lmdif:unknown_interface
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            integer :: iflag
        end subroutine fcnd2
        subroutine fcnd3(m,n,x,fvec,wa3,iflag) ! in :minpack:src/lmstr.f:lmstr:unknown_interface
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            integer :: iflag
        end subroutine fcnd3
        subroutine fcnj(n,x,fvec,fjac,ldfjac,iflag) ! in :minpack:src/hybrj.f:hybrj:unknown_interface
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: iflag
        end subroutine fcnj
        subroutine fcnj2(m,n,x,fvec,fjac,ldfjac,iflag) ! in :minpack:src/lmder.f:lmder:unknown_interface
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: iflag
        end subroutine fcnj2
    end interface hybrd_user_interface
end python module minpack__user__routines
python module minpack ! in 
    interface  ! in :minpack
        subroutine hybrd(fcn,n,x,fvec,xtol,maxfev,ml,mu,epsfcn,diag,mode,factor,nprint,info,nfev,fjac,ldfjac,r,lr,qtf,wa1,wa2,wa3,wa4) ! in :minpack:src/hybrd.f
            note(Evaluate functions.) fcn
            note(The number of functions and variables.) n
            note(On input x must contain&
                 an initial estimate of the solution vector. On output x&
                 contains the final estimate of the solution vector.) x
            note(The functions evaluated at the output x.) fvec
            note(Termination occurs when the relative error between two consecutive&
                 iterates is at most xtol.) xtol
            note(Termination&
                 occurs when the number of calls to fcn is at least maxfev&
                 by the end of an iteration. ) maxfev
            note(The number of subdiagonals within the band of the&
                 jacobian matrix. If the jacobian is not banded, set&
                 ml to at least n - 1.) ml
            note(The number of superdiagonals within the band of the&
                 jacobian matrix. If the jacobian is not banded, set&
                 mu to at least n - 1.) mu
            note( Determines  suitable&
                 step length for the forward-difference approximation. This&
                 approximation assumes that the relative errors in the&
                 functions are of the order of epsfcn. If epsfcn is less&
                 than the machine precision, it is assumed that the relative&
                 errors in the functions are of the order of the machine&
                 precision. ) epsfcn
            note( If mode = 1 [see&
                 below], diag is internally set. If mode = 2, diag&
                 contains multiplicative scale factors for the variables.) diag
            note( If mode = 1, the&
                 variables will be scaled internally. If mode = 2,&
                 the scaling is specified by the input diag. other&
                 values of mode are equivalent to mode = 1.) mode
            note( Determines the&
                 initial step bound. This bound is set to the product of&
                 factor and the euclidean norm of diag*x if nonzero, or else&
                 to factor itself. In most cases factor should lie in the&
                 interval [.1,100.]. 100. is a generally recommended value.) factor
            note( Enables controlled&
                 printing of iterates if it is positive. In this case,&
                 fcn is called with iflag = 0 at the beginning of the first&
                 iteration and every nprint iterations thereafter and&
                 immediately prior to return, with x and fvec available&
                 for printing. If nprint is not positive, no special calls&
                 of fcn with iflag = 0 are made.) nprint
            note( If the user has&
                 terminated execution, info is set to the [negative]&
                 value of iflag. See description of fcn. Otherwise,&
                 info is set as follows.&
                 info = 0   improper input parameters.&
                 info = 1   relative error between two consecutive iterates&
                 is at most xtol.&
                 info = 2   number of calls to fcn has reached or exceeded&
                 maxfev.&
                 info = 3   xtol is too small. No further improvement in&
                 the approximate solution x is possible.&
                 info = 4   Iteration is not making good progress, as&
                 measured by the improvement from the last&
                 five jacobian evaluations.&
                 info = 5   Iteration is not making good progress, as&
                 measured by the improvement from the last&
                 ten iterations.) info
            note(The number of calls to fcn.) nfev
            note(Contains the&
                 orthogonal matrix q produced by the qr factorization&
                 of the final approximate jacobian.) fjac
            note(Specifies the leading dimension of the array fjac.) ldfjac
            note(Contains the&
                 upper triangular matrix produced by the qr factorization&
                 of the final approximate jacobian, stored rowwise.) r
            note( lr is a positive integer input variable not less than&
                 [n*[n+1]]/2.) lr
            note( qtf is an output array of length n which contains &
                 the vector [q transpose]*fvec.) qtf
            note(wa1, wa2, wa3, and wa4 are work arrays) wa1
            use minpack__user__routines, fcn => fcnd
            external fcn
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            double precision :: xtol = 1.49012e-8
            integer :: maxfev=200*(n+1)
            integer :: ml=n-1
            integer :: mu=n-1
            double precision :: epsfcn=0.0
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag=1
            integer :: mode=1
            double precision :: factor=100
            integer :: nprint=0
            integer :: info
            integer :: nfev
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)==n,shape(fjac,1)==ldfjac),depend(n,ldfjac) :: fjac
            integer optional,check(ldfjac>=n),depend(n) :: ldfjac=n
            double precision dimension(lr),check(rank(r)==1,len(r)>=lr),depend(lr) :: r
            integer :: lr=(n*(n+1))/2
            double precision dimension(n),check(rank(qtf)==1,len(qtf)>=n),depend(n) :: qtf
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            double precision dimension(n),check(rank(wa4)==1,len(wa4)>=n),depend(n) :: wa4
            depend(n) maxfev,ml,mu
            optional diag,info,nfev,fjac,r,qtf,wa1,wa2,wa3,wa4,fvec
            intent(inout) nfev
            intent(out) info
        end subroutine hybrd
        subroutine lmdif(fcn,m,n,x,fvec,ftol,xtol,gtol,maxfev,epsfcn,diag,mode,factor,nprint,info,nfev,fjac,ldfjac,ipvt,qtf,wa1,wa2,wa3,wa4) ! in :minpack:src/lmdif.f
            use minpack__user__routines, fcn => fcnd2
            external fcn
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision :: ftol=1.49012e-8
            double precision :: xtol=1.49012e-8
            double precision :: gtol=0
            integer :: maxfev=200*(n+1)
            double precision :: epsfcn=0.0
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            integer :: mode=1
            double precision :: factor=100
            integer :: nprint=0
            integer :: info
            integer :: nfev
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)==n,shape(fjac,1)==ldfjac),depend(n,ldfjac) :: fjac=0
            integer optional :: ldfjac=m
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision dimension(n),check(rank(qtf)==1,len(qtf)>=n),depend(n) :: qtf
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            double precision dimension(m),check(rank(wa4)==1,len(wa4)>=m),depend(m) :: wa4
            optional ftol,xtol,gtol,maxfev,mode,factor,nprint,nfev,info
            optional diag,wa1,wa2,wa3,wa4,qtf,ipvt,fjac
            depend(n) maxfev
            depend(m) ldfjac
            intent(out) info
            intent(inout) nfev
        end subroutine lmdif
    end interface
    interface unchecked
        subroutine chkder(m,n,x,fvec,fjac,ldfjac,xp,fvecp,mode,err) ! in :minpack:src/chkder.f
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            double precision dimension(n),check(rank(xp)==1,len(xp)>=n),depend(n) :: xp
            double precision dimension(m),check(rank(fvecp)==1,len(fvecp)>=m),depend(m) :: fvecp
            integer :: mode
            double precision dimension(m),check(rank(err)==1,len(err)>=m),depend(m) :: err
        end subroutine chkder
        subroutine covar(n,r,ldr,ipvt,tol,wa) ! in :minpack:src/covar.f
            integer optional,check(shape(r,0)==n),depend(r) :: n=shape(r,0)
            double precision dimension(ldr,n),check(rank(r)==2) :: r
            integer optional,check(shape(r,1)==ldr),depend(r) :: ldr=shape(r,1)
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision :: tol
            double precision dimension(n),check(rank(wa)==1,len(wa)>=n),depend(n) :: wa
        end subroutine covar
        subroutine dmchar(ibeta,it,irnd,ngrd,machep,negep,iexp,minexp,maxexp,eps,epsneg,xmin,xmax) ! in :minpack:src/dmchar.f
            integer :: ibeta
            integer :: it
            integer :: irnd
            integer :: ngrd
            integer :: machep
            integer :: negep
            integer :: iexp
            integer :: minexp
            integer :: maxexp
            double precision :: eps
            double precision :: epsneg
            double precision :: xmin
            double precision :: xmax
        end subroutine dmchar
        subroutine dogleg(n,r,lr,diag,qtb,delta,x,wa1,wa2) ! in :minpack:src/dogleg.f
            integer optional,check(len(diag)>=n),depend(diag) :: n=len(diag)
            double precision dimension(lr),check(rank(r)==1) :: r
            integer optional,check(len(r)>=lr),depend(r) :: lr=len(r)
            double precision dimension(n),check(rank(diag)==1) :: diag
            double precision dimension(n),check(rank(qtb)==1,len(qtb)>=n),depend(n) :: qtb
            double precision :: delta
            double precision dimension(n),check(rank(x)==1,len(x)>=n),depend(n) :: x
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
        end subroutine dogleg
        function dpmpar(i) ! in :minpack:src/dpmpar.f
            integer :: i
            double precision :: dpmpar
        end function dpmpar
        function enorm(n,x) ! in :minpack:src/enorm.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision :: enorm
        end function enorm
        subroutine errjac(n,x,fjac,ldfjac,nprob) ! in :minpack:src/errjac.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: nprob
        end subroutine errjac
        subroutine fdjac1(fcn,n,x,fvec,fjac,ldfjac,iflag,ml,mu,epsfcn,wa1,wa2) ! in :minpack:src/fdjac1.f
            use minpack__user__routines, fcn => fcnd
            external fcn
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: iflag
            integer :: ml
            integer :: mu
            double precision :: epsfcn
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
        end subroutine fdjac1
        subroutine fdjac2(fcn,m,n,x,fvec,fjac,ldfjac,iflag,epsfcn,wa) ! in :minpack:src/fdjac2.f
            use minpack__user__routines, fcn => fcnd2
            external fcn
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: iflag
            double precision :: epsfcn
            double precision dimension(m),check(rank(wa)==1,len(wa)>=m),depend(m) :: wa
        end subroutine fdjac2
        subroutine grdfcn(n,x,g,nprob) ! in :minpack:src/grdfcn.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(g)==1,len(g)>=n),depend(n) :: g
            integer :: nprob
        end subroutine grdfcn
        subroutine hybrj(fcn,n,x,fvec,fjac,ldfjac,xtol,maxfev,diag,mode,factor,nprint,info,nfev,njev,r,lr,qtf,wa1,wa2,wa3,wa4) ! in :minpack:src/hybrj.f
            use minpack__user__routines, fcn => fcnj
            external fcn
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            double precision :: xtol
            integer :: maxfev
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            integer :: mode
            double precision :: factor
            integer :: nprint
            integer :: info
            integer :: nfev
            integer :: njev
            double precision dimension(lr),check(rank(r)==1) :: r
            integer optional,check(len(r)>=lr),depend(r) :: lr=len(r)
            double precision dimension(n),check(rank(qtf)==1,len(qtf)>=n),depend(n) :: qtf
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            double precision dimension(n),check(rank(wa4)==1,len(wa4)>=n),depend(n) :: wa4
        end subroutine hybrj
        subroutine lmder(fcn,m,n,x,fvec,fjac,ldfjac,ftol,xtol,gtol,maxfev,diag,mode,factor,nprint,info,nfev,njev,ipvt,qtf,wa1,wa2,wa3,wa4) ! in :minpack:src/lmder.f
            use minpack__user__routines, fcn => fcnj2
            external fcn
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            double precision :: ftol
            double precision :: xtol
            double precision :: gtol
            integer :: maxfev
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            integer :: mode
            double precision :: factor
            integer :: nprint
            integer :: info
            integer :: nfev
            integer :: njev
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision dimension(n),check(rank(qtf)==1,len(qtf)>=n),depend(n) :: qtf
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            double precision dimension(m),check(rank(wa4)==1,len(wa4)>=m),depend(m) :: wa4
        end subroutine lmder
        subroutine lmpar(n,r,ldr,ipvt,diag,qtb,delta,par,x,sdiag,wa1,wa2) ! in :minpack:src/lmpar.f
            integer optional,check(shape(r,0)==n),depend(r) :: n=shape(r,0)
            double precision dimension(ldr,n),check(rank(r)==2) :: r
            integer optional,check(shape(r,1)==ldr),depend(r) :: ldr=shape(r,1)
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            double precision dimension(n),check(rank(qtb)==1,len(qtb)>=n),depend(n) :: qtb
            double precision :: delta
            double precision :: par
            double precision dimension(n),check(rank(x)==1,len(x)>=n),depend(n) :: x
            double precision dimension(n),check(rank(sdiag)==1,len(sdiag)>=n),depend(n) :: sdiag
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
        end subroutine lmpar
        subroutine lmstr(fcn,m,n,x,fvec,fjac,ldfjac,ftol,xtol,gtol,maxfev,diag,mode,factor,nprint,info,nfev,njev,ipvt,qtf,wa1,wa2,wa3,wa4) ! in :minpack:src/lmstr.f
            use minpack__user__routines, fcn => fcnd3
            external fcn
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            double precision :: ftol
            double precision :: xtol
            double precision :: gtol
            integer :: maxfev
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            integer :: mode
            double precision :: factor
            integer :: nprint
            integer :: info
            integer :: nfev
            integer :: njev
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision dimension(n),check(rank(qtf)==1,len(qtf)>=n),depend(n) :: qtf
            double precision dimension(n),check(rank(wa1)==1,len(wa1)>=n),depend(n) :: wa1
            double precision dimension(n),check(rank(wa2)==1,len(wa2)>=n),depend(n) :: wa2
            double precision dimension(n),check(rank(wa3)==1,len(wa3)>=n),depend(n) :: wa3
            double precision dimension(m),check(rank(wa4)==1,len(wa4)>=m),depend(m) :: wa4
        end subroutine lmstr
        subroutine objfcn(n,x,f,nprob) ! in :minpack:src/objfcn.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision :: f
            integer :: nprob
        end subroutine objfcn
        subroutine qform(m,n,q,ldq,wa) ! in :minpack:src/qform.f
            integer optional,check(shape(q,0)==m),depend(q) :: m=shape(q,0)
            integer :: n
            double precision dimension(ldq,m),check(rank(q)==2) :: q
            integer optional,check(shape(q,1)==ldq),depend(q) :: ldq=shape(q,1)
            double precision dimension(m),check(rank(wa)==1,len(wa)>=m),depend(m) :: wa
        end subroutine qform
        subroutine qrfac(m,n,a,lda,pivot,ipvt,lipvt,rdiag,acnorm,wa) ! in :minpack:src/qrfac.f
            integer :: m
            integer optional,check(shape(a,0)==n),depend(a) :: n=shape(a,0)
            double precision dimension(lda,n),check(rank(a)==2) :: a
            integer optional,check(shape(a,1)==lda),depend(a) :: lda=shape(a,1)
            logical :: pivot
            integer dimension(lipvt),check(rank(ipvt)==1) :: ipvt
            integer optional,check(len(ipvt)>=lipvt),depend(ipvt) :: lipvt=len(ipvt)
            double precision dimension(n),check(rank(rdiag)==1,len(rdiag)>=n),depend(n) :: rdiag
            double precision dimension(n),check(rank(acnorm)==1,len(acnorm)>=n),depend(n) :: acnorm
            double precision dimension(n),check(rank(wa)==1,len(wa)>=n),depend(n) :: wa
        end subroutine qrfac
        subroutine qrsolv(n,r,ldr,ipvt,diag,qtb,x,sdiag,wa) ! in :minpack:src/qrsolv.f
            integer optional,check(shape(r,0)==n),depend(r) :: n=shape(r,0)
            double precision dimension(ldr,n),check(rank(r)==2) :: r
            integer optional,check(shape(r,1)==ldr),depend(r) :: ldr=shape(r,1)
            integer dimension(n),check(rank(ipvt)==1,len(ipvt)>=n),depend(n) :: ipvt
            double precision dimension(n),check(rank(diag)==1,len(diag)>=n),depend(n) :: diag
            double precision dimension(n),check(rank(qtb)==1,len(qtb)>=n),depend(n) :: qtb
            double precision dimension(n),check(rank(x)==1,len(x)>=n),depend(n) :: x
            double precision dimension(n),check(rank(sdiag)==1,len(sdiag)>=n),depend(n) :: sdiag
            double precision dimension(n),check(rank(wa)==1,len(wa)>=n),depend(n) :: wa
        end subroutine qrsolv
        subroutine r1mpyq(m,n,a,lda,v,w) ! in :minpack:src/r1mpyq.f
            integer :: m
            integer optional,check(shape(a,0)==n),depend(a) :: n=shape(a,0)
            double precision dimension(lda,n),check(rank(a)==2) :: a
            integer optional,check(shape(a,1)==lda),depend(a) :: lda=shape(a,1)
            double precision dimension(n),check(rank(v)==1,len(v)>=n),depend(n) :: v
            double precision dimension(n),check(rank(w)==1,len(w)>=n),depend(n) :: w
        end subroutine r1mpyq
        subroutine r1updt(m,n,s,ls,u,v,w,sing) ! in :minpack:src/r1updt.f
            integer optional,check(len(u)>=m),depend(u) :: m=len(u)
            integer optional,check(len(v)>=n),depend(v) :: n=len(v)
            double precision dimension(ls),check(rank(s)==1) :: s
            integer optional,check(len(s)>=ls),depend(s) :: ls=len(s)
            double precision dimension(m),check(rank(u)==1) :: u
            double precision dimension(n),check(rank(v)==1) :: v
            double precision dimension(m),check(rank(w)==1,len(w)>=m),depend(m) :: w
            logical :: sing
        end subroutine r1updt
        subroutine rwupdt(n,r,ldr,w,b,alpha,cos,sin) ! in :minpack:src/rwupdt.f
            integer optional,check(shape(r,0)==n),depend(r) :: n=shape(r,0)
            double precision dimension(ldr,n),check(rank(r)==2) :: r
            integer optional,check(shape(r,1)==ldr),depend(r) :: ldr=shape(r,1)
            double precision dimension(n),check(rank(w)==1,len(w)>=n),depend(n) :: w
            double precision dimension(n),check(rank(b)==1,len(b)>=n),depend(n) :: b
            double precision :: alpha
            double precision dimension(n),check(rank(cos)==1,len(cos)>=n),depend(n) :: cos
            double precision dimension(n),check(rank(sin)==1,len(sin)>=n),depend(n) :: sin
        end subroutine rwupdt
        subroutine ssqfcn(m,n,x,fvec,nprob) ! in :minpack:src/ssqfcn.f
            integer optional,check(len(fvec)>=m),depend(fvec) :: m=len(fvec)
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(m),check(rank(fvec)==1) :: fvec
            integer :: nprob
        end subroutine ssqfcn
        subroutine ssqjac(m,n,x,fjac,ldfjac,nprob) ! in :minpack:src/ssqjac.f
            integer :: m
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: nprob
        end subroutine ssqjac
        subroutine vecfcn(n,x,fvec,nprob) ! in :minpack:src/vecfcn.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(n),check(rank(fvec)==1,len(fvec)>=n),depend(n) :: fvec
            integer :: nprob
        end subroutine vecfcn
        subroutine vecjac(n,x,fjac,ldfjac,nprob) ! in :minpack:src/vecjac.f
            integer optional,check(len(x)>=n),depend(x) :: n=len(x)
            double precision dimension(n),check(rank(x)==1) :: x
            double precision dimension(ldfjac,n),check(rank(fjac)==2,len(fjac)>=n),depend(n) :: fjac
            integer optional,check(shape(fjac,1)==ldfjac),depend(fjac) :: ldfjac=shape(fjac,1)
            integer :: nprob
        end subroutine vecjac
    end interface 
end python module minpack


