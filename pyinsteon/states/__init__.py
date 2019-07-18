"""Device state definitions."""
from abc import ABC, abstractmethod
from ..address import Address
from ..subscriber_base import SubscriberBase


DIMMABLE_LIGHT_STATE = 'dimmable_light_state'
DIMMABLE_FAN_STATE = 'dimmable_fan_state'
ON_OFF_SWITCH_STATE = 'on_off_switch_state'
ON_OFF_SWITCH_STATE_BOTTOM = 'on_off_switch_state_bottom'
LOW_BATTERY_STATE = 'low_battery'
OPEN_CLOSE_SENSOR_STATE = 'open_close_sensor'
LIGHT_SENSOR_STATE = 'light_sensor_state'

class StateBase(SubscriberBase):
    """Device state base class."""

    def __init__(self, name: str, address: Address, group=0,
                 default=None, value_type: type = int):
        """Init the StateBase class."""
        super().__init__()
        self._name = name
        self._address = address
        self._group = group
        self._value = int(default) if default is not None else None
        self._type = value_type

    @property
    def name(self):
        """Return the name of the state."""
        return self._name

    @property
    def value(self):
        """Return the value of the state."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            self._value = self._type(value) if value is not None else None
        except TypeError:
            raise TypeError('Error setting value of State {}: '
                            'Must be of type {}'.format(self._name, self._type.__name__))
        else:
            self._call_subscribers(name=self._name, address=self._address,
                                   value=self._value, group=self._group)

    def add_handler(self, handler):
        """Subscribe to a handler to set the value of the state."""
        handler.subscribe(self._set_value)

    @abstractmethod
    def _set_value(self, **kwargs):
        """Set the value of the state from a Handler."""
