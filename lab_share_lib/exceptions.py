class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class TransientRabbitError(Error):
    """
    Raised during processing of a RabbitMQ message when a transient issue occurs.
    For example, this might be a database being inaccessible.  The message should be reprocessed.
    """

    def __init__(self, message):
        """Constructs a new processing error message.

        Arguments:
            message {str} -- A message to log and possibly show to the user/caller.
        """
        self.message = message
