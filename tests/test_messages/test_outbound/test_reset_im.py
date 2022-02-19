"""Test Reset IM."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import reset_im  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestResetIm(unittest.TestCase, OutboundBase):
    """Test Reset IM."""

    def setUp(self):
        """Test set up."""
        self.hex = "0267"
        super(TestResetIm, self).base_setup(MessageId.RESET_IM, unhexlify(self.hex))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
