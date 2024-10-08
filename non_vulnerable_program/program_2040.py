    import new
    def _set_function_name(func, name):
        func = new.function(func.func_code, func.func_globals,
                            name, func.func_defaults, func.func_closure)
        return func
else:
    def _set_function_name(func, name):
        func.__name__ = name
        return func

def deprecate(func, oldname, newname):
    import warnings
    def newfunc(*args,**kwds):
        warnings.warn("%s is deprecated, use %s" % (oldname, newname),
                      DeprecationWarning)
        return func(*args, **kwds)
    newfunc = _set_function_name(newfunc, oldname)
    doc = func.__doc__
    depdoc = '%s is DEPRECATED: use %s instead' % (oldname, newname,)
    if doc is None:
        doc = depdoc
    else:
        doc = '\n'.join([depdoc, doc])
    newfunc.__doc__ = doc
    try:
        d = func.__dict__
    except AttributeError:
        pass
    else:
        newfunc.__dict__.update(d)
    return newfunc

get_numpy_include = deprecate(get_include, 'get_numpy_include', 'get_include')


#--------------------------------------------
# Determine if two arrays can share memory
#--------------------------------------------

def byte_bounds(a):
    """(low, high) are pointers to the end-points of an array

    low is the first byte
    high is just *past* the last byte

    If the array is not single-segment, then it may not actually
    use every byte between these bounds.

    The array provided must conform to the Python-side of the array interface
    """
    ai = a.__array_interface__
    a_data = ai['data'][0]
    astrides = ai['strides']
    ashape = ai['shape']
    nd_a = len(ashape)
    bytes_a = int(ai['typestr'][2:])

    a_low = a_high = a_data
    if astrides is None: # contiguous case
        a_high += product(ashape, dtype=int)*bytes_a
    else:
        for shape, stride in zip(ashape, astrides):
            if stride < 0:
                a_low += (shape-1)*stride
            else:
                a_high += (shape-1)*stride
        a_high += bytes_a
    return a_low, a_high


def may_share_memory(a, b):
    """Determine if two arrays can share memory

    The memory-bounds of a and b are computed.  If they overlap then
    this function returns True.  Otherwise, it returns False.

    A return of True does not necessarily mean that the two arrays
    share any element.  It just means that they *might*.
    """
    a_low, a_high = byte_bounds(a)
    b_low, b_high = byte_bounds(b)
    if b_low >= a_high or a_low >= b_high:
        return False
    return True

#-----------------------------------------------------------------------------
# Function for output and information on the variables used.
#-----------------------------------------------------------------------------


def who(vardict=None):
    """Print the Numpy arrays in the given dictionary (or globals() if None).
    """
    if vardict is None:
        frame = sys._getframe().f_back
        vardict = frame.f_globals
    sta = []
    cache = {}
    for name in vardict.keys():
        if isinstance(vardict[name],ndarray):
            var = vardict[name]
            idv = id(var)
            if idv in cache.keys():
                namestr = name + " (%s)" % cache[idv]
                original=0
            else:
                cache[idv] = name
                namestr = name
                original=1
            shapestr = " x ".join(map(str, var.shape))
            bytestr = str(var.itemsize*product(var.shape))
            sta.append([namestr, shapestr, bytestr, var.dtype.name,
                        original])

    maxname = 0
    maxshape = 0
    maxbyte = 0
    totalbytes = 0
    for k in range(len(sta)):
        val = sta[k]
        if maxname < len(val[0]):
            maxname = len(val[0])
        if maxshape < len(val[1]):
            maxshape = len(val[1])
        if maxbyte < len(val[2]):
            maxbyte = len(val[2])
        if val[4]:
            totalbytes += int(val[2])

    if len(sta) > 0:
        sp1 = max(10,maxname)
        sp2 = max(10,maxshape)
        sp3 = max(10,maxbyte)
        prval = "Name %s Shape %s Bytes %s Type" % (sp1*' ', sp2*' ', sp3*' ')
        print prval + "\n" + "="*(len(prval)+5) + "\n"

    for k in range(len(sta)):
        val = sta[k]
        print "%s %s %s %s %s %s %s" % (val[0], ' '*(sp1-len(val[0])+4),
                                        val[1], ' '*(sp2-len(val[1])+5),
                                        val[2], ' '*(sp3-len(val[2])+5),
                                        val[3])
    print "\nUpper bound on total bytes  =       %d" % totalbytes
    return

#-----------------------------------------------------------------------------


# NOTE:  pydoc defines a help function which works simliarly to this
#  except it uses a pager to take over the screen.

# combine name and arguments and split to multiple lines of
#  width characters.  End lines on a comma and begin argument list
#  indented with the rest of the arguments.
def _split_line(name, arguments, width):
    firstwidth = len(name)
    k = firstwidth
    newstr = name
    sepstr = ", "
    arglist = arguments.split(sepstr)
    for argument in arglist:
        if k == firstwidth:
            addstr = ""
        else:
            addstr = sepstr
        k = k + len(argument) + len(addstr)
        if k > width:
            k = firstwidth + 1 + len(argument)
            newstr = newstr + ",\n" + " "*(firstwidth+2) + argument
        else:
            newstr = newstr + addstr + argument
    return newstr

_namedict = None
_dictlist = None

# Traverse all module directories underneath globals
# to see if something is defined
def _makenamedict(module='numpy'):
    module = __import__(module, globals(), locals(), [])
    thedict = {module.__name__:module.__dict__}
    dictlist = [module.__name__]
    totraverse = [module.__dict__]
    while 1:
        if len(totraverse) == 0:
            break
        thisdict = totraverse.pop(0)
        for x in thisdict.keys():
            if isinstance(thisdict[x],types.ModuleType):
                modname = thisdict[x].__name__
                if modname not in dictlist:
                    moddict = thisdict[x].__dict__
                    dictlist.append(modname)
                    totraverse.append(moddict)
                    thedict[modname] = moddict
    return thedict, dictlist

def info(object=None,maxwidth=76,output=sys.stdout,toplevel='numpy'):
    """Get help information for a function, class, or module.

       Example:
          >>> from numpy import *
          >>> info(polyval) # doctest: +SKIP

          polyval(p, x)

            Evaluate the polymnomial p at x.

            Description:
                If p is of length N, this function returns the value:
                p[0]*(x**N-1) + p[1]*(x**N-2) + ... + p[N-2]*x + p[N-1]
    """
    global _namedict, _dictlist
    import pydoc

    if hasattr(object,'_ppimport_importer') or \
       hasattr(object, '_ppimport_module'):
        object = object._ppimport_module
    elif hasattr(object, '_ppimport_attr'):
        object = object._ppimport_attr

    if object is None:
        info(info)
    elif isinstance(object, ndarray):
        import numpy.numarray as nn
        nn.info(object, output=output, numpy=1)
    elif isinstance(object, str):
        if _namedict is None:
            _namedict, _dictlist = _makenamedict(toplevel)
        numfound = 0
        objlist = []
        for namestr in _dictlist:
            try:
                obj = _namedict[namestr][object]
                if id(obj) in objlist:
                    print >> output, "\n     *** Repeat reference found in %s *** " % namestr
                else:
                    objlist.append(id(obj))
                    print >> output, "     *** Found in %s ***" % namestr
                    info(obj)
                    print >> output, "-"*maxwidth
                numfound += 1
            except KeyError:
                pass
        if numfound == 0:
            print >> output, "Help for %s not found." % object
        else:
            print >> output, "\n     *** Total of %d references found. ***" % numfound

    elif inspect.isfunction(object):
        name = object.func_name
        arguments = inspect.formatargspec(*inspect.getargspec(object))

        if len(name+arguments) > maxwidth:
            argstr = _split_line(name, arguments, maxwidth)
        else:
            argstr = name + arguments

        print >> output, " " + argstr + "\n"
        print >> output, inspect.getdoc(object)

    elif inspect.isclass(object):
        name = object.__name__
        arguments = "()"
        try:
            if hasattr(object, '__init__'):
                arguments = inspect.formatargspec(*inspect.getargspec(object.__init__.im_func))
                arglist = arguments.split(', ')
                if len(arglist) > 1:
                    arglist[1] = "("+arglist[1]
                    arguments = ", ".join(arglist[1:])
        except:
            pass

        if len(name+arguments) > maxwidth:
            argstr = _split_line(name, arguments, maxwidth)
        else:
            argstr = name + arguments

        print >> output, " " + argstr + "\n"
        doc1 = inspect.getdoc(object)
        if doc1 is None:
            if hasattr(object,'__init__'):
                print >> output, inspect.getdoc(object.__init__)
        else:
            print >> output, inspect.getdoc(object)

        methods = pydoc.allmethods(object)
        if methods != []:
            print >> output, "\n\nMethods:\n"
            for meth in methods:
                if meth[0] == '_':
                    continue
                thisobj = getattr(object, meth, None)
                if thisobj is not None:
                    methstr, other = pydoc.splitdoc(inspect.getdoc(thisobj) or "None")
                print >> output, "  %s  --  %s" % (meth, methstr)

    elif type(object) is types.InstanceType: ## check for __call__ method
        print >> output, "Instance of class: ", object.__class__.__name__
        print >> output
        if hasattr(object, '__call__'):
            arguments = inspect.formatargspec(*inspect.getargspec(object.__call__.im_func))
            arglist = arguments.split(', ')
            if len(arglist) > 1:
                arglist[1] = "("+arglist[1]
                arguments = ", ".join(arglist[1:])
            else:
                arguments = "()"

            if hasattr(object,'name'):
                name = "%s" % object.name
            else:
                name = "<name>"
            if len(name+arguments) > maxwidth:
                argstr = _split_line(name, arguments, maxwidth)
            else:
                argstr = name + arguments

            print >> output, " " + argstr + "\n"
            doc = inspect.getdoc(object.__call__)
            if doc is not None:
                print >> output, inspect.getdoc(object.__call__)
            print >> output, inspect.getdoc(object)

        else:
            print >> output, inspect.getdoc(object)

    elif inspect.ismethod(object):
        name = object.__name__
        arguments = inspect.formatargspec(*inspect.getargspec(object.im_func))
        arglist = arguments.split(', ')
        if len(arglist) > 1:
            arglist[1] = "("+arglist[1]
            arguments = ", ".join(arglist[1:])
        else:
            arguments = "()"

        if len(name+arguments) > maxwidth:
            argstr = _split_line(name, arguments, maxwidth)
        else:
            argstr = name + arguments

        print >> output, " " + argstr + "\n"
        print >> output, inspect.getdoc(object)

    elif hasattr(object, '__doc__'):
        print >> output, inspect.getdoc(object)


def source(object, output=sys.stdout):
    """Write source for this object to output.
    """
    try:
        print >> output,  "In file: %s\n" % inspect.getsourcefile(object)
        print >> output,  inspect.getsource(object)
    except:
        print >> output,  "Not available for this object."


""" Define a simple format for saving numpy arrays to disk with the full
information about them.

Format Version 1.0
------------------

The first 6 bytes are a magic string: exactly "\\x93NUMPY".

The next 1 byte is an unsigned byte: the major version number of the file
format, e.g. \\x01.

The next 1 byte is an unsigned byte: the minor version number of the file
format, e.g. \\x00. Note: the version of the file format is not tied to the
version of the numpy package.

The next 2 bytes form an unsigned short int: the length of the header data
HEADER_LEN.

The next HEADER_LEN bytes form the header data describing the array's format. It
is an ASCII string which contains a Python literal expression of a dictionary.
It is terminated by a newline ('\\n') and padded with spaces ('\\x20') to make
the total length of the magic string + 4 + HEADER_LEN be evenly divisible by 16
for alignment purposes.

The dictionary contains three keys:

    "descr" : dtype.descr
        An object that can be passed as an argument to the numpy.dtype()
        constructor to create the array's dtype.
    "fortran_order" : bool
        Whether the array data is Fortran-contiguous or not. Since
        Fortran-contiguous arrays are a common form of non-C-contiguity, we
        allow them to be written directly to disk for efficiency.
    "shape" : tuple of int
        The shape of the array.

For repeatability and readability, this dictionary is formatted using
pprint.pformat() so the keys are in alphabetic order.

Following the header comes the array data. If the dtype contains Python objects
(i.e. dtype.hasobject is True), then the data is a Python pickle of the array.
Otherwise the data is the contiguous (either C- or Fortran-, depending on
fortran_order) bytes of the array. Consumers can figure out the number of bytes
by multiplying the number of elements given by the shape (noting that shape=()
means there is 1 element) by dtype.itemsize.
"""

