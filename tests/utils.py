"""Utilities for testing."""
import asyncio
from binascii import unhexlify
from collections import namedtuple

try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

from functools import partial, wraps
from random import randint

import pyinsteon.protocol.protocol
from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.protocol.messages.inbound import create
from tests import _LOGGER_MESSAGES, async_connect_mock


def hex_to_inbound_message(hex_data):
    """Create an Inbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    (msg, _) = create(msg_bytes)
    return msg, msg_bytes


def check_fields_match(msg1, msg2):
    """Check fields in msg1 match fields in msg2."""

    def _check_eq_or_none(fld1, fld2):
        return fld1 is None or fld2 is None or fld1 == fld2

    match = True
    for field in msg1.fields:
        fld1 = getattr(msg1, field.name)
        fld2 = getattr(msg2, field.name)
        match = match & _check_eq_or_none(fld1, fld2)
    return match


def async_case(func):
    """Wrap a test cast around a wrapper to execute the test."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        future = func(*args, **kwargs)
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
    """Create a standard or extended message."""
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


def cmd_kwargs(cmd1, cmd2, user_data, target=None, address=None, hops_left=3):
    """Return a kwargs dict for a standard messsage command."""

    kwargs = {"cmd1": cmd1, "cmd2": cmd2, "user_data": user_data}
    if target:
        kwargs["target"] = Address(target)
        kwargs["hops_left"] = hops_left
    if address:
        kwargs["address"] = Address(address)
    return kwargs


def make_command_response_messages(
    address, topic, cmd1, cmd2, target="000000", user_data=None
):
    """Return a colleciton of ACK and Direct ACK responses to commands."""

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


def random_address():
    """Generate a random address."""
    address = ""
    for _ in range(0, 3):
        rand_int = randint(1, 255)
        if address:
            address = f"{address}."
        address = f"{address}{rand_int:02x}"
    return Address(address)


PROTOCOL_LOCK = asyncio.Lock()
MAX_LOCK = 60


@asynccontextmanager
async def async_protocol_manager():
    """Manage the protocol to ensure a single instance."""
    async with PROTOCOL_LOCK:
        protocol = await async_create_protocol()
        try:
            yield protocol
        finally:
            await async_release_protocol(protocol)


async def async_create_protocol():
    """Create a protocol using a mock transport.

    Need to ensure only one protocol is available at a time.
    """
    pyinsteon.protocol.protocol.WRITE_WAIT = 0.01
    read_queue = asyncio.Queue()
    write_queue = asyncio.Queue()
    connect_method = partial(
        async_connect_mock,
        read_queue=read_queue,
        write_queue=write_queue,
        random_nak=False,
    )
    protocol = pyinsteon.protocol.protocol.Protocol(connect_method=connect_method)
    await protocol.async_connect()
    protocol.read_queue = read_queue
    protocol.write_queue = write_queue
    return protocol


async def async_release_protocol(protocol):
    """Close the protocol and release subscriptions."""
    protocol.close()
    await asyncio.sleep(0.1)
    pub.unsubAll("send")
    pub.unsubAll("send_message")
