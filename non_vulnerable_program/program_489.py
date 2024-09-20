import re,string
_wordchars_re = re.compile(r'[^\\\'\"%s ]*' % string.whitespace)
_squote_re = re.compile(r"'(?:[^'\\]|\\.)*'")
_dquote_re = re.compile(r'"(?:[^"\\]|\\.)*"')
_has_white_re = re.compile(r'\s')
def split_quoted(s):
    s = string.strip(s)
    words = []
    pos = 0

    while s:
        m = _wordchars_re.match(s, pos)
        end = m.end()
        if end == len(s):
            words.append(s[:end])
            break

        if s[end] in string.whitespace: # unescaped, unquoted whitespace: now
            words.append(s[:end])       # we definitely have a word delimiter
            s = string.lstrip(s[end:])
            pos = 0

        elif s[end] == '\\':            # preserve whatever is being escaped;
                                        # will become part of the current word
            s = s[:end] + s[end+1:]
            pos = end+1

        else:
            if s[end] == "'":           # slurp singly-quoted string
                m = _squote_re.match(s, end)
            elif s[end] == '"':         # slurp doubly-quoted string
                m = _dquote_re.match(s, end)
            else:
                raise RuntimeError, \
                      "this can't happen (bad char '%c')" % s[end]

            if m is None:
                raise ValueError, \
                      "bad string (mismatched %s quotes?)" % s[end]

            (beg, end) = m.span()
            if _has_white_re.search(s[beg+1:end-1]):
                s = s[:beg] + s[beg+1:end-1] + s[end:]
                pos = m.end() - 2
            else:
                # Keeping quotes when a quoted word does not contain
                # white-space. XXX: send a patch to distutils
                pos = m.end()

        if pos >= len(s):
            words.append(s)
            break

    return words
ccompiler.split_quoted = split_quoted


"""distutils.command

Package containing implementation of all the standard Distutils
commands."""

__revision__ = "$Id: __init__.py,v 1.3 2005/05/16 11:08:49 pearu Exp $"

distutils_all = [  'build_py',
                   'build_scripts',
                   'clean',
                   'install_lib',
                   'install_scripts',
           'bdist',
                   'bdist_dumb',
                   'bdist_wininst',
                ]

__import__('distutils.command',globals(),locals(),distutils_all)

__all__ = ['build',
           'config_compiler',
           'config',
           'build_src',
           'build_ext',
           'build_clib',
           'install',
           'install_data',
           'install_headers',
           'bdist_rpm',
           'sdist',
          ] + distutils_all



