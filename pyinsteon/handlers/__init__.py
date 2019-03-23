"""Insteon message and command handlers."""
import asyncio
from functools import wraps
from .. import pub
from ..constants import AckNak, MessageFlagType, ResponseStatus

TIMEOUT = 3  # Time out between ACK and Direct ACK


def _post_response(obj, response: ResponseStatus):
    """Post a response status to the resonse queue."""
    if hasattr(obj, 'response_lock'):
        if obj.response_lock.locked():
            obj.message_response.put_nowait(response)
    else:
        obj.message_response.put_nowait(response)


def response_handler(func):
    """Decorator function for any inbound response handler."""
    def register_topic(instance_func, topic):
        pub.subscribe(instance_func, topic)
    func.register_topic = register_topic
    return func


def ack_handler(wait_direct_ack=False):
    """Decorator function to register the message ACK handler."""
    def register_topic(instance_func, topic):
        topic = 'ack.{}'.format(topic)
        pub.subscribe(instance_func, topic)
    async def _wait_direct_ack(lock: asyncio.Lock, queue: asyncio.Queue):
        """Wait for the direct ACK message, and post False if timeout reached."""
        try:
            if lock.locked():
                await asyncio.wait_for(lock.acquire(), TIMEOUT)
        except asyncio.TimeoutError:
            if lock.locked():
                queue.put_nowait(ResponseStatus.FAILURE)
    def setup(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if wait_direct_ack:
                asyncio.ensure_future(
                    _wait_direct_ack(self.response_lock, self.message_response))
            else:
                _post_response(self, ResponseStatus.SUCCESS)
            return func(self, *args, **kwargs)
        wrapper.register_topic = register_topic
        return wrapper
    return setup


def nak_handler(func):
    """Decorator function to register the message NAK handler."""
    def register_topic(instance_func, topic):
        topic = 'nak.{}'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _post_response(self, ResponseStatus.FAILURE)
        return func(self, *args, **kwargs)
    wrapper.register_topic = register_topic
    return wrapper


def direct_ack_handler(func):
    """Decorator function to register the DIRECT_ACK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.direct_ack'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.response_lock.locked():
            self.message_response.put_nowait(ResponseStatus.SUCCESS)
        return func(self, *args, **kwargs)
    wrapper.register_topic = register_topic
    return wrapper


def direct_nak_handler(func):
    """Decorator function to register the DIRECT_NAK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.direct_nak'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.response_lock.locked():
            self.message_response.put_nowait(ResponseStatus.UNCLEAR)
        return func(self, *args, **kwargs)
    wrapper.register_topic = register_topic
    return wrapper
