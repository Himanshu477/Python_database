from numpy.testing import *
import numpy as np

rlevel = 1

class TestRegression(TestCase):
    def test_kron_matrix(self,level=rlevel):
        """Ticket #71"""
        x = np.matrix('[1 0; 1 0]')
        assert_equal(type(np.kron(x,x)),type(x))


""" Machine limits for Float32 and Float64 and (long double) if available...
"""

__all__ = ['finfo','iinfo']

