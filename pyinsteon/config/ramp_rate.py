"""Dimmable ramp rate property."""
from ..utils import ramp_rate_to_seconds, seconds_to_ramp_rate
from .derived_property import DerivedProperty


class RampRateProperty(DerivedProperty):
    """Ramp rate property."""

    def __init__(
        self,
        address,
        name,
        ramp_rate_prop,
    ):
        """Init the RampRateProperty class."""
        super().__init__(address, name, float, False, False)

        self._ramp_rate_prop = ramp_rate_prop

    @property
    def value(self):
        """Return the ramp rate property value in seconds."""
        if self._ramp_rate_prop.value is None:
            return None
        return ramp_rate_to_seconds(self._ramp_rate_prop.value)

    @property
    def new_value(self):
        """Return the ramp rate property in seconds."""
        if self._ramp_rate_prop.new_value is None:
            return None
        return ramp_rate_to_seconds(self._ramp_rate_prop.new_value)

    @new_value.setter
    def new_value(self, value):
        """Set the ramp rate property in seconds."""
        if value is None:
            self._ramp_rate_prop.new_value = None
            return
        value = float(value)
        ramp_rate = seconds_to_ramp_rate(value)
        if int(ramp_rate) == self._ramp_rate_prop.value:
            self._ramp_rate_prop.new_value = None
            return
        self._ramp_rate_prop.new_value = int(ramp_rate)

    @property
    def is_loaded(self):
        """Return if the Operating flag has been loaded."""
        return self._ramp_rate_prop.is_loaded

    @property
    def is_dirty(self):
        """Return if the Operating flag has been changed."""
        return self._ramp_rate_prop.is_dirty
