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
    print tree
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 4)
    nose.tools.assert_equal(nodes[0], Node('010', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[1], Node(' 10', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[2], Node('  0', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[3], Node('   ', 1, 0, 0.5, 0.5))

def test_dry_run():
    tree = WCTBinary(3)
    new_params = tree.update([0, 1, 0], 0, dry_run=True)
    print new_params
    print tree
    nodes = tree.nodes_in_preorder()
    # first make sure we didn't mess with the tree at all
    nose.tools.assert_equal(len(nodes), 4)
    nose.tools.assert_equal(nodes[0], Node('010', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[1], Node(' 10', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[2], Node('  0', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[3], Node('   ', 0, 0, 1, 1))
    # next make sure we computed the right new parameters
    nose.tools.assert_equal(new_params['a'], 1)
    nose.tools.assert_equal(new_params['b'], 0)
    nose.tools.assert_equal(new_params['pe'], 0.5)
    nose.tools.assert_equal(new_params['pw'], 0.5)

def test_eidma_figure_3_2():
    tree = WCTBinary(3)
    context = [0, 1, 0]
    bits = [0, 1, 1, 0, 1, 0, 0]
    while bits:
        next_bit = bits[0]
        tree.update(context, next_bit)
        context = context[1:] + [next_bit]
        bits = bits[1:]
    print tree
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 13)
    nose.tools.assert_equal(nodes[0],  Node('011', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[1],  Node(' 11', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[2],  Node('101', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[3],  Node('001', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[4],  Node(' 01', 1, 1, 1. / 8, 3. / 16))
    nose.tools.assert_equal(nodes[5],  Node('  1', 2, 1, 1. / 16, 5. / 64))
    nose.tools.assert_equal(nodes[6],  Node('110', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[7],  Node('010', 2, 0, 3. / 8, 3. / 8))
    nose.tools.assert_equal(nodes[8],  Node(' 10', 2, 1, 1. / 16, 1. / 8))
    nose.tools.assert_equal(nodes[9],  Node('100', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[10], Node(' 00', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[11], Node('  0', 2, 2, 3. / 128, 11. / 256))
    nose.tools.assert_equal(nodes[12],
        Node('   ', 4, 3, 5. / 2048, 95. / 32768))
