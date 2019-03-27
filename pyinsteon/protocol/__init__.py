"""Protocol classes to interface with serial, socket and http devices."""
from functools import wraps, partial
from .. import pub

def topic_to_message_handler(topic):
    """Decorator to register handler to topic."""
    def register(func):
        pub.subscribe(func, 'send.{}'.format(topic))
        return func
    return register
