from ctw.ctw import decode_phases
from ctw.ctw import encode_phases
from misc.thoreau import plaintext


if __name__ == "__main__":
    msg_len, enc_data = encode_phases(plaintext, max_depth=6)
    msg_len_back, dec_data = decode_phases(msg_len, enc_data, max_depth=6)
    assert msg_len == msg_len_back
    assert dec_data == plaintext
    print len(plaintext), len(enc_data)
