"""Termostat device types."""

from ..aldb import ALDB
from .device_base import Device


class Thermostat(Device):
    """Thermostat device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the Thermostat class."""
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
        )
        self._aldb = ALDB(self._address, mem_addr=0x1FFF)
