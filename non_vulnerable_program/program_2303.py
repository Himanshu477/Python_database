    import image
    out = image.filter(in)


Conclusion
----------

There are several disadvantages of using Pyrex:

1. The syntax for Pyrex can get a bit bulky, and it can be confusing at
   first to understand what kind of objects you are getting and how to
   interface them with C-like constructs.

2. Inappropriate Pyrex syntax or incorrect calls to C-code or type-
   mismatches can result in failures such as

    1. Pyrex failing to generate the extension module source code,

    2. Compiler failure while generating the extension module binary due to
       incorrect C syntax,

    3. Python failure when trying to use the module.


3. It is easy to lose a clean separation between Python and C which makes
   re-using your C-code for other non-Python-related projects more
   difficult.

4. Multi-dimensional arrays are "bulky" to index (appropriate macros
   may be able to fix this).

5. The C-code generated by Prex is hard to read and modify (and typically
   compiles with annoying but harmless warnings).

Writing a good Pyrex extension module still takes a bit of effort
because not only does it require (a little) familiarity with C, but
also with Pyrex's brand of Python-mixed-with C. One big advantage of
Pyrex-generated extension modules is that they are easy to distribute
using distutils. In summary, Pyrex is a very capable tool for either
gluing C-code or generating an extension module quickly and should not
be over-looked. It is especially useful for people that can't or won't
write C-code or Fortran code. But, if you are already able to write
simple subroutines in C or Fortran, then I would use one of the other
approaches such as f2py (for Fortran), ctypes (for C shared-
libraries), or weave (for inline C-code).

.. index::
   single: pyrex




ctypes
======

Ctypes is a python extension module (downloaded separately for Python
<2.5 and included with Python 2.5) that allows you to call an
arbitrary function in a shared library directly from Python. This
approach allows you to interface with C-code directly from Python.
This opens up an enormous number of libraries for use from Python. The
drawback, however, is that coding mistakes can lead to ugly program
crashes very easily (just as can happen in C) because there is little
type or bounds checking done on the parameters. This is especially
true when array data is passed in as a pointer to a raw memory
location. The responsibility is then on you that the subroutine will
not access memory outside the actual array area. But, if you don't
mind living a little dangerously ctypes can be an effective tool for
quickly taking advantage of a large shared library (or writing
extended functionality in your own shared library).

.. index::
   single: ctypes

Because the ctypes approach exposes a raw interface to the compiled
code it is not always tolerant of user mistakes. Robust use of the
ctypes module typically involves an additional layer of Python code in
order to check the data types and array bounds of objects passed to
the underlying subroutine. This additional layer of checking (not to
mention the conversion from ctypes objects to C-data-types that ctypes
itself performs), will make the interface slower than a hand-written
extension-module interface. However, this overhead should be neglible
if the C-routine being called is doing any significant amount of work.
If you are a great Python programmer with weak C-skills, ctypes is an
easy way to write a useful interface to a (shared) library of compiled
code.

To use c-types you must

1. Have a shared library.

2. Load the shared library.

3. Convert the python objects to ctypes-understood arguments.

4. Call the function from the library with the ctypes arguments.


Having a shared library
-----------------------

There are several requirements for a shared library that can be used
with c-types that are platform specific. This guide assumes you have
some familiarity with making a shared library on your system (or
simply have a shared library available to you). Items to remember are:

- A shared library must be compiled in a special way ( *e.g.* using
  the -shared flag with gcc).

- On some platforms (*e.g.* Windows) , a shared library requires a
  .def file that specifies the functions to be exported. For example a
  mylib.def file might contain.

  ::

      LIBRARY mylib.dll
      EXPORTS
      cool_function1
      cool_function2

  Alternatively, you may be able to use the storage-class specifier
  __declspec(dllexport) in the C-definition of the function to avoid the
  need for this .def file.

There is no standard way in Python distutils to create a standard
shared library (an extension module is a "special" shared library
Python understands) in a cross-platform manner. Thus, a big
disadvantage of ctypes at the time of writing this book is that it is
difficult to distribute in a cross-platform manner a Python extension
that uses c-types and includes your own code which should be compiled
as a shared library on the users system.


Loading the shared library
--------------------------

A simple, but robust way to load the shared library is to get the
absolute path name and load it using the cdll object of ctypes.:

.. code-block:: python

    lib = ctypes.cdll[<full_path_name>]

However, on Windows accessing an attribute of the cdll method will
load the first DLL by that name found in the current directory or on
the PATH. Loading the absolute path name requires a little finesse for
cross-platform work since the extension of shared libraries varies.
There is a ``ctypes.util.find_library`` utility available that can
simplify the process of finding the library to load but it is not
foolproof. Complicating matters, different platforms have different
default extensions used by shared libraries (e.g. .dll -- Windows, .so
-- Linux, .dylib -- Mac OS X). This must also be taken into account if
you are using c-types to wrap code that needs to work on several
platforms.

NumPy provides a convenience function called
:func:`ctypeslib.load_library` (name, path). This function takes the name
of the shared library (including any prefix like 'lib' but excluding
the extension) and a path where the shared library can be located. It
returns a ctypes library object or raises an OSError if the library
cannot be found or raises an ImportError if the ctypes module is not
available. (Windows users: the ctypes library object loaded using
:func:`load_library` is always loaded assuming cdecl calling convention.
See the ctypes documentation under ctypes.windll and/or ctypes.oledll
for ways to load libraries under other calling conventions).

The functions in the shared library are available as attributes of the
ctypes library object (returned from :func:`ctypeslib.load_library`) or
as items using ``lib['func_name']`` syntax. The latter method for
retrieving a function name is particularly useful if the function name
contains characters that are not allowable in Python variable names.


Converting arguments
--------------------

Python ints/longs, strings, and unicode objects are automatically
converted as needed to equivalent c-types arguments The None object is
also converted automatically to a NULL pointer. All other Python
objects must be converted to ctypes-specific types. There are two ways
around this restriction that allow c-types to integrate with other
objects.

1. Don't set the argtypes attribute of the function object and define an
   :obj:`_as_parameter_` method for the object you want to pass in. The
   :obj:`_as_parameter_` method must return a Python int which will be passed
   directly to the function.

2. Set the argtypes attribute to a list whose entries contain objects
   with a classmethod named from_param that knows how to convert your
   object to an object that ctypes can understand (an int/long, string,
   unicode, or object with the :obj:`_as_parameter_` attribute).

NumPy uses both methods with a preference for the second method
because it can be safer. The ctypes attribute of the ndarray returns
an object that has an _as_parameter\_ attribute which returns an
integer representing the address of the ndarray to which it is
associated. As a result, one can pass this ctypes attribute object
directly to a function expecting a pointer to the data in your
ndarray. The caller must be sure that the ndarray object is of the
correct type, shape, and has the correct flags set or risk nasty
crashes if the data-pointer to inappropriate arrays are passsed in.

To implement the second method, NumPy provides the class-factory
function :func:`ndpointer` in the :mod:`ctypeslib` module. This
class-factory function produces an appropriate class that can be
placed in an argtypes attribute entry of a ctypes function. The class
will contain a from_param method which ctypes will use to convert any
ndarray passed in to the function to a ctypes-recognized object. In
the process, the conversion will perform checking on any properties of
the ndarray that were specified by the user in the call to :func:`ndpointer`.
Aspects of the ndarray that can be checked include the data-type, the
number-of-dimensions, the shape, and/or the state of the flags on any
array passed. The return value of the from_param method is the ctypes
attribute of the array which (because it contains the _as_parameter\_
attribute pointing to the array data area) can be used by ctypes
directly.

The ctypes attribute of an ndarray is also endowed with additional
attributes that may be convenient when passing additional information
about the array into a ctypes function. The attributes **data**,
**shape**, and **strides** can provide c-types compatible types
corresponding to the data-area, the shape, and the strides of the
array. The data attribute reutrns a ``c_void_p`` representing a
pointer to the data area. The shape and strides attributes each return
an array of ctypes integers (or None representing a NULL pointer, if a
0-d array). The base ctype of the array is a ctype integer of the same
size as a pointer on the platform. There are also methods
data_as({ctype}), shape_as(<base ctype>), and strides_as(<base
ctype>). These return the data as a ctype object of your choice and
the shape/strides arrays using an underlying base type of your choice.
For convenience, the **ctypeslib** module also contains **c_intp** as
a ctypes integer data-type whose size is the same as the size of
``c_void_p`` on the platform (it's value is None if ctypes is not
installed).


Calling the function
--------------------

The function is accessed as an attribute of or an item from the loaded
shared-library. Thus, if "./mylib.so" has a function named
"cool_function1" , I could access this function either as:

.. code-block:: python

    lib = numpy.ctypeslib.load_library('mylib','.')
    func1 = lib.cool_function1 # or equivalently
    func1 = lib['cool_function1']

In ctypes, the return-value of a function is set to be 'int' by
default. This behavior can be changed by setting the restype attribute
of the function. Use None for the restype if the function has no
return value ('void'):

.. code-block:: python

    func1.restype = None

As previously discussed, you can also set the argtypes attribute of
the function in order to have ctypes check the types of the input
arguments when the function is called. Use the :func:`ndpointer` factory
function to generate a ready-made class for data-type, shape, and
flags checking on your new function. The :func:`ndpointer` function has the
signature

.. function:: ndpointer(dtype=None, ndim=None, shape=None, flags=None)

    Keyword arguments with the value ``None`` are not checked.
    Specifying a keyword enforces checking of that aspect of the
    ndarray on conversion to a ctypes-compatible object. The dtype
    keyword can be any object understood as a data-type object. The
    ndim keyword should be an integer, and the shape keyword should be
    an integer or a sequence of integers. The flags keyword specifies
    the minimal flags that are required on any array passed in. This
    can be specified as a string of comma separated requirements, an
    integer indicating the requirement bits OR'd together, or a flags
    object returned from the flags attribute of an array with the
    necessary requirements.

Using an ndpointer class in the argtypes method can make it
significantly safer to call a C-function using ctypes and the data-
area of an ndarray. You may still want to wrap the function in an
additional Python wrapper to make it user-friendly (hiding some
obvious arguments and making some arguments output arguments). In this
process, the **requires** function in NumPy may be useful to return the right kind of array from
a given input.


Complete example
----------------

In this example, I will show how the addition function and the filter
function implemented previously using the other approaches can be
implemented using ctypes. First, the C-code which implements the
algorithms contains the functions zadd, dadd, sadd, cadd, and
dfilter2d. The zadd function is:

.. code-block:: c

    /* Add arrays of contiguous data */
    typedef struct {double real; double imag;} cdouble;
    typedef struct {float real; float imag;} cfloat;
    void zadd(cdouble *a, cdouble *b, cdouble *c, long n)
    {
        while (n--) {
            c->real = a->real + b->real;
            c->imag = a->imag + b->imag;
            a++; b++; c++;
        }
    }

with similar code for cadd, dadd, and sadd that handles complex float,
double, and float data-types, respectively:

.. code-block:: c

    void cadd(cfloat *a, cfloat *b, cfloat *c, long n)
    {
            while (n--) {
                    c->real = a->real + b->real;
                    c->imag = a->imag + b->imag;
                    a++; b++; c++;
            }
    }
    void dadd(double *a, double *b, double *c, long n)
    {
            while (n--) {
                    *c++ = *a++ + *b++;
            }
    }
    void sadd(float *a, float *b, float *c, long n)
    {
            while (n--) {
                    *c++ = *a++ + *b++;
            }
    }

The code.c file also contains the function dfilter2d:

.. code-block:: c

    /* Assumes b is contiguous and
       a has strides that are multiples of sizeof(double)
    */
    void
    dfilter2d(double *a, double *b, int *astrides, int *dims)
    {
        int i, j, M, N, S0, S1;
        int r, c, rm1, rp1, cp1, cm1;

        M = dims[0]; N = dims[1];
        S0 = astrides[0]/sizeof(double);
        S1=astrides[1]/sizeof(double);
        for (i=1; i<M-1; i++) {
            r = i*S0; rp1 = r+S0; rm1 = r-S0;
            for (j=1; j<N-1; j++) {
                c = j*S1; cp1 = j+S1; cm1 = j-S1;
                b[i*N+j] = a[r+c] +                 \
                    (a[rp1+c] + a[rm1+c] +          \
                     a[r+cp1] + a[r+cm1])*0.5 +     \
                    (a[rp1+cp1] + a[rp1+cm1] +      \
                     a[rm1+cp1] + a[rm1+cp1])*0.25;
            }
        }
    }

A possible advantage this code has over the Fortran-equivalent code is
that it takes arbitrarily strided (i.e. non-contiguous arrays) and may
also run faster depending on the optimization capability of your
compiler. But, it is a obviously more complicated than the simple code
in filter.f. This code must be compiled into a shared library. On my
Linux system this is accomplished using::

    gcc -o code.so -shared code.c

Which creates a shared_library named code.so in the current directory.
On Windows don't forget to either add __declspec(dllexport) in front
of void on the line preceeding each function definition, or write a
code.def file that lists the names of the functions to be exported.

A suitable Python interface to this shared library should be
constructed. To do this create a file named interface.py with the
following lines at the top:

.. code-block:: python

    __all__ = ['add', 'filter2d']

