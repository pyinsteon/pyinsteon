"""Modem command to get next ALDB record."""
import logging

from ..constants import ResponseStatus
from ..topics import GET_NEXT_ALL_LINK_RECORD
from . import nak_handler
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetNextAllLinkRecordHandler(OutboundHandlerBase):
    """Handle Get Next All Link Record commands."""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        super().__init__(topic=GET_NEXT_ALL_LINK_RECORD)

    @nak_handler
    async def async_handle_nak(self):
        """Receive the NAK message and return False."""
        await self._message_response.put(ResponseStatus.FAILURE)
