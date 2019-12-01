"""Manage outbound ON command to a device."""

from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import ON

class OnLevelCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        topic = '{}.{}'.format(ON, group)
        super().__init__(address, topic)
        # put the following commands in a subclass!
        self._group = group
        # self._subscriber_topic = '{}.{}'.format(self._subscriber_topic, self._group)

    #pylint: disable=arguments-differ
    def send(self, on_level=0xff):
        """Send the ON command."""
        super().send(on_level=on_level, group=self._group)

    #pylint: disable=arguments-differ
    async def async_send(self, on_level=0xff):
        """Send the ON command async."""
        return await super().async_send(on_level=on_level, group=self._group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the ON response direct ACK."""
        if self._response_lock.locked():
            self._call_subscribers(on_level=cmd2 if cmd2 else 0xff)
