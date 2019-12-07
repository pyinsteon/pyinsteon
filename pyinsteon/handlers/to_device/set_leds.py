"""KeypadLinc command handler to set the LED on/off values."""
from ..to_device.direct_command import DirectCommandHandlerBase
from .. import direct_ack_handler
from ...topics import EXTENDED_GET_SET
from ...utils import build_topic
from ...constants import MessageFlagType


class SetLedsCommandHandler(DirectCommandHandlerBase):
    """Set the LED values of a KeypadLinc device.

    TODO make compatable with the single handler per group model.
    """

    def __init__(self, address):
        """Init the SetLedCommandHandler class."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)
        self._last_bitmask = 0
        self._subscriber_topic = build_topic(
            prefix="subscriber.{}".format(self._address), # Force address
            topic="set_leds_command",
            message_type=MessageFlagType.DIRECT,
        )

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        group1: bool,
        group2: bool,
        group3: bool,
        group4: bool,
        group5: bool,
        group6: bool,
        group7: bool,
        group8: bool,
    ):
        """Set the LED values of the KPL."""
        bitmask = 0x00
        for group in range(0, 8):
            val = 1 if locals()["group{}".format(group + 1)] else 0
            bitmask = bitmask + val << group
        self._last_bitmask = bitmask
        kwargs = {"data1": 0x01, "data2": 0x09, "data3": bitmask}

        return await super().async_send(**kwargs)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        for group in range(0, 8):
            value = bool(self._last_bitmask & 1 << group)
            self._call_subscribers(group=group + 1, value=value)
