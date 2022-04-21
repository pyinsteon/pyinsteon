"""Set the LEDs of a KeyPadLinc."""

from ...constants import MessageFlagType
from ...utils import build_topic
from .extended_set import ExtendedSetCommand


def _bitmask(*args):
    bitmask = 0x00
    for group in range(0, 8):
        val = 1 if args[group] else 0
        bitmask = bitmask + (val << group)
    return bitmask


class SetLedsCommandHandler(ExtendedSetCommand):
    """Set the LEDs of a KeypadLinc."""

    def __init__(self, address):
        """Init the SetLedsCommandHandler class."""
        super().__init__(address=address, data1=0x01, data2=0x09)
        self._subscriber_topic = build_topic(
            prefix=f"handler.{self._address.id}",  # Force address
            topic="set_leds",
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
        bitmask = _bitmask(
            group1, group2, group3, group4, group5, group6, group7, group8
        )
        return await super().async_send(data3=bitmask)
