"""Test the on_level command handler."""
import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.constants import ResponseStatus
from pyinsteon.handlers.from_device.assign_to_all_link_group import (
    AssignToAllLinkGroupCommand,
)
from pyinsteon.handlers.to_device.id_request import IdRequestCommand
from pyinsteon.topics import ASSIGN_TO_ALL_LINK_GROUP

from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics


class TestIdRequest(unittest.TestCase):
    """Test the id_request command handler."""

    def setUp(self):
        """Set up the test."""
        self._cat = None
        self._subcat = None
        self._firmware = None
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def set_id(self, address, cat, subcat, firmware, group, link_mode):
        """Handle callback to on_level direct_ack."""
        self._cat = cat
        self._subcat = subcat
        self._firmware = firmware

    @async_case
    async def test_id_request(self):
        """Test ID Request command."""
        # await self.async_setup()
        address = random_address()
        modem_address = random_address()
        self._cat = None
        self._subcat = None
        self._firmware = None
        ack_topic = "ack.{}.id_request.direct".format(address.id)
        direct_ack_topic = "{}.id_request.direct_ack".format(address.id)
        id_response_topic = "{}.{}.broadcast".format(
            address.id, ASSIGN_TO_ALL_LINK_GROUP
        )
        all_link_handler = AssignToAllLinkGroupCommand(address)
        all_link_handler.subscribe(self.set_id)

        id_handler = IdRequestCommand(address)

        await asyncio.sleep(5)
        cmd1 = 0x99
        cmd2 = 0xAA
        topics = [
            TopicItem(ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": None}, 0.5),
            TopicItem(
                direct_ack_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2,
                    "target": modem_address,
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
            TopicItem(
                id_response_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2,
                    "target": Address("010203"),
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        send_topics(topics)
        assert await id_handler.async_send()
        await asyncio.sleep(1)
        assert self._cat == 1
        assert self._subcat == 2
        assert self._firmware == 3

    @async_case
    async def test_id_request_nak(self):
        """Test the ON command."""
        address = random_address()
        modem_address = random_address()
        self._cat = None
        self._subcat = None
        self._firmware = None
        ack_topic = "ack.{}.id_request.direct".format(address.id)
        direct_nak_topic = "{}.id_request.direct_nak".format(address.id)
        all_link_handler = AssignToAllLinkGroupCommand(address)
        all_link_handler.subscribe(self.set_id)
        id_handler = IdRequestCommand(address)
        cmd1 = 0x99
        cmd2 = 0xAA
        cmd2_failure = 0xFF
        cmd2_unclear = 0xFC

        topics_fail = [
            TopicItem(ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": None}, 0.5),
            TopicItem(
                direct_nak_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2_failure,
                    "target": modem_address,
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        topics_unclear = [
            TopicItem(ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": None}, 0.5),
            TopicItem(
                direct_nak_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2_unclear,
                    "target": modem_address,
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]

        send_topics(topics_fail)
        result = await id_handler.async_send()
        assert result == ResponseStatus.FAILURE

        send_topics(topics_unclear)
        result = await id_handler.async_send()
        assert result == ResponseStatus.UNCLEAR

        all_link_handler = None
        id_handler = None


if __name__ == "__main__":
    unittest.main()
