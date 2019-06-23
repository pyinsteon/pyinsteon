"""Manage outbound ON command to a device."""
from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import PRODUCT_DATA_REQUEST


class ProductDataRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, PRODUCT_DATA_REQUEST)

    #pylint: disable=arguments-differ
    def send(self):
        """Send the OFF command."""
        super().send()

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the OFF command async."""
        return await super().async_send()

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the OFF response direct ACK."""
        if user_data is None:
            return
        product_bytes = bytearray([user_data['d2'], user_data['d3'], user_data['d4']])
        product_id = int.from_bytes(product_bytes, byteorder='big')
        cat = user_data['d5']
        subcat = user_data['d6']
        self._call_subscribers(product_id=product_id, cat=cat, subcat=subcat)
