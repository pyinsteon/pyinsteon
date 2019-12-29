"""Receive an X10 message."""

from ...topics import X10_RECEIVED
from ..inbound_base import InboundHandlerBase
from .. import inbound_handler


class X10Received(InboundHandlerBase):
    """Receive an X10 message."""

    def __init__(self):
        """Init the X10Received class."""
        super().__init__(topic=X10_RECEIVED)

    @inbound_handler
    def handle_command(self, raw_x10, flags):
        """Handle inbound X10 commands."""
        self._call_subscribers(raw_x10=raw_x10, flags=flags)
