"""Utilities for testing."""
import asyncio
from binascii import unhexlify
from collections import namedtuple
from functools import wraps

from pyinsteon import pub
from pyinsteon.protocol.messages.inbound import create
from tests import _LOGGER_MESSAGES


def hex_to_inbound_message(hex_data):
    """Create an Inbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    (msg, _) = create(msg_bytes)
    return msg, msg_bytes


def check_fields_match(msg1, msg2):
    """Check fields in msg1 match fields in msg2."""

    def _check_eq_or_none(fld1, fld2):
        # _LOGGER.error(fld1 is None or
        #               fld2 is None or
        #               fld1 == fld2)
        return fld1 is None or fld2 is None or fld1 == fld2

    match = True
    for field in msg1.fields:
        fld1 = getattr(msg1, field.name)
        fld2 = getattr(msg2, field.name)
        # _LOGGER.error(fld1)
        # _LOGGER.error(fld2)
        match = match & _check_eq_or_none(fld1, fld2)
    return match


def async_case(f):
    """Wrap a test cast around a wrapper to execute the test."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


TopicItem = namedtuple("TopicItem", "topic, kwargs, delay")


def send_topics(topic_items):
    """Publish a topic message to interact with a test case."""

    async def async_send_topics(topic_items):
        for item in topic_items:
            await asyncio.sleep(item.delay)
            _LOGGER_MESSAGES.debug("RX: %s  %s", item.topic, item.kwargs)
            pub.sendMessage(item.topic, **item.kwargs)

    asyncio.ensure_future(async_send_topics(topic_items))


DataItem = namedtuple("DataItem", "data, delay")


def send_data(data_items, queue):
    """Send data to a mock connection."""

    async def async_send_data(data_items, queue):
        for item in data_items:
            await asyncio.sleep(item.delay)
            _LOGGER_MESSAGES.debug("RX: %s", item.data.hex())
            await queue.put(item.data)

    asyncio.ensure_future(async_send_data(data_items, queue))


def create_std_ext_msg(address, flags, cmd1, cmd2, user_data=None, target=None, ack=0):
    """"Create a standard or extended message."""
    from pyinsteon.address import Address
    from pyinsteon.protocol.messages.user_data import UserData

    address = Address(address)
    data = bytearray()
    data.append(0x02)
    if target:
        target = Address(target)
        msg_type = 0x51 if user_data else 0x50
    else:
        msg_type = 0x62
    data.append(msg_type)
    data.append(address.high)
    data.append(address.middle)
    data.append(address.low)
    if target:
        data.append(target.high)
        data.append(target.middle)
        data.append(target.low)
    data.append(flags)
    data.append(cmd1)
    data.append(cmd2)
    if user_data:
        user_data = UserData(user_data)
        for byte in user_data:
            data.append(user_data[byte])
    if ack:
        data.append(ack)
    return bytes(data)


def cmd_kwargs(cmd1, cmd2, user_data, target=None, address=None):
    """Return a kwargs dict for a standard messsage command."""
    from pyinsteon.address import Address

    kwargs = {"cmd1": cmd1, "cmd2": cmd2, "user_data": user_data}
    if target:
        kwargs["target"] = Address(target)
    if address:
        kwargs["address"] = Address(address)
    return kwargs


def make_command_response_messages(
    address, topic, cmd1, cmd2, target="000000", user_data=None
):
    """Return a colleciton of ACK and Direct ACK responses to commands."""
    from pyinsteon.address import Address

    address = Address(address)
    ack = "ack.{}.{}".format(address.id, topic)
    direct_ack = "{}.{}.direct_ack".format(address.id, topic)
    return [
        TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
        TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
    ]


def get_class_or_method(main_module, name):
    """Return the class or method from a string."""
    components = name.split(".")
    mod = main_module
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
