    import logging
    log = logging.getLogger('exec_command')
except ImportError:
    class logging:
        DEBUG = 0
        def info(self,message): print 'info:',message
        def warn(self,message): print 'warn:',message
        def debug(self,message): print 'debug:',message
        def basicConfig(self): pass
        def setLevel(self,level): pass
    log = logging = logging()

############################################################

def get_pythonexe():
    pythonexe = sys.executable
    if os.name in ['nt','dos']:
        fdir,fn = os.path.split(pythonexe)
        fn = fn.upper().replace('PYTHONW','PYTHON')
        pythonexe = os.path.join(fdir,fn)
        assert os.path.isfile(pythonexe),`pythonexe`+' is not a file'
    return pythonexe

############################################################

def splitcmdline(line):
    """ Inverse of ' '.join(sys.argv).
    """
    log.info('splitcmdline(%r)' % (line))
    lst = []
    flag = 0
    s,pc,cc = '','',''
    for nc in line+' ':
        if flag==0:
            flag = (pc != '\\' and \
                     ((cc=='"' and 1) or (cc=="'" and 2) or \
                       (cc==' ' and pc!=' ' and -2))) or flag
        elif flag==1:
            flag = (cc=='"' and pc!='\\' and nc==' ' and -1) or flag
        elif flag==2:
            flag = (cc=="'" and pc!='\\' and nc==' ' and -1) or flag
        if flag!=-2:
            s += cc
        if flag<0:
            flag = 0
            s = s.strip()
            if s:
                lst.append(s)
                s = ''
        pc,cc = cc,nc
    else:
        s = s.strip()
        if s:
            lst.append(s)
    log.debug('splitcmdline -> %r' % (lst))
    return lst

def test_splitcmdline():
    l = splitcmdline('a   b  cc')
    assert l==['a','b','cc'],`l`
    l = splitcmdline('a')
    assert l==['a'],`l`
    l = splitcmdline('a "  b  cc"')
    assert l==['a','"  b  cc"'],`l`
    l = splitcmdline('"a bcc"  -h')
    assert l==['"a bcc"','-h'],`l`
    l = splitcmdline(r'"\"a \" bcc" -h')
    assert l==[r'"\"a \" bcc"','-h'],`l`
    l = splitcmdline(" 'a bcc'  -h")
    assert l==["'a bcc'",'-h'],`l`
    l = splitcmdline(r"'\'a \' bcc' -h")
    assert l==[r"'\'a \' bcc'",'-h'],`l`

############################################################

def find_executable(exe, path=None):
    """ Return full path of a executable.
    """
    log.info('find_executable(%r)' % exe)
    if path is None:
        path = os.environ.get('PATH',os.defpath)
    suffices = ['']
    if os.name in ['nt','dos','os2']:
        fn,ext = os.path.splitext(exe)
        extra_suffices = ['.exe','.com','.bat']
        if ext.lower() not in extra_suffices:
            suffices = extra_suffices
    if os.path.isabs(exe):
        paths = ['']
    else:
        paths = map(os.path.abspath, path.split(os.pathsep))
    for path in paths:
        fn = os.path.join(path,exe)
        for s in suffices:
            f_ext = fn+s
            if os.path.isfile(f_ext) and os.access(f_ext,os.X_OK):
                log.debug('Found executable %s' % f_ext)
                return f_ext
    if not os.path.isfile(exe) or os.access(exe,os.X_OK):
        log.warn('Could not locate executable %s' % exe)
    return exe

############################################################

def _preserve_environment( names ):
    log.debug('_preserve_environment(%r)' % (names))
    env = {}
    for name in names:
        env[name] = os.environ.get(name)
    return env

def _update_environment( **env ):
    log.debug('_update_environment(...)')
    for name,value in env.items():
        os.environ[name] = value or ''

def exec_command( command,
                  execute_in='', use_shell=None, use_tee = None,
                  _with_python = 1,
                  **env ):
    """ Return (status,output) of executed command.

    command is a concatenated string of executable and arguments.
    The output contains both stdout and stderr messages.
    The following special keyword arguments can be used:
      use_shell - execute `sh -c command`
      use_tee   - pipe the output of command through tee
      execute_in - before command `cd execute_in` and after `cd -`.

    On NT, DOS systems the returned status is correct for external commands.
    Wild cards will not work for non-posix systems or when use_shell=0.
    """
    log.info('exec_command(%r,%s)' % (command,\
                ','.join(['%s=%r'%kv for kv in env.items()])))

    if use_tee is None:
        use_tee = os.name=='posix'
    if use_shell is None:
        use_shell = os.name=='posix'

    execute_in = os.path.abspath(execute_in)
    oldcwd = os.path.abspath(os.getcwd())
    if oldcwd!=execute_in:
        os.chdir(execute_in)
        log.debug('New cwd: %s' % execute_in)
    else:
        log.debug('Retaining cwd: %s' % oldcwd)

    oldenv = _preserve_environment( env.keys() )
    _update_environment( **env )

    try:
        # _exec_command is robust but slow, it relies on
        # usable sys.std*.fileno() descriptors, if they
        # are bad (like in win32 Idle, PyCrust environments)
        # then _exec_command_python (even slower)
        # will be used as a last resort.
        #
        # _exec_command_posix uses os.system and is faster
        # but not on all platforms os.system will return
        # a correct status.
        if _with_python and sys.__stdout__.fileno()==-1:
            st = _exec_command_python(command, **env)
        elif os.name=='posix' and sys.platform[:5]!='sunos':
            st = _exec_command_posix(command,
                                     use_shell=use_shell,
                                     use_tee=use_tee,
                                     **env)
        else:
            st = _exec_command(command, use_shell=use_shell, **env)
    finally:
        if oldcwd!=execute_in:
            os.chdir(oldcwd)
            log.debug('Restored cwd to %s' % oldcwd)
        _update_environment(**oldenv)

    return st

def _exec_command_posix( command,
                         use_shell = None,
                         use_tee = None,
                         **env ):
    log.debug('_exec_command_posix(...)')

    tmpfile = tempfile.mktemp()
    if use_tee:
        stsfile = tempfile.mktemp()
        filter = ''
        if use_tee == 2:
            filter = r'| tr -cd "\n" | tr "\n" "."; echo'
        command_posix = '( %s 2>&1 ; echo $? > %s ) | tee %s %s'\
                      % (command,stsfile,tmpfile,filter)
    else:
        command_posix = '%s > %s 2>&1' % (command,tmpfile)

    log.debug('Running os.system(%r)' % (command_posix))
    status = os.system(command_posix)

    if use_tee:
        if status:
            # if command_tee fails then fall back to robust exec_command
            log.warn('_exec_command_posix failed (status=%s)' % status)
            return _exec_command(command, use_shell=use_shell, **env)
        f = open(stsfile,'r')
        status = int(f.read())
        f.close()
        os.remove(stsfile)

    f = open(tmpfile,'r')
    text = f.read()
    f.close()
    os.remove(tmpfile)

    if text[-1:]=='\n':
        text = text[:-1]
    
    return status, text


def _exec_command_python(command, **env):
    log.debug('_exec_command_python(...)')

    python_exe = get_pythonexe()
    cmdfile = tempfile.mktemp()
    stsfile = tempfile.mktemp()
    outfile = tempfile.mktemp()

    if __name__[-12:] == 'exec_command':
        exec_dir = os.path.dirname(os.path.abspath(__file__))
    elif os.path.isfile('exec_command.py'):
        exec_dir = os.path.abspath('.')
    else:
        exec_dir = os.path.abspath(sys.argv[0])
        if os.path.isfile(exec_dir):
            exec_dir = os.path.dirname(exec_dir)

    f = open(cmdfile,'w')
    f.write('import os\n')
    f.write('import sys\n')
    f.write('sys.path.insert(0,%r)\n' % (exec_dir))
    f.write('from exec_command import exec_command\n')
    f.write('del sys.path[0]\n')
    f.write('cmd = %r\n' % command)
    f.write('os.environ = %r\n' % (os.environ))
    f.write('s,o = exec_command(cmd, _with_python=0, **%r)\n' % (env))
    f.write('f=open(%r,"w")\nf.write(str(s))\nf.close()\n' % (stsfile))
    f.write('f=open(%r,"w")\nf.write(o)\nf.close()\n' % (outfile))
    f.close()

    cmd = '%s %s' % (python_exe, cmdfile)
    status = os.system(cmd)
    assert not status,`cmd`+' failed'
    os.remove(cmdfile)

    f = open(stsfile,'r')
    status = int(f.read())
    f.close()
    os.remove(stsfile)
    
    f = open(outfile,'r')
    text = f.read()
    f.close()
    os.remove(outfile)
    
    return status, text


def _exec_command( command, use_shell=None, **env ):
    log.debug('_exec_command(...)')
    
    if use_shell is None:
        use_shell = os.name=='posix'

    using_command = 0
    if use_shell:
        # We use shell (unless use_shell==0) so that wildcards can be
        # used.
        sh = os.environ.get('SHELL','/bin/sh')
        argv = [sh,'-c',command]
    else:
        # On NT, DOS we avoid using command.com as it's exit status is
        # not related to the exit status of a command.
        argv = splitcmdline(command)

    if hasattr(os,'spawnvpe'):
        spawn_command = os.spawnvpe
    else:
        spawn_command = os.spawnve
        argv[0] = find_executable(argv[0])
        if not os.path.isfile(argv[0]):
            log.warn('Executable %s does not exist' % (argv[0]))
            if os.name in ['nt','dos']:
                # argv[0] might be internal command
                argv = [os.environ['COMSPEC'],'/C']+argv
                using_command = 1

    # sys.__std*__ is used instead of sys.std* because environments
    # like IDLE, PyCrust, etc overwrite sys.std* commands.
    so_fileno = sys.__stdout__.fileno()
    se_fileno = sys.__stderr__.fileno()
    so_flush = sys.__stdout__.flush
    se_flush = sys.__stderr__.flush
    so_dup = os.dup(so_fileno)
    se_dup = os.dup(se_fileno)

    outfile = tempfile.mktemp()
    fout = open(outfile,'w')
    if using_command:
        errfile = tempfile.mktemp()
        ferr = open(errfile,'w')

    log.debug('Running %s(%s,%r,%r,os.environ)' \
              % (spawn_command.__name__,os.P_WAIT,argv[0],argv))

    so_flush()
    se_flush()
    os.dup2(fout.fileno(),so_fileno)
    if using_command:
        os.dup2(ferr.fileno(),se_fileno)
    else:
        os.dup2(fout.fileno(),se_fileno)

    try:
        status = spawn_command(os.P_WAIT,argv[0],argv,os.environ)
    except OSError,errmess:
        status = 999
        sys.stderr.write('%s: %s'%(errmess,argv[0]))

    so_flush()
    se_flush()
    os.dup2(so_dup,so_fileno)
    os.dup2(se_dup,se_fileno)

    fout.close()
    fout = open(outfile,'r')
    text = fout.read()
    fout.close()
    os.remove(outfile)

    if using_command:
        ferr.close()
        ferr = open(errfile,'r')
        errmess = ferr.read()
        ferr.close()
        os.remove(errfile)
        if errmess and not status:
            status = 998
            if text:
                text = text + '\n'
            text = '%sCOMMAND %r FAILED: %s' %(text,command,errmess)

    if text[-1:]=='\n':
        text = text[:-1]
    if status is None:
        status = 0

    return status, text


def test_nt():
    pythonexe = get_pythonexe()

    if not (sys.platform=='win32' and os.environ.get('OSTYPE','')=='cygwin'):
        s,o=exec_command('echo Hello')
        assert s==0 and o=='Hello',(s,o)

        s,o=exec_command('echo a%AAA%')
        assert s==0 and o=='a',(s,o)

        s,o=exec_command('echo a%AAA%',AAA='Tere')
        assert s==0 and o=='aTere',(s,o)

        os.environ['BBB'] = 'Hi'
        s,o=exec_command('echo a%BBB%')
        assert s==0 and o=='aHi',(s,o)

        s,o=exec_command('echo a%BBB%',BBB='Hey')
        assert s==0 and o=='aHey', (s,o)
        s,o=exec_command('echo a%BBB%')
        assert s==0 and o=='aHi',(s,o)

    s,o=exec_command('this_is_not_a_command')
    assert s and o!='',(s,o)

    s,o=exec_command('type not_existing_file')
    assert s and o!='',(s,o)

    s,o=exec_command('echo path=%path%')
    assert s==0 and o!='',(s,o)
    
    s,o=exec_command('%s -c "import sys;sys.stderr.write(sys.platform)"' \
                     % pythonexe)
    assert s==0 and o=='win32',(s,o)

    s,o=exec_command('%s -c "raise \'Ignore me.\'"' % pythonexe)
    assert s==1 and o,(s,o)

    s,o=exec_command('%s -c "import sys;sys.stderr.write(\'0\');sys.stderr.write(\'1\');sys.stderr.write(\'2\')"'\
                     % pythonexe)
    assert s==0 and o=='012',(s,o)

    s,o=exec_command('%s -c "import sys;sys.exit(15)"' % pythonexe)
    assert s==15 and o=='',(s,o)

    s,o=exec_command('python -c "print \'Heipa\'"')
    assert s==0 and o=='Heipa',(s,o)

    print 'ok'

def test_posix():
    s,o=exec_command("echo Hello")
    assert s==0 and o=='Hello',(s,o)

    s,o=exec_command('echo $AAA')
    assert s==0 and o=='',(s,o)

    s,o=exec_command('echo "$AAA"',AAA='Tere')
    assert s==0 and o=='Tere',(s,o)


    s,o=exec_command('echo "$AAA"')
    assert s==0 and o=='',(s,o)

    os.environ['BBB'] = 'Hi'
    s,o=exec_command('echo "$BBB"')
    assert s==0 and o=='Hi',(s,o)

    s,o=exec_command('echo "$BBB"',BBB='Hey')
    assert s==0 and o=='Hey',(s,o)

    s,o=exec_command('echo "$BBB"')
    assert s==0 and o=='Hi',(s,o)


    s,o=exec_command('this_is_not_a_command')
    assert s!=0 and o!='',(s,o)

    s,o=exec_command('echo path=$PATH')
    assert s==0 and o!='',(s,o)
    
    s,o=exec_command('python -c "import sys,os;sys.stderr.write(os.name)"')
    assert s==0 and o=='posix',(s,o)

    s,o=exec_command('python -c "raise \'Ignore me.\'"')
    assert s==1 and o,(s,o)

    s,o=exec_command('python -c "import sys;sys.stderr.write(\'0\');sys.stderr.write(\'1\');sys.stderr.write(\'2\')"')
    assert s==0 and o=='012',(s,o)

    s,o=exec_command('python -c "import sys;sys.exit(15)"')
    assert s==15 and o=='',(s,o)

    s,o=exec_command('python -c "print \'Heipa\'"')
    assert s==0 and o=='Heipa',(s,o)
    
    print 'ok'

if os.name=='posix':
    test = test_posix
elif os.name in ['nt','dos']:
    test = test_nt
else:
    raise NotImplementedError,'exec_command tests for '+os.name

############################################################

if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    test_splitcmdline()
    test()



# http://www.absoft.com/literature/osxuserguide.pdf

