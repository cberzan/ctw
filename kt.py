import numpy as np


def compute_kt_table(max_a, max_b):
    """
    Return kt_table s.t. kt_table[a, b] = KT_joint(a, b).

    a = number of zeros; b = number of ones.
    """
    table = np.empty((max_a + 1, max_b + 1))
    for a in xrange(max_a + 1):
        for b in xrange(max_b + 1):
            if a == 0 and b == 0:
                val = 1
            elif a == 0:
                val = table[a][b - 1] * (b - 0.5) / (a + b)
            else:
                val = table[a - 1][b] * (a - 0.5) / (a + b)
            table[a][b] = val
    return table
