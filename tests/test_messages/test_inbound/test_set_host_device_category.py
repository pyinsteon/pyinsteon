import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, DeviceCategory, MessageId
from tests import _LOGGER, set_log_levels
from tests.utils import hex_to_inbound_message


class TestSetHostDeviceCategory(unittest.TestCase):
    def setUp(self):
        self.hex = "0266030405"
        self.hex_ack = "026603040506"
        self.message_id = MessageId(0x66)
        self.cat = DeviceCategory(0x03)
        self.subcat = int(0x04)
        self.firmware = int(0x05)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex_ack)
