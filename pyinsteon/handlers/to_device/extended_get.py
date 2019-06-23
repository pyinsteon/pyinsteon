"""Handle sending a read request for ALDB records."""
import logging

from .. import direct_ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)

class ExtendedGetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(address, EXTENDED_GET_SET)

    #pylint: disable=arguments-differ
    def send(self, group=0):
        """Send Get Operating Flags message."""
        super().send(data1=group)

    #pylint: disable=arguments-differ
    async def async_send(self, group=0):
        """Send Get Operating Flags message asyncronously."""
        return await super().async_send(data1=group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        from collections import OrderedDict
        if not user_data or not user_data['d2'] == 0x01:
            return
        data = OrderedDict()
        for i in range(1, 15):
            data['data{}'.format(i)] = user_data['d{}'.format(i)]
        self._call_subscribers(data=data)
