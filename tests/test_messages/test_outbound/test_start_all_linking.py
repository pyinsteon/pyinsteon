"""Test Start All-Linking."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.constants import AllLinkMode, MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import start_all_linking  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestStartAllLinking(unittest.TestCase, OutboundBase):
    """Test Start All-Linking."""

    def setUp(self):
        """Test set up."""
        self.hex = "02640304"
        self.message_id = MessageId.START_ALL_LINKING
        self.link_mode = AllLinkMode(0x03)
        self.group = int(0x04)

        kwargs = {"group": self.group, "link_mode": self.link_mode}

        super(TestStartAllLinking, self).base_setup(
            self.message_id, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_mode(self):
        """Test link_mode."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.link_mode == self.link_mode

    @async_case
    async def test_group(self):
        """Test group."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.group == self.group


if __name__ == "__main__":
    unittest.main()
