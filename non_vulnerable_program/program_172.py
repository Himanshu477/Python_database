import time
from weave import ext_tools
from Numeric import *

def Ramp(result, size, start, end):
    step = (end-start)/(size-1)
    for i in xrange(size):
        result[i] = start + step*i

def build_ramp_ext():
    mod = ext_tools.ext_module('ramp_ext')
    
    # type declarations
    result = array([0],Float64)
    size,start,end = 0,0.,0.
    code = """
           double step = (end-start)/(size-1);
           double val = start;
           for (int i = 0; i < size; i++)
           {
              result_data[i] = val;
              val += step; 
           }
           """
    func = ext_tools.ext_function('Ramp',code,['result','size','start','end'])
    mod.add_function(func)
    mod.compile(compiler='gcc')
         
def main():    
    arr = [0]*10000
    t1 = time.time()
    for i in xrange(200):
        Ramp(arr, 10000, 0.0, 1.0)
    t2 = time.time()
    py_time = t2 - t1
    print 'python (seconds):', py_time
    print 'arr[500]:', arr[500]
    print
    
    try:
