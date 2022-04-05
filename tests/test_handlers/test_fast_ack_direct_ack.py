"""Test a fast Direct ACK response after an ACK is received."""
import asyncio
from random import randint
from unittest import TestCase

from pyinsteon.constants import MessageFlagType
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from pyinsteon.handlers.to_device.status_request import StatusRequestCommand
from pyinsteon.topics import ON, STATUS_REQUEST
from pyinsteon.utils import build_topic
from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics


class TestFastDirectAck(TestCase):
    """Test a fast Direct Ack response after an ACK is received."""

    @async_case
    async def test_on_with_fast_direct_ack(self):
        """Test ON with fast direct ack response."""
        response_called = False

        def handle_on_response(on_level):
            """Handle the ON command response."""
            nonlocal response_called
            response_called = True

        set_log_levels(logger_topics=True)

        address = random_address()
        target = random_address()
        group = randint(0, 10)
        cmd = OnLevelCommand(address, group)
        cmd.subscribe(handle_on_response)
        ack_topic = build_topic(ON, "ack", address, group, MessageFlagType.DIRECT)
        direct_ack_topic = build_topic(
            ON, None, address, None, MessageFlagType.DIRECT_ACK
        )
        ack_topic_item = TopicItem(
            topic=ack_topic,
            kwargs={"cmd1": 0x11, "cmd2": 0xFF, "user_data": None},
            delay=0.1,
        )
        direct_ack_topic_item = TopicItem(
            topic=direct_ack_topic,
            kwargs={
                "cmd1": 0x11,
                "cmd2": 0xFF,
                "target": target,
                "user_data": None,
                "hops_left": 0,
            },
            delay=0,
        )
        send_topics([ack_topic_item, direct_ack_topic_item])
        await asyncio.sleep(0.2)
        assert response_called

    @async_case
    async def test_status_with_fast_direct_ack(self):
        """Test STATUS REQUEST with fast direct ack response."""
        response_called = False

        def handle_status_response(db_version, status):
            """Handle the ON command response."""
            nonlocal response_called
            response_called = True

        set_log_levels(logger_topics=True)

        address = random_address()
        target = random_address()
        status_type = randint(0, 10)
        cmd = StatusRequestCommand(address, status_type)
        cmd.subscribe(handle_status_response)
        ack_topic = build_topic(
            STATUS_REQUEST, "ack", address, None, MessageFlagType.DIRECT
        )
        direct_ack_topic = build_topic(
            ON, None, address, None, MessageFlagType.DIRECT_ACK
        )
        ack_topic_item = TopicItem(
            topic=ack_topic,
            kwargs={"cmd1": 0x19, "cmd2": status_type, "user_data": None},
            delay=0.1,
        )
        direct_ack_topic_item = TopicItem(
            topic=direct_ack_topic,
            kwargs={
                "cmd1": 0x11,
                "cmd2": 0x02,
                "target": target,
                "user_data": None,
                "hops_left": 0,
            },
            delay=0,
        )
        send_topics([ack_topic_item, direct_ack_topic_item])
        await asyncio.sleep(0.2)
        assert response_called
