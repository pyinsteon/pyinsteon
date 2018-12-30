from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, MESSAGE_ACK, MESSAGE_NAK
from pyinsteon.messages.message_flags import MessageFlags

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStandardSendAck(unittest.TestCase):

    def setUp(self):
        self.direct = MessageFlags(0x00)
        self.broadcast = MessageFlags(0x80)
        self.direct_ack = MessageFlags(0x20)
        self.direct_nak = MessageFlags(0xA0)
        self.all_link_cleanup = MessageFlags(0x40)
        self.all_link_broadcast = MessageFlags(0xC0)
        self.all_link_cleanup_ack = MessageFlags(0x60)
        self.all_link_cleanup_nak = MessageFlags(0xE0)

        self.extended = MessageFlags(0x10)
        self.hops = MessageFlags(0x07)  # Hops left 1, max hops 3

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _LOGGER.setLevel(logging.DEBUG)

    def test_direct(self):
        assert self.direct.is_direct

    def test_direct_not_broadcast(self):
        assert not self.direct.is_broadcast

    def test_direct_not_direct_ack(self):
        assert not self.direct.is_direct_ack

    def test_direct_not_direct_nak(self):
        assert not self.direct.is_direct_nak

    def test_direct_not_all_link_cleanup(self):
        assert not self.direct.is_all_link_cleanup

    def test_direct_not_all_link_broadcast(self):
        assert not self.direct.is_all_link_broadcast

    def test_direct_not_all_link_cleanup_ack(self):
        assert not self.direct.is_all_link_cleanup_ack

    def test_direct_not_all_link_cleanup_nak(self):
        assert not self.direct.is_all_link_cleanup_nak

    def test_broadcast(self):
        assert self.broadcast.is_broadcast

    def test_extended(self):
        assert self.extended.is_extended

    def test_direct_not_extended(self):
        assert not self.direct.is_extended

    # def test_bytes(self):
    #     assert self.msg.bytes == self.bytes_data

    # def test_hex(self):
    #     assert self.msg.hex == self.hex_data


if __name__ == '__main__':
    _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)