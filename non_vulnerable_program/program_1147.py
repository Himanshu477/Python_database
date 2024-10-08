import_ufunc(void)
{
  PyObject *numpy = PyImport_ImportModule("numpy.base.umath");
  PyObject *c_api = NULL;

  if (numpy == NULL) return -1;
  c_api = PyObject_GetAttrString(numpy, "_UFUNC_API");
  if (c_api == NULL) {Py_DECREF(numpy); return -1;}
  if (PyCObject_Check(c_api)) {
      PyUFunc_API = (void **)PyCObject_AsVoidPtr(c_api);
  }
  Py_DECREF(c_api);
  Py_DECREF(numpy);
  if (PyUFunc_API == NULL) return -1;
  return 0;
}

#endif
"""

c_template = r"""
/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *PyUFunc_API[] = {
        (void *) &PyUFunc_Type,
%s
};
"""

def generate_api(output_dir):
    ufunc_api_list = genapi.get_api_functions('UFUNC_API',
                                              'ufunc_api_order.txt')

    # API fixes for __arrayobject_api.h

    fixed = 1
    nummulti = len(ufunc_api_list)
    numtotal = fixed + nummulti

    module_list = []
    extension_list = []
    init_list = []

    #setup object API
    genapi.add_api_list(fixed, 'PyUFunc_API', ufunc_api_list,
                        module_list, extension_list, init_list)

    # Write to header
    fid = open(os.path.join(output_dir, '__ufunc_api.h'),'w')
    s = h_template % ('\n'.join(module_list), '\n'.join(extension_list))
    fid.write(s)
    fid.close()

    # Write to c-code
    fid = open(os.path.join(output_dir, '__ufunc_api.c'),'w')
    s = c_template % '\n'.join(init_list)
    fid.write(s)
    fid.close()


"""MA: a facility for dealing with missing observations
MA is generally used as a numpy.array look-alike.
by Paul F. Dubois.

Copyright 1999, 2000, 2001 Regents of the University of California.
Released for unlimited redistribution.
Adapted for numpy_core 2005 by Travis Oliphant and
(mainly) Paul Dubois.
"""
