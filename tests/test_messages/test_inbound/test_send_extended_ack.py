import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MESSAGE_ACK, MESSAGE_NAK, MessageId
from pyinsteon.protocol.messages.inbound import Inbound, create
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.protocol.messages.user_data import UserData
from tests import _LOGGER, set_log_levels
from tests.utils import hex_to_inbound_message


class TestExtendedSendAck(unittest.TestCase):
    def setUp(self):
        self.buffer = True
        self.hex_data = "0262010203140506a1a2a3a4a5a6a7a8a9aaabacadae06"
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.message_id = MessageId.SEND_EXTENDED.value
        self.address = Address("010203")
        self.flags = MessageFlags(0x14)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.user_data = UserData(unhexlify("a1a2a3a4a5a6a7a8a9aaabacadae"))
        self.ack = MESSAGE_ACK

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

    def test_user_data(self):
        assert self.msg.user_data == self.user_data

    def test_ack(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        assert len(self.msg) == 23


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
