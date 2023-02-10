"""Handler for exceptions thrown by pubsub listeners."""
from . import pub


class GeneralException(Exception):
    """General exception handler."""


class ListenerExceptionHandler(pub.IListenerExcHandler):
    """Handle exceptions from listeners of pubsub topics."""

    def __call__(self, listenerID, topicObj):
        """Call the exception handler.

        This forces the pub.ExcHandlerError to be raised.
        """
        raise GeneralException
