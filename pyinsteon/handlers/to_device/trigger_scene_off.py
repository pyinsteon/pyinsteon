"""KeypadLinc command handler to trigger a button scene."""
from .. import ack_handler, direct_ack_handler
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
        ramp_rate = 1 if fast else 0
        kwargs = {
            "data1": self._group,
            "data2": 1,
            "data3": 0,
            "data4": 0x13,
            "data5": 0,
            "data6": ramp_rate,
        }

        return await super().async_send(**kwargs)

    @ack_handler(wait_response=True)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required since the BEEP command uses the same cmd1, cmd2 values.
        """
        if not user_data and not user_data["data1"] == self._group:
            return
        return super().handle_ack(cmd1, cmd2, user_data)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK message."""
        self._call_subscribers(on_level=0)
