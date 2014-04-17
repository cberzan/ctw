# This is a simple arithmetic encoder / decoder as described on Wikipedia.
# I think it's the same as Rubin's encoder described in EIDMA section 6.1.1.
# It is not as fancy as what the CTW implementation uses. See EIDMA section
# 6.1.3 for limitations of this encoder. In particular, in split_interval,
# total_length can be small, leading to imprecise splitting. For example, if
# total_length is 2, the interval is split in half, regardless of p0.


def split_interval(a, b, p0):
    """
    Split [a, b] into [a0, b0] and [a1, b1] according to p0.
    """
    assert 0 <= a <= 0xFF
    assert 0 <= b <= 0xFF
    total_length = b - a + 1
    assert total_length >= 2
    new_length_0 = int(p0 * total_length)

    # Make sure we don't produce intervals of zero length:
    if new_length_0 == 0:
        new_length_0 = 1
    elif new_length_0 == total_length:
        new_length_0 = total_length - 1

    a0, b0 = a, a + new_length_0 - 1
    a1, b1 = a + new_length_0, b
    assert a0 <= b0
    assert a1 <= b1
    return a0, b0, a1, b1


class ArithmeticEncoder(object):
    """
    Arithmetic encoder.

    TODO usage
    explain bit order?
    """
    def __init__(self):
        # store result of encoding:
        self.msg_len = 0
        self.all_bytes = []
        self.cur_byte = 0
        self.bits_in_cur_byte = 0

        # current interval:
        self.cur_ival_a = 0
        self.cur_ival_b = 0xFF

        # finalized result:
        self.encoded_buffer = None

    def _emit_bit(self, bit):
        print "emit {}".format(bit)
        assert bit in (0, 1)
        self.cur_byte = (self.cur_byte << 1) | bit
        self.bits_in_cur_byte += 1
        if self.bits_in_cur_byte == 8:
            self.all_bytes.append(self.cur_byte)
            self.cur_byte = 0
            self.bits_in_cur_byte = 0

    def encode_bit(self, p0, bit):
        assert not self.encoded_buffer, "finalized; can't encode more bits"
        assert 0 <= p0 <= 1
        assert bit in (0, 1)

        # Scale current interval (emit bits at the beginning that can't change
        # anymore).
        while (self.cur_ival_a >> 7) == (self.cur_ival_b >> 7):
            old_a, old_b = self.cur_ival_a, self.cur_ival_b
            self._emit_bit(self.cur_ival_a >> 7)
            self.cur_ival_a = (self.cur_ival_a << 1) & 0xFF
            self.cur_ival_b = ((self.cur_ival_b << 1) & 0xFF) | 0x01
            print (
                "scaling      "
                "old_a={:08b} old_b={:08b} new_a={:08b} new_b={:08b}"
                .format(old_a, old_b, self.cur_ival_a, self.cur_ival_b))

        # Subdivide current interval according to p0, and take one of the two
        # resulting sub-intervals, based on bit.
        old_a, old_b = self.cur_ival_a, self.cur_ival_b
        a0, b0, a1, b1 = split_interval(self.cur_ival_a, self.cur_ival_b, p0)
        if bit == 0:
            self.cur_ival_a, self.cur_ival_b = a0, b0
        else:
            self.cur_ival_a, self.cur_ival_b = a1, b1
        print (
            "p0={} bit={} old_a={:08b} old_b={:08b} new_a={:08b} new_b={:08b}"
            .format(p0, bit, old_a, old_b, self.cur_ival_a, self.cur_ival_b))

        self.msg_len += 1

    def get_encoded_data(self):
        if not self.encoded_buffer:
            # Finalize encoding by emitting cur_ival_a.
            print "emitting cur_ival_a"
            for pos in range(7, -1, -1):
                self._emit_bit(1 if self.cur_ival_a & (1 << pos) else 0)

            # Pad with zeros, at least once, and up to a complete byte.
            print "padding"
            self._emit_bit(0)
            while self.bits_in_cur_byte:
                self._emit_bit(0)

            # Concatenate encoded bytes.
            self.encoded_buffer = ''.join(chr(byte) for byte in self.all_bytes)

        return self.msg_len, self.encoded_buffer


class ArithmeticDecoder(object):
    """
    Arithmetic decoder.

    TODO usage
    """
    def __init__(self, msg_len, encoded_buffer):
        self.msg_len = msg_len
        self.encoded_buffer = encoded_buffer

        # indices into encoded_buffer:
        self.byte_index = 0
        self.bit_index = 0

        # store result of decoding:
        self.decoded_bytes = []
        self.cur_byte = 0
        self.bits_in_cur_byte = 0

        # current interval:
        self.cur_ival_a = 0
        self.cur_ival_b = 0xFF

        # finalized result:
        self.decoded_buffer = None

    def _emit_bit(self, bit):
        print "emit {}".format(bit)
        assert bit in (0, 1)
        self.cur_byte = (self.cur_byte << 1) | bit
        self.bits_in_cur_byte += 1
        if self.bits_in_cur_byte == 8:
            self.decoded_bytes.append(self.cur_byte)
            self.cur_byte = 0
            self.bits_in_cur_byte = 0

    def decode_bit(self, p0):
        assert not self.decoded_buffer, "finalized; can't decode more bits"
        assert 0 <= p0 <= 1

        if 8 * len(self.decoded_bytes) + self.bits_in_cur_byte >= self.msg_len:
            raise IndexError("ran out of bits to decode")

        # Scale current interval, and advance index into encoded_buffer.
        while (self.cur_ival_a >> 7) == (self.cur_ival_b >> 7):
            old_a, old_b = self.cur_ival_a, self.cur_ival_b
            self.bit_index += 1
            if self.bit_index == 8:
                self.byte_index += 1
                self.bit_index = 0
            self.cur_ival_a = (self.cur_ival_a << 1) & 0xFF
            self.cur_ival_b = ((self.cur_ival_b << 1) & 0xFF) | 0x01
            print (
                "scaling      "
                "old_a={:08b} old_b={:08b} new_a={:08b} new_b={:08b} "
                "byte_i={} bit_i={}"
                .format(
                    old_a, old_b, self.cur_ival_a, self.cur_ival_b,
                    self.byte_index, self.bit_index))

        # Get the current encoded byte. The index is given by (byte_index,
        # bit_index), and in general it straddles two bytes.
        left_byte = ord(self.encoded_buffer[self.byte_index])
        right_byte = ord(self.encoded_buffer[self.byte_index + 1])
        left_part = (left_byte << self.bit_index) & 0xFF
        right_part = right_byte >> (8 - self.bit_index)
        encoded_byte = left_part | right_part

        # Subdivide current interval according to p0, and take one of the two
        # resulting sub-intervals, depending on where encoded_byte falls.
        old_a, old_b = self.cur_ival_a, self.cur_ival_b
        a0, b0, a1, b1 = split_interval(self.cur_ival_a, self.cur_ival_b, p0)
        if encoded_byte <= b0:
            decoded_bit = 0
            self.cur_ival_a, self.cur_ival_b = a0, b0
        else:
            decoded_bit = 1
            self.cur_ival_a, self.cur_ival_b = a1, b1
        print (
            "p0={} byte_i={} bit_i={} encoded_byte={:08b} "
            "old_a={:08b} old_b={:08b} new_a={:08b} new_b={:08b}"
            .format(
                p0, self.byte_index, self.bit_index, encoded_byte,
                old_a, old_b, self.cur_ival_a, self.cur_ival_b))

        self._emit_bit(decoded_bit)
        return decoded_bit

    def get_decoded_data(self):
        if not self.decoded_buffer:
            # If we have an incomplete byte, pad with zeros.
            print "padding"
            while self.bits_in_cur_byte:
                self._emit_bit(0)

            # Concatenate encoded bytes.
            self.decoded_buffer = ''.join(
                chr(byte) for byte in self.decoded_bytes)

        return self.msg_len, self.decoded_buffer
