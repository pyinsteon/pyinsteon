"""Handler for exceptions thrown by pubsub listeners."""
import logging
from . import pub

_LOGGER = logging.getLogger(__name__)

class ListenerExceptionHandler(pub.IListenerExcHandler):
    """Handle exceptions from listeners of pubsub topics."""
    def __call__(self, listenerID, topicObj):
        _LOGGER.error('pubsub listener Exception: %s with topic %s',
                      listenerID, topicObj.name)
