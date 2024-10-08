import nose

class NoseTester(object):
    """ Nose test runner.

    Usage: NoseTester(<package>).test()

    <package> is package path or module Default for package is None. A
    value of None finds calling module path.

    Typical call is from module __init__, and corresponds to this:

    >>> test = NoseTester().test

    In practice, because nose may not be importable, the __init__
    files actually have:

    >>> from scipy.testing.pkgtester import Tester
    >>> test = Tester().test

    The pkgtester module checks for the presence of nose on the path,
    returning this class if nose is present, and a null class
    otherwise.
    """

    def __init__(self, package=None):
        ''' Test class init

        Parameters
        ----------
        package : string or module
            If string, gives full path to package
            If None, extract calling module path
            Default is None
        '''
        if package is None:
            f = sys._getframe(1)
            package = f.f_locals.get('__file__', None)
            assert package is not None
            package = os.path.dirname(package)
        elif isinstance(package, type(os)):
            package = os.path.dirname(package.__file__)
        self.package_path = package

    def _add_doc(testtype):
        ''' Decorator to add docstring to functions using test labels

        Parameters
        ----------
        testtype : string
            Type of test for function docstring
        '''
        def docit(func):
            test_header = \
        '''Parameters
        ----------
        label : {'fast', 'full', '', attribute identifer}
            Identifies %(testtype)s to run.  This can be a string to pass to
            the nosetests executable with the'-A' option, or one of
            several special values.
            Special values are:
            'fast' - the default - which corresponds to
                nosetests -A option of
                'not slow'.
            'full' - fast (as above) and slow %(testtype)s as in
                no -A option to nosetests - same as ''
            None or '' - run all %(testtype)ss
            attribute_identifier - string passed directly to
                nosetests as '-A'
        verbose : integer
            verbosity value for test outputs, 1-10
        extra_argv : list
            List with any extra args to pass to nosetests''' \
            % {'testtype': testtype}
            func.__doc__ = func.__doc__ % {
                'test_header': test_header}
            return func
        return docit

    @_add_doc('(testtype)')
    def _test_argv(self, label, verbose, extra_argv):
        ''' Generate argv for nosetest command

        %(test_header)s
        '''
        argv = [__file__, self.package_path, '-s']
        if label and label != 'full':
            if not isinstance(label, basestring):
                raise TypeError, 'Selection label should be a string'
            if label == 'fast':
                label = 'not slow'
            argv += ['-A', label]
        argv += ['--verbosity', str(verbose)]
        if extra_argv:
            argv += extra_argv
        return argv
    
    @_add_doc('test')
    def test(self, label='fast', verbose=1, extra_argv=None, doctests=False,
             coverage=False):
        ''' Run tests for module using nose

        %(test_header)s
        doctests : boolean
            If True, run doctests in module, default False
        '''
        argv = self._test_argv(label, verbose, extra_argv)
        if doctests:
            argv+=['--with-doctest','--doctest-tests']

        if coverage:
            argv+=['--cover-package=numpy','--with-coverage',
                   '--cover-tests','--cover-inclusive','--cover-erase']

        # bypass these samples under distutils
        argv += ['--exclude','f2py_ext']
        argv += ['--exclude','f2py_f90_ext']
        argv += ['--exclude','gen_ext']
        argv += ['--exclude','pyrex_ext']
        argv += ['--exclude','swig_ext']

        nose.run(argv=argv)

    @_add_doc('benchmark')
    def bench(self, label='fast', verbose=1, extra_argv=None):
        ''' Run benchmarks for module using nose

        %(test_header)s'''
        argv = self._test_argv(label, verbose, extra_argv)
        argv += ['--match', r'(?:^|[\\b_\\.%s-])[Bb]ench' % os.sep]
        nose.run(argv=argv)


''' Null tester to signal nose tests disabled

Merely returns error reporting lack of nose package or version number
below requirements.

See pkgtester, nosetester modules

'''

class NullTester(object):
    def test(self, labels=None, *args, **kwargs):
        raise ImportError, \
              'Need nose >=0.10 for tests - see %s' % \
              'http://somethingaboutorange.com/mrl/projects/nose'
    bench = test


''' Define test function for scipy package

Module tests for presence of useful version of nose.  If present
returns NoseTester, otherwise returns a placeholder test routine
reporting lack of nose and inability to run tests.  Typical use is in
module __init__:

