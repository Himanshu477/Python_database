    from os.path import relpath
except ImportError:
    # Copied from Python 2.7
    if 'posix' in sys.builtin_module_names:
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
            from os.path import sep, curdir, join, abspath, commonprefix, \
                 pardir

            if not path:
                raise ValueError("no path specified")

            start_list = abspath(start).split(sep)
            path_list = abspath(path).split(sep)

            # Work out how much of the filepath is shared by start and path.
            i = len(commonprefix([start_list, path_list]))

            rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return curdir
            return join(*rel_list)
    elif 'nt' in sys.builtin_module_names:
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
            from os.path import sep, curdir, join, abspath, commonprefix, \
                 pardir, splitunc

            if not path:
                raise ValueError("no path specified")
            start_list = abspath(start).split(sep)
            path_list = abspath(path).split(sep)
            if start_list[0].lower() != path_list[0].lower():
                unc_path, rest = splitunc(path)
                unc_start, rest = splitunc(start)
                if bool(unc_path) ^ bool(unc_start):
                    raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)"
                                                                        % (path, start))
                else:
                    raise ValueError("path is on drive %s, start on drive %s"
                                                        % (path_list[0], start_list[0]))
            # Work out how much of the filepath is shared by start and path.
            for i in range(min(len(start_list), len(path_list))):
                if start_list[i].lower() != path_list[i].lower():
                    break
            else:
                i += 1

            rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return curdir
            return join(*rel_list)
    else:
        raise RuntimeError("Unsupported platform (no relpath available!)")


# -*- encoding:utf-8 -*-

