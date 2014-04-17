import nose

from arenc import ArithmeticDecoder
from arenc import ArithmeticEncoder
from util import byte_bit
from util import pretty_bin_buffer


def test_byte_bit():
    nose.tools.assert_equal(byte_bit(0x41, 0), 0)
    nose.tools.assert_equal(byte_bit(0x41, 1), 1)
    nose.tools.assert_equal(byte_bit(0x41, 2), 0)
    nose.tools.assert_equal(byte_bit(0x41, 3), 0)
    nose.tools.assert_equal(byte_bit(0x41, 4), 0)
    nose.tools.assert_equal(byte_bit(0x41, 5), 0)
    nose.tools.assert_equal(byte_bit(0x41, 6), 0)
    nose.tools.assert_equal(byte_bit(0x41, 7), 1)


def test_const_symmetric_prob():
    bits = [0, 1, 0, 0, 1]

    print "---------------- encoding"
    encoder = ArithmeticEncoder()
    for bit in bits:
        encoder.encode_bit(0.5, bit)
    msg_len, enc_buf = encoder.get_encoded_data()
    print "enc_buf:", pretty_bin_buffer(enc_buf)
    nose.tools.assert_equal(msg_len, len(bits))

    print "---------------- decoding"
    decoder = ArithmeticDecoder(msg_len, enc_buf)
    bits_back = []
    for i in xrange(msg_len):
        bit = decoder.decode_bit(0.5)
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
    nose.tools.assert_equal(padding_bits, [0] * (8 - msg_len % 8))
