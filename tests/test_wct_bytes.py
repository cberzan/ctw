import nose
import numpy as np

from ctw.wct_bytes import Node
from ctw.wct_bytes import WCTBytes


def make_node(path, counts_dict, pe, pw):
    counts = np.zeros(256, dtype=np.int)
    for char, count in counts_dict.iteritems():
        counts[ord(char)] = count
    return Node(path, counts, np.log(pe), np.log(pw))


def test_init():
    tree = WCTBytes(3)
    print tree
    nose.tools.assert_equal(tree.root_id, 0)
    nose.tools.assert_equal(tree.next_id, 1)
    for byte in xrange(256):
        nose.tools.assert_equal(tree.get_count(tree.root_id, byte, None), 0)
    nose.tools.assert_almost_equal(tree.get_lpw(tree.root_id, None), 0)


def test_single_update():
    tree = WCTBytes(3)
    tree.update([ord('a'), ord('b'), ord('c')], ord('d'))
    print tree
    nodes = tree.nodes_in_preorder()
    nose.tools.assert_equal(len(nodes), 4)
    p = 1. / 256
    nose.tools.assert_equal(nodes[0], make_node('abc', {'d': 1}, p, p))
    nose.tools.assert_equal(nodes[1], make_node(' bc', {'d': 1}, p, p))
    nose.tools.assert_equal(nodes[2], make_node('  c', {'d': 1}, p, p))
    nose.tools.assert_equal(nodes[3], make_node('   ', {'d': 1}, p, p))


def test_dry_run():
    tree = WCTBytes(3)
    new_params = tree.update(
        [ord('a'), ord('b'), ord('c')], ord('d'), dry_run=True)
    print new_params
    print tree
    nodes = tree.nodes_in_preorder()
    # first make sure we didn't mess with the tree at all
    nose.tools.assert_equal(len(nodes), 4)
    nose.tools.assert_equal(nodes[0], make_node('abc', {}, 1, 1))
    nose.tools.assert_equal(nodes[1], make_node(' bc', {}, 1, 1))
    nose.tools.assert_equal(nodes[2], make_node('  c', {}, 1, 1))
    nose.tools.assert_equal(nodes[3], make_node('   ', {}, 1, 1))
    # next make sure we computed the right new parameters
    nose.tools.assert_equal(new_params.counts[ord('d')], 1)
    nose.tools.assert_equal(np.sum(new_params.counts), 1)
    nose.tools.assert_equal(new_params.lpe, np.log(1. / 256))
    nose.tools.assert_equal(new_params.lpw, np.log(1. / 256))


def test_probs():
    tree = WCTBytes(3)
    context = [ord('a'), ord('b'), ord('c')]
    probs = tree.get_probs(context)
    true_probs = np.ones(256) / 256
    nose.tools.assert_true(np.sum(np.abs(probs - true_probs)) < 1e-6)
