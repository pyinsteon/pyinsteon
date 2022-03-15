"""Test the on_level command handler."""

import unittest

import pyinsteon.handlers
from pyinsteon.address import Address
from pyinsteon.constants import ResponseStatus
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from tests import set_log_levels
from tests.utils import TopicItem, async_case, send_topics


class TestNoDirectAck(unittest.TestCase):
    """Test the on_level command handler."""

    def setUp(self):
        """Set up the test."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def set_on_level(self, on_level, group):
        """Handle callback for on_level direct_ack."""
        self._on_level = on_level
        self._group = group

    @async_case
    async def test_no_direct_ack(self):
        """Test no direct ACK received."""
        self._address = Address("234567")
        self.handler = OnLevelCommand(self._address, group=1)
        self.handler.subscribe(self.set_on_level)
        self._on_level = None
        self._group = None
        self.ack_topic = "ack.{}.{}.on.direct".format(self._address.id, 1)
        orig_timeout = pyinsteon.handlers.TIMEOUT
        pyinsteon.handlers.TIMEOUT = 0.1
        cmd1 = 0x99
        cmd2 = 0xAA
        topics = [
            TopicItem(
                self.ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": None}, 0.2
            )
        ]
        send_topics(topics)
        assert (
            await self.handler.async_send(on_level=cmd2)
            == ResponseStatus.DEVICE_UNRESPONSIVE
        )
        assert self._on_level is None
        pyinsteon.handlers.TIMEOUT = orig_timeout


if __name__ == "__main__":
    unittest.main()
