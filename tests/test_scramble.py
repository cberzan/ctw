import nose

from scramble import mapping_from_seed
from scramble import scramble
from scramble import unscramble


def test_scramble():
    mapping = mapping_from_seed(666)
    text = "jigsaw falling into place"
    scrambled = scramble(text, mapping)
    nose.tools.assert_equal(len(scrambled), len(text))
    text_back = unscramble(scrambled, mapping)
    nose.tools.assert_equal(text_back, text)
