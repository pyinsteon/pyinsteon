"""Temperature state."""
from .group_base import GroupBase
from ..address import Address
from ..extended_property import ExtendedProperty
from ..constants import ThermostatMode
from ..utils import to_fahrenheit


class Temperature(GroupBase):
    """Temperature state."""

    def __init__(
        self,
        name: str,
        address: Address,
        celsius: ExtendedProperty,
        group: int = 0,
        default: int = None,
    ):
        """Init the Temperature class."""
        super().__init__(name, address, group, default, value_type=float)
        self._is_celsius = celsius

    @property
    def is_fahrenheit(self):
        """Return if the temperature format is Fahrenheit."""
        return not self._is_celsius.value

    @property
    def is_celsius(self):
        """Return if the temperature format is Fahrenheit."""
        return self._is_celsius.value

    # pylint: disable=arguments-differ
    def set_value(self, temperature):
        """Set the temperature value."""
        self.value = temperature

    @property
    def value(self):
        """Return the temperature value."""
        return to_fahrenheit(self._value) if self.is_fahrenheit else self._value

    @value.setter
    def value(self, value):
        """Set the temperature value.

        Value must be in celsius regardless of thermostat setting.
        """
        try:
            self._value = self._type(value) if value is not None else None
        except TypeError:
            raise TypeError(
                "Error setting value of State {}: "
                "Must be of type {}".format(self._name, self._type.__name__)
            )
        else:
            self._call_subscribers(
                name=self._name,
                address=self._address.id,
                value=self._value,
                group=self._group,
            )


class Humidity(GroupBase):
    """Humidity state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the Temperature class."""
        super().__init__(name, address, group, default, value_type=float)

    # pylint: disable=arguments-differ
    def set_value(self, humidity):
        """Set the temperature value."""
        self.value = humidity


class SetPoint(GroupBase):
    """SetPont state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the SetPoint class."""
        super().__init__(name, address, group, default, value_type=float)

    # pylint: disable=arguments-differ
    def set_value(self, degrees):
        """Set the Set Point value."""
        self.value = degrees


class SystemMode(GroupBase):
    """System Mode state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the SystemMode class."""
        super().__init__(name, address, group, default, value_type=ThermostatMode)

    # pylint: disable=arguments-differ
    def set_value(self, mode: ThermostatMode):
        """Set the system mode value."""
        self.value = mode

    @property
    def value(self):
        """Return the group value."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            if value > 0x0F:
                value = value >> 4
            self._value = self._type(value) if value is not None else None
        except TypeError:
            raise TypeError(
                "Error setting value of State {}: "
                "Must be of type {}".format(self._name, self._type.__name__)
            )
        else:
            self._call_subscribers(
                name=self._name,
                address=self._address.id,
                value=self._value,
                group=self._group,
            )


class FanMode(GroupBase):
    """Fan Mode state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the SystemMode class."""
        super().__init__(name, address, group, default, value_type=ThermostatMode)

    # pylint: disable=arguments-differ
    def set_value(self, mode: ThermostatMode):
        """Set the system mode value."""
        self.value = mode

    @property
    def value(self):
        """Return the group value."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            if value > 0x0F:
                value = value & 0x0F
            self._value = self._type(value) if value is not None else None
        except TypeError:
            raise TypeError(
                "Error setting value of State {}: "
                "Must be of type {}".format(self._name, self._type.__name__)
            )
        else:
            self._call_subscribers(
                name=self._name,
                address=self._address.id,
                value=self._value,
                group=self._group,
            )
