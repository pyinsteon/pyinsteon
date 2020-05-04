"""Test Send All-link Command."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode, MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_all_link_command  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSendAllLinkCommand(unittest.TestCase, OutboundBase):
    """Test Send All-link Command."""

    def setUp(self):
        """Test set up."""
        self.hex = "0261011100"
        self.group = 0x01
        self.mode = AllLinkMode.CONTROLLER

        kwargs = {"group": self.group, "cmd1": 0x11, "cmd2": 0x00}

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

    def test_cmd1(self):
        """Test cmd1."""
        assert self.msg.cmd1 == 0x11

    def test_cmd2(self):
        """Test cmd2."""
        assert self.msg.cmd2 == 0x00


if __name__ == "__main__":
    unittest.main()
