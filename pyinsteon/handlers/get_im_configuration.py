"""Modem command to get the IM configuration."""
import logging

from pyinsteon.constants import ResponseStatus

from ..topics import GET_IM_CONFIGURATION
from . import ack_handler
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetImConfigurationHandler(OutboundHandlerBase):
    """Handle Get IM Configuration commands."""

    def __init__(self):
        """Init the GetImConfigurationHandler class."""
        super().__init__(topic=GET_IM_CONFIGURATION)

    # pylint: disable=arguments-differ
    @ack_handler
    async def async_handle_ack(
        self, disable_auto_linking, monitor_mode, auto_led, deadman
    ):
        """Receive the ACK message and return True."""
        await self._message_response.put(ResponseStatus.SUCCESS)
        self._call_subscribers(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )
