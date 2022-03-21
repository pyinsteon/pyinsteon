"""Manage inbound ON command from device."""
import logging

from ...constants import MessageFlagType
from ...topics import EXTENDED_GET_RESPONSE
from .. import inbound_handler
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedGetResponseHandler(InboundHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address):
        """Init the OffInbound class."""
        super().__init__(
            topic=EXTENDED_GET_RESPONSE,
            address=address,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Extended Get response from a device."""
        data = {}
        for item in range(3, 15):
            data[f"data{item}"] = user_data[f"d{item}"]
        self._call_subscribers(group=user_data["d1"], data=data)
