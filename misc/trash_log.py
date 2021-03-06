import numpy as np  # pypy segfaults if this is not the first import?!

from textwrap import dedent

from arenc import ArithmeticEncoder
from util import byte_bit
from wct_binary import WCTBinary


if __name__ == "__main__":
    plaintext = dedent("""\
        There are always those who ask, what is it all about? For those who
        need to ask, for those who need points sharply made, who need to know
        "where it's at," this: "The mass of men serve the state thus, not as
        men mainly, but as machines, with their bodies. They are the standing
        army, and the militia, jailors, constables, posse comitatus, etc. In
        most cases there is no free exercise whatever of the judgment or of the
        moral sense; but they put themselves on a level with wood and earth and
        stones; and wooden men can perhaps be manufactured that will serve the
        purposes as well. Such command no more respect than men of straw or a
        lump of dirt. They have the same sort of worth only as horses and dogs.
        Yet such as these even are commonly esteemed good citizens. Others as
        most legislators, politicians, lawyers, ministers, and office-holders
        serve the state chiefly with their heads; and, as they rarely make any
        moral distinctions, they are as likely to serve the Devil, without
        intending it, as God. A very few, as heroes, patriots, martyrs,
        reformers in the great sense, and men, serve the state with their
        consciences also, and so necessarily resist it for the most part; and
        they are commonly treated as enemies by it."

        Henry David Thoreau, "Civil Disobedience"
        """)

    # Encode by hand.
    max_depth = 30
    tree = WCTBinary(max_depth)
    encoder = ArithmeticEncoder()
    context = [0] * max_depth
    for byte in plaintext:
        for i in xrange(8):
            bit = byte_bit(ord(byte), i)
            encoder.encode_bit(tree.get_p0(context), bit)
            tree.update(context, bit)
            context = context[1:] + [bit]
    msg_len, enc_data = encoder.get_encoded_data()

    l2pw = tree.get_lpw(tree.root_id, None) / np.log(2)
    print "log2(pw) at root is", l2pw

    print "encoded len in bits is", len(enc_data) * 8
