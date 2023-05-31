"""Modem command to get the IM configuration."""
import logging

from . import ack_handler, nak_handler
from ..data_types.im_config_flags import IMConfigurationFlags
from ..topics import MODEM, SET_IM_CONFIGURATION
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class SetImConfigurationHandler(OutboundHandlerBase):
    """Handle Set IM Configuration commands."""

    arg_spec = {
        "disable_auto_linking": "bool - Indicates if auto-linking has been disabled.",
        "monitor_mode": "bool - Indicates of monitor mode has been enabled.",
        "auto_led": "bool - Indicates if the LED is set to auto mode.",
        "deadman": "bool - Indicates if deadman mode is enabled.",
    }

    def __init__(self):
        """Init the GetImConfigurationHandler class."""
        super().__init__(topic=SET_IM_CONFIGURATION, address=MODEM)

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        disable_auto_linking: bool,
        monitor_mode: bool,
        auto_led: bool,
        deadman: bool,
    ):
        """Send the Set IM Configuration command."""
        return await super().async_send(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )

    @ack_handler
    async def async_handle_ack(self, flags: IMConfigurationFlags):
        """Receive the ACK message and return True."""
        await self._async_handle_ack()
        self._call_subscribers(
            disable_auto_linking=flags.is_auto_link,
            monitor_mode=flags.is_monitor_mode,
            auto_led=flags.is_auto_led,
            deadman=flags.is_disable_deadman,
        )

    @nak_handler
    async def async_handle_nak(self, flags: IMConfigurationFlags):
        """Receive the NAK message and return True."""
        await self._async_handle_nak()
