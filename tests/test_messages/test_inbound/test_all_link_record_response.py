import sys
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.all_link_record_flags import \
    AllLinkRecordFlags
from tests import _LOGGER, set_log_levels
from tests.utils import hex_to_inbound_message


class TestAllLinkRecordResponse(unittest.TestCase):
    def setUp(self):
        self.hex = "0257030405060708090a"
        self.message_id = MessageId(0x57)
        self.flags = AllLinkRecordFlags(0x03)
        self.group = int(0x04)
        self.address = Address("050607")
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0A)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)
