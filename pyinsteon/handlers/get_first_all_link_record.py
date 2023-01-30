"""Modem command to get next ALDB record."""
# pylint: disable=no-self-use
import logging

from . import ack_handler, nak_handler
from ..constants import ResponseStatus
from ..topics import GET_FIRST_ALL_LINK_RECORD
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetFirstAllLinkRecordHandler(OutboundHandlerBase):
    """Handle Get First All Link Record commands."""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        super().__init__(topic=GET_FIRST_ALL_LINK_RECORD)
        _LOGGER.debug("Setup GetFirstAllLinkRecordHandler")

    @ack_handler
    async def async_handle_ack(self):
        """Handle the ACK response from the modem."""
        return await self._async_handle_ack()

    @nak_handler
    async def async_handle_nak(self):
        """Handle the ACK response from the modem."""
        await self._message_response.put(ResponseStatus.FAILURE)
