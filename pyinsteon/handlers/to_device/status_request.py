"""Manage outbound ON command to a device."""
import asyncio

from ... import pub
from ...constants import MessageFlagType, ResponseStatus
from ...topics import STATUS_REQUEST
from .. import ack_handler, status_handler
from .direct_command import DirectCommandHandlerBase


class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound Status command to a device."""

    def __init__(self, address, status_type: int = 0):
        """Init the OnLevelCommand class."""
        super().__init__(topic=STATUS_REQUEST, address=address, group=None)
        self._status_type = status_type
        self._subscriber_topic = f"handler.{self._address.id}.{self._status_type}.{STATUS_REQUEST}.{str(MessageFlagType.DIRECT).lower()}"

    # pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send(status_type=self._status_type)

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
        if cmd2 == self._status_type:
            await super().async_handle_ack(cmd1, cmd2, user_data)

    @status_handler
    async def async_handle_direct_ack(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the Status Request response direct ACK.

        This handler listens to all topics for a device therefore we need to
        confirm the message is a status response.
        """
        # Need to make sure the ACK has time to aquire the lock
        await asyncio.sleep(0.05)
        if not self._response_lock.locked():
            return

        msg_type = topic.name.split(".")[-1]
        if msg_type != str(MessageFlagType.DIRECT_ACK):
            return

        self._direct_response.put_nowait(ResponseStatus.SUCCESS)

        cmd1 = kwargs.get("cmd1")
        cmd2 = kwargs.get("cmd2")
        self._call_subscribers(db_version=cmd1, status=cmd2)
