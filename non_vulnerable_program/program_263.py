import common_info
from c_spec import common_base_converter


vtk_py_to_c_template = \
"""
class %(type_name)s_handler
{
public:
    %(c_type)s convert_to_%(type_name)s(PyObject* py_obj, const char* name)
    {
        %(c_type)s vtk_ptr = (%(c_type)s) vtkPythonGetPointerFromObject(py_obj, "%(type_name)s");
        if (!vtk_ptr)
            handle_conversion_error(py_obj,"%(type_name)s", name);
        %(inc_ref_count)s
        return vtk_ptr;
    }

    %(c_type)s py_to_%(type_name)s(PyObject* py_obj, const char* name)
    {
        %(c_type)s vtk_ptr = (%(c_type)s) vtkPythonGetPointerFromObject(py_obj, "%(type_name)s");
        if (!vtk_ptr)
            handle_bad_type(py_obj,"%(type_name)s", name);
        %(inc_ref_count)s
        return vtk_ptr;
    }
};

%(type_name)s_handler x__%(type_name)s_handler = %(type_name)s_handler();
#define convert_to_%(type_name)s(py_obj,name) \\
        x__%(type_name)s_handler.convert_to_%(type_name)s(py_obj,name)
#define py_to_%(type_name)s(py_obj,name) \\
        x__%(type_name)s_handler.py_to_%(type_name)s(py_obj,name)

"""

vtk_c_to_py_template = \
"""
PyObject* %(type_name)s_to_py(vtkObjectBase* obj)
{
    return vtkPythonGetObjectFromPointer(obj);
}
"""
                  

class vtk_converter(common_base_converter):
    def __init__(self,class_name="undefined"):
        self.class_name = class_name
        common_base_converter.__init__(self)

    def init_info(self):
        common_base_converter.init_info(self)
        # These are generated on the fly instead of defined at 
        # the class level.
        self.type_name = self.class_name
        self.c_type = self.class_name + "*"
        self.to_c_return = None # not used
        self.check_func = None # not used
        hdr = self.class_name + ".h"
        # Remember that you need both the quotes!
        self.headers.extend(['"vtkPythonUtil.h"', '"vtkObject.h"',
                             '"%s"'%hdr])
        #self.include_dirs.extend(vtk_inc)
        #self.define_macros.append(('SOME_VARIABLE', '1'))
        #self.library_dirs.extend(vtk_lib)
        self.libraries.extend(['vtkCommonPython', 'vtkCommon'])
        #self.support_code.append(common_info.swig_support_code)
    
    def type_match(self,value):
        is_match = 0
        try:
            if value.IsA('vtkObject'):
                is_match = 1
        except AttributeError:
            pass
        return is_match

    def generate_build_info(self):
        if self.class_name != "undefined":
            res = common_base_converter.generate_build_info(self)
        else:
            # if there isn't a class_name, we don't want the
            # we don't want the support_code to be included
            import base_info
            res = base_info.base_info()
        return res
        
    def py_to_c_code(self):
        return vtk_py_to_c_template % self.template_vars()

    def c_to_py_code(self):
        return vtk_c_to_py_template % self.template_vars()
                    
    def type_spec(self,name,value):
        # factory
        class_name = value.__class__.__name__
        new_spec = self.__class__(class_name)
        new_spec.name = name        
        return new_spec

    def __cmp__(self,other):
        #only works for equal
        res = -1
        try:
            res = cmp(self.name,other.name) or \
                  cmp(self.__class__, other.__class__) or \
                  cmp(self.class_name, other.class_name) or \
                  cmp(self.type_name,other.type_name)
        except:
            pass
        return res

"""
# this should only be enabled on machines with access to a display device
# It'll cause problems otherwise.
def test(level=10):
    from scipy_base.testing import module_test
    module_test(__name__,__file__,level=level)

def test_suite(level=1):
    from scipy_base.testing import module_test_suite
    return module_test_suite(__name__,__file__,level=level)
"""


""" Auto test tools for SciPy

    Do not run this as root!  If you enter something
    like /usr as your test directory, it'll delete
    /usr/bin, usr/lib, etc.  So don't do it!!!
    
    
    Author: Eric Jones (eric@enthought.com)
"""
