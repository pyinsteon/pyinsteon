"""Test Get IM Configuration."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import get_im_configuration  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetImConfiguration(unittest.TestCase, OutboundBase):
    """Test Get IM Configuration."""

    def setUp(self):
        """Test set up."""
        self.hex = "0273"
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x73)
        super(TestGetImConfiguration, self).base_setup(
            MessageId(0x73), unhexlify(self.hex)
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
