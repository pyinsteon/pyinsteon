"""Test message flags data type."""
import unittest

from pyinsteon.constants import MessageFlagType
from pyinsteon.data_types.message_flags import MessageFlags
from tests import set_log_levels


class TestMessageFlags(unittest.TestCase):
    """Test message flags data type."""

    def setUp(self):
        """Test set up."""
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

        self.create = MessageFlags.create(MessageFlagType.ALL_LINK_CLEANUP, True, 3, 2)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_direct(self):
        """Test direct."""
        assert self.direct.is_direct

    def test_direct_not_broadcast(self):
        """Test direct is not broacast."""
        assert not self.direct.is_broadcast

    def test_direct_not_direct_ack(self):
        """Test direct is not direct ack."""
        assert not self.direct.is_direct_ack

    def test_direct_not_direct_nak(self):
        """Test direct is not direct nak."""
        assert not self.direct.is_direct_nak

    def test_direct_not_all_link_cleanup(self):
        """Test direct is not all link cleanup."""
        assert not self.direct.is_all_link_cleanup

    def test_direct_not_all_link_broadcast(self):
        """Test direct is not all link broadcast."""
        assert not self.direct.is_all_link_broadcast

    def test_direct_not_all_link_cleanup_ack(self):
        """Test direct is not all link cleanup ack."""
        assert not self.direct.is_all_link_cleanup_ack

    def test_direct_not_all_link_cleanup_nak(self):
        """Test direct is not all link clean up nak."""
        assert not self.direct.is_all_link_cleanup_nak

    def test_broadcast(self):
        """Test broadcast."""
        assert self.broadcast.is_broadcast

    def test_extended(self):
        """Test extended."""
        assert self.extended.is_extended

    def test_direct_not_extended(self):
        """Test direct is not extended."""
        assert not self.direct.is_extended

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.complex) == bytes([0x77])

    def test_assign_message_flags(self):
        """Test assign message flags."""
        test_val = MessageFlagType.ALL_LINK_CLEANUP_NAK
        assert self.assigned_message_flag.message_type == test_val

    def test_assign_extended(self):
        """Test assign extended."""
        assert self.assigned_extended.extended

    def test_assign_hops_left(self):
        """Test assign hops left."""
        assert self.assigned_hops.hops_left == 2

    def test_assign_max_hops(self):
        """Test assing max hops."""
        assert self.assigned_hops.max_hops == 3

    def test_created(self):
        """Test created."""
        assert (
            str(self.create)
            == "{'message_type': 'all_link_cleanup', 'extended': True, 'hops_left': 3, 'max_hops': 2}"
        )

    def test_complex_direct_ne(self):
        """Test complex direct not equal to."""
        assert self.complex != self.direct


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)
