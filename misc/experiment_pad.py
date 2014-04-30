from functools import partial

from ctw.ctw import enc_len
from ctw.ctw import enc_len_bytes
from ctw.ctw import enc_len_phases
from misc.thoreau import plaintext


def pad(data):
    """
    Take string and return string with a zero byte after each byte.
    """
    return "".join(char + "\x00" for char in data)


if __name__ == "__main__":
    original_plaintext_len = len(plaintext)
    plaintext = pad(plaintext)
    for enc_len_func, alg_desc in (
            (partial(enc_len, max_depth=48), "WCTBinary"),
            (partial(enc_len_phases, max_depth=6), "WCTPhases"),
            (partial(enc_len_bytes, max_depth=6), "WCTBytes")):
        bits = enc_len_func(plaintext)
        print (
            "{:10} on {:10}: total {} bits or {} bytes; {} bits / byte"
            .format(alg_desc, "padded", bits, bits / 8,
                    bits / original_plaintext_len))
