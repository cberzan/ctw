class WCTInterface(object):
    """
    Common interface for weighted context trees.

    A "piece" is a bit or a byte, in our current implementation.
    """
    def dummy_initial_context(self):
        """
        Return dummy initial context for the first piece to encode.
        """
        raise NotImplementedError()

    def data_to_pieces(self, data):
        """
        Split data string into sequence of pieces to encode.
        """
        raise NotImplementedError()

    def update(self, context, next_piece):
        """
        Update the tree upon seeing next_piece after the given context.
        """
        raise NotImplementedError()
