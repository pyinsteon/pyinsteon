"""Test broadcast messages for deduplication."""
from random import randint
import unittest
from unittest.mock import patch
from asyncio import sleep

import pyinsteon
from pyinsteon import pub
from pyinsteon.handlers.from_device.broadcast_command import MAX_DUP, MIN_DUP
from pyinsteon.handlers.from_device.assign_to_all_link_group import (
    AssignToAllLinkGroupCommand,
)
from pyinsteon.handlers.from_device.delete_from_all_link_group import (
    DeleteFromAllLinkGroupCommand,
)
from pyinsteon.handlers.from_device.manual_change import ManualChangeInbound
from pyinsteon.handlers.from_device.off_fast import OffFastInbound
from pyinsteon.handlers.from_device.off import OffInbound
from pyinsteon.handlers.from_device.on_fast import OnFastInbound
from pyinsteon.handlers.from_device.on_level import OnLevelInbound
from pyinsteon.topics import (
    ASSIGN_TO_ALL_LINK_GROUP,
    DELETE_FROM_ALL_LINK_GROUP,
    STOP_MANUAL_CHANGE,
    OFF_FAST,
    OFF,
    ON_FAST,
    ON,
)
from pyinsteon.utils import subscribe_topic
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics

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


def create_topic(topic, address, group, hops, delay):
    """Create a TopicItem."""
    cmd1 = 0x11
    cmd2 = 0x00
    target = "0000{:02d}".format(group)
    kwargs = cmd_kwargs(
        cmd1=cmd1, cmd2=cmd2, user_data=None, target=target, hops_left=hops
    )
    if topic in [ASSIGN_TO_ALL_LINK_GROUP, DELETE_FROM_ALL_LINK_GROUP]:
        msg_topic = MSG_NO_GROUP.format(address.id, topic)
    else:
        msg_topic = MSG.format(address.id, group, topic)
    return TopicItem(msg_topic, kwargs=kwargs, delay=delay)


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
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        subscribe_topic(self.handle_topics, pub.ALL_TOPICS)

    async def handle_topics(self, topic=pub.AUTO_TOPIC):
        """Handle the on topic."""
        if topic.name.startswith("handler"):
            self.call_count += 1

    @async_case
    async def test_dup(self):
        """Test two messages with Hops reduction within MAX_DUP seconds => 1 call."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                topics = [
                    create_topic(topic, address, group, 3, 0),
                    create_topic(topic, address, group, 2, 0.4),
                ]
                self.call_count = 0
                send_topics(topics)
                await sleep(.5)
                assert self.call_count == 1

    @async_case
    async def test_dup_gt_MAX_DUP_sec(self):
        """Test two messages outside MAX_DUP seconds => 2 calls."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                topics = [
                    create_topic(topic, address, group, 3, 0.0),
                    create_topic(topic, address, group, 3, 0.6),
                ]
                send_topics(topics)
                await sleep(0.7)
                assert self.call_count == 2

    @async_case
    async def test_dup_reduce_hops_gt_MAX_DUP_sec(self):
        """Test two messages with hops reduction gt MAX_DUP seconds => 2 calls."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                topics = [
                    create_topic(topic, address, group, 3, 0.0),
                    create_topic(topic, address, group, 2, 0.6),
                ]
                send_topics(topics)
                await sleep(0.7)
                assert self.call_count == 2

    @async_case
    async def test_dup_same_hops_lt_MIN_DUP_sec(self):
        """Test two messages same hops within 1 seconds => 1 call."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                topics = [
                    create_topic(topic, address, group, 2, 0.0),
                    create_topic(topic, address, group, 2, 0.2),
                ]
                send_topics(topics)
                await sleep(0.3)
                assert self.call_count == 1

    @async_case
    async def test_dup_same_hops_gt_MIN_DUP_sec(self):
        """Test two messages same hops gt MIN_DUP seconds => 2 calls."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                topics = [
                    create_topic(topic, address, group, 2, 0.0),
                    create_topic(topic, address, group, 2, 0.4),
                ]
                send_topics(topics)
                await sleep(0.5)
                assert self.call_count == 2

    @async_case
    async def test_dup_increase_hops_lt_MAX_DUP_sec(self):
        """Test two messages increase hops within 2 seconds => 2 calls."""

        with patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MIN_DUP", 0.3
        ), patch.object(
            pyinsteon.handlers.from_device.broadcast_command, "MAX_DUP", 0.5
        ):
            for topic, command in COMMANDS.items():
                group = randint(1, 9)
                address = random_address()
                if command in NO_GROUP_CMDS:
                    handler = command(address)
                else:
                    handler = command(address, group)
                self.call_count = 0
                topics = [
                    create_topic(topic, address, group, 2, 0.0),
                    create_topic(topic, address, group, 3, 0.4),
                ]
                send_topics(topics)
                await sleep(0.5)
                assert self.call_count == 2
