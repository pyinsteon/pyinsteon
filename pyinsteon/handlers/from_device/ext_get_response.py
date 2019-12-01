"""Manage inbound ON command from device."""
from .. import inbound_handler
from ..inbound_base import InboundHandlerBase
from ...topics import EXTENDED_GET_SET


class ExtendedGetResponseHandler(InboundHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address):
        """Init the OffInbound class."""
        topic = '{}.{}.direct'.format(address.id, EXTENDED_GET_SET)
        super().__init__(topic)

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data):
        """Handle the Extended Get response from a device."""
        from collections import OrderedDict
        if user_data is None or user_data['d2'] != 0x01:
            return
        data = OrderedDict()
        for i in range(3, 15):
            data['data{}'.format(i)] = user_data['d{}'.format(i)]
        self._call_subscribers(group=user_data['d1'], data=data)
