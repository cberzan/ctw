import numpy as np

from arenc import ArithmeticDecoder
from arenc import ArithmeticEncoder
from util import byte_bit
from wct_binary import WCTBinary
from wct_bytes import WCTBytes
from wct_phases import WCTPhases


def encode(data, max_depth=3):
    """
    Encode data using WCTBinary and return (msg_len, enc_data).
    """
    tree = WCTBinary(max_depth)
    encoder = ArithmeticEncoder()
    context = [0] * max_depth
    for byte in data:
        for i in xrange(8):
            bit = byte_bit(ord(byte), i)
            encoder.encode_bit(tree.get_p0(context), bit)
            tree.update(context, bit)
            context = context[1:] + [bit]
    print "tree size is", tree.next_id
    return encoder.get_encoded_data()


def decode(msg_len, enc_data, max_depth=3):
    """
    Decode enc_data using WCTBinary and return (msg_len, dec_data).
    """
    tree = WCTBinary(max_depth)
    decoder = ArithmeticDecoder(msg_len, enc_data)
    context = [0] * max_depth
    for i in xrange(msg_len):
        bit = decoder.decode_bit(tree.get_p0(context))
        tree.update(context, bit)
        context = context[1:] + [bit]
    return decoder.get_decoded_data()


def enc_len(data, max_depth=3):
    """
    Build WCTBinary and report the length of the encoded message (in bits).
    """
    tree = WCTBinary(max_depth)
    context = [0] * max_depth
    for byte in data:
        for i in xrange(8):
            bit = byte_bit(ord(byte), i)
            tree.update(context, bit)
            context = context[1:] + [bit]
    l2pw = tree.get_lpw(tree.root_id, None) / np.log(2)
    print "tree l2pw is", l2pw
    return -l2pw


def encode_phases(data, max_depth=3):
    """
    Encode data using WCTPhases and return (msg_len, enc_data)
    """
    tree = WCTPhases(max_depth)
    encoder = ArithmeticEncoder()
    context = [0] * max_depth
    for byte in data:
        phase = ()
        for i in xrange(8):
            bit = byte_bit(ord(byte), i)
            encoder.encode_bit(tree.get_p0(context, phase), bit)
            tree.update(context, phase, bit)
            phase += (bit,)
        context = context[1:] + [ord(byte)]
    print "tree size is", sum(t.next_id for t in tree.phase_trees.values())
    return encoder.get_encoded_data()


def decode_phases(msg_len, enc_data, max_depth=3):
    """
    Decode enc_data using WCTPhases and return (msg_len, dec_data).
    """
    tree = WCTPhases(max_depth)
    decoder = ArithmeticDecoder(msg_len, enc_data)
    context = [0] * max_depth
    for i in xrange(msg_len / 8):
        phase = ()
        for j in xrange(8):
            bit = decoder.decode_bit(tree.get_p0(context, phase))
            tree.update(context, phase, bit)
            phase += (bit,)
        byte = 0
        for bit in phase:
            byte = (byte << 1) | bit
        context = context[1:] + [byte]
    return decoder.get_decoded_data()


def enc_len_phases(data, max_depth=3):
    """
    Build WCTPhases and report the length of the encoded message (in bits).
    """
    tree = WCTPhases(max_depth)
    context = [0] * max_depth
    for byte in data:
        phase = ()
        for i in xrange(8):
            bit = byte_bit(ord(byte), i)
            tree.update(context, phase, bit)
            phase += (bit,)
        context = context[1:] + [ord(byte)]
    print "tree size is", sum(t.next_id for t in tree.phase_trees.values())
    raise NotImplementedError()
    # FIXME: No idea what's the probability of the whole sequence...


def encode_bytes(data, max_depth=3):
    """
    Encode data using WCTBytes and return (msg_len, enc_data).
    """
    # Don't yet have an arithmetic encoder that works on bytes.
    raise NotImplementedError()


def decode_bytes(msg_len, enc_data, max_depth=3):
    """
    Decode enc_data using WCTBytes and return (msg_len, dec_data).
    """
    # Don't yet have an arithmetic decoder that works on bytes.
    raise NotImplementedError()


def enc_len_bytes(data, max_depth=3):
    """
    Build WCTBytes and report the length of the encoded message (in bits).
    """
    tree = WCTBytes(max_depth)
    context = [0] * max_depth
    for byte in data:
        byte = ord(byte)
        tree.update(context, byte)
        context = context[1:] + [byte]
    l2pw = tree.get_lpw(tree.root_id, None) / np.log(2)
    print "tree l2pw is", l2pw
    return -l2pw
