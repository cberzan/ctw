from collections import namedtuple
from StringIO import StringIO
import numpy as np

from wct_binary import Node
from wct_binary import NodeParams


class WCTGeneralContextBinaryCounts(object):
    """
    A weighted context tree that allows for an arbitrary context dictionary
    size but only keeps bit counts at each node.
    """
    MAX_NODES = 20000
    NO_CHILD = -1  # so we can store children indices in an int array

    def __init__(self, depth, context_syms=2):
        self.depth = depth
        self.context_syms = context_syms
        self.arr_a = np.zeros(self.MAX_NODES, dtype=np.int)
        self.arr_b = np.zeros(self.MAX_NODES, dtype=np.int)
        self.arr_lpe = np.zeros(self.MAX_NODES)
        self.arr_lpw = np.zeros(self.MAX_NODES)
        self.arr_children = np.zeros((self.MAX_NODES, self.context_syms),
                                     dtype=np.int)
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
        for node in self.nodes_in_preorder():
            print >>stream, node
        return stream.getvalue()

    def nodes_in_preorder(self):
        """
        Return list of Nodes in preorder (1 child, then 0 child, then self).
        """
        return self._nodes_rec(self.root_id, "")

    def _nodes_rec(self, node_id, path):
        """
        Recursive helper for nodes_in_preorder().
        """
        nodes = []
        maxlen = len(str(self.context_syms))
        children = self.arr_children[node_id, :]
        for s in range(self.context_syms)[::-1]:
            if children[s] == self.NO_CHILD:
                continue
            newpath = '{: <{width}} {}'.format(s, path, width=maxlen).strip()
            nodes += self._nodes_rec(children[s], newpath)
        nodes.append(Node(
            " " * ((maxlen+1) * self.depth - len(path) - 1) + path,
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
            assert all(self.arr_children[node_id, :] == self.NO_CHILD)
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
        self.arr_children[self.next_id, :] = self.NO_CHILD
        node_id = self.next_id
        self.next_id += 1
        return node_id

    def _get_or_create_child(self, node_id, context_sym):
        """
        Return child_id for given node_id and bit.
        """
        assert context_sym in range(self.context_syms)
        child_arr = self.arr_children[:, context_sym]
        if child_arr[node_id] == self.NO_CHILD:
            child_id = self._create_leaf()
            child_arr[node_id] = child_id
        return child_arr[node_id]

    def _sanity_check(self, node_id):
        """
        Assert invariants on the given node.
        """
        a, b = self.arr_a[node_id], self.arr_b[node_id]
        children = self.arr_children[node_id, :]
        if all(children == self.NO_CHILD):
            # Leaf.
            pass
        else:
            # Non-leaf.
            assert a == sum(self.get_a(child, 0) for child in children)
            assert b == sum(self.get_b(child, 0) for child in children)

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
        children = self.arr_children[node_id, :]
        if all(children == self.NO_CHILD):
            # Leaf.
            new_lpw = new_lpe
        else:
            # Non-leaf.
            child_lpw_sum = 0
            for s in range(self.context_syms):
                child_lpw_sum += child_params.lpw if child_bit == s else \
                    self.get_lpw(children[s], 0)
            new_lpw = np.logaddexp(np.log(0.5) + new_lpe,
                                   np.log(0.5) + child_lpw_sum)

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
