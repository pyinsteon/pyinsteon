"""Test broadcast messages for deduplication."""

from datetime import datetime, timedelta
from random import randint
import unittest
from unittest.mock import patch

from pyinsteon import pub
from pyinsteon.handlers.from_device import broadcast_command
from pyinsteon.handlers.from_device.assign_to_all_link_group import (
    AssignToAllLinkGroupCommand,
)
from pyinsteon.handlers.from_device.broadcast_command import MAX_DUP, MIN_DUP
from pyinsteon.handlers.from_device.delete_from_all_link_group import (
    DeleteFromAllLinkGroupCommand,
)
from pyinsteon.handlers.from_device.manual_change import ManualChangeInbound
from pyinsteon.handlers.from_device.off import OffInbound
from pyinsteon.handlers.from_device.off_fast import OffFastInbound
from pyinsteon.handlers.from_device.on_fast import OnFastInbound
from pyinsteon.handlers.from_device.on_level import OnLevelInbound
from pyinsteon.topics import (
    ASSIGN_TO_ALL_LINK_GROUP,
    DELETE_FROM_ALL_LINK_GROUP,
    OFF,
    OFF_FAST,
    ON,
    ON_FAST,
    STOP_MANUAL_CHANGE,
)
from pyinsteon.utils import subscribe_topic, unsubscribe_topic

from tests import set_log_levels
from tests.utils import async_case, cmd_kwargs, random_address

MSG = "{}.{}.{}.all_link_broadcast"
MSG_NO_GROUP = "{}.{}.all_link_broadcast"


COMMANDS = {
    ASSIGN_TO_ALL_LINK_GROUP: AssignToAllLinkGroupCommand,
    DELETE_FROM_ALL_LINK_GROUP: DeleteFromAllLinkGroupCommand,
    STOP_MANUAL_CHANGE: ManualChangeInbound,
    OFF_FAST: OffFastInbound,
    OFF: OffInbound,
    ON_FAST: OnFastInbound,
    ON: OnLevelInbound,
}
NO_GROUP_CMDS = [AssignToAllLinkGroupCommand, DeleteFromAllLinkGroupCommand]


class FakeClock:
    """Stand in for datetime inside the handler so the tests own elapsed time."""

    def __init__(self):
        """Init the FakeClock class."""
        self._now = datetime(2020, 1, 1)

    def __call__(self, *args, **kwargs):
        """Build a datetime, the handler does this for its initial timestamp."""
        return datetime(*args, **kwargs)

    def now(self):
        """Return the current fake time."""
        return self._now

    def advance(self, seconds):
        """Move the fake time forward."""
        self._now += timedelta(seconds=seconds)


def send_broadcast(topic, address, group, hops):
    """Publish one broadcast message the way the protocol layer would."""
    target = "0000{:02d}".format(group)
    kwargs = cmd_kwargs(
        cmd1=0x11, cmd2=0x00, user_data=None, target=target, hops_left=hops
    )
    if topic in [ASSIGN_TO_ALL_LINK_GROUP, DELETE_FROM_ALL_LINK_GROUP]:
        msg_topic = MSG_NO_GROUP.format(address.id, topic)
    else:
        msg_topic = MSG.format(address.id, group, topic)
    pub.sendMessage(msg_topic, **kwargs)


class TestBroadcastMessageDedup(unittest.TestCase):
    """Test broadcast messages for deduplication.

    1. Two messages with Hops reduction within MAX_DUP seconds => 1 call
    2. Two messages outside MAX_DUP seconds => 2 calls
    3. Two messages with hops reduction gt MAX_DUP seconds => 2 calls
    4. Two messages same hops within MIN_DUP seconds => 1 call
    5. Two messages same hops gt MIN_DUP seconds => 2 calls
    6. Two messages increase hops within MAX_DUP seconds => 2 calls

    """

    def setUp(self):
        """Set up the test."""
        self.call_count = 0
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        subscribe_topic(self.handle_topics, "handler")

    def tearDown(self) -> None:
        """Tear down the test."""
        unsubscribe_topic(self.handle_topics, "handler")

    def handle_topics(self, topic=pub.AUTO_TOPIC):
        """Count the messages that made it through the handler."""
        self.call_count += 1

    def two_messages(self, first_hops, second_hops, gap, expected):
        """Send two messages gap seconds apart to every broadcast handler type."""
        clock = FakeClock()
        with patch.object(broadcast_command, "datetime", clock):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                send_broadcast(topic, address, group, first_hops)
                clock.advance(gap)
                send_broadcast(topic, address, group, second_hops)
                assert self.call_count == expected, f"{topic}: {self.call_count}"
                del handler

    @async_case
    async def test_dup(self):
        """Test two messages with Hops reduction within MAX_DUP seconds => 1 call."""
        self.two_messages(3, 2, MAX_DUP - 0.1, 1)

    @async_case
    async def test_dup_gt_MAX_DUP_sec(self):
        """Test two messages outside MAX_DUP seconds => 2 calls."""
        self.two_messages(3, 3, MAX_DUP + 0.1, 2)

    @async_case
    async def test_dup_reduce_hops_gt_MAX_DUP_sec(self):
        """Test two messages with hops reduction gt MAX_DUP seconds => 2 calls."""
        self.two_messages(3, 2, MAX_DUP + 0.1, 2)

    @async_case
    async def test_dup_same_hops_lt_MIN_DUP_sec(self):
        """Test two messages same hops within MIN_DUP seconds => 1 call."""
        self.two_messages(2, 2, MIN_DUP - 0.1, 1)

    @async_case
    async def test_dup_same_hops_gt_MIN_DUP_sec(self):
        """Test two messages same hops gt MIN_DUP seconds => 2 calls."""
        self.two_messages(2, 2, MIN_DUP + 0.1, 2)

    @async_case
    async def test_dup_increase_hops_lt_MAX_DUP_sec(self):
        """Test two messages increase hops within MAX_DUP seconds => 2 calls."""
        self.two_messages(2, 3, MAX_DUP - 0.1, 2)


if __name__ == "__main__":
    unittest.main()
