    from distutils.log import *
    from distutils.log import Log as old_Log
    from distutils.log import _global_log
    class Log(old_Log):
        def _log(self, level, msg, args):
            if level>= self.threshold:
                print _global_color_map[level](msg % args)
                sys.stdout.flush()
    _global_log.__class__ = Log

else:
    exec """
# Here follows (slightly) modified copy of Python 2.3 distutils/log.py

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4
FATAL = 5
class Log:

    def __init__(self, threshold=WARN):
        self.threshold = threshold

    def _log(self, level, msg, args):
        if level >= self.threshold:
            print _global_color_map[level](msg % args)
            sys.stdout.flush()

    def log(self, level, msg, *args):
        self._log(level, msg, args)

    def debug(self, msg, *args):
        self._log(DEBUG, msg, args)
    
    def info(self, msg, *args):
        self._log(INFO, msg, args)
    
    def warn(self, msg, *args):
        self._log(WARN, red_text(msg), args)
    
    def error(self, msg, *args):
        self._log(ERROR, msg, args)
    
    def fatal(self, msg, *args):
        self._log(FATAL, msg, args)

_global_log = Log()
log = _global_log.log
debug = _global_log.debug
info = _global_log.info
warn = _global_log.warn
error = _global_log.error
fatal = _global_log.fatal

def set_threshold(level):
    _global_log.threshold = level

def set_verbosity(v):
    if v <= 0:
        set_threshold(WARN)
    elif v == 1:
        set_threshold(INFO)
    elif v >= 2:
        set_threshold(DEBUG)
"""

