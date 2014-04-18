import nose

from wct_binary import Node
from wct_binary import WCTBinary


def test_init():
    tree = WCTBinary(3)
    print tree
    nose.tools.assert_equal(tree.root_id, 0)
    nose.tools.assert_equal(tree.next_id, 1)
    nose.tools.assert_equal(tree.get_a(tree.root_id, None), 0)
    nose.tools.assert_equal(tree.get_b(tree.root_id, None), 0)
    nose.tools.assert_almost_equal(tree.get_pw(tree.root_id, None), 1)


def test_single_update():
    tree = WCTBinary(3)
    tree.update([0, 1, 0], 0)
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 4)
    print tree
    nose.tools.assert_equal(nodes[0], Node('010', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[1], Node(' 10', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[2], Node('  0', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[3], Node('   ', 1, 0, 0.5, 0.5))
