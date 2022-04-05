"""Test Manage All-Link Record."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import AckNak, ManageAllLinkRecordAction, MessageId
from pyinsteon.data_types.all_link_record_flags import AllLinkRecordFlags
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestManageAllLinkRecord(unittest.TestCase):
    """Test Manage All-Link Record."""

    def setUp(self):
        """Set up test."""
        self.hex = "026F400405060708090a0b"
        self.hex_ack = "026F400405060708090a0b06"
        self.message_id = MessageId(0x6F)
        self.action = ManageAllLinkRecordAction(0x40)
        self.flags = AllLinkRecordFlags(0x04)
        self.group = int(0x05)
        self.address = Address("060708")
        self.data1 = int(0x09)
        self.data2 = int(0x0A)
        self.data3 = int(0x0B)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test ID."""
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        """Test ACK/NAK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex_ack)
