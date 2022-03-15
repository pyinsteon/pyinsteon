"""Test the on/off manager."""
import unittest
from asyncio import sleep

from pyinsteon.address import Address
from pyinsteon.constants import MessageFlagType
from pyinsteon.managers.on_level_manager import OnLevelManager
from pyinsteon.topics import OFF, OFF_FAST, ON, ON_FAST
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics


class TestOnLevelManager(unittest.TestCase):
    """Test the on/off manager.

    1. On message => on_level = 255 & call_count = 1
    2. Off message => on_level = 0 & call_count = 1
    3. On_fast message => on_level = 255 & call_count = 1
    4. Off_fast message => on_level = 0 & call_count = 1
    5. Two On messages within 2 sec => on_level = 255 & call_count = 1
    6. Two Off messages within 2 sec => on_level = 0 & call_count = 1
    7. Two On_fast messages within 2 sec => on_level = 255 & call_count = 1
    8. Two Off_fast messages within 2 sec => on_level = 0 & call_count = 1
    9. On All-Link Cleanup message => on_level = 255 & call_count = 1
    10. Off All-Link Cleanup message => on_level = 0 & call_count = 1
    11. On_fast All-Link Cleanup message => on_level = 255 & call_count = 1
    12. Off_fast All-Link Cleanup message => on_level = 0 & call_count = 1
    13. One on and one off message => on_level = 0 & call_count = 2
    14. One on and one on cleanup => on_level = 255 and call_count = 1
    15. One of and one off cleanup => on_level = 0 and call_count = 1
    """

    def setUp(self):
        """Set up the test."""
        self.address = random_address()
        self.group = 6
        self.target = Address(f"0000{self.group:02d}")
        self.on_level_manager = OnLevelManager(self.address, self.group)
        self.on_level_manager.subscribe(self.handle_on_off)
        self.on_level = None
        self.call_count = 0
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def handle_on_off(self, on_level):
        """Handle the on/off commands."""
        self.on_level = on_level
        self.call_count += 1

    async def run_test(self, topics, on_level_expected, call_count_expected):
        """Run the test and validate outcomes."""
        sleep_for = 0.2
        for topic in topics:
            sleep_for += topic.delay
        send_topics(topics)
        await sleep(sleep_for)
        assert self.on_level == on_level_expected
        assert self.call_count == call_count_expected

    def create_topic(self, topic, msg_type, group, kwargs, delay):
        """Create a topic item."""
        full_topic = f"{repr(self.address)}.{group}.{topic}.{str(msg_type).lower()}"
        return TopicItem(topic=full_topic, kwargs=kwargs, delay=delay)

    @async_case
    async def test_on(self):
        """Test On message => on_level = 255 & call_count = 1."""
        kwargs = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(ON, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs, 0.1)
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off(self):
        """Test Off message => on_level = 0 & call_count = 1."""
        kwargs = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(OFF, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs, 0.1)
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_fast(self):
        """Test Off message => on_level = 0 & call_count = 1."""
        kwargs = cmd_kwargs(0x12, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(
                ON_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs, 0.1
            )
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_fast(self):
        """Test Off message => on_level = 0 & call_count = 1."""
        kwargs = cmd_kwargs(0x14, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(
                OFF_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs, 0.1
            )
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_2_msg_reduce_hops(self):
        """Test two On messages within 2 sec => on_level = 255 & call_count = 1."""
        kwargs0 = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=2)
        topics = [
            self.create_topic(ON, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1),
            self.create_topic(ON, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs1, 0.3),
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_2_msg_reduce_hops(self):
        """Test two Off messages within 2 sec => on_level = 0 & call_count = 1."""
        kwargs0 = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=2)
        topics = [
            self.create_topic(OFF, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1),
            self.create_topic(OFF, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs1, 0.3),
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_fast_2_msg_reduce_hops(self):
        """Test two On_fast messages within 2 sec => on_level = 255 & call_count = 1."""
        kwargs0 = cmd_kwargs(0x12, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x12, 0x00, None, self.target, hops_left=2)
        topics = [
            self.create_topic(
                ON_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1
            ),
            self.create_topic(
                ON_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs1, 0.3
            ),
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_fast_2_msg_reduce_hops(self):
        """Test two Off_fast messages within 2 sec => on_level = 255 & call_count = 1."""
        kwargs0 = cmd_kwargs(0x14, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x14, 0x00, None, self.target, hops_left=2)
        topics = [
            self.create_topic(
                OFF_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1
            ),
            self.create_topic(
                OFF_FAST, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs1, 0.3
            ),
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_cleanup(self):
        """Test On All-Link Cleanup message => on_level = 255 & call_count = 1."""
        kwargs = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(ON, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs, 0.1)
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_cleanup(self):
        """Test Off All-Link Cleanup message => on_level = 0 & call_count = 1."""
        kwargs = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(OFF, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs, 0.1)
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_fast_cleanup(self):
        """Test On_fast All-Link Cleanup message => on_level = 255 & call_count = 1."""
        kwargs = cmd_kwargs(0x12, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(ON_FAST, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs, 0.1)
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_fast_cleanup(self):
        """Test Off_fast All-Link Cleanup message => on_level = 0 & call_count = 1."""
        kwargs = cmd_kwargs(0x14, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(
                OFF_FAST, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs, 0.1
            )
        ]
        await self.run_test(topics, 0, 1)

    @async_case
    async def test_on_then_off(self):
        """Test one on and one off message => on_level = 0 & call_count = 2."""
        kwargs0 = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(ON, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1),
            self.create_topic(OFF, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs1, 0.3),
        ]
        await self.run_test(topics, 0, 2)

    @async_case
    async def test_on_and_on_cleanup(self):
        """Test one on and one on cleanup => on_level = 255 and call_count = 1."""
        kwargs0 = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x11, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(ON, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1),
            self.create_topic(ON, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs1, 0.3),
        ]
        await self.run_test(topics, 255, 1)

    @async_case
    async def test_off_and_off_cleanup(self):
        """Test one off and one off cleanup => on_level = 255 and call_count = 1."""
        kwargs0 = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        kwargs1 = cmd_kwargs(0x13, 0x00, None, self.target, hops_left=3)
        topics = [
            self.create_topic(OFF, MessageFlagType.ALL_LINK_BROADCAST, 6, kwargs0, 0.1),
            self.create_topic(OFF, MessageFlagType.ALL_LINK_CLEANUP, 6, kwargs1, 0.3),
        ]
        await self.run_test(topics, 0, 1)
