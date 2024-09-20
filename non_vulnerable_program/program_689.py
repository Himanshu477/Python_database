import_ufunc(void)
{ 
  PyObject *numpy = PyImport_ImportModule("scipy.base.umath");
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

""" % ('\n'.join(module_list), 
       '\n'.join(extension_list))

# Write to header
fid = open('__ufunc_api.h','w')
fid.write(outstr)
fid.close()


outstr = r"""
/* These pointers will be stored in the C-object for use in other
    extension modules
*/

void *PyUFunc_API[] = {
        (void *) &PyUFunc_Type,
%s
};
""" % '\n'.join(init_list)

# Write to c-code
fid = open('__ufunc_api.c','w')
fid.write(outstr)
fid.close()






### DO NOT EDIT THIS FILE!!!
### DO NOT TRY TO COMMIT THIS FILE TO CVS REPOSITORY!!!
cvs_version = (1,46,243,2019)


#!/usr/bin/env python

__all__ = ['run_main','compile','f2py_testing']

