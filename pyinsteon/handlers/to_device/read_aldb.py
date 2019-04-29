"""Handle sending a read request for ALDB records."""
import asyncio
import logging
from .direct_command import DirectCommandHandlerBase
from ...topics import EXTENDED_READ_WRITE_ALDB
from .. import ack_handler, direct_ack_handler
from pyinsteon.address import Address


_LOGGER = logging.getLogger(__name__)

class ReadALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(address, EXTENDED_READ_WRITE_ALDB)

    #pylint: disable=arguments-differ
    def send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message."""
        asyncio.ensure_future(self.async_send(mem_addr=mem_addr, num_recs=num_recs))

    #pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message asyncronously."""
        await super().async_send(action=0x00, mem_addr=mem_addr, num_recs=num_recs)

    @ack_handler(wait_response=True)
    def handle_ack(self, cmd2, user_data):
        """Handle the message ACK.

            Overriding the standard ACK handler to ensure we do not
            wait for the direct ACK message. This message should
            return True once the message is sent rather than after the
            Direct ACK.
        """

    @direct_ack_handler
    def handle_direct_ack(self, cmd2, target, user_data):
        """Handle an ALDB read or a write response."""
        from ...aldb.aldb_record import create_from_userdata
        _LOGGER.debug('ALDB Read Direct ACK received')
        if user_data:
            is_response = user_data['d2'] == 0x01
            record = create_from_userdata(user_data)
            self._call_subscribers(is_response=is_response, record=record)
