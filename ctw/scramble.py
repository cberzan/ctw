#!/usr/bin/env python

"""
Read stdin, scramble it through a 1-1 byte mapping, and write to stdout.

Usage:
    ./scramble.py <in.txt >out.txt

Note: Does not work in PyPy because numpy.random.permutation is not
implemented.
"""


import numpy as np
import sys


def check_mapping(mapping):
    """
    Verify that `mapping` is a 1-1 mapping on bytes.
    """
    assert set(mapping.keys()) == set(range(256))
    assert set(mapping.values()) == set(range(256))


def invert_mapping(mapping):
    """
    Invert the given 1-1 byte mapping.
    """
    check_mapping(mapping)
    return dict((v, k) for k, v in mapping.iteritems())


def scramble(string, mapping):
    """
    Pass the given `string` through the given `mapping`.
    """
    check_mapping(mapping)
    return "".join(chr(mapping[ord(c)]) for c in string)


def unscramble(string, mapping):
    """
    Undo the effects of `scramble`.
    """
    return scramble(string, invert_mapping(mapping))


def mapping_from_seed(seed):
    """
    Return a random mapping obtained using the given seed.
    """
    np.random.seed(seed)
    keys = range(256)
    values = np.random.permutation(keys)
    return dict((k, v) for k, v in zip(keys, values))


if __name__ == "__main__":
    mapping = mapping_from_seed(666)
    print scramble(sys.stdin.read(), mapping)
