    import pre as re
    False = 0
    True = 1

comment_block_exp = re.compile(r'/\*(?:\s|.)*?\*/')
subroutine_exp = re.compile(r'subroutine (?:\s|.)*?end subroutine.*')
function_exp = re.compile(r'function (?:\s|.)*?end function.*')
reg = re.compile(r"\ssubroutine\s(.+)\(.*\)")

def parse_structure(astr):
    spanlist = []
    for typ in [subroutine_exp, function_exp]:
        ind = 0
        while 1:
            a = typ.search(astr[ind:])
            if a is None:
                break
            tup = a.span()
            tup = (ind+tup[0],ind+tup[1])
            spanlist.append(tup)
            ind  = tup[1]

    spanlist.sort()
    return spanlist

# return n copies of substr with template replacement
_special_names = {'_c':'s,d,c,z',
                  '_t':'real,double precision,complex,double complex'
                  }
template_re = re.compile(r"<([^<>]*)>")
named_re = re.compile(r"<([^<>]*)=([^<>]*)>")
list_re = re.compile(r"<([^,>]+(,\s*[^,>]+)+)>")

def conv(astr):
    b = astr.split(',')
    return ','.join([x.strip().lower() for x in b]), len(b)

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

def listrepl(match):
    global _names, _numsubs
    thelist,num = conv(match.group(1))
    if (_numsubs is None):
        _numsubs = num
    elif (_numsubs != num):
        raise ValueError, "subroutine mismatch %s" % substr
    name = None
    for key in _names.keys():    # see if list is already in dictionary
        if _names[key] == thelist:
            name = key
    if name is None:      # this list is not in the dictionary yet
        name = "%s" % unique_key(_names)
        _names[name] = thelist
    return "<%s>" % name

def namerepl(match):
    global _names, _thissub
    name = match.group(1)
    return _names[name][_thissub]

def expand_sub(substr):
    global _names, _numsubs, _thissub
    # find all named replacements
    reps = named_re.findall(substr)
    _names = {}
    _names.update(_special_names)
    _numsubs = None
    for rep in reps:
        name = rep[0].strip().lower()
        thelist,num = conv(rep[1])
        if (_numsubs is None):
            _numsubs = num
        elif (_numsubs != _num):
            raise ValueError, "subroutine mismatch %s" % substr 
        _names[name] = thelist

    substr = named_re.sub(r"<\1>",substr)  # get rid of definition templates
    substr = list_re.sub(listrepl, substr) # convert all lists to named templates
                                           #  newnames are constructed as needed

    # make lists out of string entries in name dictionary
    for name in _names.keys():
        entry = _names[name]
        _names[name] = entry.split(',')

    # now replace all keys for each of the lists
    mystr = ''
    for k in range(_numsubs):
        _thissub = k
        mystr += template_re.sub(namerepl, substr)
        mystr += "\n"
    return mystr

_head = \
"""C  This file was autogenerated from a template  DO NOT EDIT!!!!
C     Changes should be made to the original source (.src) file
C

"""

def process_filestr(allstr):
    newstr = allstr.lower()
    writestr = _head

    struct = parse_structure(newstr)
    #  return a (sorted) list of tuples for each function or subroutine
    #  each tuple is the start and end of a subroutine or function to be expanded
    
    oldend = 0
    for sub in struct:
        writestr += newstr[oldend:sub[0]]
        obj = slice(sub[0],sub[1])
        expanded = expand_sub(newstr[obj])
        writestr += expanded
        oldend =  sub[1]

    writestr += newstr[oldend:]
    return writestr
    
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
    writestr = process_filestr(allstr)
    outfile.write(writestr)


#!/usr/bin/env python
