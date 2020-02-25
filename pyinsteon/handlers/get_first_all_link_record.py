"""Modem command to get next ALDB record."""
# pylint: disable=no-self-use
import logging

from . import ack_handler, nak_handler
from ..topics import GET_FIRST_ALL_LINK_RECORD
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetFirstAllLinkRecordHandler(OutboundHandlerBase):
    """Handle Get First All Link Record commands."""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        super().__init__(topic=GET_FIRST_ALL_LINK_RECORD)
        _LOGGER.debug("Setup GetFirstAllLinkRecordHandler")

    @ack_handler()
    def handle_ack(self):
        """Handle the ACK message and return True."""

    @nak_handler
    def handle_nak(self, **kwargs):
        """Receive the NAK message and return False."""
