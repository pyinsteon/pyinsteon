"""Manage outbound ON command to a device."""
from ... import pub
from .. import status_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import STATUS_REQUEST

class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST)

    #pylint: disable=arguments-differ, useless-super-delegation
    def send(self, status_type: int = 0):
        """Send the ON command."""
        super().send(status_type=status_type)

    #pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self, status_type: int = 0):
        """Send the ON command async."""
        return await super().async_send(status_type=status_type)

    @status_handler
    def handle_direct_ack(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd2 = kwargs.get('cmd2')
        if cmd2 is not None:
            self._call_subscribers(status=cmd2)
