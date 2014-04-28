def byte_bit(byte, bit_index):
    """
    Return bit in `byte` at position `bit_index` where 0 is leftmost.
    """
    assert 0 <= byte <= 0xFF
    assert 0 <= bit_index < 8
    return (byte >> (7 - bit_index)) & 0x01


def pretty_bin_buffer(buf):
    return " ".join("{:08b}".format(ord(char)) for char in buf)
