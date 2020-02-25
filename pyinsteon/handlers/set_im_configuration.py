"""Modem command to get the IM configuration."""
import logging

from . import ack_handler
from ..topics import SET_IM_CONFIGURATION
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class SetImConfigurationHandler(OutboundHandlerBase):
    """Handle Set IM Configuration commands."""

    def __init__(self):
        """Init the GetImConfigurationHandler class."""
        super().__init__(topic=SET_IM_CONFIGURATION)

    # pylint: disable=arguments-differ
    def send(
        self,
        disable_auto_linking: bool,
        monitor_mode: bool,
        auto_led: bool,
        deadman: bool,
    ):
        """Send the Set IM Configuration command."""
        super().send(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )

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

    @ack_handler(wait_response=False)
    def handle_ack(self, disable_auto_linking, monitor_mode, auto_led, deadman):
        """Receive the ACK message and return True."""
