"""Device state definitions."""
from abc import ABC, abstractmethod
from ..address import Address
from ..subscriber_base import SubscriberBase


DIMMABLE_LIGHT = 'dimmable_light'
DIMMABLE_FAN = 'dimmable_fan'
DIMMABLE_OUTLET = 'dimmable_outlet'
ON_OFF_SWITCH = 'on_off_switch'
ON_OFF_OUTLET_TOP = 'on_off_outlet_top'
ON_OFF_OUTLET_BOTTOM = 'on_off_outlet_bottom'
LOW_BATTERY = 'low_battery'
OPEN_CLOSE_SENSOR = 'open_close_sensor'
LIGHT_SENSOR = 'light_sensor'
LEAK_SENSOR = 'leak_sensor'
DOOR_SENSOR = 'door_sensor'
MOTION_SENSOR = 'motion_sensor'
SMOKE_SENSOR = 'smoke_sensor'
CO_SENSOR = 'co_sensor'
TEST_SENSOR = 'test_sensor'
NEW_SENSOR = 'new_sensor'
HEARTBEAT = 'heartbeat'
SENSOR_MALFUNCTION = 'sensor_malfunction'

ON_OFF_SWITCH_MAIN = '{}_{}'.format(ON_OFF_SWITCH, 'main')
ON_OFF_SWITCH_A = '{}_{}'.format(ON_OFF_SWITCH, 'a')
ON_OFF_SWITCH_B = '{}_{}'.format(ON_OFF_SWITCH, 'b')
ON_OFF_SWITCH_C = '{}_{}'.format(ON_OFF_SWITCH, 'c')
ON_OFF_SWITCH_D = '{}_{}'.format(ON_OFF_SWITCH, 'd')
ON_OFF_SWITCH_E = '{}_{}'.format(ON_OFF_SWITCH, 'e')
ON_OFF_SWITCH_F = '{}_{}'.format(ON_OFF_SWITCH, 'f')
ON_OFF_SWITCH_G = '{}_{}'.format(ON_OFF_SWITCH, 'g')
ON_OFF_SWITCH_H = '{}_{}'.format(ON_OFF_SWITCH, 'h')

DIMMABLE_LIGHT_MAIN = '{}_{}'.format(DIMMABLE_LIGHT, 'main')
# DIMMABLE_LIGHT_A = '{}_{}'.format(DIMMABLE_LIGHT, 'a')
# DIMMABLE_LIGHT_B = '{}_{}'.format(DIMMABLE_LIGHT, 'b')
# DIMMABLE_LIGHT_C = '{}_{}'.format(DIMMABLE_LIGHT, 'c')
# DIMMABLE_LIGHT_D = '{}_{}'.format(DIMMABLE_LIGHT, 'd')
# DIMMABLE_LIGHT_E = '{}_{}'.format(DIMMABLE_LIGHT, 'e')
# DIMMABLE_LIGHT_F = '{}_{}'.format(DIMMABLE_LIGHT, 'f')
# DIMMABLE_LIGHT_G = '{}_{}'.format(DIMMABLE_LIGHT, 'g')
# DIMMABLE_LIGHT_H = '{}_{}'.format(DIMMABLE_LIGHT, 'h')


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
