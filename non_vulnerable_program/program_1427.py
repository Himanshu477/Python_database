import sys,string,fileinput,re,pprint,os,copy
from auxfuncs import *

# Global flags:
strictf77=1          # Ignore `!' comments unless line[0]=='!'
sourcecodeform='fix' # 'fix','free'
quiet=0              # Be verbose if 0 (Obsolete: not used any more)
verbose=1            # Be quiet if 0, extra verbose if > 1.
tabchar=4*' '
pyffilename=''
f77modulename=''
skipemptyends=0      # for old F77 programs without 'program' statement
ignorecontains=1
dolowercase=1
debug=[]
## do_analyze = 1

###### global variables

## use reload(crackfortran) to reset these variables

groupcounter=0
grouplist={groupcounter:[]}
neededmodule=-1
expectbegin=1
skipblocksuntil=-1
usermodules=[]
f90modulevars={}
gotnextfile=1
filepositiontext=''
currentfilename=''
skipfunctions=[]
skipfuncs=[]
onlyfuncs=[]
include_paths=[]
previous_context = None

###### Some helper functions
def show(o,f=0):pprint.pprint(o)
errmess=sys.stderr.write
def outmess(line,flag=1):
    global filepositiontext
    if not verbose: return
    if not quiet:
        if flag:sys.stdout.write(filepositiontext)
        sys.stdout.write(line)
re._MAXCACHE=50
defaultimplicitrules={}
for c in "abcdefghopqrstuvwxyz$_": defaultimplicitrules[c]={'typespec':'real'}
for c in "ijklmn": defaultimplicitrules[c]={'typespec':'integer'}
del c
badnames={}
invbadnames={}
for n in ['int','double','float','char','short','long','void','case','while',
          'return','signed','unsigned','if','for','typedef','sizeof','union',
          'struct','static','register','new','break','do','goto','switch',
          'continue','else','inline','extern','delete','const','auto',
          'len','rank','shape','index','slen','size','_i',
          'flen','fshape',
          'string','complex_double','float_double','stdin','stderr','stdout',
          'type','default']:
    badnames[n]=n+'_bn'
    invbadnames[n+'_bn']=n
def rmbadname1(name):
    if badnames.has_key(name):
        errmess('rmbadname1: Replacing "%s" with "%s".\n'%(name,badnames[name]))
        return badnames[name]
    return name
def rmbadname(names): return map(rmbadname1,names)

def undo_rmbadname1(name):
    if invbadnames.has_key(name):
        errmess('undo_rmbadname1: Replacing "%s" with "%s".\n'\
                %(name,invbadnames[name]))
        return invbadnames[name]
    return name
def undo_rmbadname(names): return map(undo_rmbadname1,names)

def getextension(name):
    i=string.rfind(name,'.')
    if i==-1: return ''
    if '\\' in name[i:]: return ''
    if '/' in name[i:]: return ''
    return name[i+1:]

is_f_file = re.compile(r'.*[.](for|ftn|f77|f)\Z',re.I).match
_has_f_header = re.compile(r'-[*]-\s*fortran\s*-[*]-',re.I).search
_has_f90_header = re.compile(r'-[*]-\s*f90\s*-[*]-',re.I).search
_has_fix_header = re.compile(r'-[*]-\s*fix\s*-[*]-',re.I).search
_free_f90_start = re.compile(r'[^c*]\s*[^\s\d\t]',re.I).match
def is_free_format(file):
    """Check if file is in free format Fortran."""
    # f90 allows both fixed and free format, assuming fixed unless
    # signs of free format are detected.
    result = 0
    f = open(file,'r')
    line = f.readline()
    n = 15 # the number of non-comment lines to scan for hints
    if _has_f_header(line):
        n = 0
    elif _has_f90_header(line):
        n = 0
        result = 1
    while n>0 and line:
        if line[0]!='!':
            n -= 1
            if (line[0]!='\t' and _free_f90_start(line[:5])) or line[-2:-1]=='&':
                result = 1
                break
        line = f.readline()
    f.close()
    return result


####### Read fortran (77,90) code
def readfortrancode(ffile,dowithline=show,istop=1):
    """
    Read fortran codes from files and
     1) Get rid of comments, line continuations, and empty lines; lower cases.
     2) Call dowithline(line) on every line.
     3) Recursively call itself when statement \"include '<filename>'\" is met.
    """
    global gotnextfile,filepositiontext,currentfilename,sourcecodeform,strictf77,\
           beginpattern,quiet,verbose,dolowercase,include_paths
    if not istop:
        saveglobals=gotnextfile,filepositiontext,currentfilename,sourcecodeform,strictf77,\
           beginpattern,quiet,verbose,dolowercase
    if ffile==[]: return
    localdolowercase = dolowercase
    cont=0
    finalline=''
    ll=''
    commentline=re.compile(r'(?P<line>([^"]*"[^"]*"[^"!]*|[^\']*\'[^\']*\'[^\'!]*|[^!]*))!{1}(?P<rest>.*)')
    includeline=re.compile(r'\s*include\s*(\'|")(?P<name>[^\'"]*)(\'|")',re.I)
    cont1=re.compile(r'(?P<line>.*)&\s*\Z')
    cont2=re.compile(r'(\s*&|)(?P<line>.*)')
    mline_mark = re.compile(r".*?'''")
    if istop: dowithline('',-1)
    ll,l1='',''
    spacedigits=[' ']+map(str,range(10))
    filepositiontext=''
    fin=fileinput.FileInput(ffile)
    while 1:
        l=fin.readline()
        if not l: break
        if fin.isfirstline():
            filepositiontext=''
            currentfilename=fin.filename()
            gotnextfile=1
            l1=l
            strictf77=0
            sourcecodeform='fix'
            ext = os.path.splitext(currentfilename)[1]
            if is_f_file(currentfilename) and \
                   not (_has_f90_header(l) or _has_fix_header(l)):
                strictf77=1   
            elif is_free_format(currentfilename) and not _has_fix_header(l):
                sourcecodeform='free'
            if strictf77: beginpattern=beginpattern77
            else: beginpattern=beginpattern90
            outmess('\tReading file %s (format:%s%s)\n'\
                    %(`currentfilename`,sourcecodeform,
                      strictf77 and ',strict' or ''))

        l=string.expandtabs(l).replace('\xa0',' ')
        while not l=='':                       # Get rid of newline characters
            if l[-1] not in "\n\r\f": break
            l=l[:-1]
        if not strictf77:
            r=commentline.match(l)
            if r:
                l=r.group('line')+' ' # Strip comments starting with `!'
                rl=r.group('rest')
                if string.lower(rl[:4])=='f2py': # f2py directive
                    l = l + 4*' '
                    r=commentline.match(rl[4:])
                    if r: l=l+r('line')
                    else: l = l + rl[4:]
        if string.strip(l)=='': # Skip empty line
            cont=0
            continue
        if sourcecodeform=='fix':
            if l[0] in ['*','c','!','C','#']:
                if string.lower(l[1:5])=='f2py': # f2py directive
                    l='     '+l[5:]
                else: # Skip comment line
                    cont=0
                    continue
            elif strictf77:
                if len(l)>72: l=l[:72]
            if not (l[0] in spacedigits):
                raise 'readfortrancode: Found non-(space,digit) char in the first column.\n\tAre you sure that this code is in fix form?\n\tline=%s'%`l`

            if (not cont or strictf77) and (len(l)>5 and not l[5]==' '):
                # Continuation of a previous line
                ll=ll+l[6:]
                finalline=''
                origfinalline=''
            else:
                if not strictf77:
                    # F90 continuation
                    r=cont1.match(l)
                    if r: l=r.group('line') # Continuation follows ..
                    if cont:
                        ll=ll+cont2.match(l).group('line')
                        finalline=''
                        origfinalline=''
                    else:
                        l='     '+l[5:] # clean up line beginning from possible digits.
                        if localdolowercase: finalline=string.lower(ll)
                        else: finalline=ll
                        origfinalline=ll
                        ll=l
                    cont=(r is not None)
                else:
                    l='     '+l[5:] # clean up line beginning from possible digits.
                    if localdolowercase: finalline=string.lower(ll)
                    else: finalline=ll
                    origfinalline =ll
                    ll=l

        elif sourcecodeform=='free':
            if not cont and ext=='.pyf' and mline_mark.match(l):
                l = l + '\n'
                while 1:
                    lc = fin.readline()
                    if not lc:
                        errmess('Unexpected end of file when reading multiline\n')
                        break
                    l = l + lc
                    if mline_mark.match(lc):
                        break
                l = l.rstrip()
            r=cont1.match(l)
            if r: l=r.group('line') # Continuation follows ..
            if cont:
                ll=ll+cont2.match(l).group('line')
                finalline=''
                origfinalline=''
            else:
                if localdolowercase: finalline=string.lower(ll)
                else: finalline=ll
                origfinalline =ll
                ll=l
            cont=(r is not None)
        else:
            raise ValueError,"Flag sourcecodeform must be either 'fix' or 'free': %s"%`sourcecodeform`
        filepositiontext='Line #%d in %s:"%s"\n\t' % (fin.filelineno()-1,currentfilename,l1)
        m=includeline.match(origfinalline)
        if m:
            fn=m.group('name')
            if os.path.isfile(fn):
                readfortrancode(fn,dowithline=dowithline,istop=0)
            else:
                include_dirs = [os.path.dirname(currentfilename)] + include_paths
                foundfile = 0
                for inc_dir in include_dirs:
                    fn1 = os.path.join(inc_dir,fn)
                    if os.path.isfile(fn1):
                        foundfile = 1
                        readfortrancode(fn1,dowithline=dowithline,istop=0)
                        break
                if not foundfile:
                    outmess('readfortrancode: could not find include file %s. Ignoring.\n'%(`fn`))
        else:
            dowithline(finalline)
        l1=ll
    if localdolowercase:
        finalline=string.lower(ll)
    else: finalline=ll
    origfinalline = ll
    filepositiontext='Line #%d in %s:"%s"\n\t' % (fin.filelineno()-1,currentfilename,l1)
    m=includeline.match(origfinalline)
    if m:
        fn=m.group('name')
        fn1=os.path.join(os.path.dirname(currentfilename),fn)
        if os.path.isfile(fn):
            readfortrancode(fn,dowithline=dowithline,istop=0)
        elif os.path.isfile(fn1):
            readfortrancode(fn1,dowithline=dowithline,istop=0)
        else:
            outmess('readfortrancode: could not find include file %s. Ignoring.\n'%(`fn`))
    else:
        dowithline(finalline)
    filepositiontext=''
    fin.close()
    if istop: dowithline('',1)
    else:
        gotnextfile,filepositiontext,currentfilename,sourcecodeform,strictf77,\
           beginpattern,quiet,verbose,dolowercase=saveglobals

########### Crack line
beforethisafter=r'\s*(?P<before>%s(?=\s*(\b(%s)\b)))'+ \
                          r'\s*(?P<this>(\b(%s)\b))'+ \
                          r'\s*(?P<after>%s)\s*\Z'
##
fortrantypes='character|logical|integer|real|complex|double\s*(precision\s*(complex|)|complex)|type(?=\s*\([\w\s,=(*)]*\))|byte'
typespattern=re.compile(beforethisafter%('',fortrantypes,fortrantypes,'.*'),re.I),'type'
typespattern4implicit=re.compile(beforethisafter%('',fortrantypes+'|static|automatic|undefined',fortrantypes+'|static|automatic|undefined','.*'),re.I)
#
functionpattern=re.compile(beforethisafter%('([a-z]+[\w\s(=*+-/)]*?|)','function','function','.*'),re.I),'begin'
subroutinepattern=re.compile(beforethisafter%('[a-z\s]*?','subroutine','subroutine','.*'),re.I),'begin'
#modulepattern=re.compile(beforethisafter%('[a-z\s]*?','module','module','.*'),re.I),'begin'
#
groupbegins77=r'program|block\s*data'
beginpattern77=re.compile(beforethisafter%('',groupbegins77,groupbegins77,'.*'),re.I),'begin'
groupbegins90=groupbegins77+r'|module|python\s*module|interface|type(?!\s*\()'
beginpattern90=re.compile(beforethisafter%('',groupbegins90,groupbegins90,'.*'),re.I),'begin'
groupends=r'end|endprogram|endblockdata|endmodule|endpythonmodule|endinterface'
endpattern=re.compile(beforethisafter%('',groupends,groupends,'[\w\s]*'),re.I),'end'
#endifs='end\s*(if|do|where|select|while|forall)'
endifs='(end\s*(if|do|where|select|while|forall))|(module\s*procedure)'
endifpattern=re.compile(beforethisafter%('[\w]*?',endifs,endifs,'[\w\s]*'),re.I),'endif'
#
implicitpattern=re.compile(beforethisafter%('','implicit','implicit','.*'),re.I),'implicit'
dimensionpattern=re.compile(beforethisafter%('','dimension|virtual','dimension|virtual','.*'),re.I),'dimension'
externalpattern=re.compile(beforethisafter%('','external','external','.*'),re.I),'external'
optionalpattern=re.compile(beforethisafter%('','optional','optional','.*'),re.I),'optional'
requiredpattern=re.compile(beforethisafter%('','required','required','.*'),re.I),'required'
publicpattern=re.compile(beforethisafter%('','public','public','.*'),re.I),'public'
privatepattern=re.compile(beforethisafter%('','private','private','.*'),re.I),'private'
intrisicpattern=re.compile(beforethisafter%('','intrisic','intrisic','.*'),re.I),'intrisic'
intentpattern=re.compile(beforethisafter%('','intent|depend|note|check','intent|depend|note|check','\s*\(.*?\).*'),re.I),'intent'
parameterpattern=re.compile(beforethisafter%('','parameter','parameter','\s*\(.*'),re.I),'parameter'
datapattern=re.compile(beforethisafter%('','data','data','.*'),re.I),'data'
callpattern=re.compile(beforethisafter%('','call','call','.*'),re.I),'call'
entrypattern=re.compile(beforethisafter%('','entry','entry','.*'),re.I),'entry'
callfunpattern=re.compile(beforethisafter%('','callfun','callfun','.*'),re.I),'callfun'
commonpattern=re.compile(beforethisafter%('','common','common','.*'),re.I),'common'
usepattern=re.compile(beforethisafter%('','use','use','.*'),re.I),'use'
containspattern=re.compile(beforethisafter%('','contains','contains',''),re.I),'contains'
formatpattern=re.compile(beforethisafter%('','format','format','.*'),re.I),'format'
## Non-fortran and f2py-specific statements
f2pyenhancementspattern=re.compile(beforethisafter%('','threadsafe|fortranname|callstatement|callprotoargument|usercode|pymethoddef','threadsafe|fortranname|callstatement|callprotoargument|usercode|pymethoddef','.*'),re.I|re.S),'f2pyenhancements'
multilinepattern = re.compile(r"\s*(?P<before>''')(?P<this>.*?)(?P<after>''')\s*\Z",re.S),'multiline'
##

def _simplifyargs(argsline):
    a = []
    for n in string.split(markoutercomma(argsline),'@,@'):
        for r in '(),':
            n = string.replace(n,r,'_')
        a.append(n)
    return string.join(a,',')

crackline_re_1 = re.compile(r'\s*(?P<result>\b[a-z]+[\w]*\b)\s*[=].*',re.I)
def crackline(line,reset=0):
    """
    reset=-1  --- initialize
    reset=0   --- crack the line
    reset=1   --- final check if mismatch of blocks occured

    Cracked data is saved in grouplist[0].
    """
    global beginpattern,groupcounter,groupname,groupcache,grouplist,gotnextfile,\
           filepositiontext,currentfilename,neededmodule,expectbegin,skipblocksuntil,\
           skipemptyends,previous_context
    if ';' in line and not (f2pyenhancementspattern[0].match(line) or
                            multilinepattern[0].match(line)):
        for l in line.split(';'):
            assert reset==0,`reset` # XXX: non-zero reset values need testing
            crackline(l,reset)
        return
    if reset<0:
        groupcounter=0
        groupname={groupcounter:''}
        groupcache={groupcounter:{}}
        grouplist={groupcounter:[]}
        groupcache[groupcounter]['body']=[]
        groupcache[groupcounter]['vars']={}
        groupcache[groupcounter]['block']=''
        groupcache[groupcounter]['name']=''
        neededmodule=-1
        skipblocksuntil=-1
        return
    if reset>0:
        fl=0
        if f77modulename and neededmodule==groupcounter: fl=2
        while groupcounter>fl:
            outmess('crackline: groupcounter=%s groupname=%s\n'%(`groupcounter`,`groupname`))
            outmess('crackline: Mismatch of blocks encountered. Trying to fix it by assuming "end" statement.\n')
            grouplist[groupcounter-1].append(groupcache[groupcounter])
            grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
            del grouplist[groupcounter]
            groupcounter=groupcounter-1
        if f77modulename and neededmodule==groupcounter:
            grouplist[groupcounter-1].append(groupcache[groupcounter])
            grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
            del grouplist[groupcounter]
            groupcounter=groupcounter-1 # end interface
            grouplist[groupcounter-1].append(groupcache[groupcounter])
            grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
            del grouplist[groupcounter]
            groupcounter=groupcounter-1 # end module
            neededmodule=-1
        return
    if line=='': return
    flag=0
    for pat in [dimensionpattern,externalpattern,intentpattern,optionalpattern,
                requiredpattern,
                parameterpattern,datapattern,publicpattern,privatepattern,
                intrisicpattern,
                endifpattern,endpattern,
                formatpattern,
                beginpattern,functionpattern,subroutinepattern,
                implicitpattern,typespattern,commonpattern,
                callpattern,usepattern,containspattern,
                entrypattern,
                f2pyenhancementspattern,
                multilinepattern
                ]:
        m = pat[0].match(line)
        if m:
            break
        flag=flag+1
    if not m:
        re_1 = crackline_re_1
        if 0<=skipblocksuntil<=groupcounter:return
        if groupcache[groupcounter].has_key('externals'):
            for name in groupcache[groupcounter]['externals']:
                if invbadnames.has_key(name):
                    name=invbadnames[name]
                if groupcache[groupcounter].has_key('interfaced') and name in groupcache[groupcounter]['interfaced']: continue
                m1=re.match(r'(?P<before>[^"]*)\b%s\b\s*@\(@(?P<args>[^@]*)@\)@.*\Z'%name,markouterparen(line),re.I)
                if m1:
                    m2 = re_1.match(m1.group('before'))
                    a = _simplifyargs(m1.group('args'))
                    if m2:
                        line='callfun %s(%s) result (%s)'%(name,a,m2.group('result'))
                    else: line='callfun %s(%s)'%(name,a)
                    m = callfunpattern[0].match(line)
                    if not m:
                        outmess('crackline: could not resolve function call for line=%s.\n'%`line`)
                        return
                    analyzeline(m,'callfun',line)
                    return
        if verbose>1:
            previous_context = None
            outmess('crackline:%d: No pattern for line\n'%(groupcounter))
        return
    elif pat[1]=='end':
        if 0<=skipblocksuntil<groupcounter:
            groupcounter=groupcounter-1
            if skipblocksuntil<=groupcounter: return
        if groupcounter<=0:
            raise 'crackline: groupcounter(=%s) is nonpositive. Check the blocks.'\
                  % (groupcounter)
        m1 = beginpattern[0].match((line))
        if (m1) and (not m1.group('this')==groupname[groupcounter]):
            raise 'crackline: End group %s does not match with previous Begin group %s\n\t%s'%(`m1.group('this')`,`groupname[groupcounter]`,filepositiontext)
        if skipblocksuntil==groupcounter:
            skipblocksuntil=-1
        grouplist[groupcounter-1].append(groupcache[groupcounter])
        grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
        del grouplist[groupcounter]
        groupcounter=groupcounter-1
        if not skipemptyends:
            expectbegin=1
    elif pat[1] == 'begin':
        if 0<=skipblocksuntil<=groupcounter:
            groupcounter=groupcounter+1
            return
        gotnextfile=0
        analyzeline(m,pat[1],line)
        expectbegin=0
    elif pat[1]=='endif':
        pass
    elif pat[1]=='contains':
        if ignorecontains: return
        if 0<=skipblocksuntil<=groupcounter: return
        skipblocksuntil=groupcounter
    else:
        if 0<=skipblocksuntil<=groupcounter:return
        analyzeline(m,pat[1],line)

def markouterparen(line):
    l='';f=0
    for c in line:
        if c=='(':
            f=f+1
            if f==1: l=l+'@(@'; continue
        elif c==')':
            f=f-1
            if f==0: l=l+'@)@'; continue
        l=l+c
    return l
def markoutercomma(line,comma=','):
    l='';f=0
    cc=''
    for c in line:
        if (not cc or cc==')') and c=='(':
            f=f+1
            cc = ')'
        elif not cc and c=='\'' and (not l or l[-1]!='\\'):
            f=f+1
            cc = '\''
        elif c==cc:
            f=f-1
            if f==0:
                cc=''
        elif c==comma and f==0:
            l=l+'@'+comma+'@'
            continue
        l=l+c
    assert not f,`f,line,l,cc`
    return l
def unmarkouterparen(line):
    r = string.replace(string.replace(line,'@(@','('),'@)@',')')
    return r
def appenddecl(decl,decl2,force=1):
    if not decl: decl={}
    if not decl2: return decl
    if decl is decl2: return decl
    for k in decl2.keys():
        if k=='typespec':
            if force or not decl.has_key(k): decl[k]=decl2[k]
        elif k=='attrspec':
            for l in decl2[k]:
                decl=setattrspec(decl,l,force)
        elif k=='kindselector':
            decl=setkindselector(decl,decl2[k],force)
        elif k=='charselector':
            decl=setcharselector(decl,decl2[k],force)
        elif k in ['=','typename']:
            if force or not decl.has_key(k): decl[k]=decl2[k]
        elif k=='note':
            pass
        elif k in ['intent','check','dimension','optional','required']:
            errmess('appenddecl: "%s" not implemented.\n'%k)
        else:
            raise 'appenddecl: Unknown variable definition key:', k
    return decl

selectpattern=re.compile(r'\s*(?P<this>(@\(@.*?@\)@|[*][\d*]+|[*]\s*@\(@.*?@\)@|))(?P<after>.*)\Z',re.I)
nameargspattern=re.compile(r'\s*(?P<name>\b[\w$]+\b)\s*(@\(@\s*(?P<args>[\w\s,]*)\s*@\)@|)\s*(result(\s*@\(@\s*(?P<result>\b[\w$]+\b)\s*@\)@|))*\s*\Z',re.I)
callnameargspattern=re.compile(r'\s*(?P<name>\b[\w$]+\b)\s*@\(@\s*(?P<args>.*)\s*@\)@\s*\Z',re.I)
real16pattern = re.compile(r'([-+]?(?:\d+(?:\.\d*)?|\d*\.\d+))[dD]((?:[-+]?\d+)?)')
real8pattern = re.compile(r'([-+]?((?:\d+(?:\.\d*)?|\d*\.\d+))[eE]((?:[-+]?\d+)?)|(\d+\.\d*))')

_intentcallbackpattern = re.compile(r'intent\s*\(.*?\bcallback\b',re.I)
def _is_intent_callback(vdecl):
    for a in vdecl.get('attrspec',[]):
        if _intentcallbackpattern.match(a):
            return 1
    return 0

def _resolvenameargspattern(line):
    line = markouterparen(line)
    m1=nameargspattern.match(line)
    if m1: return m1.group('name'),m1.group('args'),m1.group('result')
    m1=callnameargspattern.match(line)
    if m1: return m1.group('name'),m1.group('args'),None
    return None,[],None
    
def analyzeline(m,case,line):
    global groupcounter,groupname,groupcache,grouplist,filepositiontext,\
           currentfilename,f77modulename,neededinterface,neededmodule,expectbegin,\
           gotnextfile,previous_context
    block=m.group('this')
    if case != 'multiline':
        previous_context = None
    if expectbegin and case not in ['begin','call','callfun','type'] \
       and not skipemptyends and groupcounter<1:
        newname=string.split(os.path.basename(currentfilename),'.')[0]
        outmess('analyzeline: no group yet. Creating program group with name "%s".\n'%newname)
        gotnextfile=0
        groupcounter=groupcounter+1
        groupname[groupcounter]='program'
        groupcache[groupcounter]={}
        grouplist[groupcounter]=[]
        groupcache[groupcounter]['body']=[]
        groupcache[groupcounter]['vars']={}
        groupcache[groupcounter]['block']='program'
        groupcache[groupcounter]['name']=newname
        groupcache[groupcounter]['from']='fromsky'
        expectbegin=0
    if case in ['begin','call','callfun']:
        # Crack line => block,name,args,result
        block = block.lower()
        if re.match(r'block\s*data',block,re.I): block='block data'
        if re.match(r'python\s*module',block,re.I): block='python module'
        name,args,result = _resolvenameargspattern(m.group('after'))
        if name is None:
            if block=='block data':
                name = '_BLOCK_DATA_'
            else:
                name = ''
            if block not in ['interface','block data']:
                outmess('analyzeline: No name/args pattern found for line.\n')

        previous_context = (block,name,groupcounter)
        if args: args=rmbadname(map(string.strip,string.split(markoutercomma(args),'@,@')))
        else: args=[]
        if '' in args:
            while '' in args:
                args.remove('')
            outmess('analyzeline: argument list is malformed (missing argument).\n')
            
        # end of crack line => block,name,args,result
        needmodule=0
        needinterface=0

        if case in ['call','callfun']:
            needinterface=1
            if not groupcache[groupcounter].has_key('args'): return
            if name not in groupcache[groupcounter]['args']:
                return
            for it in grouplist[groupcounter]:
                if it['name']==name: return
            if name in groupcache[groupcounter]['interfaced']: return
            block={'call':'subroutine','callfun':'function'}[case]
        if f77modulename and neededmodule==-1 and groupcounter<=1:
            neededmodule=groupcounter+2
            needmodule=1
            needinterface=1        
        # Create new block(s)
        groupcounter=groupcounter+1
        groupcache[groupcounter]={}
        grouplist[groupcounter]=[]
        if needmodule:
            if verbose>1:
                outmess('analyzeline: Creating module block %s\n'%`f77modulename`,0)
            groupname[groupcounter]='module'
            groupcache[groupcounter]['block']='python module'
            groupcache[groupcounter]['name']=f77modulename
            groupcache[groupcounter]['from']=''
            groupcache[groupcounter]['body']=[]
            groupcache[groupcounter]['externals']=[]
            groupcache[groupcounter]['interfaced']=[]
            groupcache[groupcounter]['vars']={}
            groupcounter=groupcounter+1
            groupcache[groupcounter]={}
            grouplist[groupcounter]=[]
        if needinterface:
            if verbose>1:
                outmess('analyzeline: Creating additional interface block.\n',0)
            groupname[groupcounter]='interface'
            groupcache[groupcounter]['block']='interface'
            groupcache[groupcounter]['name']='unknown_interface'
            groupcache[groupcounter]['from']='%s:%s'%(groupcache[groupcounter-1]['from'],groupcache[groupcounter-1]['name'])
            groupcache[groupcounter]['body']=[]
            groupcache[groupcounter]['externals']=[]
            groupcache[groupcounter]['interfaced']=[]
            groupcache[groupcounter]['vars']={}
            groupcounter=groupcounter+1
            groupcache[groupcounter]={}
            grouplist[groupcounter]=[]
        groupname[groupcounter]=block
        groupcache[groupcounter]['block']=block
        if not name: name='unknown_'+block
        groupcache[groupcounter]['prefix']=m.group('before')
        groupcache[groupcounter]['name']=rmbadname1(name)
        groupcache[groupcounter]['result']=result
        if groupcounter==1:
            groupcache[groupcounter]['from']=currentfilename
        else:
            if f77modulename and groupcounter==3:
                groupcache[groupcounter]['from']='%s:%s'%(groupcache[groupcounter-1]['from'],currentfilename)
            else:
                groupcache[groupcounter]['from']='%s:%s'%(groupcache[groupcounter-1]['from'],groupcache[groupcounter-1]['name'])
        for k in groupcache[groupcounter].keys():
            if not groupcache[groupcounter][k]: del groupcache[groupcounter][k]
        groupcache[groupcounter]['args']=args
        groupcache[groupcounter]['body']=[]
        groupcache[groupcounter]['externals']=[]
        groupcache[groupcounter]['interfaced']=[]
        groupcache[groupcounter]['vars']={}
        groupcache[groupcounter]['entry']={}
        # end of creation
        if block=='type':
            groupcache[groupcounter]['varnames'] = []

        if case in ['call','callfun']: # set parents variables
            if name not in groupcache[groupcounter-2]['externals']:
                groupcache[groupcounter-2]['externals'].append(name)
            groupcache[groupcounter]['vars']=copy.deepcopy(groupcache[groupcounter-2]['vars'])
            #try: del groupcache[groupcounter]['vars'][groupcache[groupcounter-2]['name']]
            #except: pass
            try: del groupcache[groupcounter]['vars'][name][groupcache[groupcounter]['vars'][name]['attrspec'].index('external')]
            except: pass
        if block in ['function','subroutine']: # set global attributes
            try: groupcache[groupcounter]['vars'][name]=appenddecl(groupcache[groupcounter]['vars'][name],groupcache[groupcounter-2]['vars'][''])
            except: pass
            if case=='callfun': # return type
                if result and groupcache[groupcounter]['vars'].has_key(result):
                    if not name==result:
                        groupcache[groupcounter]['vars'][name]=appenddecl(groupcache[groupcounter]['vars'][name],groupcache[groupcounter]['vars'][result])
            #if groupcounter>1: # name is interfaced
            try: groupcache[groupcounter-2]['interfaced'].append(name)
            except: pass
        if block=='function':
            t=typespattern[0].match(m.group('before')+' '+name)
            if t:
                typespec,selector,attr,edecl=cracktypespec0(t.group('this'),t.group('after'))
                updatevars(typespec,selector,attr,edecl)
        if case in ['call','callfun']:
            grouplist[groupcounter-1].append(groupcache[groupcounter])
            grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
            del grouplist[groupcounter]
            groupcounter=groupcounter-1 # end routine
            grouplist[groupcounter-1].append(groupcache[groupcounter])
            grouplist[groupcounter-1][-1]['body']=grouplist[groupcounter]
            del grouplist[groupcounter]
            groupcounter=groupcounter-1 # end interface
    elif case=='entry':
        name,args,result=_resolvenameargspattern(m.group('after'))
        if name is not None:
            if args:
                args=rmbadname(map(string.strip,string.split(markoutercomma(args),'@,@')))
            else: args=[]        
            assert result is None,`result`
            groupcache[groupcounter]['entry'][name] = args
            previous_context = ('entry',name,groupcounter)
    elif case=='type':
        typespec,selector,attr,edecl=cracktypespec0(block,m.group('after'))
        last_name = updatevars(typespec,selector,attr,edecl)
        if last_name is not None:
            previous_context = ('variable',last_name,groupcounter)
    elif case in ['dimension','intent','optional','required','external','public','private','intrisic']:
        edecl=groupcache[groupcounter]['vars']
        ll=m.group('after')
        i=string.find(ll,'::')
        if i<0 and case=='intent':
            i=string.find(markouterparen(ll),'@)@')-2
            ll=ll[:i+1]+'::'+ll[i+1:]
            i=string.find(ll,'::')
            if ll[i:]=='::' and groupcache[groupcounter].has_key('args'):
                outmess('All arguments will have attribute %s%s\n'%(m.group('this'),ll[:i]))
                ll = ll + string.join(groupcache[groupcounter]['args'],',')
        if i<0:i=0;pl=''
        else: pl=string.strip(ll[:i]);ll=ll[i+2:]
        ch = string.split(markoutercomma(pl),'@,@')
        if len(ch)>1:
            pl = ch[0]
            outmess('analyzeline: cannot handle multiple attributes without type specification. Ignoring %r.\n' % (','.join(ch[1:])))
        last_name = None
        for e in map(string.strip,string.split(markoutercomma(ll),'@,@')):
            m1=namepattern.match(e)
            if not m1:
                if case in ['public','private']: k=''
                else:
                    print m.groupdict()
                    outmess('analyzeline: no name pattern found in %s statement for %s. Skipping.\n'%(case,`e`))
                    continue
            else:
                k=rmbadname1(m1.group('name'))
            if not edecl.has_key(k): edecl[k]={}
            if case=='dimension': ap=case+m1.group('after')
            if case=='intent':
                ap=m.group('this')+pl
                if _intentcallbackpattern.match(ap):
                    if k not in groupcache[groupcounter]['args']:
                        if groupcounter>1 and \
                               string.find(groupcache[groupcounter-2]['name'],
                                           '__user__')==-1:
                            outmess('analyzeline: appending intent(callback) %s'\
                                    ' to %s arguments\n' % (k,groupcache[groupcounter]['name']))
                            groupcache[groupcounter]['args'].append(k)
                    else:
                        errmess('analyzeline: intent(callback) %s is already'\
                                ' in argument list' % (k))
            if case in ['optional','required','public','external','private','intrisic']: ap=case
            if edecl[k].has_key('attrspec'): edecl[k]['attrspec'].append(ap)
            else: edecl[k]['attrspec']=[ap]
            if case=='external':
                if groupcache[groupcounter]['block']=='program':
                    outmess('analyzeline: ignoring program arguments\n')
                    continue
                if k not in groupcache[groupcounter]['args']:
                    #outmess('analyzeline: ignoring external %s (not in arguments list)\n'%(`k`))
                    continue
                if not groupcache[groupcounter].has_key('externals'):
                    groupcache[groupcounter]['externals']=[]
                groupcache[groupcounter]['externals'].append(k)
            last_name = k
        groupcache[groupcounter]['vars']=edecl
        if last_name is not None:
            previous_context = ('variable',last_name,groupcounter)
    elif case=='parameter':
        edecl=groupcache[groupcounter]['vars']
        ll=string.strip(m.group('after'))[1:-1]
        last_name = None
        for e in string.split(markoutercomma(ll),'@,@'):
            try:
                k,initexpr=map(string.strip,string.split(e,'='))
            except:
                outmess('analyzeline: could not extract name,expr in parameter statement "%s" of "%s"\n'%(e,ll));continue
            params = get_parameters(edecl)
            k=rmbadname1(k)
            if not edecl.has_key(k): edecl[k]={}
            if edecl[k].has_key('=') and (not edecl[k]['=']==initexpr):
                outmess('analyzeline: Overwriting the value of parameter "%s" ("%s") with "%s".\n'%(k,edecl[k]['='],initexpr))
            t = determineexprtype(initexpr,params)
            if t:
                if t.get('typespec')=='real':
                    tt = list(initexpr)
                    for m in real16pattern.finditer(initexpr):
                        tt[m.start():m.end()] = list(\
                            initexpr[m.start():m.end()].lower().replace('d', 'e'))
                    initexpr = "".join(tt)
                elif t.get('typespec')=='complex':
                    initexpr = initexpr[1:].lower().replace('d','e').\
                               replace(',','+1j*(')
            try:
                v = eval(initexpr,{},params)
            except (SyntaxError,NameError),msg:
                errmess('analyzeline: Failed to evaluate %r. Ignoring: %s\n'\
                        % (initexpr, msg))
                continue
            edecl[k]['='] = repr(v)
            if edecl[k].has_key('attrspec'):
                edecl[k]['attrspec'].append('parameter')
            else: edecl[k]['attrspec']=['parameter']
            last_name = k
        groupcache[groupcounter]['vars']=edecl
        if last_name is not None:
            previous_context = ('variable',last_name,groupcounter)
    elif case=='implicit':
        if string.lower(string.strip(m.group('after')))=='none':
            groupcache[groupcounter]['implicit']=None
        elif m.group('after'):
            if groupcache[groupcounter].has_key('implicit'):
                impl=groupcache[groupcounter]['implicit']
            else: impl={}
            if impl is None:
                outmess('analyzeline: Overwriting earlier "implicit none" statement.\n')
                impl={}
            for e in string.split(markoutercomma(m.group('after')),'@,@'):
                decl={}
                m1=re.match(r'\s*(?P<this>.*?)\s*(\(\s*(?P<after>[a-z-, ]+)\s*\)\s*|)\Z',e,re.I)
                if not m1:
                    outmess('analyzeline: could not extract info of implicit statement part "%s"\n'%(e));continue
                m2=typespattern4implicit.match(m1.group('this'))
                if not m2:
                    outmess('analyzeline: could not extract types pattern of implicit statement part "%s"\n'%(e));continue
                typespec,selector,attr,edecl=cracktypespec0(m2.group('this'),m2.group('after'))
                kindselect,charselect,typename=cracktypespec(typespec,selector)
                decl['typespec']=typespec
                decl['kindselector']=kindselect
                decl['charselector']=charselect
                decl['typename']=typename
                for k in decl.keys():
                    if not decl[k]: del decl[k]
                for r in string.split(markoutercomma(m1.group('after')),'@,@'):
                    if '-' in r:
                        try: begc,endc=map(string.strip,string.split(r,'-'))
                        except:
                            outmess('analyzeline: expected "<char>-<char>" instead of "%s" in range list of implicit statement\n'%r);continue
                    else: begc=endc=string.strip(r)
                    if not len(begc)==len(endc)==1:
                        outmess('analyzeline: expected "<char>-<char>" instead of "%s" in range list of implicit statement (2)\n'%r);continue
                    for o in range(ord(begc),ord(endc)+1):
                        impl[chr(o)]=decl
            groupcache[groupcounter]['implicit']=impl
    elif case=='data':
        ll=[]
        dl='';il='';f=0;fc=1
        for c in m.group('after'):
            if c=="'": fc=not fc
            if c=='/' and fc: f=f+1;continue
            if f==0: dl=dl+c
            elif f==1: il=il+c
            elif f==2:
                dl = dl.strip()
                if dl.startswith(','):
                    dl = dl[1:].strip()
                ll.append([dl,il])
                dl=c;il='';f=0
        if f==2:
            dl = dl.strip()
            if dl.startswith(','):
                dl = dl[1:].strip()
            ll.append([dl,il])
        vars={}
        if groupcache[groupcounter].has_key('vars'):
            vars=groupcache[groupcounter]['vars']
        last_name = None
        for l in ll:
            l=map(string.strip,l)
            if l[0][0]==',':l[0]=l[0][1:]
            if l[0][0]=='(':
                outmess('analyzeline: implied-DO list "%s" is not supported. Skipping.\n'%l[0])
                continue
            #if '(' in l[0]:
            #    #outmess('analyzeline: ignoring this data statement.\n')
            #    continue
            i=0;j=0;llen=len(l[1])
            for v in rmbadname(map(string.strip,string.split(markoutercomma(l[0]),'@,@'))):
                fc=0
                while (i<llen) and (fc or not l[1][i]==','):
                    if l[1][i]=="'": fc=not fc
                    i=i+1
                i=i+1
                #v,l[1][j:i-1]=name,initvalue
                if not vars.has_key(v):
                    vars[v]={}
                if vars[v].has_key('=') and not vars[v]['=']==l[1][j:i-1]:
                    outmess('analyzeline: changing init expression of "%s" ("%s") to "%s"\n'%(v,vars[v]['='],l[1][j:i-1]))
                vars[v]['=']=l[1][j:i-1]
                j=i
                last_name = v
        groupcache[groupcounter]['vars']=vars
        if last_name is not None:
            previous_context = ('variable',last_name,groupcounter)
    elif case=='common':
        line=string.strip(m.group('after'))
        if not line[0]=='/':line='//'+line
        cl=[]
        f=0;bn='';ol=''
        for c in line:
            if c=='/':f=f+1;continue
            if f>=3:
                bn = string.strip(bn)
                if not bn: bn='_BLNK_'
                cl.append([bn,ol])
                f=f-2;bn='';ol=''
            if f%2: bn=bn+c
            else: ol=ol+c
        bn = string.strip(bn)
        if not bn: bn='_BLNK_'
        cl.append([bn,ol])
        commonkey={}
        if groupcache[groupcounter].has_key('common'):
            commonkey=groupcache[groupcounter]['common']
        for c in cl:
            if commonkey.has_key(c[0]):
                outmess('analyzeline: previously defined common block encountered. Skipping.\n')
                continue
            commonkey[c[0]]=[]
            for i in map(string.strip,string.split(markoutercomma(c[1]),'@,@')):
                if i: commonkey[c[0]].append(i)
        groupcache[groupcounter]['common']=commonkey
        previous_context = ('common',bn,groupcounter)
    elif case=='use':
        m1=re.match(r'\A\s*(?P<name>\b[\w]+\b)\s*((,(\s*\bonly\b\s*:|(?P<notonly>))\s*(?P<list>.*))|)\s*\Z',m.group('after'),re.I)
        if m1:
            mm=m1.groupdict()
            if not groupcache[groupcounter].has_key('use'): groupcache[groupcounter]['use']={}
            name=m1.group('name')
            groupcache[groupcounter]['use'][name]={}
            isonly=0
            if mm.has_key('list') and mm['list'] is not None:
                if mm.has_key('notonly') and mm['notonly'] is None:isonly=1
                groupcache[groupcounter]['use'][name]['only']=isonly
                ll=map(string.strip,string.split(mm['list'],','))
                rl={}
                for l in ll:
                    if '=' in l:
                        m2=re.match(r'\A\s*(?P<local>\b[\w]+\b)\s*=\s*>\s*(?P<use>\b[\w]+\b)\s*\Z',l,re.I)
                        if m2: rl[string.strip(m2.group('local'))]=string.strip(m2.group('use'))
                        else:
                            outmess('analyzeline: Not local=>use pattern found in %s\n'%`l`)
                    else:
                        rl[l]=l
                    groupcache[groupcounter]['use'][name]['map']=rl
            else:
                pass
            
        else:
            print m.groupdict()
            outmess('analyzeline: Could not crack the use statement.\n')
    elif case in ['f2pyenhancements']:
        if not groupcache[groupcounter].has_key ('f2pyenhancements'):
            groupcache[groupcounter]['f2pyenhancements'] = {}
        d = groupcache[groupcounter]['f2pyenhancements']
        if m.group('this')=='usercode' and d.has_key('usercode'):
            if type(d['usercode']) is type(''):
                d['usercode'] = [d['usercode']]
            d['usercode'].append(m.group('after'))
        else:
            d[m.group('this')] = m.group('after')
    elif case=='multiline':
        if previous_context is None:
            if verbose:
                outmess('analyzeline: No context for multiline block.\n')
            return
        gc = groupcounter
        #gc = previous_context[2]
        appendmultiline(groupcache[gc],
                        previous_context[:2],
                        m.group('this'))
    else:
        if verbose>1:
            print m.groupdict()
            outmess('analyzeline: No code implemented for line.\n')

def appendmultiline(group, context_name,ml):
    if not group.has_key('f2pymultilines'):
        group['f2pymultilines'] = {}
    d = group['f2pymultilines']
    if not d.has_key(context_name):
        d[context_name] = []
    d[context_name].append(ml)
    return

def cracktypespec0(typespec,ll):
    selector=None
    attr=None
    if re.match(r'double\s*complex',typespec,re.I): typespec='double complex'
    elif re.match(r'double\s*precision',typespec,re.I): typespec='double precision'
    else: typespec=string.lower(string.strip(typespec))
    m1=selectpattern.match(markouterparen(ll))
    if not m1:
        outmess('cracktypespec0: no kind/char_selector pattern found for line.\n')
        return
    d=m1.groupdict()
    for k in d.keys(): d[k]=unmarkouterparen(d[k])
    if typespec in ['complex','integer','logical','real','character','type']:
        selector=d['this']
        ll=d['after']
    i=string.find(ll,'::')
    if i>=0:
        attr=string.strip(ll[:i])
        ll=ll[i+2:]
    return typespec,selector,attr,ll
#####
namepattern=re.compile(r'\s*(?P<name>\b[\w]+\b)\s*(?P<after>.*)\s*\Z',re.I)
kindselector=re.compile(r'\s*(\(\s*(kind\s*=)?\s*(?P<kind>.*)\s*\)|[*]\s*(?P<kind2>.*?))\s*\Z',re.I)
charselector=re.compile(r'\s*(\((?P<lenkind>.*)\)|[*]\s*(?P<charlen>.*))\s*\Z',re.I)
lenkindpattern=re.compile(r'\s*(kind\s*=\s*(?P<kind>.*?)\s*(@,@\s*len\s*=\s*(?P<len>.*)|)|(len\s*=\s*|)(?P<len2>.*?)\s*(@,@\s*(kind\s*=\s*|)(?P<kind2>.*)|))\s*\Z',re.I)
lenarraypattern=re.compile(r'\s*(@\(@\s*(?!/)\s*(?P<array>.*?)\s*@\)@\s*[*]\s*(?P<len>.*?)|([*]\s*(?P<len2>.*?)|)\s*(@\(@\s*(?!/)\s*(?P<array2>.*?)\s*@\)@|))\s*(=\s*(?P<init>.*?)|(@\(@|)/\s*(?P<init2>.*?)\s*/(@\)@|)|)\s*\Z',re.I)
def removespaces(expr):
    expr=string.strip(expr)
    if len(expr)<=1: return expr
    expr2=expr[0]
    for i in range(1,len(expr)-1):
        if expr[i]==' ' and \
           ((expr[i+1] in "()[]{}= ") or (expr[i-1] in "()[]{}= ")): continue
        expr2=expr2+expr[i]
    expr2=expr2+expr[-1]
    return expr2
def markinnerspaces(line):
    l='';f=0
    cc='\''
    cc1='"'
    cb=''
    for c in line:
        if cb=='\\' and c in ['\\','\'','"']:
            l=l+c;
            cb=c
            continue 
        if f==0 and c in ['\'','"']: cc=c; cc1={'\'':'"','"':'\''}[c]
        if c==cc:f=f+1
        elif c==cc:f=f-1
        elif c==' ' and f==1: l=l+'@_@'; continue
        l=l+c;cb=c
    return l
def updatevars(typespec,selector,attrspec,entitydecl):
    global groupcache,groupcounter
    last_name = None
    kindselect,charselect,typename=cracktypespec(typespec,selector)
    if attrspec:
        attrspec=map(string.strip,string.split(markoutercomma(attrspec),'@,@'))
        l = []
        c = re.compile(r'(?P<start>[a-zA-Z]+)')
        for a in attrspec:
            m = c.match(a)
            if m:
                s = string.lower(m.group('start'))
                a = s + a[len(s):]
            l.append(a)
        attrspec = l
    el=map(string.strip,string.split(markoutercomma(entitydecl),'@,@'))
    el1=[]
    for e in el:
        for e1 in map(string.strip,string.split(markoutercomma(removespaces(markinnerspaces(e)),comma=' '),'@ @')):
            if e1: el1.append(string.replace(e1,'@_@',' '))
    for e in el1:
        m=namepattern.match(e)
        if not m:
            outmess('updatevars: no name pattern found for entity=%s. Skipping.\n'%(`e`))
            continue
        ename=rmbadname1(m.group('name'))
        edecl={}
        if groupcache[groupcounter]['vars'].has_key(ename):
            edecl=groupcache[groupcounter]['vars'][ename].copy()
            has_typespec = edecl.has_key('typespec')
            if not has_typespec:
                edecl['typespec']=typespec
            elif typespec and (not typespec==edecl['typespec']):
                outmess('updatevars: attempt to change the type of "%s" ("%s") to "%s". Ignoring.\n' % (ename,edecl['typespec'],typespec))
            if not edecl.has_key('kindselector'):
                edecl['kindselector']=copy.copy(kindselect)
            elif kindselect:
                for k in kindselect.keys():
                    if edecl['kindselector'].has_key(k) and (not kindselect[k]==edecl['kindselector'][k]):
                        outmess('updatevars: attempt to change the kindselector "%s" of "%s" ("%s") to "%s". Ignoring.\n' % (k,ename,edecl['kindselector'][k],kindselect[k]))
                    else: edecl['kindselector'][k]=copy.copy(kindselect[k])
            if not edecl.has_key('charselector') and charselect:
                if not has_typespec:
                    edecl['charselector']=charselect
                else:
                    errmess('updatevars:%s: attempt to change empty charselector to %r. Ignoring.\n' \
                            %(ename,charselect))
            elif charselect:
                for k in charselect.keys():
                    if edecl['charselector'].has_key(k) and (not charselect[k]==edecl['charselector'][k]):
                        outmess('updatevars: attempt to change the charselector "%s" of "%s" ("%s") to "%s". Ignoring.\n' % (k,ename,edecl['charselector'][k],charselect[k]))
                    else: edecl['charselector'][k]=copy.copy(charselect[k])
            if not edecl.has_key('typename'):
                edecl['typename']=typename
            elif typename and (not edecl['typename']==typename):
                outmess('updatevars: attempt to change the typename of "%s" ("%s") to "%s". Ignoring.\n' % (ename,edecl['typename'],typename))
            if not edecl.has_key('attrspec'):
                edecl['attrspec']=copy.copy(attrspec)
            elif attrspec:
                for a in attrspec:
                    if a not in edecl['attrspec']:
                        edecl['attrspec'].append(a)
        else:
            edecl['typespec']=copy.copy(typespec)
            edecl['kindselector']=copy.copy(kindselect)
            edecl['charselector']=copy.copy(charselect)
            edecl['typename']=typename
            edecl['attrspec']=copy.copy(attrspec)
        if m.group('after'):
            m1=lenarraypattern.match(markouterparen(m.group('after')))
            if m1:
                d1=m1.groupdict()
                for lk in ['len','array','init']:
                    if d1[lk+'2'] is not None: d1[lk]=d1[lk+'2']; del d1[lk+'2']
                for k in d1.keys():
                    if d1[k] is not None: d1[k]=unmarkouterparen(d1[k])
                    else: del d1[k]
                if d1.has_key('len') and d1.has_key('array'):
                    if d1['len']=='':
                        d1['len']=d1['array']
                        del d1['array']
                    else:
                        d1['array']=d1['array']+','+d1['len']
                        del d1['len']
                        errmess('updatevars: "%s %s" is mapped to "%s %s(%s)"\n'%(typespec,e,typespec,ename,d1['array']))
                if d1.has_key('array'):
                    dm = 'dimension(%s)'%d1['array']
                    if not edecl.has_key('attrspec') or (not edecl['attrspec']):
                        edecl['attrspec']=[dm]
                    else:
                        edecl['attrspec'].append(dm)
                        for dm1 in edecl['attrspec']:
                            if dm1[:9]=='dimension' and dm1!=dm:
                                del edecl['attrspec'][-1]
                                errmess('updatevars:%s: attempt to change %r to %r. Ignoring.\n' \
                                        % (ename,dm1,dm))
                                break
                            
                if d1.has_key('len'):
                    if typespec in ['complex','integer','logical','real']:
                        if (not edecl.has_key('kindselector')) or (not edecl['kindselector']):
                            edecl['kindselector']={}
                        edecl['kindselector']['*']=d1['len']
                    elif typespec == 'character':
                        if (not edecl.has_key('charselector')) or (not edecl['charselector']): edecl['charselector']={}
                        if edecl['charselector'].has_key('len'): del edecl['charselector']['len']
                        edecl['charselector']['*']=d1['len']
                if d1.has_key('init'):
                    if edecl.has_key('=') and (not edecl['=']==d1['init']):
                        outmess('updatevars: attempt to change the init expression of "%s" ("%s") to "%s". Ignoring.\n' % (ename,edecl['='],d1['init']))
                    else:
                        edecl['=']=d1['init']
            else:
                outmess('updatevars: could not crack entity declaration "%s". Ignoring.\n'%(ename+m.group('after')))
        for k in edecl.keys():
            if not edecl[k]: del edecl[k]
        groupcache[groupcounter]['vars'][ename]=edecl
        if groupcache[groupcounter].has_key('varnames'):
            groupcache[groupcounter]['varnames'].append(ename)
        last_name = ename
    return last_name

def cracktypespec(typespec,selector):
    kindselect=None
    charselect=None
    typename=None
    if selector:
        if typespec in ['complex','integer','logical','real']:
            kindselect=kindselector.match(selector)
            if not kindselect:
                outmess('cracktypespec: no kindselector pattern found for %s\n'%(`selector`))
                return
            kindselect=kindselect.groupdict()
            kindselect['*']=kindselect['kind2']
            del kindselect['kind2']
            for k in kindselect.keys():
                if not kindselect[k]: del kindselect[k]
            for k,i in kindselect.items():
                kindselect[k] = rmbadname1(i)
        elif typespec=='character':
            charselect=charselector.match(selector)
            if not charselect:
                outmess('cracktypespec: no charselector pattern found for %s\n'%(`selector`))
                return
            charselect=charselect.groupdict()
            charselect['*']=charselect['charlen']
            del charselect['charlen']
            if charselect['lenkind']:
                lenkind=lenkindpattern.match(markoutercomma(charselect['lenkind']))
                lenkind=lenkind.groupdict()
                for lk in ['len','kind']:
                    if lenkind[lk+'2']:
                        lenkind[lk]=lenkind[lk+'2']
                    charselect[lk]=lenkind[lk]
                    del lenkind[lk+'2']
            del charselect['lenkind']
            for k in charselect.keys():
                if not charselect[k]: del charselect[k]
            for k,i in charselect.items():
                charselect[k] = rmbadname1(i)
        elif typespec=='type':
            typename=re.match(r'\s*\(\s*(?P<name>\w+)\s*\)',selector,re.I)
            if typename: typename=typename.group('name')
            else: outmess('cracktypespec: no typename found in %s\n'%(`typespec+selector`))
        else:
            outmess('cracktypespec: no selector used for %s\n'%(`selector`))
    return kindselect,charselect,typename
######
def setattrspec(decl,attr,force=0):
    if not decl: decl={}
    if not attr: return decl
    if not decl.has_key('attrspec'):
        decl['attrspec']=[attr]
        return decl
    if force: decl['attrspec'].append(attr)
    if attr in decl['attrspec']: return decl
    if attr=='static' and 'automatic' not in decl['attrspec']:
        decl['attrspec'].append(attr)
    elif attr=='automatic' and 'static' not in decl['attrspec']:
        decl['attrspec'].append(attr)
    elif attr=='public' and 'private' not in decl['attrspec']:
        decl['attrspec'].append(attr)
    elif attr=='private' and 'public' not in decl['attrspec']:
        decl['attrspec'].append(attr)
    else:
        decl['attrspec'].append(attr)
    return decl
def setkindselector(decl,sel,force=0):
    if not decl: decl={}
    if not sel: return decl
    if not decl.has_key('kindselector'):
        decl['kindselector']=sel
        return decl
    for k in sel.keys():
        if force or not decl['kindselector'].has_key(k):
            decl['kindselector'][k]=sel[k]
    return decl
def setcharselector(decl,sel,force=0):
    if not decl: decl={}
    if not sel: return decl
    if not decl.has_key('charselector'):
        decl['charselector']=sel
        return decl
    for k in sel.keys():
        if force or not decl['charselector'].has_key(k):
            decl['charselector'][k]=sel[k]
    return decl
def getblockname(block,unknown='unknown'):
    if block.has_key('name'): return block['name']
    return unknown
###### post processing
def setmesstext(block):
    global filepositiontext
    try: filepositiontext='In: %s:%s\n'%(block['from'],block['name'])
    except: pass

def get_usedict(block):
    usedict = {}
    if block.has_key('parent_block'):
        usedict = get_usedict(block['parent_block'])
    if block.has_key('use'):
        usedict.update(block['use'])
    return usedict

def get_useparameters(block, param_map=None):
    global f90modulevars
    if param_map is None:
        param_map = {}
    usedict = get_usedict(block)
    if not usedict:
        return param_map
    for usename,mapping in usedict.items():
        usename = string.lower(usename)
        if not f90modulevars.has_key(usename):
            continue
        mvars = f90modulevars[usename]
        params = get_parameters(mvars)
        if not params:
            continue
        # XXX: apply mapping
        if mapping:
            errmess('get_useparameters: mapping for %s not impl.' % (mapping))
        for k,v in params.items():
            if param_map.has_key(k):
                outmess('get_useparameters: overriding parameter %s with'\
                        ' value from module %s' % (`k`,`usename`))
            param_map[k] = v
    return param_map

def postcrack2(block,tab='',param_map=None):
    global f90modulevars
    if not f90modulevars:
        return block
    if type(block)==types.ListType:
        ret = []
        for g in block:
            g = postcrack2(g,tab=tab+'\t',param_map=param_map)
            ret.append(g)
        return ret
    setmesstext(block)
    outmess('%sBlock: %s\n'%(tab,block['name']),0)

    if param_map is None:
        param_map = get_useparameters(block)

    if param_map is not None and block.has_key('vars'):
        vars = block['vars']
        for n in vars.keys():
            var = vars[n]
            if var.has_key('kindselector'):
                kind = var['kindselector']
                if kind.has_key('kind'):
                    val = kind['kind']
                    if param_map.has_key(val):
                        kind['kind'] = param_map[val]
    new_body = []
    for b in block['body']:
        b = postcrack2(b,tab=tab+'\t',param_map=param_map)
        new_body.append(b)
    block['body'] = new_body

    return block

def postcrack(block,args=None,tab=''):
    """
    TODO:
          function return values
          determine expression types if in argument list
    """
    global usermodules,onlyfunctions
    if type(block)==types.ListType:
        gret=[]
        uret=[]
        for g in block:
            setmesstext(g)
            g=postcrack(g,tab=tab+'\t')
            if g.has_key('name') and string.find(g['name'],'__user__')>=0: # sort user routines to appear first
                uret.append(g)
            else:
                gret.append(g)
        return uret+gret
    setmesstext(block)
    if (not type(block)==types.DictType) and not block.has_key('block'):
        raise 'postcrack: Expected block dictionary instead of ',block
    if block.has_key('name') and not block['name']=='unknown_interface':
        outmess('%sBlock: %s\n'%(tab,block['name']),0)
    blocktype=block['block']
    block=analyzeargs(block)
    block=analyzecommon(block)
    block['vars']=analyzevars(block)
    block['sortvars']=sortvarnames(block['vars'])
    if block.has_key('args') and block['args']:
        args=block['args']
    block['body']=analyzebody(block,args,tab=tab)

    userisdefined=[]
##     fromuser = []
    if block.has_key('use'):
        useblock=block['use']
        for k in useblock.keys():
            if string.find(k,'__user__')>=0:
                userisdefined.append(k)
##                 if useblock[k].has_key('map'):
##                     for n in useblock[k]['map'].values():
##                         if n not in fromuser: fromuser.append(n)
    else: useblock={}
    name=''
    if block.has_key('name'):name=block['name']
    if block.has_key('externals') and block['externals']:# and not userisdefined: # Build a __user__ module
        interfaced=[]
        if block.has_key('interfaced'): interfaced=block['interfaced']
        mvars=copy.copy(block['vars'])
        if name: mname=name+'__user__routines'
        else: mname='unknown__user__routines'
        if mname in userisdefined:
            i=1
            while '%s_%i'%(mname,i) in userisdefined: i=i+1
            mname='%s_%i'%(mname,i)
        interface={'block':'interface','body':[],'vars':{},'name':name+'_user_interface'}
        for e in block['externals']:
##             if e in fromuser:
##                 outmess('  Skipping %s that is defined explicitly in another use statement\n'%(`e`))
##                 continue
            if e in interfaced:
                edef=[]
                j=-1
                for b in block['body']:
                    j=j+1
                    if b['block']=='interface':
                        i=-1
                        for bb in b['body']:
                            i=i+1
                            if bb.has_key('name') and bb['name']==e:
                                edef=copy.copy(bb)
                                del b['body'][i]
                                break
                        if edef:
                            if not b['body']: del block['body'][j]
                            del interfaced[interfaced.index(e)]
                            break
                interface['body'].append(edef)
            else:
                if mvars.has_key(e) and not isexternal(mvars[e]):
                    interface['vars'][e]=mvars[e]
        if interface['vars'] or interface['body']:
            block['interfaced']=interfaced
            mblock={'block':'python module','body':[interface],'vars':{},'name':mname,'interfaced':block['externals']}
            useblock[mname]={}
            usermodules.append(mblock)
    if useblock:
        block['use']=useblock
    return block

def sortvarnames(vars):
    indep = []
    dep = []
    for v in vars.keys():
        if vars[v].has_key('depend') and vars[v]['depend']:
            dep.append(v)
            #print '%s depends on %s'%(v,vars[v]['depend'])
        else: indep.append(v)
    n = len(dep)
    i = 0
    while dep: #XXX: How to catch dependence cycles correctly?
        v = dep[0]
        fl = 0
        for w in dep[1:]:
            if w in vars[v]['depend']:
                fl = 1
                break
        if fl:
            dep = dep[1:]+[v]
            i = i + 1
            if i>n:
                errmess('sortvarnames: failed to compute dependencies because'
                        ' of cyclic dependencies between '
                        +string.join(dep,', ')+'\n')
                indep = indep + dep
                break
        else:
            indep.append(v)
            dep = dep[1:]
            n = len(dep)
            i = 0
    #print indep
    return indep

def analyzecommon(block):
    if not hascommon(block): return block
    commonvars=[]
    for k in block['common'].keys():
        comvars=[]
        for e in block['common'][k]:
            m=re.match(r'\A\s*\b(?P<name>.*?)\b\s*(\((?P<dims>.*?)\)|)\s*\Z',e,re.I)
            if m:
                dims=[]
                if m.group('dims'):
                    dims=map(string.strip,string.split(markoutercomma(m.group('dims')),'@,@'))
                n=string.strip(m.group('name'))
                if block['vars'].has_key(n):
                    if block['vars'][n].has_key('attrspec'):
                        block['vars'][n]['attrspec'].append('dimension(%s)'%(string.join(dims,',')))
                    else:
                        block['vars'][n]['attrspec']=['dimension(%s)'%(string.join(dims,','))]
                else:
                    if dims:
                        block['vars'][n]={'attrspec':['dimension(%s)'%(string.join(dims,','))]}
                    else: block['vars'][n]={}
                if n not in commonvars: commonvars.append(n)
            else:
                n=e
                errmess('analyzecommon: failed to extract "<name>[(<dims>)]" from "%s" in common /%s/.\n'%(e,k))
            comvars.append(n)
        block['common'][k]=comvars
    if not block.has_key('commonvars'):
        block['commonvars']=commonvars
    else:
        block['commonvars']=block['commonvars']+commonvars
    return block
def analyzebody(block,args,tab=''):
    global usermodules,skipfuncs,onlyfuncs,f90modulevars
    setmesstext(block)
    body=[]
    for b in block['body']:
        b['parent_block'] = block
        if b['block'] in ['function','subroutine']:
            if args is not None and b['name'] not in args:
                continue
            else:
                as=b['args']
            if b['name'] in skipfuncs:
                continue
            if onlyfuncs and b['name'] not in onlyfuncs:
                continue
        else: as=args
        b=postcrack(b,as,tab=tab+'\t')
        if b['block']=='interface' and not b['body']:
            if not b.has_key('f2pyenhancements'):
                continue
        if string.replace(b['block'],' ','')=='pythonmodule':
            usermodules.append(b)
        else:
            if b['block']=='module':
                f90modulevars[b['name']] = b['vars']
            body.append(b)
    return body
def buildimplicitrules(block):
    setmesstext(block)
    implicitrules=defaultimplicitrules
    attrrules={}
    if block.has_key('implicit'):
        if block['implicit'] is None:
            implicitrules=None
            if verbose>1:
                outmess('buildimplicitrules: no implicit rules for routine %s.\n'%`block['name']`)
        else:
            for k in block['implicit'].keys():
                if block['implicit'][k].get('typespec') not in ['static','automatic']:
                    implicitrules[k]=block['implicit'][k]
                else:
                    attrrules[k]=block['implicit'][k]['typespec']
    return implicitrules,attrrules

def myeval(e,g=None,l=None):
    r = eval(e,g,l)
    if type(r) in [type(0),type(0.0)]:
        return r
    raise ValueError,'r=%r' % (r)

getlincoef_re_1 = re.compile(r'\A\b\w+\b\Z',re.I)
def getlincoef(e,xset): # e = a*x+b ; x in xset
    try:
        c = int(myeval(e,{},{}))
        return 0,c,None
    except: pass
    if getlincoef_re_1.match(e):
        return 1,0,e
    len_e = len(e)
    for x in xset:
        if len(x)>len_e: continue
        re_1 = re.compile(r'(?P<before>.*?)\b'+x+r'\b(?P<after>.*)',re.I)
        m = re_1.match(e)
        if m:
            try:
                m1 = re_1.match(e)
                while m1:
                    ee = '%s(%s)%s'%(m1.group('before'),0,m1.group('after'))
                    m1 = re_1.match(ee)
                b = myeval(ee,{},{})
                m1 = re_1.match(e)
                while m1:
                    ee = '%s(%s)%s'%(m1.group('before'),1,m1.group('after'))
                    m1 = re_1.match(ee)
                a = myeval(ee,{},{}) - b
                m1 = re_1.match(e)
                while m1:
                    ee = '%s(%s)%s'%(m1.group('before'),0.5,m1.group('after'))
                    m1 = re_1.match(ee)
                c = myeval(ee,{},{})
                if (a*0.5+b==c):
                    return a,b,x
            except: pass
            break    
    return None,None,None

_varname_match = re.compile(r'\A[a-z]\w*\Z').match
def getarrlen(dl,args,star='*'):
    edl = []
    try: edl.append(myeval(dl[0],{},{}))
    except: edl.append(dl[0])
    try: edl.append(myeval(dl[1],{},{}))
    except: edl.append(dl[1])
    if type(edl[0]) is type(0):
        p1 = 1-edl[0]
        if p1==0: d = str(dl[1])
        elif p1<0: d = '%s-%s'%(dl[1],-p1)
        else: d = '%s+%s'%(dl[1],p1)
    elif type(edl[1]) is type(0):
        p1 = 1+edl[1]
        if p1==0: d='-(%s)' % (dl[0])
        else: d='%s-(%s)' % (p1,dl[0])
    else: d = '%s-(%s)+1'%(dl[1],dl[0])
    try: return `myeval(d,{},{})`,None,None
    except: pass
    d1,d2=getlincoef(dl[0],args),getlincoef(dl[1],args)
    if None not in [d1[0],d2[0]]:
        if (d1[0],d2[0])==(0,0):
            return `d2[1]-d1[1]+1`,None,None
        b = d2[1] - d1[1] + 1
        d1 = (d1[0],0,d1[2])
        d2 = (d2[0],b,d2[2])
        if d1[0]==0 and d2[2] in args:
            if b<0: return '%s * %s - %s'%(d2[0],d2[2],-b),d2[2],'+%s)/(%s)'%(-b,d2[0])
            elif b: return '%s * %s + %s'%(d2[0],d2[2],b),d2[2],'-%s)/(%s)'%(b,d2[0])
            else: return '%s * %s'%(d2[0],d2[2]),d2[2],')/(%s)'%(d2[0])
        if d2[0]==0 and d1[2] in args:

            if b<0: return '%s * %s - %s'%(-d1[0],d1[2],-b),d1[2],'+%s)/(%s)'%(-b,-d1[0])
            elif b: return '%s * %s + %s'%(-d1[0],d1[2],b),d1[2],'-%s)/(%s)'%(b,-d1[0])
            else: return '%s * %s'%(-d1[0],d1[2]),d1[2],')/(%s)'%(-d1[0])
        if d1[2]==d2[2] and d1[2] in args:
            a = d2[0] - d1[0]
            if not a: return `b`,None,None
            if b<0: return '%s * %s - %s'%(a,d1[2],-b),d2[2],'+%s)/(%s)'%(-b,a)
            elif b: return '%s * %s + %s'%(a,d1[2],b),d2[2],'-%s)/(%s)'%(b,a)
            else: return '%s * %s'%(a,d1[2]),d2[2],')/(%s)'%(a)
        if d1[0]==d2[0]==1:
            c = str(d1[2])
            if c not in args:
                if _varname_match(c):
                    outmess('\tgetarrlen:variable "%s" undefined\n' % (c))
                c = '(%s)'%c
            if b==0: d='%s-%s' % (d2[2],c)
            elif b<0: d='%s-%s-%s' % (d2[2],c,-b)
            else: d='%s-%s+%s' % (d2[2],c,b)
        elif d1[0]==0:
            c2 = str(d2[2])
            if c2 not in args:
                if _varname_match(c2):
                    outmess('\tgetarrlen:variable "%s" undefined\n' % (c2))
                c2 = '(%s)'%c2
            if d2[0]==1: pass
            elif d2[0]==-1: c2='-%s' %c2
            else: c2='%s*%s'%(d2[0],c2)

            if b==0: d=c2
            elif b<0: d='%s-%s' % (c2,-b)
            else: d='%s+%s' % (c2,b)
        elif d2[0]==0:
            c1 = str(d1[2])
            if c1 not in args:
                if _varname_match(c1):
                    outmess('\tgetarrlen:variable "%s" undefined\n' % (c1))
                c1 = '(%s)'%c1
            if d1[0]==1: c1='-%s'%c1
            elif d1[0]==-1: c1='+%s'%c1
            elif d1[0]<0: c1='+%s*%s'%(-d1[0],c1)
            else: c1 = '-%s*%s' % (d1[0],c1)

            if b==0: d=c1
            elif b<0: d='%s-%s' % (c1,-b)
            else: d='%s+%s' % (c1,b)
        else:
            c1 = str(d1[2])
            if c1 not in args:
                if _varname_match(c1):
                    outmess('\tgetarrlen:variable "%s" undefined\n' % (c1))
                c1 = '(%s)'%c1
            if d1[0]==1: c1='-%s'%c1
            elif d1[0]==-1: c1='+%s'%c1
            elif d1[0]<0: c1='+%s*%s'%(-d1[0],c1)
            else: c1 = '-%s*%s' % (d1[0],c1)
            
            c2 = str(d2[2])
            if c2 not in args:
                if _varname_match(c2):
                    outmess('\tgetarrlen:variable "%s" undefined\n' % (c2))
                c2 = '(%s)'%c2
            if d2[0]==1: pass
            elif d2[0]==-1: c2='-%s' %c2
            else: c2='%s*%s'%(d2[0],c2)

            if b==0: d='%s%s' % (c2,c1)
            elif b<0: d='%s%s-%s' % (c2,c1,-b)
            else: d='%s%s+%s' % (c2,c1,b)
    return d,None,None

word_pattern = re.compile(r'\b[a-z][\w$]*\b',re.I)

def _get_depend_dict(name, vars, deps):
    if vars.has_key(name):
        words = vars[name].get('depend',[])

        if vars[name].has_key('=') and not isstring(vars[name]):
            for word in word_pattern.findall(vars[name]['=']):
                if word not in words and vars.has_key(word):
                    words.append(word)
        for word in words[:]:
            for w in deps.get(word,[]) \
                    or _get_depend_dict(word, vars, deps):
                if w not in words:
                    words.append(w)
    else:
        outmess('_get_depend_dict: no dependence info for %s\n' % (`name`))
        words = []
    deps[name] = words
    return words

def _calc_depend_dict(vars):
    names = vars.keys()
    depend_dict = {}
    for n in names:
        _get_depend_dict(n, vars, depend_dict)
    return depend_dict

def get_sorted_names(vars):
    """
    """
    depend_dict = _calc_depend_dict(vars)
    names = []
    for name in depend_dict.keys():
        if not depend_dict[name]:
            names.append(name)
            del depend_dict[name]
    while depend_dict:
        for name, lst in depend_dict.items():
            new_lst = [n for n in lst if depend_dict.has_key(n)]
            if not new_lst:
                names.append(name)
                del depend_dict[name]
            else:
                depend_dict[name] = new_lst
    return [name for name in names if vars.has_key(name)]

def _kind_func(string):
    #XXX: return something sensible.
    if string[0] in "'\"":
        string = string[1:-1]
    if real16pattern.match(string):
        return 16
    elif real8pattern.match(string):
        return 8
    return 'kind('+string+')'

def _selected_int_kind_func(r):
    #XXX: This should be processor dependent
    m = 10**r
    if m<=2**8: return 1
    if m<=2**16: return 2
    if m<=2**32: return 4
    if m<=2**64: return 8
    if m<=2**128: return 16
    return -1

def get_parameters(vars, global_params={}):
    params = copy.copy(global_params)
    g_params = copy.copy(global_params)
    for name,func in [('kind',_kind_func),
                      ('selected_int_kind',_selected_int_kind_func),
                      ]:
        if not g_params.has_key(name):
            g_params[name] = func
    param_names = []
    for n in get_sorted_names(vars):
        if vars[n].has_key('attrspec') and 'parameter' in vars[n]['attrspec']:
            param_names.append(n)
    kind_re = re.compile(r'\bkind\s*\(\s*(?P<value>.*)\s*\)',re.I)
    selected_int_kind_re = re.compile(r'\bselected_int_kind\s*\(\s*(?P<value>.*)\s*\)',re.I)
    for n in param_names:
        if vars[n].has_key('='):
            v = vars[n]['=']
            if islogical(vars[n]):
                v = v.lower()
                for repl in [
                    ('.false.','False'),
                    ('.true.','True'),
                    #TODO: test .eq., .neq., etc replacements.
                    ]:
                    v = v.replace(*repl)
            v = kind_re.sub(r'kind("\1")',v)
            v = selected_int_kind_re.sub(r'selected_int_kind(\1)',v)
            if isinteger(vars[n]) and not selected_int_kind_re.match(v):
                v = v.split('_')[0]
            if isdouble(vars[n]):
                tt = list(v)
                for m in real16pattern.finditer(v):
                    tt[m.start():m.end()] = list(\
                            v[m.start():m.end()].lower().replace('d', 'e'))
                v = string.join(tt,'')
            if iscomplex(vars[n]):
                if v[0]=='(' and v[-1]==')':
                    l = markoutercomma(v[1:-1]).split('@,@')
                    print n,params
            try:
                params[n] = eval(v,g_params,params)
            except Exception,msg:
                params[n] = v
                #print params
                outmess('get_parameters: got "%s" on %s\n' % (msg,`v`))
            if isstring(vars[n]) and type(params[n]) is type(0):
                params[n] = chr(params[n])
            nl = string.lower(n)
            if nl!=n:
                params[nl] = params[n]
        else:
            print vars[n]
            outmess('get_parameters:parameter %s does not have value?!\n'%(`n`))
    return params

def _eval_length(length,params):
    if length in ['(:)','(*)','*']:
        return '(*)'
    return _eval_scalar(length,params)

_is_kind_number = re.compile('\d+_').match

def _eval_scalar(value,params):
    if _is_kind_number(value):
        value = value.split('_')[0]
    try:
        value = str(eval(value,{},params))
    except (NameError, SyntaxError):
        return value
    except Exception,msg:
        errmess('"%s" in evaluating %r '\
                '(available names: %s)\n' \
                % (msg,value,params.keys()))
    return value

def analyzevars(block):
    global f90modulevars
    setmesstext(block)
    implicitrules,attrrules=buildimplicitrules(block)
    vars=copy.copy(block['vars'])
    if block['block']=='function' and not vars.has_key(block['name']):
        vars[block['name']]={}
    if block['vars'].has_key(''):
        del vars['']
        if block['vars'][''].has_key('attrspec'):
            gen=block['vars']['']['attrspec']
            for n in vars.keys():
                for k in ['public','private']:
                    if k in gen:
                        vars[n]=setattrspec(vars[n],k)
    svars=[]
    args = block['args']
    for a in args:
        try:
            vars[a]
            svars.append(a)
        except KeyError:
            pass
    for n in vars.keys():
        if n not in args: svars.append(n)

    params = get_parameters(vars, get_useparameters(block))

    dep_matches = {}
    name_match = re.compile(r'\w[\w\d_$]*').match
    for v in vars.keys():
        m = name_match(v)
        if m:
            n = v[m.start():m.end()]
            try:
                dep_matches[n]
            except KeyError:
                dep_matches[n] = re.compile(r'.*\b%s\b'%(v),re.I).match
    for n in svars:
        if n[0] in attrrules.keys():
            vars[n]=setattrspec(vars[n],attrrules[n[0]])
        if not vars[n].has_key('typespec'):
            if not(vars[n].has_key('attrspec') and 'external' in vars[n]['attrspec']):
                if implicitrules:
                    ln0 = string.lower(n[0])
                    for k in implicitrules[ln0].keys():
                        if k=='typespec' and implicitrules[ln0][k]=='undefined':
                            continue
                        if not vars[n].has_key(k):
                            vars[n][k]=implicitrules[ln0][k]
                        elif k=='attrspec':
                            for l in implicitrules[ln0][k]:
                                vars[n]=setattrspec(vars[n],l)
                elif n in block['args']:
                    outmess('analyzevars: typespec of variable %s is not defined in routine %s.\n'%(`n`,block['name']))

        if vars[n].has_key('charselector'):
            if vars[n]['charselector'].has_key('len'):
                l = vars[n]['charselector']['len']
                try:
                    l = str(eval(l,{},params))
                except:
                    pass
                vars[n]['charselector']['len'] = l

        if vars[n].has_key('kindselector'):
            if vars[n]['kindselector'].has_key('kind'):
                l = vars[n]['kindselector']['kind']
                try:
                    l = str(eval(l,{},params))
                except:
                    pass
                vars[n]['kindselector']['kind'] = l

        savelindims = {}
        if vars[n].has_key('attrspec'):
            attr=vars[n]['attrspec']
            attr.reverse()
            vars[n]['attrspec']=[]
            dim,intent,depend,check,note=None,None,None,None,None
            for a in attr:
                if a[:9]=='dimension': dim=(string.strip(a[9:]))[1:-1]
                elif a[:6]=='intent': intent=(string.strip(a[6:]))[1:-1]
                elif a[:6]=='depend': depend=(string.strip(a[6:]))[1:-1]
                elif a[:5]=='check': check=(string.strip(a[5:]))[1:-1]
                elif a[:4]=='note': note=(string.strip(a[4:]))[1:-1]
                else: vars[n]=setattrspec(vars[n],a)
                if intent:
                    if not vars[n].has_key('intent'): vars[n]['intent']=[]
                    for c in map(string.strip,string.split(markoutercomma(intent),'@,@')):
                        if not c in vars[n]['intent']:
                            vars[n]['intent'].append(c)
                    intent=None
                if note:
                    note=string.replace(note,'\\n\\n','\n\n')
                    note=string.replace(note,'\\n ','\n')
                    if not vars[n].has_key('note'): vars[n]['note']=[note]
                    else: vars[n]['note'].append(note)
                    note=None
                if depend is not None:
                    if not vars[n].has_key('depend'): vars[n]['depend']=[]
                    for c in rmbadname(map(string.strip,string.split(markoutercomma(depend),'@,@'))):
                        if c not in vars[n]['depend']:
                            vars[n]['depend'].append(c)
                    depend=None
                if check is not None:
                    if not vars[n].has_key('check'): vars[n]['check']=[]
                    for c in map(string.strip,string.split(markoutercomma(check),'@,@')):
                        if not c in vars[n]['check']:
                            vars[n]['check'].append(c)
                    check=None
            if dim and not vars[n].has_key('dimension'):
                vars[n]['dimension']=[]
                for d in rmbadname(map(string.strip,string.split(markoutercomma(dim),'@,@'))):
                    star = '*'
                    if d==':': star=':'
                    if params.has_key(d):
                        d = str(params[d])
                    for p in params.keys():
                        m = re.match(r'(?P<before>.*?)\b'+p+r'\b(?P<after>.*)',d,re.I)
                        if m:
                            #outmess('analyzevars:replacing parameter %s in %s (dimension of %s) with %s\n'%(`p`,`d`,`n`,`params[p]`))
                            d = m.group('before')+str(params[p])+m.group('after')
                    if d==star:
                        dl = [star]
                    else:
                        dl=string.split(markoutercomma(d,':'),'@:@')
                    if len(dl)==2 and '*' in dl: # e.g. dimension(5:*)
                        dl = ['*']
                        d = '*'
                    if len(dl)==1 and not dl[0]==star: dl = ['1',dl[0]]
                    if len(dl)==2:
                        d,v,di = getarrlen(dl,block['vars'].keys())
                        if d[:4] == '1 * ': d = d[4:]
                        if di and di[-4:] == '/(1)': di = di[:-4]
                        if v: savelindims[d] = v,di
                    vars[n]['dimension'].append(d)
        if vars[n].has_key('dimension'):
            if isintent_c(vars[n]):
                shape_macro = 'shape'
            else:
                shape_macro = 'shape'#'fshape'
            if isstringarray(vars[n]):
                if vars[n].has_key('charselector'):
                    d = vars[n]['charselector']
                    if d.has_key('*'):
                        d = d['*']
                        errmess('analyzevars: character array "character*%s %s(%s)" is considered as "character %s(%s)"; "intent(c)" is forced.\n'\
                                %(d,n,
                                  ','.join(vars[n]['dimension']),
                                  n,','.join(vars[n]['dimension']+[d])))
                        vars[n]['dimension'].append(d)
                        del vars[n]['charselector']
                        if not vars[n].has_key('intent'):
                            vars[n]['intent'] = []
                        if 'c' not in vars[n]['intent']:
                            vars[n]['intent'].append('c')
                    else:
                        errmess("analyzevars: charselector=%r unhandled." % (d))
        if not vars[n].has_key('check') and block.has_key('args') and n in block['args']:
            flag=not vars[n].has_key('depend')
            if flag: vars[n]['depend']=[]
            vars[n]['check']=[]
            if vars[n].has_key('dimension'):
                #/----< no check
                #vars[n]['check'].append('rank(%s)==%s'%(n,len(vars[n]['dimension'])))
                i=-1; ni=len(vars[n]['dimension'])
                for d in vars[n]['dimension']:
                    ddeps=[] # dependecies of 'd'
                    ad=''
                    pd=''
                    #origd = d
                    if not vars.has_key(d):
                        if savelindims.has_key(d):
                            pd,ad='(',savelindims[d][1]
                            d = savelindims[d][0]
                        else:
                            for r in block['args']:
                            #for r in block['vars'].keys():
                                if not vars.has_key(r): continue
                                if re.match(r'.*?\b'+r+r'\b',d,re.I):
                                    ddeps.append(r)
                    if vars.has_key(d):
                        if vars[d].has_key('attrspec'):
                            for aa in vars[d]['attrspec']:
                                if aa[:6]=='depend':
                                    ddeps=ddeps+string.split((string.strip(aa[6:]))[1:-1],',')
                        if vars[d].has_key('depend'):
                            ddeps=ddeps+vars[d]['depend']
                    i=i+1
                    if vars.has_key(d) and (not vars[d].has_key('depend')) \
                       and (not vars[d].has_key('=')) and (d not in vars[n]['depend']) \
                       and l_or(isintent_in,isintent_inout,isintent_inplace)(vars[n]):
                        vars[d]['depend']=[n]
                        if ni>1:
                            vars[d]['=']='%s%s(%s,%s)%s'% (pd,shape_macro,n,i,ad)
                        else:
                            vars[d]['=']='%slen(%s)%s'% (pd,n,ad)
                        #  /---< no check
                        if 1 and not vars[d].has_key('check'):
                            if ni>1:
                                vars[d]['check']=['%s%s(%s,%i)%s==%s'\
                                                  %(pd,shape_macro,n,i,ad,d)]
                            else:
                                vars[d]['check']=['%slen(%s)%s>=%s'%(pd,n,ad,d)]
                        if not vars[d].has_key('attrspec'): vars[d]['attrspec']=['optional']
                        if ('optional' not in vars[d]['attrspec']) and\
                           ('required' not in vars[d]['attrspec']):
                            vars[d]['attrspec'].append('optional')
                    elif d not in ['*',':']:
                        #/----< no check 
                        #if ni>1: vars[n]['check'].append('shape(%s,%i)==%s'%(n,i,d))
                        #else: vars[n]['check'].append('len(%s)>=%s'%(n,d))
                        if flag:                            
                            if vars.has_key(d):
                                if n not in ddeps:
                                    vars[n]['depend'].append(d)
                            else:
                                vars[n]['depend'] = vars[n]['depend'] + ddeps
            elif isstring(vars[n]):
                length='1'
                if vars[n].has_key('charselector'):
                    if vars[n]['charselector'].has_key('*'):
                        length = _eval_length(vars[n]['charselector']['*'],
                                              params)
                        vars[n]['charselector']['*']=length
                    elif vars[n]['charselector'].has_key('len'):
                        length = _eval_length(vars[n]['charselector']['len'],
                                              params)
                        del vars[n]['charselector']['len']
                        vars[n]['charselector']['*']=length

            if not vars[n]['check']: del vars[n]['check']
            if flag and not vars[n]['depend']: del vars[n]['depend']
        if vars[n].has_key('='):
            if not vars[n].has_key('attrspec'): vars[n]['attrspec']=[]
            if ('optional' not in vars[n]['attrspec']) and \
               ('required' not in vars[n]['attrspec']):
                vars[n]['attrspec'].append('optional')
            if not vars[n].has_key('depend'):
                vars[n]['depend']=[]
                for v,m in dep_matches.items():
                    if m(vars[n]['=']): vars[n]['depend'].append(v)
                if not vars[n]['depend']: del vars[n]['depend']
            if isscalar(vars[n]):
                vars[n]['='] = _eval_scalar(vars[n]['='],params)

    for n in vars.keys():
        if n==block['name']: # n is block name
            if vars[n].has_key('note'):
                block['note']=vars[n]['note']
            if block['block']=='function':
                if block.has_key('result') and vars.has_key(block['result']):
                    vars[n]=appenddecl(vars[n],vars[block['result']])
                if block.has_key('prefix'):
                    pr=block['prefix']; ispure=0; isrec=1
                    pr1=string.replace(pr,'pure','')
                    ispure=(not pr==pr1)
                    pr=string.replace(pr1,'recursive','')
                    isrec=(not pr==pr1)
                    m=typespattern[0].match(pr)
                    if m:
                        typespec,selector,attr,edecl=cracktypespec0(m.group('this'),m.group('after'))
                        kindselect,charselect,typename=cracktypespec(typespec,selector)
                        vars[n]['typespec']=typespec
                        if kindselect:
                            if kindselect.has_key('kind'):
                                try:
                                    kindselect['kind'] = eval(kindselect['kind'],{},params)
                                except:
                                    pass
                            vars[n]['kindselector']=kindselect
                        if charselect: vars[n]['charselector']=charselect
                        if typename: vars[n]['typename']=typename
                        if ispure: vars[n]=setattrspec(vars[n],'pure')
                        if isrec: vars[n]=setattrspec(vars[n],'recursive')
                    else:
                        outmess('analyzevars: prefix (%s) were not used\n'%`block['prefix']`)
    if not block['block'] in ['module','pythonmodule','python module','block data']:
        if block.has_key('commonvars'):
            neededvars=copy.copy(block['args']+block['commonvars'])
        else:
            neededvars=copy.copy(block['args'])
        for n in vars.keys():
            if l_or(isintent_callback,isintent_aux)(vars[n]):
                neededvars.append(n)
        if block.has_key('entry'):
            neededvars.extend(block['entry'].keys())
            for k in block['entry'].keys():
                for n in block['entry'][k]:
                    if n not in neededvars:
                        neededvars.append(n)
        if block['block']=='function':
            if block.has_key('result'):
                neededvars.append(block['result'])
            else:
                neededvars.append(block['name'])
        if block['block'] in ['subroutine','function']:
            name = block['name']
            if vars.has_key(name) and vars[name].has_key('intent'):
                block['intent'] = vars[name]['intent']
        if block['block'] == 'type':
            neededvars.extend(vars.keys())
        for n in vars.keys():
            if n not in neededvars:
                del vars[n]
    return vars
analyzeargs_re_1 = re.compile(r'\A[a-z]+[\w$]*\Z',re.I)
def analyzeargs(block):
    setmesstext(block)
    implicitrules,attrrules=buildimplicitrules(block)
    if not block.has_key('args'): block['args']=[]
    args=[]
    re_1 = analyzeargs_re_1
    for a in block['args']:
        if not re_1.match(a): # `a` is an expression
            at=determineexprtype(a,block['vars'],implicitrules)
            na='e_'
            for c in a:
                if c not in string.lowercase+string.digits: c='_'
                na=na+c
            if na[-1]=='_': na=na+'e'
            else: na=na+'_e'
            a=na
            while block['vars'].has_key(a) or a in block['args']: a=a+'r'
            block['vars'][a]=at            
        args.append(a)
        if not block['vars'].has_key(a):
            block['vars'][a]={}
        if block.has_key('externals') and a in block['externals']+block['interfaced']:
            block['vars'][a]=setattrspec(block['vars'][a],'external')
    block['args']=args

    if block.has_key('entry'):
        for k,args1 in block['entry'].items():
            for a in args1:
                if not block['vars'].has_key(a):
                    block['vars'][a]={}

    for b in block['body']:
        if b['name'] in args:
            if not block.has_key('externals'): block['externals']=[]
            if b['name'] not in block['externals']:
                block['externals'].append(b['name'])
    if block.has_key('result') and not block['vars'].has_key(block['result']):
        block['vars'][block['result']]={}
    return block
determineexprtype_re_1 = re.compile(r'\A\(.+?[,].+?\)\Z',re.I)
determineexprtype_re_2 = re.compile(r'\A[+-]?\d+(_(P<name>[\w]+)|)\Z',re.I)
determineexprtype_re_3 = re.compile(r'\A[+-]?[\d.]+[\d+-de.]*(_(P<name>[\w]+)|)\Z',re.I)
determineexprtype_re_4 = re.compile(r'\A\(.*\)\Z',re.I)
determineexprtype_re_5 = re.compile(r'\A(?P<name>\w+)\s*\(.*?\)\s*\Z',re.I)
def _ensure_exprdict(r):
    if type(r) is type(0):
        return {'typespec':'integer'}
    if type(r) is type(0.0):
        return {'typespec':'real'}
    if type(r) is type(0j):
        return {'typespec':'complex'}
    assert type(r) is type({}),`r`
    return r

def determineexprtype(expr,vars,rules={}):
    if vars.has_key(expr):
        return _ensure_exprdict(vars[expr])
    expr=string.strip(expr)
    if determineexprtype_re_1.match(expr):
        return {'typespec':'complex'}
    m=determineexprtype_re_2.match(expr)
    if m:
        if m.groupdict().has_key('name') and m.group('name'):
            outmess('determineexprtype: selected kind types not supported (%s)\n'%`expr`)
        return {'typespec':'integer'}
    m = determineexprtype_re_3.match(expr)
    if m:
        if m.groupdict().has_key('name') and m.group('name'):
            outmess('determineexprtype: selected kind types not supported (%s)\n'%`expr`)
        return {'typespec':'real'}
    for op in ['+','-','*','/']:
        for e in map(string.strip,string.split(markoutercomma(expr,comma=op),'@'+op+'@')):
            if vars.has_key(e):
                return _ensure_exprdict(vars[e])
    t={}
    if determineexprtype_re_4.match(expr): # in parenthesis
        t=determineexprtype(expr[1:-1],vars,rules)
    else:
        m = determineexprtype_re_5.match(expr)
        if m:
            rn=m.group('name')
            t=determineexprtype(m.group('name'),vars,rules)
            if t and t.has_key('attrspec'): del t['attrspec']
            if not t:
                if rules.has_key(rn[0]):
                    return _ensure_exprdict(rules[rn[0]])
    if expr[0] in '\'"':
        return {'typespec':'character','charselector':{'*':'*'}}
    if not t:
        outmess('determineexprtype: could not determine expressions (%s) type.\n'%(`expr`))
    return t
######
def crack2fortrangen(block,tab='\n'):
    setmesstext(block)
    ret=''
    if type(block) is type([]):
        for g in block:
            ret=ret+crack2fortrangen(g,tab)
        return ret
    prefix=''
    name=''
    args=''
    blocktype=block['block']
    if blocktype=='program': return ''
    al=[]
    if block.has_key('name'): name=block['name']
    if block.has_key('args'):
        vars = block['vars']
        al = [a for a in block['args'] if not isintent_callback(vars[a])]
        if block['block']=='function' or al:
            args='(%s)'%string.join(al,',')
    f2pyenhancements = ''
    if block.has_key('f2pyenhancements'):
        for k in block['f2pyenhancements'].keys():
            f2pyenhancements = '%s%s%s %s'%(f2pyenhancements,tab+tabchar,k,block['f2pyenhancements'][k])
    intent_lst = block.get('intent',[])[:]
    if blocktype=='function' and 'callback' in intent_lst:
        intent_lst.remove('callback')
    if intent_lst:
        f2pyenhancements = '%s%sintent(%s) %s'%\
                           (f2pyenhancements,tab+tabchar,
                            string.join(intent_lst,','),name)
    use=''
    if block.has_key('use'):
        use=use2fortran(block['use'],tab+tabchar)
    common=''
    if block.has_key('common'):
        common=common2fortran(block['common'],tab+tabchar)
    if name=='unknown_interface': name=''
    result=''
    if block.has_key('result'):
        result=' result (%s)'%block['result']
        if block['result'] not in al:
            al.append(block['result'])
    #if block.has_key('prefix'): prefix=block['prefix']+' '
    body=crack2fortrangen(block['body'],tab+tabchar)
    vars=vars2fortran(block,block['vars'],al,tab+tabchar)
    mess=''
    if block.has_key('from'):
        mess='! in %s'%block['from']
    if block.has_key('entry'):
        entry_stmts = ''
        for k,i in block['entry'].items():
            entry_stmts = '%s%sentry %s(%s)' \
                          % (entry_stmts,tab+tabchar,k,string.join(i,','))
        body = body + entry_stmts
    if blocktype=='block data' and name=='_BLOCK_DATA_':
        name = ''
    ret='%s%s%s %s%s%s %s%s%s%s%s%s%send %s %s'%(tab,prefix,blocktype,name,args,result,mess,f2pyenhancements,use,vars,common,body,tab,blocktype,name)
    return ret
def common2fortran(common,tab=''):
    ret=''
    for k in common.keys():
        if k=='_BLNK_':
            ret='%s%scommon %s'%(ret,tab,string.join(common[k],','))
        else:
            ret='%s%scommon /%s/ %s'%(ret,tab,k,string.join(common[k],','))
    return ret
def use2fortran(use,tab=''):
    ret=''
    for m in use.keys():
        ret='%s%suse %s,'%(ret,tab,m)
        if use[m]=={}:
            if ret and ret[-1]==',': ret=ret[:-1]
            continue
        if use[m].has_key('only') and use[m]['only']:
            ret='%s,only:'%(ret)
        if use[m].has_key('map') and use[m]['map']:
            c=' '
            for k in use[m]['map'].keys():
                if k==use[m]['map'][k]:
                    ret='%s%s%s'%(ret,c,k); c=','
                else:
                    ret='%s%s%s=>%s'%(ret,c,k,use[m]['map'][k]); c=','
        if ret and ret[-1]==',': ret=ret[:-1]
    return ret
def true_intent_list(var):
    lst = var['intent']
    ret = []
    for intent in lst:
        try:
            exec('c = isintent_%s(var)' % intent)
        except NameError:
            c = 0
        if c:
            ret.append(intent)
    return ret
def vars2fortran(block,vars,args,tab=''):
    """
    TODO:
    public sub
    ...
    """
    setmesstext(block)
    ret=''
    nout=[]
    for a in args:
        if block['vars'].has_key(a): nout.append(a)
    if block.has_key('commonvars'):
        for a in block['commonvars']:
            if vars.has_key(a):
                if a not in nout: nout.append(a)
            else: errmess('vars2fortran: Confused?!: "%s" is not defined in vars.\n'%a)
    if block.has_key('varnames'):
        nout.extend(block['varnames'])
    for a in vars.keys():
        if a not in nout: nout.append(a)
    for a in nout:
        if vars[a].has_key('depend'):
            for d in vars[a]['depend']:
                if vars.has_key(d) and vars[d].has_key('depend') and a in vars[d]['depend']:
                    errmess('vars2fortran: Warning: cross-dependence between variables "%s" and "%s"\n'%(a,d))
        if block.has_key('externals') and a in block['externals']:
            if isintent_callback(vars[a]):
                ret='%s%sintent(callback) %s'%(ret,tab,a)
            ret='%s%sexternal %s'%(ret,tab,a)
            if isoptional(vars[a]):
                ret='%s%soptional %s'%(ret,tab,a)
            if vars.has_key(a) and not vars[a].has_key('typespec'):
                continue
            cont=1
            for b in block['body']:
                if a==b['name'] and b['block']=='function': cont=0;break
            if cont: continue
        if not vars.has_key(a):
            show(vars)
            outmess('vars2fortran: No definition for argument "%s".\n'%a)
            continue
        if a==block['name'] and not block['block']=='function':
            continue
        if not vars[a].has_key('typespec'):
            if vars[a].has_key('attrspec') and 'external' in vars[a]['attrspec']:
                if a in args:
                    ret='%s%sexternal %s'%(ret,tab,a)
                continue
            show(vars[a])
            outmess('vars2fortran: No typespec for argument "%s".\n'%a)
            continue
        vardef=vars[a]['typespec']
        if vardef=='type' and vars[a].has_key('typename'):
            vardef='%s(%s)'%(vardef,vars[a]['typename'])
        selector={}
        if vars[a].has_key('kindselector'): selector=vars[a]['kindselector']
        elif vars[a].has_key('charselector'): selector=vars[a]['charselector']
        if selector.has_key('*'):
            if selector['*'] in ['*',':']:
                vardef='%s*(%s)'%(vardef,selector['*'])
            else:
                vardef='%s*%s'%(vardef,selector['*'])
        else:
            if selector.has_key('len'):
                vardef='%s(len=%s'%(vardef,selector['len'])
                if selector.has_key('kind'):
                    vardef='%s,kind=%s)'%(vardef,selector['kind'])
                else:
                    vardef='%s)'%(vardef)
            elif selector.has_key('kind'):
                vardef='%s(kind=%s)'%(vardef,selector['kind'])
        c=' '
        if vars[a].has_key('attrspec'):
            attr=[]
            for l in vars[a]['attrspec']:
                if l not in ['external']:
                    attr.append(l)
            if attr:
                vardef='%s %s'%(vardef,string.join(attr,','))
                c=','
        if vars[a].has_key('dimension'):
#             if not isintent_c(vars[a]):
#                 vars[a]['dimension'].reverse()
            vardef='%s%sdimension(%s)'%(vardef,c,string.join(vars[a]['dimension'],','))
            c=','
        if vars[a].has_key('intent'):
            lst = true_intent_list(vars[a])
            if lst:
                vardef='%s%sintent(%s)'%(vardef,c,string.join(lst,','))
            c=','
        if vars[a].has_key('check'):
            vardef='%s%scheck(%s)'%(vardef,c,string.join(vars[a]['check'],','))
            c=','
        if vars[a].has_key('depend'):
            vardef='%s%sdepend(%s)'%(vardef,c,string.join(vars[a]['depend'],','))
            c=','
        if vars[a].has_key('='):
            v = vars[a]['=']
            if vars[a]['typespec'] in ['complex','double complex']:
                try:
                    v = eval(v)
                    v = '(%s,%s)' % (v.real,v.imag)
                except:
                    pass
            vardef='%s :: %s=%s'%(vardef,a,v)
        else:
            vardef='%s :: %s'%(vardef,a)
        ret='%s%s%s'%(ret,tab,vardef)
    return ret
######

def crackfortran(files):
    global usermodules
    outmess('Reading fortran codes...\n',0)
    readfortrancode(files,crackline)
    outmess('Post-processing...\n',0)
    usermodules=[]
    postlist=postcrack(grouplist[0])
    outmess('Post-processing (stage 2)...\n',0)
    postlist=postcrack2(postlist)
    return usermodules+postlist
def crack2fortran(block):
    global f2py_version
    pyf=crack2fortrangen(block)+'\n'
    header="""!    -*- f90 -*-
! Note: the context of this file is case sensitive.
"""
    footer="""
! This file was auto-generated with f2py (version:%s).
! See http://cens.ioc.ee/projects/f2py2e/
"""%(f2py_version)
    return header+pyf+footer

if __name__ == "__main__":
    files=[]
    funcs=[]
    f=1;f2=0;f3=0
    showblocklist=0
    for l in sys.argv[1:]:
        if l=='': pass
        elif l[0]==':':
            f=0
        elif l=='-quiet':
            quiet=1
            verbose=0
        elif l=='-verbose':
            verbose=2
            quiet=0
        elif l=='-fix':
            if strictf77:
                outmess('Use option -f90 before -fix if Fortran 90 code is in fix form.\n',0)
            skipemptyends=1
            sourcecodeform='fix'
        elif l=='-skipemptyends':
            skipemptyends=1
        elif l=='--ignore-contains':
            ignorecontains=1
        elif l=='-f77':
            strictf77=1
            sourcecodeform='fix'
        elif l=='-f90':
            strictf77=0
            sourcecodeform='free'
            skipemptyends=1
        elif l=='-h':
            f2=1
        elif l=='-show':
            showblocklist=1
        elif l=='-m':
            f3=1
        elif l[0]=='-':
            errmess('Unknown option %s\n'%`l`)
        elif f2:
            f2=0
            pyffilename=l
        elif f3:
            f3=0
            f77modulename=l
        elif f:
            try:
                open(l).close()
                files.append(l)
            except IOError,detail:
                errmess('IOError: %s\n'%str(detail))
        else:
            funcs.append(l)
    if not strictf77 and f77modulename and not skipemptyends:
        outmess("""\
  Warning: You have specifyied module name for non Fortran 77 code
  that should not need one (expect if you are scanning F90 code
  for non module blocks but then you should use flag -skipemptyends
  and also be sure that the files do not contain programs without program statement).
""",0)

    postlist=crackfortran(files,funcs)
    if pyffilename:
        outmess('Writing fortran code to file %s\n'%`pyffilename`,0)
        pyf=crack2fortran(postlist)
        f=open(pyffilename,'w')
        f.write(pyf)
        f.close()
    if showblocklist:
        show(postlist)


#!/usr/bin/env python
"""
collectinput - Collects all files that are included to a main Latex document
               with \input or \include commands. These commands must be
               in separate lines.

Copyright 1999 Pearu Peterson all rights reserved,
Pearu Peterson <pearu@ioc.ee>          
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.

Pearu Peterson

Usage:
    collectinput <infile> <outfile>
    collectinput <infile>           # <outfile>=inputless_<infile>
    collectinput                    # in and out are stdin and stdout
"""

__version__ = "0.0"

stdoutflag=0
