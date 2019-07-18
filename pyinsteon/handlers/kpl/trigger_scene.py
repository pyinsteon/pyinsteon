"""KeypadLinc command handler to set the LED on/off values."""
from . import direct_ack_handler, DirectCommandHandlerBase
from ...topics import EXTENDED_GET_SET

class TriggerSceneCommandHandler(DirectCommandHandlerBase):
    """Set the LED values of a KeypadLinc device."""

    def __init__(self, address):
        """Init the SetLedCommandHandler class."""
        super().__init__(address=address, topic=EXTENDED_GET_SET)
        self._last_group = 0
        self._last_on = False
        self._last_on_level = 0

    #pylint: disable=arguments-differ
    async def async_send(self, group: int, on: bool, on_level: int = None, fast_on: bool = False):
        """Set the LED values of the KPL."""
        self._last_group = group
        self._last_on = on
        self._last_on_level = on_level
        action = 0 if on_level is None else 1
        cmd1 = 0x11 if on else 0x13
        cmd2 = 0
        on_level = 0 if on_level is None else on_level
        ramp_rate = 1 if fast_on else 0
        kwargs = {'data1': group,
                  'data2': action,
                  'data3': on_level,
                  'data4': cmd1,
                  'data5': cmd2,
                  'data6': ramp_rate}

        return await super().async_send(**kwargs)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        self._call_subscribers(group=self._last_group, on=self._last_on,
                               on_level=self._last_on_level)
    