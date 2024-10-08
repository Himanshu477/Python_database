import os

ref_dir = os.path.join(os.path.dirname(__file__))

__all__ = [f[:-3] for f in os.listdir(ref_dir) if f.endswith('.py') and
           not f.startswith('__')]

__doc__ = 'The following topics are available:\n' + \
          '\n - '.join([''] + __all__)

__all__.extend(['__doc__'])


"""

========================
Broadcasting over arrays
========================

Placeholder for broadcasting documentation.

"""


"""

==============
Array indexing
==============

Placeholder for array indexing documentation.

"""


