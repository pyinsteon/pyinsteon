"""Manage inbound ON command from device."""
from .. import inbound_handler
from ..inbound_base import InboundHandlerBase
from ...topics import EXTENDED_GET_SET
from ...address import Address
from ...utils import build_topic
from ...constants import MessageFlagType


class ExtendedGetResponseHandler(InboundHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address):
        """Init the OffInbound class."""
        self._address = Address(address)
        super().__init__(
            topic=EXTENDED_GET_SET,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="subscriber.{}".format(self._address), # Force address
            topic="ext_get_response",
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data):
        """Handle the Extended Get response from a device."""
        from collections import OrderedDict

        if user_data is None or user_data["d2"] != 0x01:
            return
        data = OrderedDict()
        for i in range(3, 15):
            data["data{}".format(i)] = user_data["d{}".format(i)]
        self._call_subscribers(group=user_data["d1"], data=data)
