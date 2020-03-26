"""Modem command to get the IM configuration."""
import logging

from . import ack_handler
from ..topics import GET_IM_CONFIGURATION
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetImConfigurationHandler(OutboundHandlerBase):
    """Handle Get IM Configuration commands."""

    def __init__(self):
        """Init the GetImConfigurationHandler class."""
        super().__init__(topic=GET_IM_CONFIGURATION)

    @ack_handler()
    def handle_ack(self, disable_auto_linking, monitor_mode, auto_led, deadman):
        """Receive the ACK message and return True."""

        self._call_subscribers(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )
