"""Test Send All-link Command."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode, MessageId
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_all_link_command
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSendAllLinkCommand(unittest.TestCase, OutboundBase):
    """Test Send All-link Command."""

    def setUp(self):
        """Test set up."""
        self.hex = "02610101"
        self.group = 0x01
        self.mode = AllLinkMode.CONTROLLER

        kwargs = {"group": self.group, "mode": self.mode}

        super(TestSendAllLinkCommand, self).base_setup(
            MessageId.SEND_ALL_LINK_COMMAND, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_group(self):
        """Test group."""
        assert self.msg.group == self.group

    def test_mode(self):
        """Test mode."""
        assert self.msg.mode == self.mode


if __name__ == "__main__":
    unittest.main()
