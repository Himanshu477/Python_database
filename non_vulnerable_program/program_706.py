from auxfuncs import *
import capi_maps
import cfuncs
import func2subr
from crackfortran import rmbadname
##############

def findcommonblocks(block,top=1):
    ret = []
    if hascommon(block):
        for n in block['common'].keys():
            vars={}
            for v in block['common'][n]:
                vars[v]=block['vars'][v]
            ret.append((n,block['common'][n],vars))
    elif hasbody(block):
        for b in block['body']:
            ret=ret+findcommonblocks(b,0)
    if top:
        tret=[]
        names=[]
        for t in ret:
            if t[0] not in names:
                names.append(t[0])
                tret.append(t)
        return tret
    return ret

def buildhooks(m):
    ret = {'commonhooks':[],'initcommonhooks':[],'docs':['"COMMON blocks:\\n"']}
    fwrap = ['']
    def fadd(line,s=fwrap): s[0] = '%s\n      %s'%(s[0],line)
    chooks = ['']
    def cadd(line,s=chooks): s[0] = '%s\n%s'%(s[0],line)
    ihooks = ['']
    def iadd(line,s=ihooks): s[0] = '%s\n%s'%(s[0],line)
    doc = ['']
    def dadd(line,s=doc): s[0] = '%s\n%s'%(s[0],line)
    for (name,vnames,vars) in findcommonblocks(m):
        lower_name = string.lower(name)
        hnames,inames = [],[]
        for n in vnames:
            if isintent_hide(vars[n]): hnames.append(n)
            else: inames.append(n)
        if hnames:
            outmess('\t\tConstructing COMMON block support for "%s"...\n\t\t  %s\n\t\t  Hidden: %s\n'%(name,string.join(inames,','),string.join(hnames,',')))
        else:
            outmess('\t\tConstructing COMMON block support for "%s"...\n\t\t  %s\n'%(name,string.join(inames,',')))
        fadd('subroutine f2pyinit%s(setupfunc)'%name)
        fadd('external setupfunc')
        for n in vnames:
            fadd(func2subr.var2fixfortran(vars,n))
        if name=='_BLNK_':
            fadd('common %s'%(string.join(vnames,',')))
        else:
            fadd('common /%s/ %s'%(name,string.join(vnames,',')))
        fadd('call setupfunc(%s)'%(string.join(inames,',')))
        fadd('end\n')
        cadd('static FortranDataDef f2py_%s_def[] = {'%(name))
        idims=[]
        for n in inames:
            ct = capi_maps.getctype(vars[n])
            at = capi_maps.c2capi_map[ct]
            dm = capi_maps.getarrdims(n,vars[n])
            if dm['dims']: idims.append('(%s)'%(dm['dims']))
            else: idims.append('')
            dms=string.strip(dm['dims'])
            if not dms: dms='-1'
            cadd('\t{\"%s\",%s,{{%s}},%s},'%(n,dm['rank'],dms,at))
        cadd('\t{NULL}\n};')
        inames1 = rmbadname(inames)
        inames1_tps = string.join(map(lambda s:'char *'+s,inames1),',')
        cadd('static void f2py_setup_%s(%s) {'%(name,inames1_tps))
        cadd('\tint i_f2py=0;')
        for n in inames1:
            cadd('\tf2py_%s_def[i_f2py++].data = %s;'%(name,n))
        cadd('}')
        if '_' in lower_name:
            F_FUNC='F_FUNC_US'
        else:
            F_FUNC='F_FUNC'
        cadd('extern void %s(f2pyinit%s,F2PYINIT%s)(void(*)(%s));'\
             %(F_FUNC,lower_name,string.upper(name),
               string.join(['char*']*len(inames1),',')))
        cadd('static void f2py_init_%s(void) {'%name)
        cadd('\t%s(f2pyinit%s,F2PYINIT%s)(f2py_setup_%s);'\
             %(F_FUNC,lower_name,string.upper(name),name))
        cadd('}\n')
        iadd('\tPyDict_SetItemString(d, \"%s\", PyFortranObject_New(f2py_%s_def,f2py_init_%s));'%(name,name,name))
        tname = string.replace(name,'_','\\_')
        dadd('\\subsection{Common block \\texttt{%s}}\n'%(tname))
        dadd('\\begin{description}')
        for n in inames:
            dadd('\\item[]{{}\\verb@%s@{}}'%(capi_maps.getarrdocsign(n,vars[n])))
            if hasnote(vars[n]):
                note = vars[n]['note']
                if type(note) is type([]): note=string.join(note,'\n')
                dadd('--- %s'%(note))
        dadd('\\end{description}')
        ret['docs'].append('"\t/%s/ %s\\n"'%(name,string.join(map(lambda v,d:v+d,inames,idims),',')))
    ret['commonhooks']=chooks
    ret['initcommonhooks']=ihooks
    ret['latexdoc']=doc[0]
    if len(ret['docs'])<=1: ret['docs']=''
    return ret,fwrap[0]



#!/usr/bin/env python
"""
crackfortran --- read fortran (77,90) code and extract declaration information.
    Usage is explained in the comment block below.

Copyright 1999-2004 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>          
Permission to use, modify, and distribute this software is given under the
terms of the LGPL.  See http://www.fsf.org

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
$Date: 2005/09/27 07:13:49 $
Pearu Peterson
"""
__version__ = "$Revision: 1.177 $"[10:-1]

