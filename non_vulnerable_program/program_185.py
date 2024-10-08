import os as _os
import __builtin__

_open = __builtin__.open

_BLOCKSIZE = 512

error = IOError                         # For anydbm

class _Database:

    def __init__(self, file, mode):
        self._mode = mode
        self._dirfile = file + _os.extsep + 'dir'
        self._datfile = file + _os.extsep + 'dat'
        self._bakfile = file + _os.extsep + 'bak'
        # Mod by Jack: create data file if needed
        try:
            f = _open(self._datfile, 'r')
        except IOError:
            f = _open(self._datfile, 'w', self._mode)
        f.close()
        self._update()

    def _update(self):
        self._index = {}
        try:
            f = _open(self._dirfile)
        except IOError:
            pass
        else:
            while 1:
                line = f.readline().rstrip()
                if not line: break
                key, (pos, siz) = eval(line)
                self._index[key] = (pos, siz)
            f.close()

    def _commit(self):
        try: _os.unlink(self._bakfile)
        except _os.error: pass
        try: _os.rename(self._dirfile, self._bakfile)
        except _os.error: pass
        f = _open(self._dirfile, 'w', self._mode)
        for key, (pos, siz) in self._index.items():
            f.write("%s, (%s, %s)\n" % (`key`, `pos`, `siz`))
        f.close()

    def __getitem__(self, key):
        pos, siz = self._index[key]     # may raise KeyError
        f = _open(self._datfile, 'rb')
        f.seek(pos)
        dat = f.read(siz)
        f.close()
        return dat

    def _addval(self, val):
        f = _open(self._datfile, 'rb+')
        f.seek(0, 2)
        pos = int(f.tell())
## Does not work under MW compiler
##              pos = ((pos + _BLOCKSIZE - 1) / _BLOCKSIZE) * _BLOCKSIZE
##              f.seek(pos)
        npos = ((pos + _BLOCKSIZE - 1) // _BLOCKSIZE) * _BLOCKSIZE
        f.write('\0'*(npos-pos))
        pos = npos

        f.write(val)
        f.close()
        return (pos, len(val))

    def _setval(self, pos, val):
        f = _open(self._datfile, 'rb+')
        f.seek(pos)
        f.write(val)
        f.close()
        return (pos, len(val))

    def _addkey(self, key, (pos, siz)):
        self._index[key] = (pos, siz)
        f = _open(self._dirfile, 'a', self._mode)
        f.write("%s, (%s, %s)\n" % (`key`, `pos`, `siz`))
        f.close()

    def __setitem__(self, key, val):
        if not type(key) == type('') == type(val):
            raise TypeError, "keys and values must be strings"
        if not self._index.has_key(key):
            (pos, siz) = self._addval(val)
            self._addkey(key, (pos, siz))
        else:
            pos, siz = self._index[key]
            oldblocks = (siz + _BLOCKSIZE - 1) / _BLOCKSIZE
            newblocks = (len(val) + _BLOCKSIZE - 1) / _BLOCKSIZE
            if newblocks <= oldblocks:
                pos, siz = self._setval(pos, val)
                self._index[key] = pos, siz
            else:
                pos, siz = self._addval(val)
                self._index[key] = pos, siz

    def __delitem__(self, key):
        del self._index[key]
        self._commit()

    def keys(self):
        return self._index.keys()

    def has_key(self, key):
        return self._index.has_key(key)

    def __contains__(self, key):
        return self._index.has_key(key)

    def iterkeys(self):
        return self._index.iterkeys()
    __iter__ = iterkeys

    def __len__(self):
        return len(self._index)

    def close(self):
        self._commit()
        self._index = None
        self._datfile = self._dirfile = self._bakfile = None

    def __del__(self):
        if self._index is not None:
            self._commit()
  


def open(file, flag=None, mode=0666):
    # flag, mode arguments are currently ignored
    return _Database(file, mode)


