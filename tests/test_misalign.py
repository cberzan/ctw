import nose

from ctw.misalign import add_leading_0_bit


def test_add_leading_0_bit():
    in_data = "abcd"
    out_data = add_leading_0_bit(in_data)
    out_bytes = [ord(char) for char in out_data]
    out_bytes_ref = [0x30, 0x98, 0x8C, 0x66, 0x40]
    nose.tools.assert_equal(out_bytes, out_bytes_ref)
