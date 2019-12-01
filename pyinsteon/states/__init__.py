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
LEAK_SENSOR_STATE = 'leak_sensor_state'
DOOR_SENSOR_STATE = 'door_sensor_state'
MOTION_SENSOR_STATE = 'motion_sensor_state'
SMOKE_SENSOR_STATE = 'smoke_sensor_state'
CO_SENSOR_STATE = 'co_sensor_state'
TEST_SENSOR_STATE = 'test_sensor_state'
NEW_SENSOR_STATE = 'new_sensor_state'
LOW_BATTERY_STATE = 'low_battery_state'
HEARTBEAT_STATE = 'heartbeat_state'
SENSOR_MALFUNCTION_STATE = 'sensor_malfunction_state'

class StateBase(SubscriberBase):
    """Device state base class."""

    def __init__(self, name: str, address: Address, group=0,
                 default=None, value_type: type = int):
        """Init the StateBase class."""
        self._address = Address(address)
        topic = 'state_{}_{}_{}'.format(self._address.id, name, group)
        super().__init__(subscriber_topic=topic)
        self._name = name
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

    @abstractmethod
    def set_value(self, **kwargs):
        """Set the value of the state from a Handler."""
