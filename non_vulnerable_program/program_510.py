    import pre as re
    False = 0
    True = 1

def parse_structure(astr):
    spanlist = []
    # subroutines
    ind = 0
    while 1:
        start = astr.find("/**begin repeat", ind)
        if start == -1:
            break
        start2 = astr.find("*/",start)
        start2 = astr.find("\n",start2)
        fini1 = astr.find("/**end repeat**/",start2)
        fini2 = astr.find("\n",fini1)
        spanlist.append((start, start2+1, fini1, fini2+1))
        ind = fini2
    spanlist.sort()
    return spanlist

# return n copies of substr with template replacement
_special_names = {}

template_re = re.compile(r"@([\w]+)@")
named_re = re.compile(r"#([\w]*)=([^#]*?)#")

parenrep = re.compile(r"[(]([^)]*?)[)]\*(\d+)")
def paren_repl(obj):
    torep = obj.group(1)
    numrep = obj.group(2)
    return ','.join([torep]*int(numrep))

plainrep = re.compile(r"([^*]+)\*(\d+)")

def conv(astr):
    # replaces all occurrences of '(a,b,c)*4' in astr
    #  with 'a,b,c,a,b,c,a,b,c,a,b,c'
    astr = parenrep.sub(paren_repl,astr)
    # replaces occurences of xxx*3 with xxx, xxx, xxx
    astr = ','.join([plainrep.sub(paren_repl,x.strip()) for x in astr.split(',')])
    return astr

def unique_key(adict):
    # this obtains a unique key given a dictionary
    # currently it works by appending together n of the letters of the
    #   current keys and increasing n until a unique key is found
    # -- not particularly quick
    allkeys = adict.keys()
    done = False
    n = 1
    while not done:
        newkey = "".join([x[:n] for x in allkeys])
        if newkey in allkeys:
            n += 1
        else:
            done = True
    return newkey

def namerepl(match):
    global _names, _thissub
    name = match.group(1)
    return _names[name][_thissub]

def expand_sub(substr,namestr):
    global _names, _thissub
    # find all named replacements
    reps = named_re.findall(namestr)
    _names = {}
    _names.update(_special_names)
    numsubs = None
    for rep in reps:
        name = rep[0].strip()
        thelist = conv(rep[1])
        _names[name] = thelist

    # make lists out of string entries in name dictionary
    for name in _names.keys():
        entry = _names[name]
        entrylist = entry.split(',')
        _names[name] = entrylist
        num = len(entrylist)
        if numsubs is None:
            numsubs = num
        elif (numsubs != num):
            print namestr
            print substr
            raise ValueError, "Mismatch in number to replace"

    # now replace all keys for each of the lists
    mystr = ''
    for k in range(numsubs):
        _thissub = k
        mystr += template_re.sub(namerepl, substr)
        mystr += "\n\n"
    return mystr


_head = \
"""/*  This file was autogenerated from a template  DO NOT EDIT!!!!
       Changes should be made to the original source (.src) file
*/

"""

def get_line_header(str,beg):
    extra = []
    ind = beg-1
    char = str[ind]
    while (ind > 0) and (char != '\n'):
        extra.insert(0,char)
        ind = ind - 1
        char = str[ind]
    return ''.join(extra)

def process_str(allstr):
    newstr = allstr
    writestr = _head

    struct = parse_structure(newstr)
    #  return a (sorted) list of tuples for each begin repeat section
    #  each tuple is the start and end of a region to be template repeated
    
    oldend = 0
    for sub in struct:
        writestr += newstr[oldend:sub[0]]
        expanded = expand_sub(newstr[sub[1]:sub[2]],newstr[sub[0]:sub[1]])
        writestr += expanded
        oldend =  sub[3]


    writestr += newstr[oldend:]
    return writestr

include_src_re = re.compile(r"(\n|\A)#include\s*['\"](?P<name>[\w\d./\\]+[.]src)['\"]",re.I)

def resolve_includes(source):
    d = os.path.dirname(source)
    fid = open(source)
    lines = []
    for line in fid.readlines():
        m = include_src_re.match(line)
        if m:
            fn = m.group('name')
            if not os.path.isabs(fn):
                fn = os.path.join(d,fn)
            if os.path.isfile(fn):
                print 'Including file',fn
                lines.extend(resolve_includes(fn))
            else:
                lines.append(line)
        else:
            lines.append(line)
    fid.close()
    return lines

def process_file(source):
    lines = resolve_includes(source)
    return process_str(''.join(lines))

if __name__ == "__main__":

    try:
        file = sys.argv[1]
    except IndexError:
        fid = sys.stdin
        outfile = sys.stdout
    else:
        fid = open(file,'r')
        (base, ext) = os.path.splitext(file)
        newname = base
        outfile = open(newname,'w')

    allstr = fid.read()
    writestr = process_str(allstr)
    outfile.write(writestr)



