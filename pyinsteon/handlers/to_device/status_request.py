"""Manage outbound ON command to a device."""
from ... import pub
from .. import status_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import STATUS_REQUEST


class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound Status command to a device.

    TODO Confirm that the status command is best with a single status handler
    rather than a handler per status command (ie. one for state 1 and one for
    state 2)
    """

    def __init__(self, address, status_type: int = 0):
        """Init the OnLevelCommand class."""
        super().__init__(topic=STATUS_REQUEST, address=address)
        self._status_type = status_type

    # pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send(status_type=self._status_type)

    # pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send(status_type=self._status_type)

    @status_handler
    def handle_direct_ack(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd1 = kwargs.get("cmd1")
        cmd2 = kwargs.get("cmd2")
        if cmd2 is not None:
            self._call_subscribers(db_version=cmd1, status=cmd2)
