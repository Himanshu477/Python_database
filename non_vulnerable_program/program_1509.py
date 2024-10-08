import re
import sys
class Statement:

    def __init__(self, parent, item, name=None):
        self.parent = parent
        self.reader = parent.reader
        self.item = item
        if name is None:
            name = item.label
        self.name = name
        
        # If statement instance is constructed by error, set isvalid to False
        self.isvalid = True

    def get_intent_tab(self,colon='',deintent=False):
        from block import Block
        tab = ''
        p = self.parent
        while isinstance(p, Block):
            tab += '  '
            p = p.parent
        if deintent:
            tab = tab[:-2]
        s = self.item.label
        if s:
            tab = tab[len(s)+len(colon):]
            if not tab: tab = ' '
            tab = s + colon + tab
        return tab

# End statements

class EndStatement(Statement):
    """
    END [<blocktype> [<name>]]

    EndStatement instances have attributes:
      name
      isvalid
    """

    def __init__(self, parent, item):
        Statement.__init__(self, parent, item)
        line = item.get_line().replace(' ','')[3:]
        if line.startswith(self.blocktype):
            line = line[len(self.blocktype):].strip()
        else:
            if line:
                # not the end of expected block
                line = ''
                self.isvalid = False
        if line:
            if not line==parent.name:
                message = self.reader.format_message(\
                        'WARNING',
                        'expected the end of %r block but got end of %r, skipping.'\
                        % (parent.name, line),
                        item.span[0],item.span[1])
                print >> sys.stderr, message
                self.isvalid = False
        self.name = parent.name

    def __str__(self):
        return self.get_intent_tab()[:-2] + 'END %s %s'\
               % (self.blocktype.upper(),self.name or '')

class EndProgram(EndStatement):
    """
    END [PROGRAM [name]]
    """
    start_re = re.compile(r'end(\s*program\s*\w*|)\Z', re.I).match
    blocktype = 'program'

class EndModule(EndStatement):
    """
    END [MODULE [name]]
    """
    start_re = re.compile(r'end(\s*module\s*\w*|)\Z', re.I).match
    blocktype = 'module'

class EndBlockData(EndStatement):
    """
    END [BLOCK DATA [name]]
    """
    start_re = re.compile(r'end(\s*block\s*data\s*\w*|)\Z', re.I).match
    blocktype = 'blockdata'


class EndPythonModule(EndStatement):
    """
    END PYTHON MODULE name
    """
    start_re = re.compile(r'end\s*python\s*module\s*\w+\Z', re.I).match
    blocktype = 'pythonmodule'

class EndType(EndStatement):
    """
    END TYPE [name]
    """
    start_re = re.compile(r'end\s*type\s*\w*', re.I).match
    blocktype = 'type'

class EndInterface(EndStatement):
    """
    END INTERFACE [name]
    """
    start_re = re.compile(r'end\s*interface\s*\w*', re.I).match
    blocktype = 'interface'

class EndSubroutine(EndStatement):
    """
    END [SUBROUTINE [name]]
    """
    start_re = re.compile(r'end\s*(subroutine\s*\w*|)', re.I).match
    blocktype = 'subroutine'

class EndFunction(EndStatement):
    """
    END [FUNCTION [name]]
    """
    start_re = re.compile(r'end\s*(function\s*\w*|)', re.I).match
    blocktype = 'function'

class EndIfThen(EndStatement):
    """
    END IF [name]
    """
    start_re = re.compile(r'end\s*if\s*\w*', re.I).match
    blocktype = 'if'

class EndSelect(EndStatement):
    """
    END SELECT [name]
    """
    start_re = re.compile(r'end\s*select\s*\w*', re.I).match
    blocktype = 'select'

class EndDo(EndStatement):
    """
    END DO [name]
    """
    start_re = re.compile(r'end\s*do\s*\w*', re.I).match
    blocktype = 'do'

# Begin statements

class BeginStatement(Statement):
    """ <blocktype> <name>

    BeginStatement instances have the following attributes:
      name
      isvalid
    """
    def __init__(self, parent, item):
        name = item.get_line().replace(' ','')[len(self.blocktype):].strip()
        if not name:
            name = '__'+self.blocktype.upper()+'__'
        Statement.__init__(self, parent, item, name)

class Program(BeginStatement):
    """ PROGRAM [name]
    """
    blocktype = 'program'
    start_re = re.compile(r'program\s*\w*\Z', re.I).match

class Module(BeginStatement):
    """
    MODULE <name>
    """
    blocktype = 'module'
    start_re = re.compile(r'module\s*\w+\Z', re.I).match

    def __str__(self):
        s = self.get_intent_tab(deintent=True)
        s += 'MODULE '+ self.name
        return s

class PythonModule(BeginStatement):
    """
    PYTHON MODULE <name>
    """
    blocktype = 'pythonmodule'
    start_re = re.compile(r'python\s*module\s*\w+\Z', re.I).match

class BlockData(BeginStatement):
    """
    BLOCK DATA [name]
    """
    blocktype = 'blockdata'
    start_re = re.compile(r'block\s*data\s*\w*\Z', re.I).match

class Interface(BeginStatement):
    """
    INTERFACE [<generic-spec>]
    """
    blocktype = 'interface'
    start_re = re.compile(r'interface\s*\w*\Z', re.I).match

class Subroutine(BeginStatement):
    """
    [prefix] SUBROUTINE <name> [ ( [<dummy-arg-list>] ) [<proc-language-binding-spec>]]

    Subroutine instance has the following attributes:
      name
      args
    """
    blocktype = 'subroutine'
    start_re = re.compile(r'[\w\s]*subroutine\s*\w+', re.I).match

    begin_re = re.compile(r'(?P<prefix>[\w\s]*)\s*subroutine\s*(?P<name>\w+)', re.I).match
    def __init__(self, parent, item):
        BeginStatement.__init__(self, parent, item)
        line = item.get_line()
        m = self.begin_re(line)
        self.name = m.group('name')
        line = line[m.end():].strip()
        args = []
        if line.startswith('('):
            assert line.endswith(')'),`line`
            for a in line.split(','):
                args.append(a.strip())
        self.args = args
        
        
    def __str__(self):
        s = self.get_intent_tab(deintent=True)
        s += 'SUBROUTINE %s (%s)' % (self.name, ', '.join(self.args))
        return s

class Function(BeginStatement):
    """
    """
    blocktype = 'function'
    start_re = re.compile(r'([\w\s]+(\(\s*\w+\s*\)|)|)\s*function\s*\w+', re.I).match
    begin_re = re.compile(r'(?P<prefix>([\w\s](\(\s*\w+\s*\)|))*)\s*function\s*(?P<name>\w+)', re.I).match

    def __init__(self, parent, item):
        m = self.begin_re(item.get_line())
        name = m.group('name')
        BeginStatement.__init__(self, parent, item, name)

class Type(BeginStatement):
    """
    TYPE [[type-attr-spec-list] ::] <name> [(type-param-name-list)]
    """

    blocktype = 'type'
    start_re = re.compile(r'type(?!\s*\()(.*::|)\s*\w+\Z', re.I).match
    begin_re = re.compile(r'type(?!\s*\()(.*::|)\s*(?P<name>\w+)\Z', re.I).match

    def __init__(self, parent, item):
        BeginStatement.__init__(self, parent, item)
        m = self.begin_re(item.get_line())
        self.name = m.group('name')
        


class IfThen(BeginStatement):
    """
    IF ( <scalar-logical-expr> ) THEN

    IfThen instance has the following attributes:
      expr
    """

    blocktype = 'ifthen'
    start_re = re.compile(r'if\s*\(.*\)\s*then\Z', re.I).match

    def __init__(self, parent, item):
        Statement.__init__(self, parent, item)
        line = item.get_line()[2:-4].strip()
        assert line[0]=='(' and line[-1]==')',`line`
        self.expr = line[1:-1].strip()

    def __str__(self):
        s = self.get_intent_tab(colon=':',deintent=True)
        s += 'IF (%s) THEN' % (self.expr)
        return s

class Do(BeginStatement):
    """
    """
    blocktype = 'do'
    start_re = re.compile(r'do\b\s*\d*', re.I).match
    begin_re = re.compile(r'do\b\s*(?P<label>\d*)', re.I).match

    def __init__(self, parent, item):
        label = self.begin_re(item.get_line()).group('label').strip()
        self.endlabel = label
        BeginStatement.__init__(self, parent, item)
        self.name = item.label

class Select(BeginStatement):

    blocktype = 'select'
    start_re = re.compile(r'select\s*case\s*\(', re.I).match

# Other statements

class Use(Statement):
    """ Use statement class.

    use [ [, <module-nature>] ::] <name> [, <rename-list> ]
    use [ [, <module-nature>] ::] <name> ONLY : [ <only-list> ]

    Use instance has attributes:
      isuseonly    - boolean
      modulename   - name
      modulenature - list of names
      use_list     - list of 3-tuples (<name|operator>, <local>, <use>)
    """
    start_re = re.compile(r'use\b').match
    stmt_re = re.compile(r'use\b((?P<modulenature>[\w,\s]*)\s*::|)\s*(?P<name>\w+)',re.I).match
    only_re = re.compile(r'only\s*:',re.I).match
    op_rename_re = re.compile(r'operator\s*\(\s*(?P<localop>[^)]+)\s*\)\s*=\s*\>'\
                              r'\s*operator\s*\(\s*(?P<useop>[^)]+)\s*\)', re.I).match
    rename_re = re.compile(r'(?P<localname>\w+)\s*=\s*\>\s*(?P<usename>\w+)',re.I).match

    def __init__(self, parent, item):
        Statement.__init__(self, parent, item)
        self.isuseonly = False

        line = item.get_line()
        m = self.stmt_re(line)
        self.modulename = m.group('name')

        # init modulenature
        self.modulenature = []
        mn = m.group('modulenature') or ''
        for n in mn.split(','):
            n = n.strip()
            if not n: continue
            self.modulenature.append(n)

        # process the rest of the line
        self.use_list = []
        rest = line[m.end():].strip()
        only_m = self.only_re(rest)
        if only_m:
            self.isuseonly = True
            rest = rest[only_m.end():].strip()
        for n in rest.split(','):
            n = n.strip()
            if not n: continue
            m1 = self.op_rename_re(n)
            if m1:
                localop, useop = m1.group('localop'),m1.group('useop')
                self.use_list.append(('operator',localop,useop))
                continue
            m1 = self.rename_re(n)
            if m1:
                localname, usename = m1.group('localname'),m1.group('usename')
                self.use_list.append(('name',localname,usename))
                continue
            self.use_list.append(('name',n,n))

    def __str__(self):
        s = self.get_intent_tab()
        l = ['USE'] + self.modulenature
        s += ', '.join(l) + ' :: ' + self.modulename
        l = []
        for type,local,use in self.use_list:
            if type=='name':
                if local==name: l.append(local)
                else: l.append('%s => %s' % (local, use))
            else:
                assert type=='operator',`type`
                l.append('OPERATOR(%s) => OPERATOR(%s)' % (local, use))
        if self.isuseonly:
            s += ', ONLY: ' + ', '.join(l)
        else:
            if l: s+= ', ' + ', '.join(l)
        return s

class Import(Statement):
    """Import statement class

