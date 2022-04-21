"""Utilities for testing."""
import asyncio
from binascii import unhexlify
from collections import namedtuple
from io import StringIO

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
        asyncio.run(future)

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
    from pyinsteon.data_types.user_data import UserData

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
async def async_protocol_manager(
    connect_method=None,
    read_queue=None,
    write_queue=None,
    random_nak=False,
    auto_ack=True,
    connect=True,
    retry=True,
    retries=None,
    **kwargs,
):
    """Manage the protocol to ensure a single instance."""
    async with PROTOCOL_LOCK:
        protocol = await async_create_protocol(
            connect_method=connect_method,
            read_queue=read_queue,
            write_queue=write_queue,
            random_nak=random_nak,
            auto_ack=auto_ack,
            connect=connect,
            retry=retry,
            retries=retries,
            **kwargs,
        )
        try:
            yield protocol
        finally:
            await async_release_protocol(protocol)
            await asyncio.sleep(0.1)


async def async_create_protocol(
    connect_method=None,
    read_queue=None,
    write_queue=None,
    random_nak=False,
    auto_ack=True,
    connect=True,
    retry=True,
    retries=None,
    **kwargs,
):
    """Create a protocol using a mock transport.

    Need to ensure only one protocol is available at a time.
    """
    pyinsteon.protocol.protocol.WRITE_WAIT = 0.01
    mock_connect = connect_method is None
    connect_method = async_connect_mock if connect_method is None else connect_method
    read_queue = asyncio.Queue() if read_queue is None else read_queue
    write_queue = asyncio.Queue() if write_queue is None else write_queue
    if not retry:
        retries = [1]
    if mock_connect:
        partial_connect_method = partial(
            connect_method,
            read_queue=read_queue,
            write_queue=write_queue,
            random_nak=random_nak,
            auto_ack=auto_ack,
            connect=connect,
            retries=retries,
        )
    else:
        partial_connect_method = partial(connect_method, **kwargs)
    protocol = pyinsteon.protocol.protocol.Protocol(
        connect_method=partial_connect_method
    )
    try:
        await protocol.async_connect(retry=retry)
    except ConnectionError as ex:
        await async_release_protocol(protocol)
        await asyncio.sleep(0.01)
        raise ex
    protocol.read_queue = read_queue
    protocol.write_queue = write_queue
    return protocol


async def async_release_protocol(protocol):
    """Close the protocol and release subscriptions."""
    protocol.close()
    await asyncio.sleep(0.3)
    pub.unsubAll("send")


class MockHttpResponse:
    """Mock HTTP response class."""

    status = 200
    buffer = None

    @classmethod
    async def text(cls):
        """Return the HTML text."""
        return cls.buffer


class MockHttpClientSession:
    """Mock the ClientSession class."""

    def __init__(self, *arg, **kwargs):
        """Init the MockHttpClientSession class."""
        self.exception_to_throw = None
        self.buffer = None
        self.response = MockHttpResponse()

    @asynccontextmanager
    async def get(self, url):
        """Mock the get function."""
        if self.exception_to_throw is not None:
            raise self.exception_to_throw
        yield self.response

    @asynccontextmanager
    async def post(self, url):
        """Mock the post function."""
        if self.exception_to_throw is not None:
            raise self.exception_to_throw
        yield self.response

    async def close(self):
        """Close the mock connection."""


@asynccontextmanager
async def create_mock_http_client(
    *args, status=200, exception_error=None, buffer=None, **kwargs
):
    """Create a mock HTTP client."""
    mock_client = MockHttpClientSession()
    mock_client.response.status = status
    mock_client.exception_to_throw = exception_error
    mock_client.response.buffer = buffer
    yield mock_client


class MockSerial:
    """Mock serial connection."""

    def __init__(self):
        """Init the MockSerial class."""
        self.kwargs = None
        self.call_count = 0
        self.iostream = StringIO()
        self.serial_for_url_exception = None
        self.write_exception = None
        self.msg = None

    def serial_for_url(self, *args, **kwargs):
        """Mock the serial_for_url method."""
        self.call_count += 1
        self.kwargs = kwargs
        if self.serial_for_url_exception:
            raise self.serial_for_url_exception
        return self

    def read(self, *args, **kwargs):
        """Mock the read method."""
        return 0

    def write(self, data):
        """Mock the write method."""
        if self.write_exception:
            raise self.write_exception
        self.msg = data

    def close(self, *args, **kwargs):
        """Mock the close method."""

    def flush(self, *args, **kwargs):
        """Mock the flush method."""

    def fileno(self):
        """Return a fileno."""
        return 1
