"""Base class to handle Broadcast messages from devices."""

from datetime import datetime

from .. import broadcast_handler
from ...constants import MessageFlagType
from ..inbound_base import InboundHandlerBase

MIN_DUP = 0.7
MAX_DUP = 2


class BroadcastCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound Broadcast messages."""

    def __init__(self, topic, address, group=None):
        """Init the broadcast_handlerBase class."""
        self._group = group
        super().__init__(
            topic=topic,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )
        self._last_command = datetime(1, 1, 1)
        self._last_hops_left = None
        self._last_cmd2 = None
        self._last_userdata = None

    @broadcast_handler
    def receive_message(self, cmd1, cmd2, target, user_data, hops_left):
        """Receive the inbound message."""
        if not self._is_first_message(cmd2, user_data, target, hops_left):
            return
        self._handle_message_received(cmd1, cmd2, target, user_data, hops_left)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the received message."""

    def _is_first_message(self, cmd2, user_data, target, hops_left):
        """Test if the message is a duplicate."""
        curr_time = datetime.now()
        tdelta = curr_time - self._last_command
        if tdelta.days > 0:
            delta = 9999
        else:
            delta = tdelta.seconds + tdelta.microseconds / 1000000
        self._last_command = curr_time

        if cmd2 != self._last_cmd2 or user_data != self._last_userdata:
            self._last_cmd2 = cmd2
            self._last_userdata = user_data
            self._last_hops_left = hops_left
            return True
        self._last_cmd2 = cmd2
        self._last_userdata = user_data

        if target.middle != 0 and hops_left == self._last_hops_left and delta < MIN_DUP:
            return False

        if (
            self._last_hops_left is None
            or (hops_left == self._last_hops_left and delta > MIN_DUP)
            or hops_left > self._last_hops_left
            or delta >= MAX_DUP
        ):
            self._last_hops_left = hops_left
            return True
        return False
