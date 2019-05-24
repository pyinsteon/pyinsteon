"""Insteon message and command handlers."""
import asyncio
from functools import wraps
import logging
from .. import pub
from ..constants import AckNak, MessageFlagType, ResponseStatus


TIMEOUT = 3  # Time out between ACK and Direct ACK
_LOGGER = logging.getLogger(__name__)


def _post_response(obj, response: ResponseStatus):
    """Post a response status to the resonse queue."""
    if hasattr(obj, 'response_lock'):
        if obj.response_lock.locked():
            obj.message_response.put_nowait(response)
    else:
        obj.message_response.put_nowait(response)

async def _async_post_response(obj, response, func, args, kwargs):
    """Used to ensure the lock is locked before posting a response."""
    if obj.response_lock.locked():
        # Only trigger the message response if the response_lock is still
        # locked. This ensures status messages are not responded to.
        await obj.message_response.put(response)
        if obj.response_lock.locked():
            obj.response_lock.release()
        func(obj, *args, **kwargs)

def inbound_handler(func):
    """Decorator function for any inbound message handler."""
    def register_topic(instance_func, topic):
        pub.subscribe(instance_func, topic)
    func.register_topic = register_topic
    return func


def ack_handler(wait_response=False):
    """Decorator function to register the message ACK handler."""
    def register_topic(instance_func, topic):
        topic = 'ack.{}'.format(topic)
        pub.subscribe(instance_func, topic)

    async def _wait_response(lock: asyncio.Lock, queue: asyncio.Queue):
        """Wait for the direct ACK message, and post False if timeout reached."""
        # Need to consider the risk of this. We may be unlocking a prior send command.
        # This would mean that the prior command will terminate. What happens when the 
        # prior command returns a direct ACK then this command returns a direct ACK?
        # Do not believe this is an issue but need to test.
        if lock.locked():
            lock.release()
        await lock.acquire()
        try:
            await asyncio.wait_for(lock.acquire(), TIMEOUT)
        except asyncio.TimeoutError:
            if lock.locked():
                await queue.put(ResponseStatus.FAILURE)
        if lock.locked():
            lock.release()

    def setup(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if wait_response:
                asyncio.ensure_future(
                    _wait_response(self.response_lock, self.message_response))
            else:
                _post_response(self, ResponseStatus.SUCCESS)
            return func(self, *args, **kwargs)
        wrapper.register_topic = register_topic
        return wrapper
    return setup


def nak_handler(func):
    """Decorator function to register the message NAK handler.

    This should only be used if the command requires a special NAK
    handler. Under normal conditions all NAK responses are resent by the
    Protocol.
    """
    def register_topic(instance_func, topic):
        topic = 'nak.{}'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _post_response(self, ResponseStatus.FAILURE)
        return func(self, *args, **kwargs)
    wrapper.register_topic = register_topic
    return wrapper


def response_handler(response_topic=None):
    """Decorator function to register the response handler.

    Parameter:
        response_topic: Used when the response topic is different than the
        send topic.
    """
    def register_topic(instance_func, topic):
        response_topic = response_topic if response_topic else topic
        pub.subscribe(instance_func, response_topic)
    def setup(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            asyncio.ensure_future(
                _async_post_response(self, ResponseStatus.SUCCESS, func, args, kwargs)
            )
        wrapper.register_topic = register_topic
        return wrapper
    return setup


def direct_ack_handler(func):
    """Decorator function to register the DIRECT_ACK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.direct_ack'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.SUCCESS, func, args, kwargs)
        )
    wrapper.register_topic = register_topic
    return wrapper


def status_handler(func):
    """Decorator function to register the status response handler."""
    def register_status(instance_func, address):
        from ..address import Address
        # This registers all messages for a device but only triggers on
        # status messages if they return within the TIMEOUT period
        address = Address(address)
        pub.subscribe(instance_func, address.id)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.SUCCESS, func, args, kwargs)
        )
    wrapper.register_status = register_status
    return wrapper


def direct_nak_handler(func):
    """Decorator function to register the DIRECT_NAK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.direct_nak'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.UNCLEAR, func, args, kwargs)
        )
    wrapper.register_topic = register_topic
    return wrapper


def broadcast_handler(func):
    """Decorator function to register the BROADCAST message handler."""
    def register_topic(instance_func, topic):
        topic_broadcast = '{}.broadcast'.format(topic)
        topic_all_link_broadcast = '{}.all_link_broadcast'.format(topic)
        pub.subscribe(instance_func, topic_broadcast)
        pub.subscribe(instance_func, topic_all_link_broadcast)
    func.register_topic = register_topic
    return func
