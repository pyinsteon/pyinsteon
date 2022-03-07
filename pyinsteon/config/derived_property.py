"""Base class for a derived property."""

from ..constants import PropertyType
from ..topics import EXTENDED_PROPERTIES_CHANGED
from ..utils import subscribe_topic
from .device_flag import DeviceFlagBase


class DerivedProperty(DeviceFlagBase):
    """Base class for a derived property."""

    def __init__(
        self,
        address,
        name,
        value_type,
        is_reversed=False,
        is_read_only=False,
    ):
        """Init the DerivedProperty class."""
        super().__init__(
            address,
            "derived_property",
            name,
            value_type,
            is_reversed,
            is_read_only,
            prop_type=PropertyType.DERIVED,
        )
        subscribe_topic(
            self._properties_updated,
            f"{self._address.id}.{EXTENDED_PROPERTIES_CHANGED}",
        )

    def _properties_updated(self):
        """Update values based on underlying properties."""
        self._call_subscribers(name=self._name, value=self.value)

    def load(self, value):
        """Do nothing.

        Loading is done via the underlying property.
        """
