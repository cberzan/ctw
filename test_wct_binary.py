import nose
import numpy as np

from wct_binary import Node
from wct_binary import WCTBinary

def make_node(path, a, b, pe, pw):
    return Node(path, a, b, np.log(pe), np.log(pw))


def test_init():
    tree = WCTBinary(3)
    print tree
    nose.tools.assert_equal(tree.root_id, 0)
    nose.tools.assert_equal(tree.next_id, 1)
    nose.tools.assert_equal(tree.get_a(tree.root_id, None), 0)
    nose.tools.assert_equal(tree.get_b(tree.root_id, None), 0)
    nose.tools.assert_almost_equal(tree.get_lpw(tree.root_id, None), 0)


def test_single_update():
    tree = WCTBinary(3)
    tree.update([0, 1, 0], 0)
    print tree
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 4)
    nose.tools.assert_equal(nodes[0], make_node('010', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[1], make_node(' 10', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[2], make_node('  0', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[3], make_node('   ', 1, 0, 0.5, 0.5))


def test_dry_run():
    tree = WCTBinary(3)
    new_params = tree.update([0, 1, 0], 0, dry_run=True)
    print new_params
    print tree
    nodes = tree.nodes_in_preorder()
    # first make sure we didn't mess with the tree at all
    nose.tools.assert_equal(len(nodes), 4)
    nose.tools.assert_equal(nodes[0], make_node('010', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[1], make_node(' 10', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[2], make_node('  0', 0, 0, 1, 1))
    nose.tools.assert_equal(nodes[3], make_node('   ', 0, 0, 1, 1))
    # next make sure we computed the right new parameters
    nose.tools.assert_equal(new_params.a, 1)
    nose.tools.assert_equal(new_params.b, 0)
    nose.tools.assert_equal(new_params.lpe, np.log(0.5))
    nose.tools.assert_equal(new_params.lpw, np.log(0.5))


def test_eidma_figure_3_2():
    tree = WCTBinary(3)
    context = [0, 1, 0]
    bits = [0, 1, 1, 0, 1, 0, 0]
    tree.update_many(context, bits)
    print tree
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 13)
    nose.tools.assert_equal(nodes[0],  make_node('011', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[1],  make_node(' 11', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[2],  make_node('101', 1, 0, 0.5, 0.5))
    nose.tools.assert_equal(nodes[3],  make_node('001', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[4],  make_node(' 01', 1, 1, 1. / 8, 3. / 16))
    nose.tools.assert_equal(nodes[5],  make_node('  1', 2, 1, 1. / 16, 5. / 64))
    nose.tools.assert_equal(nodes[6],  make_node('110', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[7],  make_node('010', 2, 0, 3. / 8, 3. / 8))
    nose.tools.assert_equal(nodes[8],  make_node(' 10', 2, 1, 1. / 16, 1. / 8))
    nose.tools.assert_equal(nodes[9],  make_node('100', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[10], make_node(' 00', 0, 1, 0.5, 0.5))
    nose.tools.assert_equal(nodes[11], make_node('  0', 2, 2, 3. / 128, 11. / 256))
    nose.tools.assert_equal(nodes[12],
        make_node('   ', 4, 3, 5. / 2048, 95. / 32768))

    p0 = tree.get_p0([1, 0, 0])
    nose.tools.assert_almost_equal(p0, 0.42105263157894735)


def test_dummy_updates():
    tree = WCTBinary(3)
    context = [0, 1, 0]
    bits = [0, 1, 1, 0, 1, 0, 0]
    tree.update_many(context, bits)

    params = tree.update([1, 0, 0], 0, dry_run=True)
    nose.tools.assert_equal(params.a, 5)
    nose.tools.assert_equal(params.b, 3)
    nose.tools.assert_almost_equal(params.lpe, np.log(0.001373291015625))
    nose.tools.assert_almost_equal(params.lpw, np.log(0.001220703125))

    params = tree.update([1, 0, 0], 1, dry_run=True)
    nose.tools.assert_equal(params.a, 4)
    nose.tools.assert_equal(params.b, 4)
    nose.tools.assert_almost_equal(params.lpe, np.log(0.001068115234375))
    nose.tools.assert_almost_equal(params.lpw, np.log(0.001678466796875))


def test_p0():
    tree = WCTBinary(3)
    context = [0, 1, 0]
    p0 = tree.get_p0(context)
    nose.tools.assert_almost_equal(p0, 0.5)
