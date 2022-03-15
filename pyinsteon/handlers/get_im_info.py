"""Modem command to get next ALDB record."""
import logging

from pyinsteon.constants import ResponseStatus

from ..topics import GET_IM_INFO
from . import ack_handler
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetImInfoHandler(OutboundHandlerBase):
    """Handle Get IM Info commands."""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        super().__init__(topic=GET_IM_INFO)

    # pylint: disable=arguments-differ
    @ack_handler
    async def async_handle_ack(self, address, cat, subcat, firmware):
        """Receive the ACK message and return True."""
        await self._message_response.put(ResponseStatus.SUCCESS)
        self._call_subscribers(
            address=address, cat=cat, subcat=subcat, firmware=firmware
        )
