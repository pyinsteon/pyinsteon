"""Operating flag or Extended Property for all device types."""
from .subscriber_base import SubscriberBase


class DeviceFlagBase(SubscriberBase):
    """Operating flag or Extended Property."""

    def __init__(self, topic, name, flag_type: type):
        """Init the DeviceFlag class."""
        super().__init__(topic)
        self._name = name
        self._value = None
        self._type = flag_type
        self._new_value = None
        self._is_dirty = False
        self._is_loaded = False

    @property
    def name(self):
        """Return the flag name."""
        return self._name

    @property
    def value(self):
        """Return the value of the flag."""
        return self._value

    @property
    def new_value(self):
        """Return the new value of the flag."""
        return self._new_value

    @new_value.setter
    def new_value(self, value):
        """Set the new value of the flag.

        This is the primary method to set the value of the flag.
        It sets the `new_value` property and the `is_dirty` property.
        """
        if value != self._value:
            self._new_value = self._type(value)
            self._is_dirty = True

    @property
    def is_dirty(self):
        """Return if the Operating flag has been changed."""
        return self._is_dirty

    @property
    def is_loaded(self):
        """Return if the Operating flag has been loaded."""
        return self._is_loaded

    def load(self, value):
        """Load the flag from the device value.

        Only use this method to update the value of the flag from the value
        of the device.

        This method updates the `is_loaded` property and clears the `new value` and
        `is_dirty` properties.
        """
        self._value = self._type(value) if value is not None else self._type(0)
        self._is_dirty = False
        self._new_value = None
        self._is_loaded = True
        self._call_subscribers(name=self._name, value=self._value)
