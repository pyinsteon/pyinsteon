"""Manage inbound ON command from device."""
import logging
from collections import OrderedDict

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType
from ...topics import EXTENDED_GET_RESPONSE
from ...utils import build_topic
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedGetResponseHandler(InboundHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address):
        """Init the OffInbound class."""
        self._address = Address(address)
        super().__init__(
            topic=EXTENDED_GET_RESPONSE,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),  # Force address
            topic=EXTENDED_GET_RESPONSE,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Extended Get response from a device."""
        data = OrderedDict()
        for item in range(3, 15):
            data["data{}".format(item)] = user_data["d{}".format(item)]
        self._call_subscribers(group=user_data["d1"], data=data)
