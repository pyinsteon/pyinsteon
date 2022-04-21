"""Test Manage All-Link Record."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.constants import ManageAllLinkRecordAction, MessageId
from pyinsteon.data_types.all_link_record_flags import AllLinkRecordFlags

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import manage_all_link_record  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestManageAllLinkRecord(unittest.TestCase, OutboundBase):
    """Test Manage All-Link Record."""

    def setUp(self):
        """Test set up."""
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
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_action(self):
        """Test action."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.action == self.action

    @async_case
    async def test_flags(self):
        """Test flags."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.flags == self.flags

    @async_case
    async def test_group(self):
        """Test group."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.group == self.group

    @async_case
    async def test_target(self):
        """Test target."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.target == self.target

    @async_case
    async def test_data1(self):
        """Test data1."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.data1 == self.data1

    @async_case
    async def test_data2(self):
        """Test data2."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.data2 == self.data2

    @async_case
    async def test_data3(self):
        """Test data3."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.data3 == self.data3


if __name__ == "__main__":
    unittest.main()
