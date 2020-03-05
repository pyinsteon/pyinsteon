"""Test Set IM Configuration."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.im_config_flags import IMConfigurationFlags
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import set_im_configuration
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSetImConfiguration(unittest.TestCase, OutboundBase):
    """Test Set IM Configuration."""

    def setUp(self):
        """Test set up."""
        self.hex = "026B30"
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.SET_IM_CONFIGURATION
        self.flags = IMConfigurationFlags(0x30)

        kwargs = {
            "disable_auto_linking": self.flags.is_auto_link,
            "monitor_mode": self.flags.is_monitor_mode,
            "auto_led": self.flags.is_auto_led,
            "deadman": self.flags.is_disable_deadman,
        }

        super(TestSetImConfiguration, self).base_setup(
            self.message_id, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_flags(self):
        """Test flags."""
        assert self.msg.flags == self.flags


if __name__ == "__main__":
    unittest.main()
