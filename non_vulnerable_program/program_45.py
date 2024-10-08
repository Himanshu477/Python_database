    import wx_spec
    default_type_factories.append(wx_spec.wx_specification())
except: 
    pass    
   
def blitz(expr,local_dict=None, global_dict=None,check_size=1,verbose=0):
    # this could call inline, but making a copy of the
    # code here is more efficient for several reasons.
    global function_catalog
          
    # this grabs the local variables from the *previous* call
    # frame -- that is the locals from the function that called
    # inline.
    call_frame = sys._getframe().f_back
    if local_dict is None:
        local_dict = call_frame.f_locals
    if global_dict is None:
        global_dict = call_frame.f_globals

    # 1. Check the sizes of the arrays and make sure they are compatible.
    #    This is expensive, so unsetting the check_size flag can save a lot
    #    of time.  It also can cause core-dumps if the sizes of the inputs 
    #    aren't compatible.    
    if check_size and not size_check.check_expr(expr,local_dict,global_dict):
        raise 'inputs failed to pass size check.'
    
    # 2. try local cache    
    try:
        results = apply(function_cache[expr],(local_dict,global_dict))
        return results
    except: 
        pass
    try:
        results = attempt_function_call(expr,local_dict,global_dict)
    # 3. build the function    
    except ValueError:
        # This section is pretty much the only difference 
        # between blitz and inline
        ast = parser.suite(expr)
        ast_list = ast.tolist()
        expr_code = ast_to_blitz_expr(ast_list)
        arg_names = harvest_variables(ast_list)
        module_dir = global_dict.get('__file__',None)
        #func = inline_tools.compile_function(expr_code,arg_names,
        #                                    local_dict,global_dict,
        #                                    module_dir,auto_downcast = 1)
        func = inline_tools.compile_function(expr_code,arg_names,local_dict,        
                                             global_dict,module_dir,
                                             compiler='gcc',auto_downcast=1,
                                             verbose = verbose,
                                             type_factories = blitz_type_factories)
        function_catalog.add_function(expr,func,module_dir)
        try:                                            
            results = attempt_function_call(expr,local_dict,global_dict)
        except ValueError:                                                
            print 'warning: compilation failed. Executing as python code'
            exec expr in global_dict, local_dict
            
def ast_to_blitz_expr(ast_seq):
    """ Convert an ast_sequence to a blitz expression.
    """
    
    # Don't overwrite orignal sequence in call to transform slices.
    ast_seq = copy.deepcopy(ast_seq)    
    slice_handler.transform_slices(ast_seq)
    
    # Build the actual program statement from ast_seq
    expr = ast_tools.ast_to_string(ast_seq)
    
    # Now find and replace specific symbols to convert this to
    # a blitz++ compatible statement.
    # I'm doing this with string replacement here.  It could
    # also be done on the actual ast tree (and probably should from
    # a purest standpoint...).
    
    # this one isn't necessary but it helps code readability
    # and compactness. It requires that 
    #   Range _all = blitz::Range::all();
    # be included in the generated code.    
    # These could all alternatively be done to the ast in
    # build_slice_atom()
    expr = string.replace(expr,'slice(_beg,_end)', '_all' )    
    expr = string.replace(expr,'slice', 'blitz::Range' )
    expr = string.replace(expr,'[','(')
    expr = string.replace(expr,']', ')' )
    expr = string.replace(expr,'_stp', '1' )
    
    # Instead of blitz::fromStart and blitz::toEnd.  This requires
    # the following in the generated code.
    #   Range _beg = blitz::fromStart;
    #   Range _end = blitz::toEnd;
    #expr = string.replace(expr,'_beg', 'blitz::fromStart' )
    #expr = string.replace(expr,'_end', 'blitz::toEnd' )
    
    return expr + ';\n'

def test_function():
    from code_blocks import module_header

    expr = "ex[:,1:,1:] = k +  ca_x[:,1:,1:] * ex[:,1:,1:]" \
                         "+ cb_y_x[:,1:,1:] * (hz[:,1:,1:] - hz[:,:-1,1:])"\
                         "- cb_z_x[:,1:,1:] * (hy[:,1:,1:] - hy[:,1:,:-1])"        
    #ast = parser.suite('a = (b + c) * sin(d)')
    ast = parser.suite(expr)
    k = 1.
    ex = ones((1,1,1),typecode=Float32)
    ca_x = ones((1,1,1),typecode=Float32)
    cb_y_x = ones((1,1,1),typecode=Float32)
    cb_z_x = ones((1,1,1),typecode=Float32)
    hz = ones((1,1,1),typecode=Float32)
    hy = ones((1,1,1),typecode=Float32)
    blitz(expr)
    """
    ast_list = ast.tolist()
    
    expr_code = ast_to_blitz_expr(ast_list)
    arg_list = harvest_variables(ast_list)
    arg_specs = assign_variable_types(arg_list,locals())
    
    func,template_types = create_function('test_function',expr_code,arg_list,arg_specs)
    init,used_names = create_module_init('compile_sample','test_function',template_types)
    #wrapper = create_wrapper(mod_name,func_name,used_names)
    return string.join( [module_header,func,init],'\n')
    """
def test():
    from scipy_test import module_test
    module_test(__name__,__file__)

def test_suite():
    from scipy_test import module_test_suite
    return module_test_suite(__name__,__file__)    

if __name__ == "__main__":
    test_function()

""" Tools for compiling C/C++ code to extension modules

    The main function, build_extension(), takes the C/C++ file
    along with some other options and builds a Python extension.
    It uses distutils for most of the heavy lifting.
    
    choose_compiler() is also useful (mainly on windows anyway)
    for trying to determine whether MSVC++ or gcc is available.
    MSVC doesn't handle templates as well, so some of the code emitted
    by the python->C conversions need this info to choose what kind
    of code to create.
    
    The other main thing here is an alternative version of the MingW32
    compiler class.  The class makes it possible to build libraries with
    gcc even if the original version of python was built using MSVC.  It
    does this by converting a pythonxx.lib file to a libpythonxx.a file.
    Note that you need write access to the pythonxx/lib directory to do this.
"""

