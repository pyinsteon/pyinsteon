"""Test the protocol class."""
import asyncio
import unittest
from functools import partial

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.topics import ON


from tests import async_connect_mock
from tests.utils import (send_topics, send_data, create_std_ext_msg,
                        async_case, DataItem, TopicItem)


class TestProtocol(unittest.TestCase):
    """Test the protocol class."""

    def setUp(self):
        """Setup the tests."""
        self._read_queue = asyncio.Queue()
        self._write_queue = asyncio.Queue()
        self._protocol = None
        self._connect_method = partial(async_connect_mock,
                                       read_queue=self._read_queue,
                                       write_queue=self._write_queue)
        self._protocol = Protocol(connect_method=self._connect_method)
        self._last_topic = ''
        pub.subscribe(self._topic_received, pub.ALL_TOPICS)

    def _topic_received(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Receive the OFF topic for a device."""
        self._last_topic = topic.name

    @async_case
    async def test_send_on_topic(self):
        """Test sending the ON command."""
        address = Address('010101')
        on_topic = 'send.{}'.format(ON)
        topics = [TopicItem(on_topic, {'address':address, 'on_level': 0xff, 'group': 0}, .5)]
        await self._protocol.async_connect()
        send_topics(topics)
        await asyncio.sleep(2)
        assert self._last_topic == 'ack.{}.on.direct'.format(address.id)

    @async_case
    async def test_receive_on_msg(self):
        """Test receiving an ON message."""
        address = Address('020202')
        byte_data = create_std_ext_msg(address, 0x80, 0x11, 0xff, target=Address('000001'))
        on_cmd = DataItem(byte_data, .5)
        data = [on_cmd]
        await self._protocol.async_connect()
        send_data(data, self._read_queue)
        await asyncio.sleep(2)
        assert self._last_topic == '{}.on.broadcast'.format(address.id)
