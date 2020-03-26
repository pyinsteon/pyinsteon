"""Test Start All-Linking."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode, MessageId
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import start_all_linking
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestStartAllLinking(unittest.TestCase, OutboundBase):
    """Test Start All-Linking."""

    def setUp(self):
        """Test set up."""
        self.hex = "02640304"
        self.message_id = MessageId.START_ALL_LINKING
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)

        kwargs = {"group": self.group, "mode": self.mode}

        super(TestStartAllLinking, self).base_setup(
            self.message_id, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_mode(self):
        """Test mode."""
        assert self.msg.mode == self.mode

    def test_group(self):
        """Test group."""
        assert self.msg.group == self.group


if __name__ == "__main__":
    unittest.main()
