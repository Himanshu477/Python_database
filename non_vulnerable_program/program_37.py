import base_info

blitz_support_code =  \
"""

// This should be declared only if they are used by some function
// to keep from generating needless warnings. for now, we'll always
// declare them.

int _beg = blitz::fromStart;
int _end = blitz::toEnd;
blitz::Range _all = blitz::Range::all();

// simple meta-program templates to specify python typecodes
// for each of the numeric types.
template<class T>
class py_type{public: enum {code = 100};};
class py_type<char>{public: enum {code = PyArray_CHAR};};
class py_type<unsigned char>{public: enum { code = PyArray_UBYTE};};
class py_type<short>{public:  enum { code = PyArray_SHORT};};
class py_type<int>{public: enum { code = PyArray_LONG};};// PyArray_INT has troubles;
class py_type<long>{public: enum { code = PyArray_LONG};};
class py_type<float>{public: enum { code = PyArray_FLOAT};};
class py_type<double>{public: enum { code = PyArray_DOUBLE};};
class py_type<complex<float> >{public: enum { code = PyArray_CFLOAT};};
class py_type<complex<double> >{public: enum { code = PyArray_CDOUBLE};};

template<class T, int N>
static blitz::Array<T,N> py_to_blitz(PyObject* py_obj,char* name)
{

    PyArrayObject* arr_obj = py_to_numpy(py_obj,name);
    numpy_check_size(arr_obj,N,name);
    numpy_check_type(arr_obj,py_type<T>::code,name);
    
    blitz::TinyVector<int,N> shape(0);
    blitz::TinyVector<int,N> strides(0);
    int stride_acc = 1;
    //for (int i = N-1; i >=0; i--)
    for (int i = 0; i < N; i++)
    {
        shape[i] = arr_obj->dimensions[i];
        strides[i] = arr_obj->strides[i]/sizeof(T);
    }
    //return blitz::Array<T,N>((T*) arr_obj->data,shape,        
    return blitz::Array<T,N>((T*) arr_obj->data,shape,strides,
                             blitz::neverDeleteData);
}
"""


