"""Modem command to get next ALDB record."""
# pylint: disable=no-self-use
import logging

from ..constants import ResponseStatus
from ..topics import READ_EEPROM
from . import ack_handler, nak_handler
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReadEepromHandler(OutboundHandlerBase):
    """Handle Read EEPROM commands."""

    def __init__(self):
        """Init the ReadEepromHandler class."""
        super().__init__(topic=READ_EEPROM)
        _LOGGER.debug("Setup ReadEepromHandler")

    # pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int):
        """Send the Read from EEPROM message."""
        mem_array = mem_addr.to_bytes(2, "big")

        return await super().async_send(mem_hi=mem_array[0], mem_low=mem_array[1] - 7)

    # pylint: disable=arguments-differ
    @ack_handler
    async def async_handle_ack(self, mem_hi: int, mem_low: int):
        """Send the Read from EEPROM message."""
        await super().async_handle_ack(mem_hi=mem_hi, mem_low=mem_low)

    @nak_handler
    async def async_handle_nak(self, mem_hi: int, mem_low: int):
        """Receive the NAK message and return False."""
        await self._message_response.put(ResponseStatus.FAILURE)
