"""Manage outbound ON command to a device."""
from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import OFF_FAST


class OffFastCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        topic = '{}.{}'.format(OFF_FAST, group)
        super().__init__(address, topic)
        # put the following commands in a subclass!
        self._group = group
        # self._subscriber_topic = '{}.{}'.format(self._subscriber_topic, self._group)

    #pylint: disable=arguments-differ
    def send(self):
        """Send the OFF command."""
        super().send(group=self._group)

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the OFF command async."""
        return await super().async_send(group=self._group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the OFF response direct ACK."""
        self._call_subscribers(on_level=0)
