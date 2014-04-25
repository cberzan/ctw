from wct_general_context import WCTGeneralContextBinaryCounts as WCT
import numpy as np

class WCTPhases(object):
    """
    Weighted context tree that operates with phases.

    More specifically, within the current byte, the preceding bits are used to
    select a binary WCT. Then the preceding bytes are used as context for the
    selected tree.

    Still need more specifics? So demanding. Read:
    http://www.ele.tue.nl/ctw/overview/structure.html
    """
    def __init__(self, max_depth, context_syms=256):
        self.depth = max_depth
        self.context_syms = context_syms
        self.phase_trees = {}

    def update(self, context, phase, next_bit, dry_run=False):
        if phase not in self.phase_trees:
            self.phase_trees[phase] = WCT(self.depth, self.context_syms)
        tree = self.phase_trees[phase]
        return tree.update(context, next_bit, dry_run)

    def get_p0(self, context, phase):
        """
        Return conditional probability that the next bit is zero.
        """
        dummy0 = self.update(context, phase, 0, dry_run=True)
        dummy1 = self.update(context, phase, 1, dry_run=True)
        return np.exp(dummy0.lpw - np.logaddexp(dummy0.lpw, dummy1.lpw))
