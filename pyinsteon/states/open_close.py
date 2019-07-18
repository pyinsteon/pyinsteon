"""Open / Close sensor states."""
from . import StateBase
from ..address import Address

class NormallyOpen(StateBase):
    """Normally open sensor state."""

    def __init__(self, name: str, address: Address, group: int = 0,
                 default: int = None):
        """Init the OnLevel class."""
        super().__init__(name, address, group, default, value_type=int)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = 0xff if on_level else 0


class NormallyClosed(StateBase):
    """Normally closed sensor state."""

    def __init__(self, name: str, address: Address, group: int = 0,
                 default: int = None):
        """Init the OnLevel class."""
        super().__init__(name, address, group, default, value_type=int)

    #pylint: disable=arguments-differ
    def _set_value(self, on_level, group):
        """Set the value of the state from the handlers."""
        if self._group == group:
            self.value = 0 if on_level else 0xff
