#!/usr/bin/env python

"""
Read stdin, misalign it (adding a 0 bit before each byte), and write to stdout.

Usage:
    ./misalign.py <in.txt >out.txt
"""


import sys


def add_leading_0_bit(data):
    """
    Take string, return string with an extra 0 bit prepende to each byte.
    """
    out_bytes = []
    cur_byte = 0
    cur_bits = 0
    for byte in data:
        byte = ord(byte)
        cur_byte = (cur_byte << 1)
        cur_bits += 1
        cur_byte = (cur_byte << 8) | byte
        cur_bits += 8
        while cur_bits >= 8:
            out_byte = cur_byte >> (cur_bits - 8)
            assert 0 <= out_byte < 256
            out_bytes.append(out_byte)
            cur_byte -= out_byte << (cur_bits - 8)
            cur_bits -= 8
    # Padding:
    if cur_bits:
        out_byte = cur_byte << (8 - cur_bits)
        assert 0 <= out_byte < 256
        out_bytes.append(out_byte)
    return "".join(chr(byte) for byte in out_bytes)


if __name__ == "__main__":
    print add_leading_0_bit(sys.stdin.read())
