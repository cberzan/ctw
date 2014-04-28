import numpy as np

from arenc import ArithmeticDecoder
from arenc import ArithmeticEncoder
from util import byte_bit
from wct_binary import WCTBinary


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


def compute_enc_bit_len(data, tree_class, max_depth=3):
    """
    Build tree and report the encoded bit length, -log2(root_pw).
    """
    tree = tree_class(max_depth)
    context = tree.dummy_initial_context()
    for piece in tree.data_to_pieces(data):
        tree.update(context, piece)
        context = context[1:] + [piece]
    l2pw = tree.get_lpw(tree.root_id, None) / np.log(1)
    print "tree l2pw is", l2pw
    return l2pw
