"""Test broadcast messages for deduplication."""
import unittest
from asyncio import sleep

from pyinsteon.handlers.from_device.on_level import OnLevelInbound
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics

ON_MSG = "{}.{}.on.all_link_broadcast"
ON_CLEANUP = "{}.{}.on.all_link_cleanup"


class TestBroadcastMessageDedup(unittest.TestCase):
    """Test broadcast messages for deduplication.

    1. Two messages with Hops reduction within 2 seconds => 1 call
    2. Two messages outside two seconds => 2 calls
    3. Two messages with hops reduction gt two seconds => 2 calls
    4. Two messages same hops within 1 seconds => 1 call
    4. Two messages same hops gt 1 seconds => 2 calls
    5. Two messages increase hops within 2 seconds => 2 calls

    """

    def setUp(self):
        """Set up the test."""
        self.call_count = 0
        self.address = repr(random_address())
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def create_topic(self, group, hops, delay):
        """Create a TopicItem."""
        group = 3
        cmd1 = 0x11
        cmd2 = 0x00
        target = "0000{:02d}".format(group)
        kwargs = cmd_kwargs(
            cmd1=cmd1, cmd2=cmd2, user_data=None, target=target, hops_left=hops
        )
        return TopicItem(ON_MSG.format(self.address, group), kwargs=kwargs, delay=delay)

    def handle_on_topic(self, on_level):
        """Handle the on topic."""
        self.call_count += 1

    @async_case
    async def test_dup_on(self):
        """Test two messages with Hops reduction within 2 seconds => 1 call."""
        topics = [self.create_topic(3, 3, 0.1), self.create_topic(3, 2, 0.9)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(2)
        assert self.call_count == 1

    @async_case
    async def test_dup_on_gt_2_sec(self):
        """Test two messages outside two seconds => 2 calls."""
        topics = [self.create_topic(3, 3, 0.1), self.create_topic(3, 3, 2.2)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(2.5)
        assert self.call_count == 2

    @async_case
    async def test_dup_on_reduce_hops_gt_2_sec(self):
        """Test two messages with hops reduction gt two seconds => 2 calls."""
        topics = [self.create_topic(3, 3, 0.1), self.create_topic(3, 2, 2.1)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(2.4)
        assert self.call_count == 2

    @async_case
    async def test_dup_on_same_hops_lt_1_sec(self):
        """Test two messages same hops within 1 seconds => 1 call."""
        topics = [self.create_topic(3, 2, 0.1), self.create_topic(3, 2, 0.9)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(1.3)
        assert self.call_count == 1

    @async_case
    async def test_dup_on_same_hops_gt_1_sec(self):
        """Test two messages same hops gt 1 seconds => 2 calls."""
        topics = [self.create_topic(3, 2, 0.1), self.create_topic(3, 2, 1.1)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(1.3)
        assert self.call_count == 2

    @async_case
    async def test_dup_on_increase_hops_lt_2_sec(self):
        """Test two messages increase hops within 2 seconds => 2 calls."""
        topics = [self.create_topic(3, 2, 0.1), self.create_topic(3, 3, 0.9)]

        on_handler = OnLevelInbound(self.address, 3)
        on_handler.subscribe(self.handle_on_topic)
        send_topics(topics)
        await sleep(1.3)
        assert self.call_count == 2
