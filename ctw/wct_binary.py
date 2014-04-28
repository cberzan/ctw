from collections import namedtuple
from StringIO import StringIO
import numpy as np


NodeParams = namedtuple('NodeParams', ['a', 'b', 'lpe', 'lpw'])


class Node(object):
    """
    Self-contained representation of a node in a WCTBinary.

    Note: This structure is not space-efficient. It is used only by
    WCTBinary.__str__ and the tests. It is NOT used during the normal
    operation of WCTBinary.
    """
    def __init__(self, path, a, b, lpe, lpw):
        self.path = path
        self.a = a
        self.b = b
        self.lpe = lpe
        self.lpw = lpw

    def __repr__(self):
        return "{}: a={} b={} lpe={} lpw={}".format(
            self.path, self.a, self.b, self.lpe, self.lpw)

    def __eq__(self, other):
        return (
            self.path == other.path and
            self.a == other.a and
            self.b == other.b and
            np.abs(self.lpe - other.lpe) < 1e-7 and
            np.abs(self.lpw - other.lpw) < 1e-7)

    def clone(self):
        return Node(self.path, self.a, self.b, self.lpe, self.lpw)


class WCTBinary(object):
    """
    Binary weighted context tree.
    """
    MAX_NODES = 2000000
    NO_CHILD = -1  # so we can store children indices in an int array

    def __init__(self, depth):
        self.depth = depth
        self.arr_a = np.zeros(self.MAX_NODES, dtype=np.int)
        self.arr_b = np.zeros(self.MAX_NODES, dtype=np.int)
        self.arr_lpe = np.zeros(self.MAX_NODES)
        self.arr_lpw = np.zeros(self.MAX_NODES)
        self.arr_0c = np.zeros(self.MAX_NODES, dtype=np.int)
        self.arr_1c = np.zeros(self.MAX_NODES, dtype=np.int)
        self.next_id = 0
        self.root_id = self._create_leaf()

    def get_a(self, node_id, default):
        if node_id == self.NO_CHILD:
            return default
        else:
            return self.arr_a[node_id]

    def get_b(self, node_id, default):
        if node_id == self.NO_CHILD:
            return default
        else:
            return self.arr_b[node_id]

    def get_lpw(self, node_id, default):
        if node_id == self.NO_CHILD:
            return default
        else:
            return self.arr_lpw[node_id]

    def __str__(self):
        stream = StringIO()
        for node in self.nodes_in_postorder():
            print >>stream, node
        return stream.getvalue()

    def nodes_in_postorder(self):
        """
        Return list of Nodes in postorder (1 child, then 0 child, then self).
        """
        return self._nodes_rec(self.root_id, "")

    def _nodes_rec(self, node_id, path):
        """
        Recursive helper for nodes_in_postorder().
        """
        nodes = []
        if self.arr_1c[node_id] != self.NO_CHILD:
            nodes += self._nodes_rec(self.arr_1c[node_id], "1" + path)
        if self.arr_0c[node_id] != self.NO_CHILD:
            nodes += self._nodes_rec(self.arr_0c[node_id], "0" + path)
        nodes.append(Node(
            " " * (self.depth - len(path)) + path,
            self.arr_a[node_id], self.arr_b[node_id],
            self.arr_lpe[node_id], self.arr_lpw[node_id]))
        return nodes

    def update_many(self, context, bits):
        """
        Update tree sequentially with the given bits.

        `context` is the context for the first bit.
        """
        assert bits
        context = context[:]
        for next_bit in bits:
            result = self.update(context, next_bit)
            context = context[1:] + [next_bit]
        return result

    def update(self, context, next_bit, dry_run=False):
        """
        Update tree upon seeing next_bit after the given context.
        """
        assert len(context) == self.depth
        return self._update_rec(self.root_id, context[:], next_bit, dry_run)

    def _update_rec(self, node_id, context, next_bit, dry_run=False):
        """
        Recursive helper for update().
        """
        # Recursively update the appropriate child.
        if not context:
            # Leaf.
            assert self.arr_0c[node_id] == self.NO_CHILD
            assert self.arr_1c[node_id] == self.NO_CHILD
            child_bit = None
            child_params = None
        else:
            # Non-leaf.
            child_bit = context.pop()
            child_id = self._get_or_create_child(node_id, child_bit)
            child_params = self._update_rec(
                child_id, context, next_bit, dry_run)

        # Now update this node.
        new_params = self._update_node(node_id, next_bit,
                                       child_bit, child_params, dry_run)
        self._sanity_check(node_id)
        return new_params

    def _create_leaf(self):
        assert self.next_id < self.MAX_NODES
        self.arr_a[self.next_id] = 0
        self.arr_b[self.next_id] = 0
        self.arr_lpe[self.next_id] = 0
        self.arr_lpw[self.next_id] = 0
        self.arr_0c[self.next_id] = self.NO_CHILD
        self.arr_1c[self.next_id] = self.NO_CHILD
        node_id = self.next_id
        self.next_id += 1
        return node_id

    def _get_or_create_child(self, node_id, bit):
        """
        Return child_id for given node_id and bit.
        """
        assert bit in (0, 1)
        child_arr = (self.arr_0c, self.arr_1c)[bit]
        if child_arr[node_id] == self.NO_CHILD:
            child_id = self._create_leaf()
            child_arr[node_id] = child_id
        return child_arr[node_id]

    def _sanity_check(self, node_id):
        """
        Assert invariants on the given node.
        """
        a, b = self.arr_a[node_id], self.arr_b[node_id]
        i0c, i1c = self.arr_0c[node_id], self.arr_1c[node_id]
        if i0c == self.NO_CHILD and i1c == self.NO_CHILD:
            # Leaf.
            pass
        else:
            # Non-leaf.
            assert a == self.get_a(i0c, 0) + self.get_a(i1c, 0)
            assert b == self.get_b(i0c, 0) + self.get_b(i1c, 0)

    def _update_node(self, node_id, next_bit, child_bit, child_params,
                     dry_run=False):
        """
        Update a, b, lpe, lpw for the given node.
        """
        assert next_bit in (0, 1)

        # Update a, b, lpe:
        a, b = self.arr_a[node_id], self.arr_b[node_id]
        lpe = self.arr_lpe[node_id]
        if next_bit == 0:
            new_lpe = lpe + np.log((a + 0.5) / (a + b + 1))
            new_a, new_b = a + 1, b
        else:
            new_lpe = lpe + np.log((b + 0.5) / (a + b + 1))
            new_a, new_b = a, b + 1

        # Update lpw.
        i0c, i1c = self.arr_0c[node_id], self.arr_1c[node_id]
        if i0c == self.NO_CHILD and i1c == self.NO_CHILD:
            # Leaf.
            new_lpw = new_lpe
        else:
            # Non-leaf.
            lpw0 = child_params.lpw if child_bit == 0 else self.get_lpw(i0c, 0)
            lpw1 = child_params.lpw if child_bit == 1 else self.get_lpw(i1c, 0)
            new_lpw = np.logaddexp(np.log(0.5) + new_lpe,
                                   np.log(0.5) + lpw0 + lpw1)

        if not dry_run:
            self.arr_a[node_id] = new_a
            self.arr_b[node_id] = new_b
            self.arr_lpe[node_id] = new_lpe
            self.arr_lpw[node_id] = new_lpw

        return NodeParams(new_a, new_b, new_lpe, new_lpw)

    def get_p0(self, context):
        """
        Return conditional probability that next bit is zero.
        """
        dummy0 = self.update(context, 0, dry_run=True)
        dummy1 = self.update(context, 1, dry_run=True)
        return np.exp(dummy0.lpw - np.logaddexp(dummy0.lpw, dummy1.lpw))
