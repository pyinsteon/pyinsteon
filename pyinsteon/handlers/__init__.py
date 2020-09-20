"""Insteon message and command handlers."""
import asyncio
import logging
from functools import wraps

from ..utils import subscribe_topic
from ..address import Address
from ..constants import MessageFlagType, ResponseStatus
from ..utils import build_topic

TIMEOUT = 3  # Time out between ACK and Direct ACK
_LOGGER = logging.getLogger(__name__)


async def _async_post_response(
    obj, response: ResponseStatus, func=None, args=None, kwargs=None
):
    """Post a response status to the resonse queue."""
    if hasattr(obj, "response_lock"):
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


def _register_handler(
    instance_func, topic, prefix=None, address=None, group=None, message_type=None
):
    full_topic = build_topic(
        topic=topic,
        prefix=prefix,
        address=address,
        group=group,
        message_type=message_type,
    )
    subscribe_topic(instance_func, full_topic)


def inbound_handler(func):
    """Register any inbound message handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=group,
            message_type=message_type,
        )

    func.register_topic = register_topic
    return func


def ack_handler(wait_response=False, timeout=TIMEOUT):
    """Register the message ACK handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound ACK message."""
        _register_handler(
            instance_func,
            topic,
            prefix="ack",
            address=address,
            group=group,
            message_type=message_type,
        )

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
            if hasattr(self, "group"):
                group = (
                    1 if not kwargs.get("user_data") else kwargs.get("user_data")["d1"]
                )
                if self.group != group:
                    return
            if wait_response:
                asyncio.ensure_future(
                    _wait_response(self.response_lock, self.message_response)
                )
            else:
                asyncio.ensure_future(
                    _async_post_response(self, ResponseStatus.SUCCESS)
                )
            return func(self, *args, **kwargs)

        wrapper.register_topic = register_topic
        return wrapper

    return setup


def nak_handler(func):
    """Register the message NAK handler.

    This should only be used if the command requires a special NAK
    handler. Under normal conditions all NAK responses are resent by the
    Protocol.
    """

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound ACK message."""
        _register_handler(
            instance_func,
            topic,
            prefix="nak",
            address=address,
            group=group,
            message_type=message_type,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs)
        )

    wrapper.register_topic = register_topic
    return wrapper


def direct_ack_handler(func):
    """Register the DIRECT_ACK response handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound ACK message."""
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=None,
            message_type=MessageFlagType.DIRECT_ACK,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.SUCCESS, func, args, kwargs)
        )

    wrapper.register_topic = register_topic
    return wrapper


def status_ack_handler(timeout=TIMEOUT):
    """Register the message ACK handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound ACK message."""
        _register_handler(
            instance_func,
            topic,
            prefix="ack",
            address=address,
            group=group,
            message_type=message_type,
        )

    async def _wait_response(self):
        """Wait for the direct ACK message, and post False if timeout reached."""
        # TODO: Need to consider the risk of this. We may be unlocking a prior send command.
        # This would mean that the prior command will terminate. What happens when the
        # prior command returns a direct ACK then this command returns a direct ACK?
        # Do not believe this is an issue but need to test.
        if self.response_lock.locked():
            self.response_lock.release()
        await self.response_lock.acquire()
        try:
            await asyncio.wait_for(self.response_lock.acquire(), TIMEOUT)
        except asyncio.TimeoutError:
            if self.response_lock.locked():
                await self.message_response.put(ResponseStatus.FAILURE)
        if self.response_lock.locked():
            self.response_lock.release()
        self.status_active = False

    def setup(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cmd2 = kwargs.get("cmd2")
            if cmd2 == self.status_type:
                self.status_active = True
                asyncio.ensure_future(_wait_response(self))
                return func(self, *args, **kwargs)

        wrapper.register_topic = register_topic
        return wrapper

    return setup


def status_handler(func):
    """Register the status response handler."""

    def register_status(instance_func, address):
        # This registers all messages for a device but only triggers on
        # status messages if they return within the TIMEOUT period
        address = Address(address)
        subscribe_topic(instance_func, address.id)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.status_active:
            topic = kwargs.get("topic")
            msg_type = topic.name.split(".")[-1]
            if msg_type == str(MessageFlagType.DIRECT_ACK):
                asyncio.ensure_future(
                    _async_post_response(
                        self, ResponseStatus.SUCCESS, func, args, kwargs
                    )
                )

    wrapper.register_status = register_status
    return wrapper


def direct_nak_handler(func):
    """Register the DIRECT_NAK response handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound DIRECT NAK message."""
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=None,
            message_type=MessageFlagType.DIRECT_NAK,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.UNCLEAR, func, args, kwargs)
        )

    wrapper.register_topic = register_topic
    return wrapper


def broadcast_handler(func):
    """Register the BROADCAST message handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound BROADCAST message."""
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=group,
            message_type=MessageFlagType.BROADCAST,
        )
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrap the handler to test for duplicate messages."""
        if self.is_first_message(**kwargs):
            return func(self, *args, **kwargs)

    wrapper.register_topic = register_topic
    return wrapper


def all_link_cleanup_ack_handler(func):
    """Register the all_link_cleanup ACK response handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound BROADCAST message."""
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=None,
            message_type=MessageFlagType.ALL_LINK_CLEANUP_ACK,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs)
        )

    wrapper.register_topic = register_topic
    return wrapper


def all_link_cleanup_nak_handler(func):
    """Register the all_link_cleanup NAK response handler."""

    def register_topic(
        instance_func, topic, address=None, group=None, message_type=None
    ):
        """Register an inbound BROADCAST message."""
        _register_handler(
            instance_func,
            topic,
            prefix=None,
            address=address,
            group=None,
            message_type=MessageFlagType.ALL_LINK_CLEANUP_NAK,
        )

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        asyncio.ensure_future(
            _async_post_response(self, ResponseStatus.FAILURE, func, args, kwargs)
        )

    wrapper.register_topic = register_topic
    return wrapper
