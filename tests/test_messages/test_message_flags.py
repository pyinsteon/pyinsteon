"""Test message flags data type."""
import unittest

from pyinsteon.constants import MessageFlagType
from pyinsteon.protocol.messages.message_flags import MessageFlags, create
from tests import _LOGGER, set_log_levels


class TestMessageFlags(unittest.TestCase):

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

        self.complex = MessageFlags(0x77)  # All Link Cleanup, extended, 1, 3
        self.assigned_message_flag = MessageFlags(0x00)
        self.assigned_message_flag.message_type = MessageFlagType.ALL_LINK_CLEANUP_NAK

        self.assigned_extended = MessageFlags(0x00)
        self.assigned_extended.extended = True

        self.assigned_hops = MessageFlags(0x00)
        self.assigned_hops.hops_left = 2
        self.assigned_hops.max_hops = 3

        self.create = create(MessageFlagType.ALL_LINK_CLEANUP, True, 3, 2)
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)

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

    def test_bytes(self):
        assert bytes(self.complex) == bytes([0x77])

    def test_assign_message_flags(self):
        test_val = MessageFlagType.ALL_LINK_CLEANUP_NAK
        assert self.assigned_message_flag.message_type == test_val

    def test_assign_extended(self):
        assert self.assigned_extended.extended == True

    def test_assign_hops_left(self):
        assert self.assigned_hops.hops_left == 2

    def test_assign_max_hops(self):
        assert self.assigned_hops.max_hops == 3

    def test_created(self):
        assert str(self.create) == "{'message_type': 'all_link_cleanup', 'extended': True, 'hops_left': 3, 'max_hops': 2}"

    def test_complex_direct_ne(self):
        assert self.complex != self.direct


if __name__ == '__main__':
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)
