from tests import _LOGGER, set_log_levels
import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_im_info
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetImInfo(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "0260"
        super(TestGetImInfo, self).base_setup(
            MessageId.GET_IM_INFO, unhexlify(self.hex)
        )
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
