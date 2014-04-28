from textwrap import dedent
import nose

from ctw.ctw import decode
from ctw.ctw import encode


def test_small():
    plaintext = "abracadabra"
    msg_len, enc_data = encode(plaintext)
    msg_len_back, dec_data = decode(msg_len, enc_data)
    nose.tools.assert_equal(msg_len, msg_len_back)
    nose.tools.assert_equal(dec_data, plaintext)
    print plaintext, len(plaintext)
    print enc_data.encode('hex'), len(enc_data)


def test_large():
    plaintext = dedent("""\
        and so necessarily resist it for the most part; and they are commonly
        treated as enemies by it. (Thoreau)
        """)
    msg_len, enc_data = encode(plaintext, max_depth=30)
    msg_len_back, dec_data = decode(msg_len, enc_data, max_depth=30)
    nose.tools.assert_equal(msg_len, msg_len_back)
    nose.tools.assert_equal(dec_data, plaintext)
    print len(plaintext), len(enc_data)
