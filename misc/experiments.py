from functools import partial

from ctw.ctw import enc_len
from ctw.ctw import enc_len_bytes
from ctw.ctw import enc_len_phases
from ctw.misalign import add_leading_0_bit
from ctw.scramble import mapping_from_seed
from ctw.scramble import scramble
from misc.thoreau import plaintext


if __name__ == "__main__":
    mapping = mapping_from_seed(666)
    scrambled_plaintext = scramble(plaintext, mapping)
    misaligned_plaintext = add_leading_0_bit(plaintext)

    for text, text_desc in (
            (plaintext, "plain"),
            (scrambled_plaintext, "scrambled"),
            (misaligned_plaintext, "misaligned")):
        for enc_len_func, alg_desc in (
                (partial(enc_len, max_depth=48), "WCTBinary"),
                (partial(enc_len_phases, max_depth=6), "WCTPhases"),
                (partial(enc_len_bytes, max_depth=6), "WCTBytes")):
            bits = enc_len_func(text)
            print (
                "{:10} on {:10}: total {} bits or {} bytes; {} bits / byte"
                .format(alg_desc, text_desc, bits, bits / 8,
                        bits / len(plaintext)))
