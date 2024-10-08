    from a variety of probability distributions. In addition to the
    distribution-specific arguments, each method takes a keyword argument
    size=None. If size is None, then a single value is generated and returned.
    If size is an integer, then a 1-D scipy array filled with generated values
    is returned. If size is a tuple, then a scipy array with that shape is
    filled and returned.
    """
    cdef rk_state *internal_state

    def __init__(self, seed=None):
        self.internal_state = <rk_state*>PyMem_Malloc(sizeof(rk_state))

        self.seed(seed)

    def __dealloc__(self):
        if self.internal_state != NULL:
            PyMem_Free(self.internal_state)

    def seed(self, seed=None):
        """Seed the generator.

        seed(seed=None)

        seed can be an integer, an array (or other sequence) of integers of any
        length, or None. If seed is None, then RandomState will try to read data
        from /dev/urandom (or the Windows analogue) if available or seed from
        the clock otherwise.
        """
        cdef rk_error errcode
        cdef ndarray obj "arrayObject_obj"
        if seed is None:
            errcode = rk_randomseed(self.internal_state)
        elif type(seed) is int:
            rk_seed(seed, self.internal_state)
        else:
            obj = <ndarray>PyArray_ContiguousFromObject(seed, PyArray_LONG, 1, 1)
            init_by_array(self.internal_state, <unsigned long *>(obj.data),
                obj.dimensions[0])

    def get_state(self):
        """Return a tuple representing the internal state of the generator.

        get_state() -> ('MT19937', int key[624], int pos)
        """
        cdef ndarray state "arrayObject_state"
        state = <ndarray>_sp.empty(624, _sp.Int)
        memcpy(<void*>(state.data), self.internal_state.key, 624*sizeof(long))
        return ('MT19937', state, self.internal_state.pos)
        
    def set_state(self, state):
        """Set the state from a tuple.
        
        state = ('MT19937', int key[624], int pos)
        
        set_state(state)
        """
        cdef ndarray obj "arrayObject_obj"
        cdef int pos
        algorithm_name = state[0]
        if algorithm_name != 'MT19937':
            raise ValueError("algorithm must be 'MT19937'")
        key, pos = state[1:]
        obj = <ndarray>PyArray_ContiguousFromObject(key, PyArray_LONG, 1, 1)
        if obj.dimensions[0] != 624:
            raise ValueError("state must be 624 longs")
        memcpy(self.internal_state.key, <void*>(obj.data), 624*sizeof(long))
        self.internal_state.pos = pos
    
    # Pickling support:
    def __getstate__(self):
        return self.get_state()

    def __setstate__(self, state):
        self.set_state(state)

    def __reduce__(self):
        return (_sp.random.__RandomState_ctor, (), self.get_state())

    # Basic distributions:
    def random_sample(self, size=None):
        """Return random floats in the half-open interval [0.0, 1.0).

        random_sample(size=None) -> random values
        """
        return cont0_array(self.internal_state, rk_double, size)

    def tomaxint(self, size=None):
        """Returns random integers x such that 0 <= x <= sys.maxint.

        tomaxint(size=None) -> random values
        """
        return disc0_array(self.internal_state, rk_long, size)

    def randint(self, low, high=None, size=None):
        """Return random integers x such that low <= x < high.

        randint(low, high=None, size=None) -> random values

        If high is None, then 0 <= x < low.
        """
        cdef long lo, hi, diff
        cdef long *array_data
        cdef ndarray array "arrayObject"
        cdef long length
        cdef long i

        if high is None:
            lo = 0
            hi = low
        else:
            lo = low
            hi = high

        diff = hi - lo - 1
        if diff < 0:
            raise ValueError("low >= high")
    
        if size is None:
            return rk_interval(diff, self.internal_state)
        else:
            array = <ndarray>_sp.empty(size, _sp.Int)
            length = PyArray_SIZE(array)
            array_data = <long *>array.data
            for i from 0 <= i < length:
                array_data[i] = lo + <long>rk_interval(diff, self.internal_state)
            return array

    def bytes(self, unsigned int length):
        """Return random bytes.

        bytes(length) -> str
        """
        cdef void *bytes
        bytes = PyMem_Malloc(length)
        rk_fill(bytes, length, self.internal_state)
        bytestring = PyString_FromString(<char*>bytes)
        PyMem_Free(bytes)
        return bytestring

    def uniform(self, double low=0.0, double high=1.0, size=None):
        """Uniform distribution over [low, high).

        uniform(low=0.0, high=1.0, size=None) -> random values
        """
        return cont2_array(self.internal_state, rk_uniform, size, low, 
            high-low)

    def rand(self, *args):
        """Return an array of the given dimensions which is initialized to 
        random numbers from a uniform distribution in the range [0,1).

        rand(d0, d1, ..., dn) -> random values
        """
        if len(args) == 0:
            return self.random_sample()
        else:
            return self.random_sample(size=args)

    def randn(self, *args):
        """Returns zero-mean, unit-variance Gaussian random numbers in an 
        array of shape (d0, d1, ..., dn).

        randn(d0, d1, ..., dn) -> random values
        """
        if len(args) == 0:
            return self.standard_normal()
        else:
            return self.standard_normal(args)

    def random_integers(self, low, high=None, size=None):
        """Return random integers x such that low <= x <= high.

        random_integers(low, high=None, size=None) -> random values.

        If high is None, then 1 <= x <= low.
        """
        if high is None:
            high = low
            low = 1
        return self.randint(low, high+1, size)

    # Complicated, continuous distributions:
    def standard_normal(self, size=None):
        """Standard Normal distribution (mean=0, stdev=1).

        standard_normal(size=None) -> random values
        """
        return cont0_array(self.internal_state, rk_gauss, size)

    def normal(self, double loc=0.0, double scale=1.0, size=None):
        """Normal distribution (mean=loc, stdev=scale).

        normal(loc=0.0, scale=1.0, size=None) -> random values
        """
        if scale <= 0:
            raise ValueError("scale <= 0")
        return cont2_array(self.internal_state, rk_normal, size, loc, scale)

    def beta(self, double a, double b, size=None):
        """Beta distribution over [0, 1].

        beta(a, b, size=None) -> random values
        """
        if a <= 0:
            raise ValueError("a <= 0")
        elif b <= 0:
            raise ValueError("b <= 0")
        return cont2_array(self.internal_state, rk_beta, size, a, b)

    def exponential(self, double scale=1.0, size=None):
        """Exponential distribution.

        exponential(scale=1.0, size=None) -> random values
        """
        if scale <= 0:
            raise ValueError("scale <= 0")
        return cont1_array(self.internal_state, rk_exponential, size, scale)

    def standard_exponential(self, size=None):
        """Standard exponential distribution (scale=1).

        standard_exponential(size=None) -> random values
        """
        return cont0_array(self.internal_state, rk_standard_exponential, size)

    def standard_gamma(self, double shape, size=None):
        """Standard Gamma distribution.

        standard_gamma(shape, size=None) -> random values
        """
        if shape <= 0:
            raise ValueError("shape <= 0")
        return cont1_array(self.internal_state, rk_standard_gamma, size, shape)

    def gamma(self, double shape, double scale=1.0, size=None):
        """Gamma distribution.

        gamma(shape, scale=1.0, size=None) -> random values
        """
        if shape <= 0:
            raise ValueError("shape <= 0")
        elif scale <= 0:
            raise ValueError("scale <= 0")
        return cont2_array(self.internal_state, rk_gamma, size, shape, scale)

    def f(self, double dfnum, double dfden, size=None):
        """F distribution.

        f(dfnum, dfden, size=None) -> random values
        """
        if dfnum <= 0:
            raise ValueError("dfnum <= 0")
        elif dfden <= 0:
            raise ValueError("dfden <= 0")
        return cont2_array(self.internal_state, rk_f, size, dfnum, dfden)

    def noncentral_f(self, double dfnum, double dfden, double nonc, size=None):
        """Noncentral F distribution.

        noncentral_f(dfnum, dfden, nonc, size=None) -> random values
        """
        if dfnum <= 1:
            raise ValueError("dfnum <= 1")
        elif dfden <= 0:
            raise ValueError("dfden <= 0")
        elif nonc < 0:
            raise ValueError("nonc < 0")
        return cont3_array(self.internal_state, rk_noncentral_f, size, dfnum,
            dfden, nonc)

    def chisquare(self, double df, size=None):
        """Chi^2 distribution.

        chisquare(df, size=None) -> random values
        """
        if df <= 0:
            raise ValueError("df <= 0")
        return cont1_array(self.internal_state, rk_chisquare, size, df)

    def noncentral_chisquare(self, double df, double nonc, size=None):
        """Noncentral Chi^2 distribution.

        noncentral_chisquare(df, nonc, size=None) -> random values
        """
        if df <= 1:
            raise ValueError("df <= 1")
        elif nonc < 0:
            raise ValueError("nonc < 0")
        return cont2_array(self.internal_state, rk_noncentral_chisquare, size,
            df, nonc)
    
    def standard_cauchy(self, size=None):
        """Standard Cauchy with mode=0.

        standard_cauchy(size=None)
        """
        return cont0_array(self.internal_state, rk_standard_cauchy, size)

    def standard_t(self, double df, size=None):
        """Standard Student's t distribution with df degrees of freedom.

        standard_t(df, size=None)
        """
        if df <= 0:
            raise ValueError("df <= 0")
        return cont1_array(self.internal_state, rk_standard_t, size, df)

    def vonmises(self, double mu, double kappa, size=None):
        """von Mises circular distribution with mode mu and dispersion parameter
        kappa on [-pi, pi].

        vonmises(mu, kappa, size=None)
        """
        if kappa < 0:
            raise ValueError("kappa < 0")
        return cont2_array(self.internal_state, rk_vonmises, size, mu, kappa)

    def pareto(self, double a, size=None):
        """Pareto distribution.

        pareto(a, size=None)
        """
        if a <= 0:
            raise ValueError("a <= 0")
        return cont1_array(self.internal_state, rk_pareto, size, a)

    def weibull(self, double a, size=None):
        """Weibull distribution.

        weibull(a, size=None)
        """
        if a <= 0:
            raise ValueError("a <= 0")
        return cont1_array(self.internal_state, rk_weibull, size, a)

    def power(self, double a, size=None):
        """Power distribution.

        power(a, size=None)
        """
        if a <= 0:
            raise ValueError("a <= 0")
        return cont1_array(self.internal_state, rk_power, size, a)

    def laplace(self, double loc=0.0, double scale=1.0, size=None):
        """Laplace distribution.
        
        laplace(loc=0.0, scale=1.0, size=None)
        """
        if scale <= 0.0:
            raise ValueError("scale <= 0.0")
        return cont2_array(self.internal_state, rk_laplace, size, loc, scale)
    
    def gumbel(self, double loc=0.0, double scale=1.0, size=None):
        """Gumbel distribution.
        
        gumbel(loc=0.0, scale=1.0, size=None)
        """
        if scale <= 0.0:
            raise ValueError("scale <= 0.0")
        return cont2_array(self.internal_state, rk_gumbel, size, loc, scale)
    
    def logistic(self, double loc=0.0, double scale=1.0, size=None):
        """Logistic distribution.
        
        logistic(loc=0.0, scale=1.0, size=None)
        """
        if scale <= 0.0:
            raise ValueError("scale <= 0.0")
        return cont2_array(self.internal_state, rk_logistic, size, loc, scale)

    def lognormal(self, double mean=0.0, double sigma=1.0, size=None):
        """Log-normal distribution.
        
        Note that the mean parameter is not the mean of this distribution, but 
        the underlying normal distribution.
        
            lognormal(mean, sigma) <=> exp(normal(mean, sigma))
        
        lognormal(mean=0.0, sigma=1.0, size=None)
        """
        if sigma <= 0.0:
            raise ValueError("sigma <= 0.0")
        return cont2_array(self.internal_state, rk_lognormal, size, mean, sigma)
    
    def rayleigh(self, double scale=1.0, size=None):
        """Rayleigh distribution.
        
        rayleigh(scale=1.0, size=None)
        """
        if scale <= 0.0:
            raise ValueError("scale <= 0.0")
        return cont1_array(self.internal_state, rk_rayleigh, size, scale)
    
    def wald(self, double mean, double scale, size=None):
        """Wald (inverse Gaussian) distribution.
        
        wald(mean, scale, size=None)
        """
        if mean <= 0.0:
            raise ValueError("mean <= 0.0")
        elif scale <= 0.0:
            raise ValueError("scale <= 0.0")
        return cont2_array(self.internal_state, rk_wald, size, mean, scale)

    def triangular(self, double left, double mode, double right, size=None):
        """Triangular distribution starting at left, peaking at mode, and 
        ending at right (left <= mode <= right).
        
        triangular(left, mode, right, size=None)
        """
        if left > mode:
            raise ValueError("left > mode")
        elif mode > right:
            raise ValueError("mode > right")
        elif left == right:
            raise ValueError("left == right")
        return cont3_array(self.internal_state, rk_triangular, size, left, 
            mode, right)

    # Complicated, discrete distributions:
    def binomial(self, long n, double p, size=None):
        """Binomial distribution of n trials and p probability of success.

        binomial(n, p, size=None) -> random values
        """
        if n <= 0:
            raise ValueError("n <= 0")
        elif p < 0:
            raise ValueError("p < 0")
        elif p > 1:
            raise ValueError("p > 1")
        return discnp_array(self.internal_state, rk_binomial, size, n, p)

    def negative_binomial(self, long n, double p, size=None):
        """Negative Binomial distribution.

        negative_binomial(n, p, size=None) -> random values
        """
        if n <= 0:
            raise ValueError("n <= 0")
        elif p < 0:
            raise ValueError("p < 0")
        elif p > 1:
            raise ValueError("p > 1")
        return discnp_array(self.internal_state, rk_negative_binomial, size, n,
            p)

    def poisson(self, double lam=1.0, size=None):
        """Poisson distribution.

        poisson(lam=1.0, size=None) -> random values
        """
        if lam <= 0:
            raise ValueError("lam <= 0")
        return discd_array(self.internal_state, rk_poisson, size, lam)

    def zipf(self, double a, size=None):
        """Zipf distribution.
        
        zipf(a, size=None)
        """
        if a <= 1.0:
            raise ValueError("a <= 1.0")
        return discd_array(self.internal_state, rk_zipf, size, a)
    
    def geometric(self, double p, size=None):
        """Geometric distribution with p being the probability of "success" on
        an individual trial.
        
        geometric(p, size=None)
        """
        if p < 0.0:
            raise ValueError("p < 0.0")
        elif p > 1.0:
            raise ValueError("p > 1.0")
        return discd_array(self.internal_state, rk_geometric, size, p)
    
    def hypergeometric(self, long ngood, long nbad, long nsample, size=None):
        """Hypergeometric distribution.
        
        Consider an urn with ngood "good" balls and nbad "bad" balls. If one 
        were to draw nsample balls from the urn without replacement, then 
        the hypergeometric distribution describes the distribution of "good" 
        balls in the sample.
        
        hypergeometric(ngood, nbad, nsample, size=None)        
        """
        if ngood < 1:
            raise ValueError("ngood < 1")
        elif nbad < 1:
            raise ValueError("nbad < 1")
        elif ngood + nbad < nsample:
            raise ValueError("ngood + nbad < nsample")
        elif nsample < 1:
            raise ValueError("nsample < 1")
        return discnmN_array(self.internal_state, rk_hypergeometric, size,
            ngood, nbad, nsample)

    def logseries(self, double p, size=None):
        """Logarithmic series distribution.
        
        logseries(p, size=None)
        """
        if p < 0:
            raise ValueError("p < 0")
        elif p > 1:
            raise ValueError("p > 1")
        return discd_array(self.internal_state, rk_logseries, size, p)

    # Multivariate distributions:
    def multivariate_normal(self, mean, cov, size=None):
        """Return an array containing multivariate normally distributed random numbers
        with specified mean and covariance.

        multivariate_normal(mean, cov) -> random values
        multivariate_normal(mean, cov, [m, n, ...]) -> random values

        mean must be a 1 dimensional array. cov must be a square two dimensional
        array with the same number of rows and columns as mean has elements.

        The first form returns a single 1-D array containing a multivariate
        normal.

        The second form returns an array of shape (m, n, ..., cov.shape[0]).
        In this case, output[i,j,...,:] is a 1-D array containing a multivariate
        normal.
        """
        # Check preconditions on arguments
        mean = _sp.array(mean)
        cov = _sp.array(cov)
        if size is None:
            shape = []
        else:
            shape = size
        if len(mean.shape) != 1:
               raise ArgumentError("mean must be 1 dimensional")
        if (len(cov.shape) != 2) or (cov.shape[0] != cov.shape[1]):
               raise ArgumentError("cov must be 2 dimensional and square")
        if mean.shape[0] != cov.shape[0]:
               raise ArgumentError("mean and cov must have same length")
        # Compute shape of output
        if isinstance(shape, int):
            shape = [shape]
        final_shape = list(shape[:])
        final_shape.append(mean.shape[0])
        # Create a matrix of independent standard normally distributed random
        # numbers. The matrix has rows with the same length as mean and as
        # many rows are necessary to form a matrix of shape final_shape.
        x = standard_normal(_sp.multiply.reduce(final_shape))
        x.shape = (_sp.multiply.reduce(final_shape[0:len(final_shape)-1]),
                   mean.shape[0])
        # Transform matrix of standard normals into matrix where each row
        # contains multivariate normals with the desired covariance.
        # Compute A such that matrixmultiply(transpose(A),A) == cov.
        # Then the matrix products of the rows of x and A has the desired
        # covariance. Note that sqrt(s)*v where (u,s,v) is the singular value
        # decomposition of cov is such an A.
        
        from scipy.corelinalg import svd
        # XXX: we really should be doing this by Cholesky decomposition
        (u,s,v) = svd(cov)
        x = _sp.matrixmultiply(x*_sp.sqrt(s),v)
        # The rows of x now have the correct covariance but mean 0. Add
        # mean to each row. Then each row will have mean mean.
        _sp.add(mean,x,x)
        x.shape = tuple(final_shape)
        return x

    def multinomial(self, long n, object pvals, size=None):
        """Multinomial distribution.
        
        multinomial(n, pvals, size=None) -> random values

        pvals is a sequence of probabilities that should sum to 1 (however, the
        last element is always assumed to account for the remaining probability
        as long as sum(pvals[:-1]) <= 1).
        """
        cdef long d
        cdef ndarray parr "arrayObject_parr", mnarr "arrayObject_mnarr"
        cdef double *pix
        cdef long *mnix
        cdef long i, j, dn
        cdef double Sum

        d = len(pvals)
        parr = <ndarray>PyArray_ContiguousFromObject(pvals, PyArray_DOUBLE, 1, 1)
        pix = <double*>parr.data

        if kahan_sum(pix, d-1) > 1.0:
            raise ValueError("sum(pvals) > 1.0")

        if size is None:
            shape = (d,)
        elif type(size) is int:
            shape = (size, d)
        else:
            shape = size + (d,)

        multin = _sp.zeros(shape, _sp.Int)
        mnarr = <ndarray>multin
        mnix = <long*>mnarr.data
        i = 0
        while i < PyArray_SIZE(mnarr):
            Sum = 1.0
            dn = n
            for j from 0 <= j < d-1:
                mnix[i+j] = rk_binomial(self.internal_state, dn, pix[j]/Sum)
                dn = dn - mnix[i+j]
                if dn <= 0:
                    break
                Sum = Sum - pix[j]
            if dn > 0:
                mnix[i+d-1] = dn

            i = i + d

        return multin

    # Shuffling and permutations:
    def shuffle(self, object x):
        """Modify a sequence in-place by shuffling its contents.
        
        shuffle(x)
        """
        cdef long i, j

        # adaptation of random.shuffle()
        i = len(x) - 1
        while i > 0:
            j = rk_interval(i, self.internal_state)
            x[i], x[j] = x[j], x[i]
            i = i - 1
                
    def permutation(self, object x):
        """Given an integer, return a shuffled sequence of integers >= 0 and 
        < x; given a sequence, return a shuffled array copy.

        permutation(x)
        """
        if type(x) is int:
            arr = _sp.arange(x)
        else:
            arr = _sp.array(x)
        self.shuffle(arr)
        return arr    

_rand = RandomState()
seed = _rand.seed
get_state = _rand.get_state
set_state = _rand.set_state
random_sample = _rand.random_sample
randint = _rand.randint
bytes = _rand.bytes
uniform = _rand.uniform
rand = _rand.rand
randn = _rand.randn
random_integers = _rand.random_integers
standard_normal = _rand.standard_normal
normal = _rand.normal
beta = _rand.beta
exponential = _rand.exponential
standard_exponential = _rand.standard_exponential
standard_gamma = _rand.standard_gamma
gamma = _rand.gamma
f = _rand.f
noncentral_f = _rand.noncentral_f
chisquare = _rand.chisquare
noncentral_chisquare = _rand.noncentral_chisquare
standard_cauchy = _rand.standard_cauchy
standard_t = _rand.standard_t
vonmises = _rand.vonmises
pareto = _rand.pareto
weibull = _rand.weibull
power = _rand.power
laplace = _rand.laplace
gumbel = _rand.gumbel
logistic = _rand.logistic
lognormal = _rand.lognormal
rayleigh = _rand.rayleigh
wald = _rand.wald
triangular = _rand.triangular

binomial = _rand.binomial
negative_binomial = _rand.negative_binomial
poisson = _rand.poisson
zipf = _rand.zipf
geometric = _rand.geometric
hypergeometric = _rand.hypergeometric
logseries = _rand.logseries

multivariate_normal = _rand.multivariate_normal
multinomial = _rand.multinomial

shuffle = _rand.shuffle
permutation = _rand.permutation



