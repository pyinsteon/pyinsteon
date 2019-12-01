"""Manage outbound ON command to a device."""

from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import ON_FAST


class OnFastCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnFastCommand class."""
        topic = '{}.{}'.format(ON_FAST, group)
        super().__init__(address, topic)
        # put the following commands in a subclass!
        self._group = group
        # self._subscriber_topic = '{}.{}'.format(self._subscriber_topic, self._group)

    #pylint: disable=arguments-differ
    def send(self, on_level=0xff):
        """Send the ON FAST command."""
        super().send(on_level=0xff, group=self._group)

    #pylint: disable=arguments-differ
    async def async_send(self, on_level=0xff):
        """Send the ON FAST command async."""
        return await super().async_send(on_level=on_level, group=self._group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the ON FAST response direct ACK."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xff)
