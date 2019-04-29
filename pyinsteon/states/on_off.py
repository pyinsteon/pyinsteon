"""On / Off state."""
from . import StateBase

class OnOff(StateBase):
    """On / Off state."""

    def _set_value(self, **kwargs):
        """Set the value of the state from the handlers."""
        value = kwargs['on_level']
        group = kwargs['group']
        if self._group == group:
            self.value = 0xff if value else 0
