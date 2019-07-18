"""On / Off state."""
from datetime import datetime, timedelta
from . import StateBase
from ..address import Address

class OnOff(StateBase):
    """On / Off state."""

    def __init__(self, name: str, address: Address, group: int = 0,
                 default: int = None):
        """Init the OnLevel class."""
        super().__init__(name, address, group, default, value_type=int)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = 0xff if on_level else 0


class LowBattery(StateBase):
    """Low battery state."""

    def __init__(self, name: str, address: Address, group: int = 0,
                 default: int = None):
        """Init the LowBattery class."""
        super().__init__(name, address, group, default, value_type=bool)
        self._last_contact = datetime(1, 1, 1)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = True
        else:
            # If we receive a message from the device that is not a low battery message
            # and the awake interval has passed (max awake period is 255 seconds),
            # then we can turn off the low battery warning. If the low battery message comes in
            # after this it will turn the warning back on.
            time_gap = datetime.now() - self._last_contact
            if time_gap.seconds > 255:
                self.value = False
