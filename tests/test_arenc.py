import nose
import random

from ctw.arenc import ArithmeticDecoder
from ctw.arenc import ArithmeticEncoder
from ctw.arenc import split_interval
from ctw.util import byte_bit
from ctw.util import pretty_bin_buffer


def test_byte_bit():
    nose.tools.assert_equal(byte_bit(0x41, 0), 0)
    nose.tools.assert_equal(byte_bit(0x41, 1), 1)
    nose.tools.assert_equal(byte_bit(0x41, 2), 0)
    nose.tools.assert_equal(byte_bit(0x41, 3), 0)
    nose.tools.assert_equal(byte_bit(0x41, 4), 0)
    nose.tools.assert_equal(byte_bit(0x41, 5), 0)
    nose.tools.assert_equal(byte_bit(0x41, 6), 0)
    nose.tools.assert_equal(byte_bit(0x41, 7), 1)


def test_split_interval():
    nose.tools.assert_equal(
        split_interval(0x00, 0xFF, 0.5),
        (0x00, 0x7F, 0x80, 0xFF))
    nose.tools.assert_equal(
        split_interval(0, 0xFF, 0.0001),
        (0x00, 0x00, 0x01, 0xFF))
    nose.tools.assert_equal(
        split_interval(0, 0xFF, 0.9999),
        (0x00, 0xFE, 0xFF, 0xFF))


def _encode_decode(bits, probs):
    assert len(bits) == len(probs)

    print "---------------- encoding"
    encoder = ArithmeticEncoder()
    for bit, prob in zip(bits, probs):
        encoder.encode_bit(prob, bit)
    msg_len, enc_buf = encoder.get_encoded_data()
    print "enc_buf:", pretty_bin_buffer(enc_buf)
    nose.tools.assert_equal(msg_len, len(bits))

    print "---------------- decoding"
    decoder = ArithmeticDecoder(msg_len, enc_buf)
    bits_back = []
    for i in xrange(msg_len):
        bit = decoder.decode_bit(probs[i])
        bits_back.append(bit)
    msg_len_back, dec_buf = decoder.get_decoded_data()
    print "dec_buf:", pretty_bin_buffer(dec_buf)
    nose.tools.assert_equal(msg_len_back, msg_len)
    nose.tools.assert_equal(bits_back, bits)

    # check the bits in dec_buf
    dec_buf_bits = []
    for i in xrange(msg_len):
        byte_index = i / 8
        bit_index = i % 8
        dec_buf_bits.append(byte_bit(ord(dec_buf[byte_index]), bit_index))
    nose.tools.assert_equal(dec_buf_bits, bits)

    # check the padding in dec_buf
    padding_bits = []
    for i in xrange(bit_index + 1, 8):
        padding_bits.append(byte_bit(ord(dec_buf[byte_index]), i))
    nose.tools.assert_equal(padding_bits, [0] * ((8 - msg_len % 8) % 8))


def test_short_msg_const_symmetric_prob():
    bits = [0, 1, 0, 0, 1]
    probs = [0.5] * len(bits)
    _encode_decode(bits, probs)


def test_short_msg_const_asymmetric_prob():
    for prob in [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]:
        print "************* trying prob={}".format(prob)
        bits = [0, 1, 0, 0, 1]
        probs = [prob] * len(bits)
        _encode_decode(bits, probs)


def test_short_msg_changing_prob():
    bits = [0, 1, 0, 0, 1, 1]
    probs = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    _encode_decode(bits, probs)


def random_test_long_msg_changing_prob():
    msg_len = 1000
    bits = []
    probs = []
    random.seed(666)
    for i in xrange(msg_len):
        bits.append(random.choice((0, 1)))
        prob = random.random()
        if prob < 0.01:
            prob = 0.01
        if prob > 0.99:
            prob = 0.99
        probs.append(prob)
    _encode_decode(bits, probs)
