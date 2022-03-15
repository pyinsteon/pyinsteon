"""Insteon message and command handlers."""
import asyncio
import logging
from functools import partial, wraps
from inspect import isawaitable, iscoroutinefunction

from ..address import Address
from ..constants import MessageFlagType
from ..utils import build_topic, subscribe_topic

TIMEOUT = 3  # Time out between ACK and Direct ACK
_LOGGER = logging.getLogger(__name__)


def _register_handler(
    func,
    presets=None,
    topic=None,
    prefix=None,
    address=None,
    group=None,
    message_type=None,
):
    """Register the function with a topic."""
    presets = presets or {}
    topic = presets.get("topic") or topic
    address = presets.get("address") or address
    get_group = presets.get("group", -1)
    group = get_group if get_group != -1 else group
    message_type = presets.get("message_type") or message_type
    full_topic = build_topic(
        topic=topic,
        prefix=presets.get("prefix"),
        address=address,
        group=group,
        message_type=message_type,
    )
    subscribe_topic(func, full_topic)


def _setup_handler(reg_func, func):
    """Set up the handler function."""

    @wraps(func)
    def _wrapper(self, *args, **kwargs):
        """Wrap a function."""
        if iscoroutinefunction(func) or isawaitable(func):
            return asyncio.create_task(func(self, *args, **kwargs))
        return func(self, *args, **kwargs)

    _wrapper.register_handler = reg_func
    return _wrapper


def inbound_handler(func):
    """Register any inbound message handler."""
    reg_func = partial(
        _register_handler,
    )
    return _setup_handler(reg_func, func)


def ack_handler(func):
    """Register the message ACK handler."""
    reg_func = partial(_register_handler, presets={"prefix": "ack"})
    return _setup_handler(reg_func, func)


def nak_handler(func):
    """Register the message NAK handler."""
    reg_func = partial(_register_handler, presets={"prefix": "nak"})
    return _setup_handler(reg_func, func)


def direct_ack_handler(func):
    """Register the DIRECT_ACK response handler."""
    reg_func = partial(
        _register_handler,
        presets={"group": None, "message_type": MessageFlagType.DIRECT_ACK},
    )
    return _setup_handler(reg_func, func)


def status_handler(func):
    """Register the status response handler."""

    def register_status(instance_func, address):
        # This registers all messages for a device but only triggers on
        # status messages if they return within the TIMEOUT period
        address = Address(address)
        subscribe_topic(instance_func, address.id)

    func.register_status = register_status
    return func


def direct_nak_handler(func):
    """Register the DIRECT_NAK response handler."""
    reg_func = partial(
        _register_handler,
        presets={"group": None, "message_type": MessageFlagType.DIRECT_NAK},
    )
    return _setup_handler(reg_func, func)


def broadcast_handler(func):
    """Register the BROADCAST message handler."""

    def _register_broadcast_handler(
        func, topic, address=None, group=None, message_type=None
    ):
        """Register the function with a topic."""
        broadcast_topic = build_topic(
            topic=topic,
            prefix=None,
            address=address,
            group=group,
            message_type=MessageFlagType.BROADCAST,
        )
        all_link_topic = build_topic(
            topic=topic,
            prefix=None,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )
        subscribe_topic(func, broadcast_topic)
        subscribe_topic(func, all_link_topic)

    reg_func = partial(_register_broadcast_handler)
    return _setup_handler(reg_func, func)


def all_link_cleanup_ack_handler(func):
    """Register the all_link_cleanup ACK response handler."""
    reg_func = partial(
        _register_handler,
        presets={"message_type": MessageFlagType.ALL_LINK_CLEANUP_ACK},
    )
    return _setup_handler(reg_func, func)


def all_link_cleanup_nak_handler(func):
    """Register the all_link_cleanup NAK response handler."""
    reg_func = partial(
        _register_handler,
        presets={"message_type": MessageFlagType.ALL_LINK_CLEANUP_ACK},
    )
    return _setup_handler(reg_func, func)
