"""Receive an All-Link record for an Insteon Modem."""

import logging

from . import inbound_handler
from ..address import Address
from ..constants import AllLinkMode
from ..topics import ALL_LINKING_COMPLETED, MODEM
from .inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class AllLinkCompletedHandler(InboundHandlerBase):
    """Receive an All-Link Completed message for an Insteon Modem."""

    arg_spec = {
        "link_mode": "AllLinkMode - All-Link mode (add or delete)",
        "group": "int - All-Link group number.",
        "target": "Address - Address of the device.",
        "cat": "int - Category of the device.",
        "subcat": "int - Subcategory of the device.",
        "firmware": "int - Firmware version of the device.",
    }

    def __init__(self):
        """Init the AllLinkRecordResponse class."""
        super().__init__(ALL_LINKING_COMPLETED, address=MODEM)

    @inbound_handler
    def handle_response(
        self,
        link_mode: AllLinkMode,
        group: int,
        target: Address,
        cat: int,
        subcat: int,
        firmware: int,
    ):
        """Recieve an all link record."""
        self._call_subscribers(
            link_mode=link_mode,
            group=group,
            target=target,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
        )
