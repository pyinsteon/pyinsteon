import sys
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import ManageAllLinkRecordAction, MessageId
from pyinsteon.protocol.messages.all_link_record_flags import \
    AllLinkRecordFlags
from pyinsteon.protocol.messages.outbound import manage_all_link_record
from tests import _LOGGER, set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestManageAllLinkRecord(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "026F400405060708090a0b"
        self.action = ManageAllLinkRecordAction(0x40)
        self.flags = AllLinkRecordFlags(0x04)
        self.group = int(0x05)
        self.target = Address("060708")
        self.data1 = int(0x09)
        self.data2 = int(0x0A)
        self.data3 = int(0x0B)

        kwargs = {
            "action": self.action,
            "flags": self.flags,
            "group": self.group,
            "target": self.target,
            "data1": self.data1,
            "data2": self.data2,
            "data3": self.data3,
        }

        super(TestManageAllLinkRecord, self).base_setup(
            MessageId.MANAGE_ALL_LINK_RECORD, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_action(self):
        assert self.msg.action == self.action

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_group(self):
        assert self.msg.group == self.group

    def test_target(self):
        assert self.msg.target == self.target

    def test_data1(self):
        assert self.msg.data1 == self.data1

    def test_data2(self):
        assert self.msg.data2 == self.data2

    def test_data3(self):
        assert self.msg.data3 == self.data3


if __name__ == "__main__":
    unittest.main()
