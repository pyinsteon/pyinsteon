"""Test converting a topic to a message."""

import unittest
from binascii import unhexlify

from pyinsteon.protocol.messages.inbound import create
from pyinsteon.protocol.msg_to_topic import convert_to_topic


class TestTopicFromMsg(unittest.TestCase):
    """Test converting message to a topic."""

    def setUp(self):
        """Setup the tests."""
        self.hex_data = "0250010203040506272829"
        # address: 01.02.03
        # target: 04.05.06
        # flags: 27 (direct_ack)
        # cmd1: 28 (set_address_msb)
        # cmd2: 29
        self.bytes_data = bytearray(unhexlify(self.hex_data))

        (self.msg, _) = create(self.bytes_data)
        for (self.topic, self.kwargs) in convert_to_topic(self.msg):
            pass

    def test_topic(self):
        """The topic is correct."""
        assert self.topic == "010203.set_address_msb.direct_ack"

    def test_cmd2(self):
        """Test cmd2 is correct in kwargs."""
        assert self.kwargs.get("cmd2") == 0x29


if __name__ == "__main__":
    unittest.main()
