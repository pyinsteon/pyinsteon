"""KeypadLinc command handler to trigger a button scene."""
from .. import ack_handler
from ...topics import EXTENDED_TRIGGER_ALL_LINK
from ..to_device.direct_command import DirectCommandHandlerBase


class TriggerSceneOffCommandHandler(DirectCommandHandlerBase):
    """KeypadLinc command handler to trigger a button scene."""

    def __init__(self, address, group):
        """Init the SetLedCommandHandler class."""
        super().__init__(topic=EXTENDED_TRIGGER_ALL_LINK, address=address, group=group)
        self._on_level = 0

    # pylint: disable=arguments-differ
    async def async_send(self, fast: bool = False):
        """Set the LED values of the KPL."""
        return await super().async_send(group=self._group, on_level=0, fast=fast)

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required since the BEEP command uses the same cmd1, cmd2 values.
        """
        if not user_data and not user_data["d1"] == self._group:
            return
        return await super().async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(on_level=0)
