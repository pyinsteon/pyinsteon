from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.protocol.messages.inbound import Inbound, create
from pyinsteon.constants import MessageId, MESSAGE_ACK, MESSAGE_NAK
from tests.utils import hex_to_inbound_message


class TestStandardSendAck(unittest.TestCase):
    def setUp(self):
        self.buffer = False
        self.hex_data = "026201020304050615"
        self.bytes_data = unhexlify(self.hex_data)
        self.message_id = MessageId.SEND_STANDARD.value
        self.address = Address("010203")
        self.flags = MessageFlags(0x04)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.ack = MESSAGE_NAK

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_data)
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_address(self):
        assert self.msg.address == self.address

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_ack(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        msg_len = len(self.msg)
        assert len(self.msg) == 9


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)
