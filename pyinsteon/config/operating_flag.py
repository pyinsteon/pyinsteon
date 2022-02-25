"""Operating flags list."""

from ..constants import PropertyType
from .device_flag import DeviceFlagBase


class OperatingFlag(DeviceFlagBase):
    """Operating flag for a device."""

    def __init__(
        self,
        address,
        name,
        value_type: type,
        is_reversed=False,
        is_read_only=False,
        prop_type=PropertyType.STANDARD,
    ):
        """Init the OperatingFlag class."""
        super().__init__(
            address,
            "operating_flag",
            name,
            value_type,
            is_reversed,
            is_read_only,
            prop_type,
        )
