"""On / Off state."""
from . import StateBase
from ..address import Address

class OnOff(StateBase):
    """On / Off state."""

    def __init__(self, name: str, address: Address, handlers: list,
                 group: int = 0, default: int = None):
        """Init the OnLevel class."""
        super().__init__(name, address, handlers, group, default, value_type=int)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group=1):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = 0xff if on_level else 0
