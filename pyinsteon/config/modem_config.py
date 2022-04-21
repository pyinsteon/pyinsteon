"""Configuration itmes for the modem."""

from ..constants import PropertyType
from .device_flag import DeviceFlagBase


class ModemConfiguration(DeviceFlagBase):
    """Configuration itmes for the modem."""

    def __init__(self, address, name):
        """Init the ModemConfiguration properties."""
        super().__init__(
            address, "modem_config", name, bool, prop_type=PropertyType.DERIVED
        )
