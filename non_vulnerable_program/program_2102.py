    from numpy.distutils.core import setup
    setup(configuration=configuration)


""" Define a simple format for saving numpy arrays to disk with the full
information about them.

WARNING: THE FORMAT IS CURRENTLY UNSTABLE. DO NOT STORE CRITICAL DATA WITH IT.
         While this code is in an SVN branch, the format may change without
         notice, without backwards compatibility, and without changing the
         format's version number. When the code moves into the trunk the format
         will be stabilized, the version number will increment as changes occur,
         and backwards compatibility with older versions will be maintained.

Format Version 1.0
------------------

The first 6 bytes are a magic string: exactly "\\x93NUMPY".

The next 1 byte is an unsigned byte: the major version number of the file
format, e.g. \\x01.

The next 1 byte is an unsigned byte: the minor version number of the file
format, e.g. \\x00. Note: the version of the file format is not tied to the
version of the numpy package.

The next 2 bytes form a little-endian unsigned short int: the length of the
header data HEADER_LEN.

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

