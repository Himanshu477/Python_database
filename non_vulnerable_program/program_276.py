from __cvs_version__ import cvs_version
cvs_minor = cvs_version[-3]
cvs_serial = cvs_version[-1]

scipy_test_version = '%(major)d.%(minor)d.%(micro)d_%(release_level)s'\
                '_%(cvs_minor)d.%(cvs_serial)d' % (locals ())


