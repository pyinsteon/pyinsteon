"""Insteon message and command handlers."""
import asyncio
from functools import wraps
import logging
from .. import pub
from ..constants import AckNak, MessageFlagType, ResponseStatus


TIMEOUT = 3  # Time out between ACK and Direct ACK
_LOGGER = logging.getLogger(__name__)


async def _async_post_response(obj, response: ResponseStatus, func=None, args=None, kwargs=None):
    """Post a response status to the resonse queue."""
    if hasattr(obj, 'response_lock'):
        if obj.response_lock.locked():
            await obj.message_response.put(response)
            if func is not None:
                func(obj, *args, **kwargs)
        if obj.response_lock.locked():
            obj.response_lock.release()
    else:
        await obj.message_response.put(response)
        if func is not None:
            func(obj, *args, **kwargs)


def inbound_handler(func):
    """Decorator function for any inbound message handler."""
    def register_topic(instance_func, topic):
        pub.subscribe(instance_func, topic)
    func.register_topic = register_topic
    return func


def ack_handler(wait_response=False, timeout=TIMEOUT):
    """Decorator function to register the message ACK handler."""
    def register_topic(instance_func, topic):
        topic = 'ack.{}'.format(topic)
        pub.subscribe(instance_func, topic)

    async def _wait_response(lock: asyncio.Lock, queue: asyncio.Queue):
        """Wait for the direct ACK message, and post False if timeout reached."""
        # TODO: Need to consider the risk of this. We may be unlocking a prior send command.
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
            if hasattr(self, 'group'):
                group = 1 if not kwargs.get('user_data') else kwargs.get('user_data')['d1']
                if self.group != group:
                    return
            if wait_response:
                asyncio.ensure_future(
                    _wait_response(self.response_lock, self.message_response))
            else:
                asyncio.ensure_future(
                    _async_post_response(self, ResponseStatus.SUCCESS))
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
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs))
    wrapper.register_topic = register_topic
    return wrapper


def response_handler(response_topic=None):
    """Decorator function to register the response handler.

    Parameter:
        response_topic: Used when the response topic is different than the
        send topic.
    """
    def register_topic(instance_func, topic):
        nonlocal response_topic
        topic = response_topic if response_topic is not None else topic
        pub.subscribe(instance_func, topic)
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
    from datetime import datetime
    last_command = datetime(1, 1, 1)
    def register_topic(instance_func, topic):
        topic_broadcast = '{}.broadcast'.format(topic)
        topic_all_link_broadcast = '{}.all_link_broadcast'.format(topic)
        pub.subscribe(instance_func, topic_broadcast)
        pub.subscribe(instance_func, topic_all_link_broadcast)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        nonlocal last_command
        curr_time = datetime.now()
        tdelta = curr_time - last_command
        last_command = curr_time
        if tdelta.seconds >= 2:
            return func(self, *args, **kwargs)

    wrapper.register_topic = register_topic
    return wrapper


def all_link_cleanup_handler(func):
    """Decorator function to register the c message handler."""
    from datetime import datetime
    last_command = datetime(1, 1, 1)
    def register_topic(instance_func, topic):
        topic = '{}.all_link_cleanup'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        nonlocal last_command
        curr_time = datetime.now()
        tdelta = curr_time - last_command
        last_command = curr_time
        if tdelta.seconds >= 2:
            return func(self, *args, **kwargs)

    wrapper.register_topic = register_topic
    return wrapper


def all_link_cleanup_ack_handler(func):
    """Decorator function to register the all_link_cleanup ACK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.all_link_cleanup_ack'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs)
        )
    wrapper.register_topic = register_topic
    return wrapper


def all_link_cleanup_nak_handler(func):
    """Decorator function to register the all_link_cleanup NAK response handler."""
    def register_topic(instance_func, topic):
        topic = '{}.all_link_cleanup_nak'.format(topic)
        pub.subscribe(instance_func, topic)
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs)
        )
    wrapper.register_topic = register_topic
    return wrapper
