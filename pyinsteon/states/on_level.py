"""On Leve state."""
import logging
from ..address import Address
from . import StateBase

_LOGGER = logging.getLogger(__name__)

class OnLevel(StateBase):
    """Variable On Level state."""

    def __init__(self, name: str, address: Address, group: int = 0,
                 default: int = None):
        """Init the OnLevel class."""
        super().__init__(name, address, group, default, value_type=int)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group=0):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = int(on_level) if on_level else 0
