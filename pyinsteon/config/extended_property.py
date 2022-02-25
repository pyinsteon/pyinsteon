"""Representaton of an extended property of a device."""

from ..constants import PropertyType
from .device_flag import DeviceFlagBase


class ExtendedProperty(DeviceFlagBase):
    """Representation of an extended property of a device."""

    def __init__(
        self,
        address,
        name,
        value_type: type,
        is_reversed=False,
        is_read_only=False,
        prop_type=PropertyType.STANDARD,
    ):
        """Init the ExtendedProperty class."""
        super().__init__(
            address, "property", name, value_type, is_reversed, is_read_only, prop_type
        )
