import_array(void)
{
  PyObject *numpy = PyImport_ImportModule("numpy.base.multiarray");
  PyObject *c_api = NULL;
  if (numpy == NULL) return -1;
  c_api = PyObject_GetAttrString(numpy, "_ARRAY_API");
  if (c_api == NULL) {Py_DECREF(numpy); return -1;}
  if (PyCObject_Check(c_api)) {
      PyArray_API = (void **)PyCObject_AsVoidPtr(c_api);
  }
  Py_DECREF(c_api);
  Py_DECREF(numpy);
  if (PyArray_API == NULL) return -1;
  return 0;
}
#endif

#endif
"""


c_template = r"""
/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *PyArray_API[] = {
        (void *) &PyBigArray_Type,
        (void *) &PyArray_Type,
        (void *) &PyArrayDescr_Type,
        (void *) &PyArrayIter_Type,
        (void *) &PyArrayMultiIter_Type,
        (int *) &PyArray_NUMUSERTYPES, 
%s
};
"""

def generate_api(output_dir):
    objectapi_list = genapi.get_api_functions('OBJECT_API',
                                              'array_api_order.txt')
    multiapi_list = genapi.get_api_functions('MULTIARRAY_API',
                                             'multiarray_api_order.txt')
    # API fixes for __arrayobject_api.h

    fixed = 6
    numtypes = len(types) + fixed
    numobject = len(objectapi_list) + numtypes
    nummulti = len(multiapi_list)
    numtotal = numobject + nummulti

    module_list = []
    extension_list = []
    init_list = []

    # setup types
    for k, atype in enumerate(types):
        num = fixed + k
        astr = "        (void *) &Py%sArrType_Type," % types[k]
        init_list.append(astr)
        astr = "static PyTypeObject Py%sArrType_Type;" % types[k]
        module_list.append(astr)
        astr = "#define Py%sArrType_Type (*(PyTypeObject *)PyArray_API[%d])" % \
               (types[k], num)
        extension_list.append(astr)

    #setup object API
    genapi.add_api_list(numtypes, 'PyArray_API', objectapi_list,
                        module_list, extension_list, init_list)

    # setup multiarray module API
    genapi.add_api_list(numobject, 'PyArray_API', multiapi_list,
                        module_list, extension_list, init_list)


    # Write to header
    fid = open(os.path.join(output_dir, '__multiarray_api.h'),'w')
    s = h_template % ('\n'.join(module_list), '\n'.join(extension_list))
    fid.write(s)
    fid.close()

    # Write to c-code
    fid = open(os.path.join(output_dir,'__multiarray_api.c'),'w')
    s = c_template % '\n'.join(init_list)
    fid.write(s)
    fid.close()


