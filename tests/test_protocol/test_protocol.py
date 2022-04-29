"""Test the protocol class."""
import asyncio
import unittest
from binascii import unhexlify
from unittest.mock import patch

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.topics import ON
from tests import set_log_levels
from tests.utils import (
    DataItem,
    TopicItem,
    async_case,
    async_protocol_manager,
    create_std_ext_msg,
    random_address,
    send_data,
    send_topics,
)


class TestProtocol(unittest.TestCase):
    """Test the protocol class."""

    def setUp(self):
        """Set up the tests."""
        self.topic = None
        self._last_topic = ""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
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
    async def test_connected(self):
        """Test the connected property."""
        with patch(
            "pyinsteon.protocol.protocol.publish_topic", self.mock_publish_topic
        ):
            async with async_protocol_manager() as protocol:
                assert self.topic == "connection.made"
                assert protocol.connected
                protocol.close()
                assert not protocol.connected
                assert protocol.message_queue

    @async_case
    async def test_connection_failed(self):
        """Test the connected property."""
        with patch(
            "pyinsteon.protocol.protocol.publish_topic", self.mock_publish_topic
        ):
            try:
                async with async_protocol_manager(connect=False, retry=False):
                    await asyncio.sleep(0.1)
                    assert False
            except ConnectionError:
                await asyncio.sleep(0.1)
                assert self.topic == "connection.failed"

    @async_case
    async def test_connection_retry(self):
        """Test the connected property."""
        with patch(
            "pyinsteon.protocol.protocol.publish_topic", self.mock_publish_topic
        ):
            try:
                async with async_protocol_manager(
                    connect=False, retry=True, retries=[1, 1]
                ) as protocol:
                    await asyncio.sleep(0.1)
                    assert protocol.connected
                    assert self.topic == "connection.made"
            except ConnectionError:
                assert False

    def mock_publish_topic(self, topic, **kwargs):
        """Mock the publish topic method."""
        self.topic = topic

    @async_case
    async def test_data_received(self):
        """Test the data_received method."""

        def dummy_nak_listener(*args, **kwargs):
            """Listen for NAK.

            This ensures we send the NAK rather than resend the message.
            """

        data = [
            {"data": "025003040506070809110b", "topic": "030405.1.on.direct"},
            {"data": "02500304050607", "topic": None},
            {"data": "0809130b", "topic": "030405.1.off.direct"},
        ]

        with patch(
            "pyinsteon.protocol.protocol.publish_topic", self.mock_publish_topic
        ):
            async with async_protocol_manager(auto_ack=False) as protocol:
                for test in data:
                    self.topic = None
                    protocol.data_received(unhexlify(test["data"]))
                    await asyncio.sleep(0.1)
                    try:
                        assert self.topic == test["topic"]
                    except AssertionError:
                        raise AssertionError(
                            f"Failed with data {test['data']}: Topic: {self.topic}  Expected: {test['topic']}"
                        )

                # Test when the modem only responds with a NAK rather than the original message.
                nak_topic = "nak.0a0b0c.1.on.direct"
                pub.subscribe(dummy_nak_listener, nak_topic)
                protocol.write(unhexlify("02620a0b0c09110b"))
                await asyncio.sleep(0.1)
                self.topic = None
                protocol.data_received(unhexlify("15"))
                await asyncio.sleep(0.1)
                assert self.topic == nak_topic

                # Test that a NAK is resent rather than published as a topic.
                self.topic = None
                protocol.data_received(unhexlify("02620d0e0f09110b15"))
                await asyncio.sleep(0.1)
                assert self.topic is None

    @async_case
    async def test_pause_resume_writer(self):
        """Test the pause_writer and resume_writer methods."""
        async with async_protocol_manager(auto_ack=False) as protocol:
            await asyncio.sleep(0.1)
            protocol.write(unhexlify("02620a0b0c09110b"))
            await asyncio.sleep(0.1)
            assert protocol.message_queue.empty()

            protocol.pause_writing()
            await asyncio.sleep(0.1)
            protocol.write(unhexlify("026201020309110b"))
            await asyncio.sleep(0.1)
            assert not protocol.message_queue.empty()

            protocol.resume_writing()
            await asyncio.sleep(0.1)
            assert protocol.message_queue.empty()
