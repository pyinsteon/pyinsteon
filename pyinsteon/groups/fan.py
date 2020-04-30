"""Fan On Level state."""
from .group_base import GroupBase
from ..address import Address
from ..constants import FanSpeed, FanSpeedRange


class FanOnLevel(GroupBase):
    """On / Off state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: FanSpeed = None
    ):
        """Init the FanOnLevel class."""
        super().__init__(name, address, group, default, value_type=FanSpeed)

    # pylint: disable=arguments-differ
    def set_value(self, on_level):
        """Set the value of the state from the handlers."""
        if on_level in FanSpeedRange.OFF:
            fan_speed = FanSpeed.OFF
        elif on_level in FanSpeedRange.LOW:
            fan_speed = FanSpeed.LOW
        elif on_level in FanSpeedRange.MEDIUM:
            fan_speed = FanSpeed.MEDIUM
        else:
            fan_speed = FanSpeed.HIGH
        self.value = fan_speed
