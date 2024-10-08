import numpy as np
from numpy.testing import TestCase, run_module_suite, assert_raises, assert_equal, assert_
import sys

class TestIndexErrors(TestCase):
    '''Tests to exercise indexerrors not covered by other tests.'''

    def test_arraytypes_fasttake(self):
        'take from a 0-length dimension'
        x = np.empty((2, 3, 0, 4))
        assert_raises(IndexError, x.take, [0], axis=2)
        assert_raises(IndexError, x.take, [1], axis=2)

    def test_maskna_take_1D(self):
        # Check exception taking from masked array
        a = np.array([1, np.NA, 2, np.NA], maskna=True)
        assert_raises(IndexError, a.take, [6])
        a = np.array(np.NA, maskna=True)
        assert_raises(IndexError, a.take, [6])

        # Check exception taking from masked 0-d array
        d = np.empty((5, 0), maskna=True)
        assert_raises(IndexError, d.take, [1], axis=1)
        assert_raises(IndexError, d.take, [0], axis=1)
        assert_raises(IndexError, d.take, [0])

    def test_take_from_object(self):
        # Check exception taking from object array
        d = np.zeros(5, dtype=object)
        assert_raises(IndexError, d.take, [6])

        # Check exception taking from 0-d array
        d = np.zeros((5, 0), dtype=object)
        assert_raises(IndexError, d.take, [1], axis=1)
        assert_raises(IndexError, d.take, [0], axis=1)
        assert_raises(IndexError, d.take, [0])

    def test_multiindex_exceptions(self):
        a = np.empty(5, dtype=object)
        assert_raises(IndexError, a.item, 20)
        a = np.empty((5, 0), dtype=object)
        assert_raises(IndexError, a.item, (0, 0))
        a = np.empty(5, dtype=object, maskna=True)
        assert_raises(IndexError, a.item, 20)
        a = np.empty((5, 0), dtype=object, maskna=True)
        assert_raises(IndexError, a.item, (0, 0))

        a = np.empty(5, dtype=object)
        assert_raises(IndexError, a.itemset, 20, 0)
        a = np.empty((5, 0), dtype=object)
        assert_raises(IndexError, a.itemset, (0, 0), 0)
        a = np.empty(5, dtype=object, maskna=True)
        assert_raises(IndexError, a.itemset, 20, 0)
        a = np.empty((5, 0), dtype=object, maskna=True)
        assert_raises(IndexError, a.itemset, (0, 0), 0)

    def test_put_exceptions(self):
        a = np.zeros((5, 5))
        assert_raises(IndexError, a.put, 100, 0)
        a = np.zeros((5, 5), dtype=object)
        assert_raises(IndexError, a.put, 100, 0)
        a = np.zeros((5, 5, 0))
        assert_raises(IndexError, a.put, 100, 0)
        a = np.zeros((5, 5, 0), dtype=object)
        assert_raises(IndexError, a.put, 100, 0)

    def test_iterators_exceptions(self):
        "cases in iterators.c"
        def assign(obj, ind, val):
            obj[ind] = val

        a = np.zeros([1,2,3])
        assert_raises(IndexError, lambda: a[0,5,None,2])
        assert_raises(IndexError, lambda: a[0,5,0,2])
        assert_raises(IndexError, lambda: assign(a, (0,5,None,2), 1))
        assert_raises(IndexError, lambda: assign(a, (0,5,0,2),  1))

        a = np.zeros([1,0,3])
        assert_raises(IndexError, lambda: a[0,0,None,2])
        assert_raises(IndexError, lambda: assign(a, (0,0,None,2), 1))

        a = np.zeros([1,2,3])
        assert_raises(IndexError, lambda: a.flat[10])
        assert_raises(IndexError, lambda: assign(a.flat, 10, 5))
        a = np.zeros([1,0,3])
        assert_raises(IndexError, lambda: a.flat[10])
        assert_raises(IndexError, lambda: assign(a.flat, 10, 5))

        a = np.zeros([1,2,3])
        assert_raises(IndexError, lambda: a.flat[np.array(10)])
        assert_raises(IndexError, lambda: assign(a.flat, np.array(10), 5))
        a = np.zeros([1,0,3])
        assert_raises(IndexError, lambda: a.flat[np.array(10)])
        assert_raises(IndexError, lambda: assign(a.flat, np.array(10), 5))

        a = np.zeros([1,2,3])
        assert_raises(IndexError, lambda: a.flat[np.array([10])])
        assert_raises(IndexError, lambda: assign(a.flat, np.array([10]), 5))
        a = np.zeros([1,0,3])
        assert_raises(IndexError, lambda: a.flat[np.array([10])])
        assert_raises(IndexError, lambda: assign(a.flat, np.array([10]), 5))

    def test_mapping(self):
        "cases from mapping.c"

        def assign(obj, ind, val):
            obj[ind] = val

        a = np.zeros((0, 10))
        assert_raises(IndexError, lambda: a[12])

        a = np.zeros((3,5))
        assert_raises(IndexError, lambda: a[(10, 20)])
        assert_raises(IndexError, lambda: assign(a, (10, 20), 1))
        a = np.zeros((3,0))
        assert_raises(IndexError, lambda: a[(1, 0)])
        assert_raises(IndexError, lambda: assign(a, (1, 0), 1))

        a = np.zeros((3,5), maskna=True)
        assert_raises(IndexError, lambda: a[(10, 20)])
        assert_raises(IndexError, lambda: assign(a, (10, 20), 1))
        a = np.zeros((3,0), maskna=True)
        assert_raises(IndexError, lambda: a[(1, 0)])
        assert_raises(IndexError, lambda: assign(a, (1, 0), 1))

        a = np.zeros((10,))
        assert_raises(IndexError, lambda: assign(a, 10, 1))
        a = np.zeros((0,))
        assert_raises(IndexError, lambda: assign(a, 10, 1))

        a = np.zeros((3,5))
        assert_raises(IndexError, lambda: a[(1, [1, 20])])
        assert_raises(IndexError, lambda: assign(a, (1, [1, 20]), 1))
        a = np.zeros((3,0))
        assert_raises(IndexError, lambda: a[(1, [0, 1])])
        assert_raises(IndexError, lambda: assign(a, (1, [0, 1]), 1))

    def test_methods(self):
        "cases from methods.c"

        a = np.zeros((3, 3))
        assert_raises(IndexError, lambda: a.item(100))
        assert_raises(IndexError, lambda: a.itemset(100, 1))
        a = np.zeros((0, 3))
        assert_raises(IndexError, lambda: a.item(100))
        assert_raises(IndexError, lambda: a.itemset(100, 1))

if __name__ == "__main__":
    run_module_suite()


def show():
    pass


# A cython wrapper for using python functions as callbacks for
# PyDataMem_SetEventHook.

cimport numpy as np

cdef extern from "Python.h":
    object PyLong_FromVoidPtr(void *)
    void *PyLong_AsVoidPtr(object)

ctypedef void PyDataMem_EventHookFunc(void *inp, void *outp, size_t size,
                                      void *user_data)
cdef extern from "numpy/arrayobject.h":
    PyDataMem_EventHookFunc * \
        PyDataMem_SetEventHook(PyDataMem_EventHookFunc *newhook,
                               void *user_data, void **old_data)

np.import_array()

cdef void pyhook(void *old, void *new, size_t size, void *user_data):
    cdef object pyfunc = <object> user_data
    pyfunc(PyLong_FromVoidPtr(old),
           PyLong_FromVoidPtr(new),
           size)

class NumpyAllocHook(object):
    def __init__(self, callback):
        self.callback = callback

    def __enter__(self):
        cdef void *old_hook, *old_data
        old_hook = <void *> \
            PyDataMem_SetEventHook(<PyDataMem_EventHookFunc *> pyhook,
                                    <void *> self.callback,
                                    <void **> &old_data)
        self.old_hook = PyLong_FromVoidPtr(old_hook)
        self.old_data = PyLong_FromVoidPtr(old_data)

    def __exit__(self):
        PyDataMem_SetEventHook(<PyDataMem_EventHookFunc *> \
                                    PyLong_AsVoidPtr(self.old_hook),
                                <void *> PyLong_AsVoidPtr(self.old_data),
                                <void **> 0)


