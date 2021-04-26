"""Test the protocol class."""
import asyncio
import unittest

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.topics import ON
from tests import set_log_levels
from tests.utils import (
    DataItem,
    TopicItem,
    async_case,
    create_std_ext_msg,
    send_data,
    send_topics,
    random_address,
    async_protocol_manager,
)


class TestProtocol(unittest.TestCase):
    """Test the protocol class."""

    def setUp(self):
        """Set up the tests."""
        self._last_topic = ""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_send_on_topic(self):
        """Test sending the ON command."""
        topic_lock = asyncio.Lock()
        async with async_protocol_manager():
            received_topic = ""

            def expected_topic_received(cmd1, cmd2, user_data, topic=pub.AUTO_TOPIC):
                nonlocal received_topic
                received_topic = topic.name
                if topic_lock.locked():
                    topic_lock.release()

            address = random_address()
            on_topic = "send.{}.1.direct".format(ON)
            topics = [
                TopicItem(
                    on_topic, {"address": address, "on_level": 0xFF, "group": 0}, 0
                )
            ]

            self._last_topic = None
            expected_topic = "ack.{}.1.on.direct".format(address.id)
            pub.subscribe(expected_topic_received, expected_topic)
            await topic_lock.acquire()
            send_topics(topics)
            try:
                await asyncio.wait_for(topic_lock.acquire(), 2)
                assert received_topic == expected_topic
            except asyncio.TimeoutError:
                assert expected_topic is None
            if topic_lock.locked():
                topic_lock.release()

    @async_case
    async def test_receive_on_msg(self):
        """Test receiving an ON message."""
        topic_lock = asyncio.Lock()
        async with async_protocol_manager() as protocol:
            last_topic = None

            def topic_received(
                cmd1, cmd2, target, user_data, hops_left, topic=pub.AUTO_TOPIC
            ):
                """Receive the OFF topic for a device."""
                nonlocal last_topic
                last_topic = topic.name
                if topic_lock.locked():
                    topic_lock.release()

            address = random_address()
            byte_data = create_std_ext_msg(
                address, 0x80, 0x11, 0xFF, target=Address("000001")
            )
            expected_topic = "{}.{}.on.broadcast".format(address.id, 1)
            pub.subscribe(topic_received, expected_topic)
            on_cmd = DataItem(byte_data, 0)
            data = [on_cmd]
            await topic_lock.acquire()
            send_data(data, protocol.read_queue)
            try:
                await asyncio.wait_for(topic_lock.acquire(), 2)
                assert last_topic == expected_topic
            except asyncio.TimeoutError:
                assert expected_topic is None
            if topic_lock.locked():
                topic_lock.release()

    @async_case
    async def test_send_on_all_link_broadcast_topic(self):
        """Test sending the broadcast ON command."""
        from pyinsteon.handlers.to_device.on_level_all_link_broadcast import (
            OnLevelAllLinkBroadcastCommand,
        )

        topic_lock = asyncio.Lock()
        async with async_protocol_manager():
            last_topic = None

            def topic_received(cmd1, cmd2, user_data, topic=pub.AUTO_TOPIC):
                """Receive the OFF topic for a device."""
                nonlocal last_topic
                last_topic = topic.name
                if topic_lock.locked():
                    topic_lock.release()

            group = 3
            target = Address(bytearray([0x00, 0x00, group]))
            ack_topic = "ack.{}.on.all_link_broadcast".format(target.id)
            pub.subscribe(topic_received, ack_topic)
            cmd = OnLevelAllLinkBroadcastCommand(group=group)
            await topic_lock.acquire()
            await cmd.async_send()  # Mock transport auto sends ACK/NAK
            try:
                await asyncio.wait_for(topic_lock.acquire(), 2)
                assert last_topic == ack_topic
            except asyncio.TimeoutError:
                assert ack_topic is None
            if topic_lock.locked():
                topic_lock.release()
