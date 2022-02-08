"""Manage outbound ON command to a device."""
from pyinsteon.constants import MessageFlagType, ResponseStatus

from ... import pub
from ...topics import STATUS_REQUEST
from .. import ack_handler, status_handler
from .direct_command import DirectCommandHandlerBase


class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound Status command to a device.

    TODO Confirm that the status command is best with a single status handler
    rather than a handler per status command (ie. one for state 1 and one for
    state 2)
    """

    def __init__(self, address, status_type: int = 0):
        """Init the OnLevelCommand class."""
        super().__init__(topic=STATUS_REQUEST, address=address)
        self._status_active = False
        self._status_type = status_type
        if status_type:
            self._subscriber_topic = f"{self._subscriber_topic}_{status_type}"

    @property
    def status_type(self):
        """Return the type of status message."""
        try:
            return self._status_type
        except AttributeError:
            return 0

    @property
    def status_active(self):
        """Return if the status command is active."""
        try:
            return self._status_active
        except AttributeError:
            return False

    @status_active.setter
    def status_active(self, value: bool):
        """Set if the status command is active."""
        self._status_active = bool(value)

    # pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self):
        """Send the ON command async."""
        response = await super().async_send(status_type=self._status_type)
        # return response
        self._status_active = False
        return response

    @ack_handler
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
        if cmd2 == self.status_type:
            self.status_active = True
            super().handle_ack(cmd1, cmd2, user_data)

    @status_handler
    def handle_direct_ack(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK.

        This handler listens to all topics for a device therefore we need to
        confirm the message is a status response.
        """
        if not self.status_active:
            return

        msg_type = topic.name.split(".")[-1]
        if msg_type != str(MessageFlagType.DIRECT_ACK):
            return

        self._message_response.put_nowait(ResponseStatus.SUCCESS)

        cmd1 = kwargs.get("cmd1")
        cmd2 = kwargs.get("cmd2")
        if cmd2 is not None:
            self._call_subscribers(db_version=cmd1, status=cmd2)
