"""Manage inbound ON command from device."""

from ...address import Address
from ...constants import RampRate
from ...data_types.user_data import UserData
from ...topics import OFF_AT_RAMP_RATE_INBOUND
from .broadcast_command import BroadcastCommandHandlerBase


class OffAtRampRateInbound(BroadcastCommandHandlerBase):
    """Off At Ramp Rate command inbound."""

    def __init__(self, address: Address, group: int):
        """Init the OnAtRampRateInbound class."""
        super().__init__(topic=OFF_AT_RAMP_RATE_INBOUND, address=address, group=group)

    def _handle_message_received(
        self, cmd1: int, cmd2: int, target: Address, user_data: UserData, hops_left: int
    ):
        """Handle the OFF command from a device."""
        on_level = ((cmd2 >> 4) * 16) + 15
        ramp_rate_byte = ((cmd2 & 0x0F) * 2) + 1
        ramp_rate = RampRate(ramp_rate_byte)
        self._call_subscribers(on_level=on_level, ramp_rate=ramp_rate)
