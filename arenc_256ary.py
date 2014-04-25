import numpy as np


WIDTH = 62


def update_interval(a, b, probs, byte):
    """
    Split [a, b] into 256 intervals according to probs.

    Return the byte-th interval.
    """
    mask = (1 << WIDTH) - 1
    assert 0 <= a <= mask
    assert 0 <= b <= mask
    total_length = b - a + 1
    assert total_length >= 256
    assert probs.shape == (256,)
    assert np.all(probs >= 0)
    assert np.abs(np.sum(probs) - 1) < 1e-6
    assert 0 <= byte <= 0xFF

    # LEFT TODO: Realized that in the worst case we have an interval s.t.
    # b = a + 1, and in that case there's no way to split it into 256 pieces.


class ArithmeticEncoder256ary(object):
    """
    Arithmetic encoder that operates on bytes.

    ```
    encoder = ArithmeticEncoder()
    for ...:
        encoder.encode_bit(probs, byte)
    result = encoder.get_encoded_data()
    ```
    """

    def __init__(self):
        # store result of encoding:
        self.msg_len = 0  # in bytes
        self.all_bytes = []
        self.cur_byte = 0
        self.bits_in_cur_byte = 0

        # current interval (resolution is 62 bits):
        self.cur_ival_a = 0
        self.cur_ival_b = (1 << WIDTH) - 1

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

    def encode_byte(self, probs, byte):
        assert not self.encoded_buffer, "finalized; can't encode more bytes"

        # Scale current interval (emit bits at the beginning that can't change
        # anymore).
        while True:
            first_bit_a = self.cur_ival_a >> (WIDTH - 1)
            first_bit_b = self.cur_ival_b >> (WIDTH - 1)
            if first_bit_a != first_bit_b:
                break
            old_a, old_b = self.cur_ival_a, self.cur_ival_b
            self._emit_bit(first_bit_a)
            mask = (1 << WIDTH) - 1
            self.cur_ival_a = (self.cur_ival_a << 1) & mask
            self.cur_ival_b = ((self.cur_ival_b << 1) & mask) + 1
            print (
                "scaling       "
                "old_a={:62b} old_b={:62b} new_a={:62b} new_b={:62b}"
                .format(old_a, old_b, self.cur_ival_a, self.cur_ival_b))

        # Subdivide current interval according to p0, and take one of the two
        # resulting sub-intervals, based on bit.
        old_a, old_b = self.cur_ival_a, self.cur_ival_b
        self.cur_ival_a, self.cur_ival_b = update_interval(
            self.cur_ival_a, self.cur_ival_b, probs, byte)
        print (
            "byte={} old_a={:62b} old_b={:62b} new_a={:62b} new_b={:62b}"
            .format(byte, old_a, old_b, self.cur_ival_a, self.cur_ival_b))

        self.msg_len += 1

    def get_encoded_data(self):
        if not self.encoded_buffer:
            # Finalize encoding by emitting cur_ival_a.
            print "emitting cur_ival_a"
            for pos in range(WIDTH - 1, -1, -1):
                self._emit_bit(1 if self.cur_ival_a & (1 << pos) else 0)

            # Pad with zeros, at least once, and up to a complete byte.
            print "padding"
            self._emit_bit(0)
            while self.bits_in_cur_byte:
                self._emit_bit(0)

            # Concatenate encoded bytes.
            self.encoded_buffer = ''.join(chr(byte) for byte in self.all_bytes)

        return self.msg_len, self.encoded_buffer
