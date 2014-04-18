import nose

from wct_binary import WCTBinary


def test_init():
    tree = WCTBinary(3)
    nose.tools.assert_equal(tree.root_id, 0)
    nose.tools.assert_equal(tree.next_id, 1)
    nose.tools.assert_equal(tree.get_a(tree.root_id, None), 0)
    nose.tools.assert_equal(tree.get_b(tree.root_id, None), 0)
    nose.tools.assert_almost_equal(tree.get_pw(tree.root_id, None), 1)
