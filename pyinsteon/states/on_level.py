"""On Leve state."""
from . import StateBase

class OnLevel(StateBase):
    """On / Off state."""

    def _set_value(self, **kwargs):
        """Set the value of the state from the handlers."""
        value = kwargs['on_level']
        group = kwargs['group']
        if self._group == group:
            self.value = value if value else 0
