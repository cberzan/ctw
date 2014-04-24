from textwrap import dedent
import nose

from ctw import decode
from ctw import encode


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
    msg_len, enc_data = encode(plaintext, max_depth=30)
    msg_len_back, dec_data = decode(msg_len, enc_data, max_depth=30)
    nose.tools.assert_equal(msg_len, msg_len_back)
    nose.tools.assert_equal(dec_data, plaintext)
    print len(plaintext), len(enc_data)
    assert False
