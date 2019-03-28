"""Modem command to get next ALDB record."""
import logging

from .outbound_base import OutboundHandlerBase
from ..topics import GET_FIRST_ALL_LINK_RECORD
from . import nak_handler, ack_handler


_LOGGER = logging.getLogger(__name__)


class GetFirstAllLinkRecordHandler(OutboundHandlerBase):
    """Handle Get First All Link Record commands"""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        super().__init__(topic=GET_FIRST_ALL_LINK_RECORD)
        _LOGGER.debug('Setup GetFirstAllLinkRecordHandler')

    @ack_handler()
    def handle_ack(self):
        """Receive the ACK message and return True."""
        _LOGGER.debug('Got ACK')

    @nak_handler
    def handle_nak(self):
        """Receive the NAK message and return False."""
        _LOGGER.debug('Got NAK')
