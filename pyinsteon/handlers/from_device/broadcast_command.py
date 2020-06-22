"""Base class to handle Broadcast messages from devices."""
from datetime import datetime
from ...address import Address
from ...constants import MessageFlagType
from ..inbound_base import InboundHandlerBase


class BroadcastCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound Broadcast messages."""

    def __init__(self, topic, address, group=None):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        self._group = group
        super().__init__(
            topic=topic,
            address=self._address,
            group=self._group,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )
        self._last_command = datetime(1, 1, 1)
        self._last_hops_left = None

    def is_first_message(self, **kwargs):
        """Test if the message is a duplicate."""
        curr_time = datetime.now()
        tdelta = curr_time - self._last_command
        self._last_command = curr_time
        hops_left = kwargs["hops_left"]
        if (
            kwargs["target"].middle != 0
            and hops_left == self._last_hops_left
            and tdelta.seconds < 1
        ):
            return False
        if (
            self._last_hops_left is None
            or (hops_left == self._last_hops_left and tdelta.seconds > 0.7)
            or hops_left > self._last_hops_left
            or tdelta.seconds >= 2
        ):
            self._last_hops_left = hops_left
            return True
        return False
