"""Protocol classes to interface with serial, socket and http devices."""
from .. import pub

def topic_to_message_handler(topic):
    """Decorator to register handler to topic."""
    def register(func):
        pub.subscribe(func, 'send.{}'.format(topic))
        def wrapper(*args, **kwargs):
            # Ensure we ahve a topic argument to the handler
            kwargs['topic'] = topic
            return func(*args, **kwargs)
        return wrapper
    return register
