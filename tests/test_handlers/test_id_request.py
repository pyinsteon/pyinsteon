"""Test the on_level command handler."""
import asyncio
import logging
import sys
import unittest

from pyinsteon.address import Address
from pyinsteon.constants import ResponseStatus
from pyinsteon.handlers.id_request import IdRequestCommand
from pyinsteon.topics import ASSIGN_TO_ALL_LINK_GROUP
from tests.utils import TopicItem, async_case, async_send_topics

from tests import _LOGGER

class TestIdRequest(unittest.TestCase):
    """Test the id_request command handler."""

    def setUp(self):
        """Set up the test."""
        self._address = '1a2b3c'
        self.handler = IdRequestCommand(self._address)
        self.handler.subscribe(self.set_id)
        self._cat = None
        self._subcat = None
        self._firmware = None
        self.ack_topic = 'ack.{}.id_request.direct'.format(self._address)
        self.direct_ack_topic = '{}.id_request.direct_ack'.format(self._address)
        self.direct_nak_topic = '{}.id_request.direct_nak'.format(self._address)
        self.id_response_topic = '{}.{}.broadcast'.format(self._address, ASSIGN_TO_ALL_LINK_GROUP)

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def set_id(self, address, cat, subcat, firmware):
        """Callback to on_level direct_ack."""
        self._cat = cat
        self._subcat = subcat
        self._firmware = firmware

    @async_case
    async def test_id_request(self):
        """Test the ON command."""
        cmd2 = 0xaa
        topics = [TopicItem(self.ack_topic,
                            {"cmd2": cmd2, "target": None, "user_data": None}, .5),
                  TopicItem(self.direct_ack_topic,
                            {"cmd2": cmd2, "target": None, "user_data": None}, .5),
                  TopicItem(self.id_response_topic,
                            {'cmd2': cmd2, 'target': Address('010203'), 'user_data': None}, .5)]
        asyncio.ensure_future(async_send_topics(topics))
        assert await self.handler.async_send()
        assert self._cat == 1
        assert self._subcat == 2
        assert self._firmware == 3

    @async_case
    async def test_id_request_nak(self):
        """Test the ON command."""
        cmd2 = 0xaa
        topics = [TopicItem(self.ack_topic,
                            {"cmd2": cmd2, "target": None, "user_data": None}, .5),
                  TopicItem(self.direct_nak_topic,
                            {"cmd2": cmd2, "target": None, "user_data": None}, .5)]
        asyncio.ensure_future(async_send_topics(topics))
        assert await self.handler.async_send() == ResponseStatus.UNCLEAR

if __name__ == '__main__':
    unittest.main()
