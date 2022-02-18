"""Test Get IM Info."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import get_im_info  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetImInfo(unittest.TestCase, OutboundBase):
    """Test Get IM Info."""

    def setUp(self):
        """Test set up."""
        self.hex = "0260"
        super(TestGetImInfo, self).base_setup(
            MessageId.GET_IM_INFO, unhexlify(self.hex)
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
