"""Test the StatusManager class."""

import asyncio
from functools import partial
import unittest
from unittest.mock import AsyncMock

from pyinsteon.constants import ResponseStatus
from pyinsteon.managers.status_manager import StatusManager
from pyinsteon.utils import subscribe_topic, unsubscribe_topic

from .. import set_log_levels
from ..utils import TopicItem, async_case, random_address, send_topics


async def handle_status(handler, db_version, status):
    """Handle the status call."""
    await handler(db_version, status)


def gen_topic_items(address, status_type, db_version, status):
    """Generate a set of topics to respond correctly to a status request."""
    ack_topic = f"ack.{address.id}.status_request.direct"
    direct_ack_topic = f"{address.id}.any_topic.direct_ack"
    return [
        TopicItem(
            ack_topic,
            {"cmd1": 0x19, "cmd2": status_type, "user_data": None},
            0.1,
        ),
        TopicItem(
            direct_ack_topic,
            {
                "cmd1": db_version,
                "cmd2": status,
                "target": address.id,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        ),
    ]


def send_status_topics(address, status_type):
    """Send the ack and direct_ack topics for a status message."""
    topic_items = gen_topic_items(address, status_type, 0x22, 0x33)
    send_topics(topic_items=topic_items)


class TestStatusManager(unittest.TestCase):
    """Test the StatusManager class."""

    def setUp(self) -> None:
        """Set up the test."""
        set_log_levels(logger="debug", logger_topics=True)
        subscribe_topic(send_status_topics, "send.status_request.direct")
        return super().setUp()

    def tearDown(self) -> None:
        """Unsubscribe to topic."""
        unsubscribe_topic(send_status_topics, "send.status_request.direct")
        return super().tearDown()

    @async_case
    async def test_single_status_call(self):
        """Test a single status call."""
        handler = AsyncMock(db_version=None, status=None)
        address = random_address()
        status_type = 0
        status_manager = StatusManager(address=address)
        status_manager.add_status_type(
            status_type=status_type,
            callback_function=partial(handle_status, handler=handler),
        )

        result = await status_manager.async_status()
        await asyncio.sleep(0.01)
        assert result == ResponseStatus.SUCCESS
        assert handler.call_count == 1

    @async_case
    async def test_two_status_calls(self):
        """Test a two status calls."""
        handler = AsyncMock(db_version=None, status=None)
        handler_1 = AsyncMock()
        address = random_address()
        status_type = 0
        status_manager = StatusManager(address=address)
        status_manager.add_status_type(
            status_type=status_type,
            callback_function=partial(handle_status, handler=handler),
        )
        status_type_1 = 1
        status_manager.add_status_type(
            status_type=status_type_1,
            callback_function=partial(handle_status, handler=handler_1),
        )

        result = await status_manager.async_status()
        await asyncio.sleep(1)
        assert result == ResponseStatus.SUCCESS
        assert handler.call_count == 1
        assert handler_1.call_count == 1

    @async_case
    async def test_overlapping_status_calls(self):
        """Test overlapping status request calls."""
        handler = AsyncMock(db_version=None, status=None)
        address = random_address()
        status_type = 0
        status_manager = StatusManager(address=address)
        status_manager.add_status_type(
            status_type=status_type,
            callback_function=partial(handle_status, handler=handler),
        )

        asyncio.ensure_future(status_manager.async_status())
        asyncio.ensure_future(status_manager.async_status())
        await status_manager.async_status()
        await asyncio.sleep(5)
        assert handler.call_count == 2
