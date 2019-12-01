"""KeypadLinc command handler to set the LED on/off values."""
from ..to_device.direct_command import DirectCommandHandlerBase
from .. import direct_ack_handler
from ...topics import EXTENDED_GET_SET

class TriggerSceneCommandHandler(DirectCommandHandlerBase):
    """Set the LED values of a KeypadLinc device.

    TODO make compatable with the single handler per group model
    """

    def __init__(self, address, group):
        """Init the SetLedCommandHandler class."""
        super().__init__(address=address, command=EXTENDED_GET_SET)
        self._group = group
        self._on_level = 0

    #pylint: disable=arguments-differ
    async def async_send(self, on_level: int = 0xff, fast_on: bool = False):
        """Set the LED values of the KPL."""
        self._on_level = on_level
        action = 0 if on_level == 0xff else 1
        cmd1 = 0x11 if on_level else 0x13
        cmd2 = self._on_level
        ramp_rate = 1 if fast_on else 0
        kwargs = {'data1': self._group,
                  'data2': action,
                  'data3': self._on_level,
                  'data4': cmd1,
                  'data5': cmd2,
                  'data6': ramp_rate}

        return await super().async_send(**kwargs)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        self._call_subscribers(on_level=self._on_level)
