"""Receive an All-Link record for an Insteon Modem."""

import logging

from . import inbound_handler
from ..address import Address
from ..constants import AllLinkMode
from ..topics import ALL_LINKING_COMPLETED
from .inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class AllLinkCompletedHandler(InboundHandlerBase):
    """Receive an All-Link Completed message for an Insteon Modem."""

    def __init__(self):
        """Init the AllLinkRecordResponse class."""
        super().__init__(ALL_LINKING_COMPLETED)

    @inbound_handler
    def handle_response(
        self,
        mode: AllLinkMode,
        group: int,
        target: Address,
        cat: int,
        subcat: int,
        firmware: int,
    ):
        """Recieve an all link record."""
        self._call_subscribers(
            mode=mode,
            group=group,
            target=target,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
        )
