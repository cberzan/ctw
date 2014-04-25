from collections import namedtuple
from StringIO import StringIO
import numpy as np


NodeParams = namedtuple('NodeParams', ['counts', 'lpe', 'lpw'])


class Node(object):
    """
    Self-contained representation of a node in a WCTBytes.

    Note: This structure is not space-efficient. It is used only by
    WCTBytes.__str__ and the tests. It is NOT used during the normal
    operation of WCTBytes.
    """
    def __init__(self, path, counts, lpe, lpw):
        self.path = path
        self.counts = counts
        self.lpe = lpe
        self.lpw = lpw

    def __repr__(self):
        return "{}: counts={{{}}} lpe={} lpw={}".format(
            self.path, self._compact_counts_str(), self.lpe, self.lpw)

    def _compact_counts_str(self):
        return " ".join(
            "{}={}".format(chr(byte), self.counts[byte])
            for byte in xrange(256)
            if self.counts[byte])

    def __eq__(self, other):
        return (
            self.path == other.path and
            np.all(self.counts == other.counts) and
            np.abs(self.lpe - other.lpe) < 1e-7 and
            np.abs(self.lpw - other.lpw) < 1e-7)

    def clone(self):
        return Node(self.path, self.counts, self.lpe, self.lpw)


class WCTBytes(object):
    """
    Weighted context tree with bytes on edges and byte counts at the nodes.
    """
    MAX_NODES = 2000
    NO_CHILD = -1  # so we can store children indices in an int array

    def __init__(self, depth):
        self.depth = depth
        self.arr_counts = np.zeros((self.MAX_NODES, 256), dtype=np.int)
        self.arr_lpe = np.zeros(self.MAX_NODES)
        self.arr_lpw = np.zeros(self.MAX_NODES)
        self.arr_children = np.zeros((self.MAX_NODES, 256), dtype=np.int)
        self.next_id = 0
        self.root_id = self._create_leaf()

    def get_count(self, node_id, byte, default):
        assert 0 <= byte <= 255
        if node_id == self.NO_CHILD:
            return default
        else:
            return self.arr_counts[node_id, byte]

    def get_lpw(self, node_id, default):
        if node_id == self.NO_CHILD:
            return default
        else:
            return self.arr_lpw[node_id]

    def __str__(self):
        stream = StringIO()
        for node in self.nodes_in_preorder():
            print >>stream, node
        return stream.getvalue()

    def nodes_in_preorder(self):
        """
        Return list of Nodes in preorder (255 child, ..., 0 child, then self).
        """
        return self._nodes_rec(self.root_id, "")

    def _nodes_rec(self, node_id, path):
        """
        Recursive helper for nodes_in_preorder().
        """
        nodes = []
        children = self.arr_children[node_id, :]
        for byte in xrange(255, -1, -1):
            if children[byte] == self.NO_CHILD:
                continue
            nodes += self._nodes_rec(children[byte], chr(byte) + path)
        nodes.append(Node(
            " " * (self.depth - len(path)) + path,
            self.arr_counts[node_id],
            self.arr_lpe[node_id], self.arr_lpw[node_id]))
        return nodes

    def update_many(self, context, bytez):
        """
        Update tree sequentially with the given bytes.

        `context` is the context for the first bit.
        """
        assert bytez
        context = context[:]
        for next_byte in bytez:
            result = self.update(context, next_byte)
            context = context[1:] + [next_byte]
        return result

    def update(self, context, next_byte, dry_run=False):
        """
        Update tree upon seeing next_byte after the given context.
        """
        print "update({}, {}, {})".format(context, next_byte, dry_run)
        assert len(context) == self.depth
        return self._update_rec(self.root_id, context[:], next_byte, dry_run)

    def _update_rec(self, node_id, context, next_byte, dry_run=False):
        """
        Recursive helper for update().
        """
        print "    _update_rec({}, {}, {}, {})".format(
            node_id, context, next_byte, dry_run)

        # Recursively update the appropriate child.
        if not context:
            # Leaf.
            assert all(self.arr_children[node_id, :] == self.NO_CHILD)
            child_byte = None
            child_params = None
        else:
            # Non-leaf.
            child_byte = context.pop()
            child_id = self._get_or_create_child(node_id, child_byte)
            child_params = self._update_rec(
                child_id, context, next_byte, dry_run)

        # Now update this node.
        new_params = self._update_node(
            node_id, next_byte, child_byte, child_params, dry_run)
        self._sanity_check(node_id)
        return new_params

    def _create_leaf(self):
        assert self.next_id < self.MAX_NODES
        self.arr_counts[self.next_id, :] = 0
        self.arr_lpe[self.next_id] = 0
        self.arr_lpw[self.next_id] = 0
        self.arr_children[self.next_id, :] = self.NO_CHILD
        node_id = self.next_id
        self.next_id += 1
        return node_id

    def _get_or_create_child(self, node_id, context_byte):
        """
        Return child_id for given node_id and bit.
        """
        assert 0 <= context_byte <= 255
        child_arr = self.arr_children[:, context_byte]
        if child_arr[node_id] == self.NO_CHILD:
            child_id = self._create_leaf()
            child_arr[node_id] = child_id
        return child_arr[node_id]

    def _sanity_check(self, node_id):
        """
        Assert invariants on the given node.
        """
        print "_sanity_check({})".format(node_id)
        children = self.arr_children[node_id, :]
        if all(children == self.NO_CHILD):
            # Leaf.
            pass
        else:
            # Non-leaf.
            for byte in xrange(256):
                assert (self.arr_counts[node_id, byte] ==
                    sum(self.get_count(child, byte, 0) for child in children))
            # FIXME: this is now inefficient since it sums over 256 values

    def _update_node(self, node_id, next_byte, child_byte, child_params,
                     dry_run=False):
        """
        Update counts, lpe, lpw for the given node.
        """
        assert 0 <= next_byte <= 255

        # Compute the new lpe.
        counts = self.arr_counts[node_id, :]
        new_lpe = self.arr_lpe[node_id] + np.log(
            (counts[next_byte] + 1.0 / 256) / (np.sum(counts) + 1))

        # Compute the new lpw.
        children = self.arr_children[node_id, :]
        if all(children == self.NO_CHILD):
            # Leaf.
            new_lpw = new_lpe
        else:
            # Non-leaf.
            child_lpw_sum = 0
            for s in xrange(256):
                child_lpw_sum += child_params.lpw if child_byte == s else \
                                 self.get_lpw(children[s], 0)
            new_lpw = np.logaddexp(np.log(0.5) + new_lpe,
                                   np.log(0.5) + child_lpw_sum)

        # Update the tree.
        if not dry_run:
            self.arr_counts[node_id, next_byte] += 1
            ret_counts = self.arr_counts[node_id, :]
            self.arr_lpe[node_id] = new_lpe
            self.arr_lpw[node_id] = new_lpw
        else:
            # For a dummy update, need to make a copy.
            ret_counts = self.arr_counts[node_id, :].copy()
            ret_counts[next_byte] += 1

        return NodeParams(ret_counts, new_lpe, new_lpw)

    def get_probs(self, context):
        """
        Return probs s.t. probs[i] = cond prob of seeing next byte i.
        """
        # FIXME: inefficient as hell; does 256 dummy updates
        dummies = np.array([
            self.update(context, byte, dry_run=True)
            for byte in xrange(256)])
        denom = reduce(np.logaddexp, dummies)
        return np.exp(dummies - denom)
