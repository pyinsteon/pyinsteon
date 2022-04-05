"""Test the modem config flags."""
import unittest

from pyinsteon.data_types.im_config_flags import IMConfigurationFlags, create
from tests import set_log_levels


class TestIMConfigFlags(unittest.TestCase):
    """Test the modem config flags."""

    def setUp(self):
        """Set up the tests for TestIMConfigFlags."""
        self.all_on_create = create(True, True, True, True)
        self.all_off_create = create(False, False, False, False)

        self.all_set = IMConfigurationFlags(0xF0)
        self.all_off = IMConfigurationFlags(0x00)

        self.auto_link = IMConfigurationFlags(0x80)
        self.monitor_mode = IMConfigurationFlags(0x40)
        self.auto_led = IMConfigurationFlags(0x20)
        self.disable_deadman = IMConfigurationFlags(0x10)

        self.auto_link_create = create(True, False, False, False)
        self.monitor_mode_create = create(False, True, False, False)
        self.auto_led_create = create(False, False, True, False)
        self.disable_deadman_create = create(False, False, False, True)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_all_on_create_bytes(self):
        """Test all on create bytes."""
        assert bytes(self.all_on_create) == bytes([0xF0])

    def test_all_off_create_bytes(self):
        """Test all off create bytes."""
        assert bytes(self.all_off_create) == bytes([0x00])

    def test_all_set_bytes(self):
        """Test all set bytes."""
        assert bytes(self.all_set) == bytes([0xF0])

    def test_all_off_bytes(self):
        """Test all off bytes."""
        assert bytes(self.all_off) == bytes([0x00])

    def test_auto_link(self):
        """Test auto link."""
        assert bytes(self.auto_link) == bytes([0x80])
        assert self.auto_link.is_auto_link
        assert not self.auto_link.is_monitor_mode
        assert not self.auto_link.is_auto_led
        assert not self.auto_link.is_disable_deadman

    def test_auto_link_create(self):
        """Test auto link create."""
        assert bytes(self.auto_link_create) == bytes([0x80])
        assert self.auto_link_create.is_auto_link
        assert not self.auto_link_create.is_monitor_mode
        assert not self.auto_link_create.is_auto_led
        assert not self.auto_link_create.is_disable_deadman

    def test_monitor_mode(self):
        """Test monitor mode."""
        assert bytes(self.monitor_mode) == bytes([0x40])
        assert not self.monitor_mode.is_auto_link
        assert self.monitor_mode.is_monitor_mode
        assert not self.monitor_mode.is_auto_led
        assert not self.monitor_mode.is_disable_deadman

    def test_monitor_mode_create(self):
        """Test monitor mode create."""
        assert bytes(self.monitor_mode_create) == bytes([0x40])
        assert not self.monitor_mode_create.is_auto_link
        assert self.monitor_mode_create.is_monitor_mode
        assert not self.monitor_mode_create.is_auto_led
        assert not self.monitor_mode_create.is_disable_deadman

    def test_auto_led(self):
        """Test auto LED."""
        assert bytes(self.auto_led) == bytes([0x20])
        assert not self.auto_led.is_auto_link
        assert not self.auto_led.is_monitor_mode
        assert self.auto_led.is_auto_led
        assert not self.auto_led.is_disable_deadman

    def test_auto_led_create(self):
        """Test create auto LED."""
        assert bytes(self.auto_led_create) == bytes([0x20])
        assert not self.auto_led_create.is_auto_link
        assert not self.auto_led_create.is_monitor_mode
        assert self.auto_led_create.is_auto_led
        assert not self.auto_led_create.is_disable_deadman

    def test_disable_deadman(self):
        """Test disable deadman."""
        assert bytes(self.disable_deadman) == bytes([0x10])
        assert not self.disable_deadman.is_auto_link
        assert not self.disable_deadman.is_monitor_mode
        assert not self.disable_deadman.is_auto_led
        assert self.disable_deadman.is_disable_deadman

    def test_disable_deadman_create(self):
        """Test disable deadman create."""
        assert bytes(self.disable_deadman_create) == bytes([0x10])
        assert not self.disable_deadman_create.is_auto_link
        assert not self.disable_deadman_create.is_monitor_mode
        assert not self.disable_deadman_create.is_auto_led
        assert self.disable_deadman_create.is_disable_deadman


if __name__ == "__main__":
    unittest.main()
