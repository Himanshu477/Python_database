from setuptools.command.develop import develop as old_develop

class develop(old_develop):
    __doc__ = old_develop.__doc__
    def install_for_development(self):
        # Build sources in-place, too.
        self.reinitialize_command('build_src', inplace=1)
        old_develop.install_for_development(self)


"""Masked arrays add-ons.

A collection of utilities for maskedarray

:author: Pierre GF Gerard-Marchant
:contact: pierregm_at_uga_dot_edu
:version: $Id: __init__.py 3473 2007-10-29 15:18:13Z jarrod.millman $
"""
__author__ = "Pierre GF Gerard-Marchant ($Author: jarrod.millman $)"
__version__ = '1.0'
__revision__ = "$Revision: 3473 $"
__date__     = '$Date: 2007-10-29 17:18:13 +0200 (Mon, 29 Oct 2007) $'

