from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.protocol.messages.inbound import Inbound, create
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.protocol.messages.user_data import UserData
from tests.utils import hex_to_inbound_message


class TestExtendedSendAck(unittest.TestCase):
    def setUp(self):
        self.hex_data = "0251112233445566778899a1a2a3a4a5a6a7a8a9aaabacadae"
        self.message_id = 0x51
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.address = Address("112233")
        self.target = Address("445566")
        self.flags = MessageFlags(0x77)
        self.cmd1 = int(0x88)
        self.cmd2 = int(0x99)
        self.user_data = UserData(unhexlify("a1a2a3a4a5a6a7a8a9aaabacadae"))

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

    def test_target(self):
        assert self.msg.target == self.target

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_user_data(self):
        assert self.msg.user_data == self.user_data

    def test_bytes(self):
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        assert len(self.msg) == 25


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
