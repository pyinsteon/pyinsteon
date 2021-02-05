"""Operating flag or Extended Property for all device types."""
from .subscriber_base import SubscriberBase


class DeviceFlagBase(SubscriberBase):
    """Operating flag or Extended Property."""

    def __init__(
        self, topic, name, flag_type: type, is_reversed=False, is_read_only=False
    ):
        """Init the DeviceFlag class."""
        super().__init__(topic)
        self._name = name
        self._value = None
        self._type = flag_type
        self._new_value = None
        self._is_dirty = False
        self._is_loaded = False
        self._reversed = is_reversed
        self._read_only = is_read_only

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
        if self._read_only:
            return

        if self._type is bool and self._reversed:
            value = not value

        if value != self._value and value is not None:
            self._new_value = self._type(value)
            self._is_dirty = True
        else:
            self._new_value = None
            self._is_dirty = False

    @property
    def is_dirty(self):
        """Return if the Operating flag has been changed."""
        return self._is_dirty

    @property
    def is_read_only(self):
        """Return the read only flag."""
        return self._read_only

    @property
    def is_loaded(self):
        """Return if the Operating flag has been loaded."""
        return self._is_loaded

    @property
    def is_reversed(self):
        """Return if the device flag is reverse of this value."""
        return self._reversed

    def load(self, value):
        """Load the flag from the device value.

        Only use this method to update the value of the flag from the value
        of the device.

        This method updates the `is_loaded` property and clears the `new value` and
        `is_dirty` properties.
        """
        if self._type is bool and self._reversed:
            value = not value
        update_value = self._type(value) if value is not None else self._type(0)
        self._is_dirty = False
        self._new_value = None
        self._is_loaded = True
        is_changed = update_value != self._value
        self._value = update_value
        if is_changed:
            self._call_subscribers(name=self._name, value=self._value)
