"""Test Set Host Device Category."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import DeviceCategory, MessageId
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import set_host_dev_cat
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSetHostDeviceCategory(unittest.TestCase, OutboundBase):
    """Test Set Host Device Category."""

    def setUp(self):
        """Test set up."""
        self.hex = "0266030405"
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.SET_HOST_DEV_CAT
        self.cat = DeviceCategory(0x03)
        self.subcat = int(0x04)
        self.firmware = int(0x05)

        kwargs = {"cat": self.cat, "subcat": self.subcat, "firmware": self.firmware}

        super(TestSetHostDeviceCategory, self).base_setup(
            self.message_id, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_cat(self):
        """Test cat."""
        assert self.msg.cat == self.cat

    def test_subcat(self):
        """Test subcat."""
        assert self.msg.subcat == self.subcat

    def test_firmware(self):
        """Test firmware."""
        assert self.msg.firmware == self.firmware


if __name__ == "__main__":
    unittest.main()
