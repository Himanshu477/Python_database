from base_spec import base_specification
from scalar_spec import numeric_to_blitz_type_mapping
from Numeric import *
from types import *
import os
import blitz_info

class array_specification(base_specification):
    _build_information = [blitz_info.array_info()]
    
    def type_match(self,value):
        return type(value) is ArrayType

    def type_spec(self,name,value):
        # factory
        new_spec = array_specification()
        new_spec.name = name
        new_spec.numeric_type = value.typecode()
        new_spec.dims = len(value.shape)
        if new_spec.dims > 11:
            msg = "Error converting variable '" + name + "'.  " \
                  "blitz only supports arrays up to 11 dimensions."
            raise ValueError, msg
        return new_spec

    def declaration_code(self,templatize = 0,inline=0):
        if inline:
            code = self.inline_decl_code()
        else:
            code = self.standard_decl_code()
        return code
    
    def inline_decl_code(self):
        type = numeric_to_blitz_type_mapping[self.numeric_type]
        dims = self.dims
        name = self.name
        var_name = self.retrieve_py_variable(inline=1)
        templ = '// blitz_array_declaration\n' \
                'py_%(name)s= %(var_name)s;\n' \
                'blitz::Array<%(type)s,%(dims)d> %(name)s =' \
                ' py_to_blitz<%(type)s,%(dims)d>(py_%(name)s,"%(name)s");\n' \
                'blitz::TinyVector<int,%(dims)d> _N%(name)s = %(name)s.shape();\n'
        code = templ % locals()
        return code

    def standard_decl_code(self):    
        type = numeric_to_blitz_type_mapping[self.numeric_type]
        dims = self.dims
        name = self.name
        var_name = self.retrieve_py_variable(inline=0)
        templ = '// blitz_array_declaration\n' \
                'blitz::Array<%(type)s,%(dims)d> %(name)s =' \
                ' py_to_blitz<%(type)s,%(dims)d>(%(var_name)s,"%(name)s");\n' \
                'blitz::TinyVector<int,%(dims)d> _N%(name)s = %(name)s.shape();\n'
        code = templ % locals()
        return code
    #def c_function_declaration_code(self):
    #    """
    #        This doesn't pass the size through.  That info is gonna have to 
    #        be redone in the c function.
    #    """
    #    templ_dict = {}
    #    templ_dict['type'] = numeric_to_blitz_type_mapping[self.numeric_type]
    #    templ_dict['dims'] = self.dims
    #    templ_dict['name'] = self.name
    #    code = 'blitz::Array<%(type)s,%(dims)d> &%(name)s' % templ_dict
    #    return code
        
    def local_dict_code(self):
        code = '// for now, array "%s" is not returned as arryas are edited' \
               ' in place (should this change?)\n' % (self.name)        
        return code

    def cleanup_code(self):
        # could use Py_DECREF here I think and save NULL test.
        code = "Py_XDECREF(py_%s);\n" % self.name
        return code

    def __repr__(self):
        msg = "(array:: name: %s, type: %s, dims: %d)" % \
                  (self.name, self.numeric_type, self.dims)
        return msg

    def __cmp__(self,other):
        #only works for equal
        return cmp(self.name,other.name) or  \
               cmp(self.numeric_type,other.numeric_type) or \
               cmp(self.dims, other.dims) or \
               cmp(self.__class__, other.__class__)

# stick this factory on the front of the type factories
