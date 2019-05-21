"""Manage outbound ON command to a device."""

from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import ON_FAST


class OnFastCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnFastCommand class."""
        super().__init__(address, ON_FAST)

    #pylint: disable=arguments-differ
    def send(self, on_level=0xff, group=0):
        """Send the ON FAST command."""
        super().send(on_level=0xff, group=group)

    #pylint: disable=arguments-differ
    async def async_send(self, on_level=0xff, group=0):
        """Send the ON FAST command async."""
        return await super().async_send(on_level=0xff, group=group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd2, target, user_data):
        """Handle the ON FAST response direct ACK."""
        group = 0
        if user_data:
            group = user_data.get('d1')
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xff, group=group)
