"""Test the protocol class."""
import asyncio
import unittest
from functools import partial

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.topics import ON


from tests import async_connect_mock, set_log_levels
from tests.utils import (
    send_topics,
    send_data,
    create_std_ext_msg,
    async_case,
    DataItem,
    TopicItem,
)


class TestProtocol(unittest.TestCase):
    """Test the protocol class."""

    def setUp(self):
        """Setup the tests."""
        self._read_queue = asyncio.Queue()
        self._write_queue = asyncio.Queue()
        self._protocol = None
        self._connect_method = partial(
            async_connect_mock,
            read_queue=self._read_queue,
            write_queue=self._write_queue,
        )
        self._protocol = Protocol(connect_method=self._connect_method)
        self._last_topic = ""
        pub.subscribe(self._topic_received, pub.ALL_TOPICS)
        set_log_levels(logger_topics=True)

    def _topic_received(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Receive the OFF topic for a device."""
        self._last_topic = topic.name

    @async_case
    async def test_send_on_topic(self):
        """Test sending the ON command."""
        address = Address("010102")
        on_topic = "send.{}.1".format(ON)
        topics = [
            TopicItem(on_topic, {"address": address, "on_level": 0xFF, "group": 0}, 0)
        ]
        await self._protocol.async_connect()
        send_topics(topics)
        await asyncio.sleep(0.1)
        assert self._last_topic == "ack.{}.1.on.direct".format(address.id)
        self._protocol.close()
        await asyncio.sleep(0.1)

    @async_case
    async def test_receive_on_msg(self):
        """Test receiving an ON message."""
        address = Address("020202")
        byte_data = create_std_ext_msg(
            address, 0x80, 0x11, 0xFF, target=Address("000001")
        )
        on_cmd = DataItem(byte_data, 0.5)
        data = [on_cmd]
        await self._protocol.async_connect()
        send_data(data, self._read_queue)
        await asyncio.sleep(2)
        assert self._last_topic == "{}.{}.on.broadcast".format(address.id, 1)
        self._protocol.close()
        await asyncio.sleep(0.1)

    @async_case
    async def test_send_on_all_link_broadcast_topic(self):
        """Test sending the ON command."""
        from pyinsteon.handlers.to_device.on_level_all_link_broadcast import (
            OnLevelAllLinkBroadcastCommand,
        )

        group = 3
        target = Address(bytearray([0x00, 0x00, group]))
        ack_topic = "ack.{}.on.all_link_broadcast".format(target.id)
        cmd = OnLevelAllLinkBroadcastCommand(group=group)
        await self._protocol.async_connect()
        await cmd.async_send()  # Mock transport auto sends ACK/NAK
        await asyncio.sleep(2)
        assert self._last_topic == ack_topic
        self._protocol.close()
        await asyncio.sleep(0.1)
