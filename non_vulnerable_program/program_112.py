import base_info


array_convert_code = \
"""
static PyArrayObject* py_to_numpy(PyObject* py_obj, char* name)
{
    PyArrayObject* arr_obj = NULL;

    if (!py_obj || !PyArray_Check(py_obj))
        handle_bad_type(py_obj,"array", name);

    // Any need to deal with INC/DEC REFs?
    Py_INCREF(py_obj);
    return (PyArrayObject*) py_obj;
}
"""

type_check_code = \
"""
void numpy_check_type(PyArrayObject* arr_obj, int numeric_type, char* name)
{
    // Make sure input has correct numeric type.
    if (arr_obj->descr->type_num != numeric_type)
    {
        char* type_names[13] = {"char","unsigned byte","byte", "short", "int", 
                                "long", "float", "double", "complex float",
                                "complex double", "object","ntype","unkown"};
        char msg[500];
        sprintf(msg,"received '%s' typed array instead of '%s' typed array for variable '%s'",
                type_names[arr_obj->descr->type_num],type_names[numeric_type],name);
        throw Py::TypeError(msg);    
    }
}
"""

size_check_code = \
"""
void numpy_check_size(PyArrayObject* arr_obj, int Ndims, char* name)
{
    if (arr_obj->nd != Ndims)
    {
        char msg[500];
        sprintf(msg,"received '%d' dimensional array instead of '%d' dimensional array for variable '%s'",
                arr_obj->nd,Ndims,name);
        throw Py::TypeError(msg);
    }    
}
"""

numeric_init_code = \
"""
Py_Initialize();
