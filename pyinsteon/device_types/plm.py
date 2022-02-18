"""Insteon Powerline Modem (PLM)."""

from ..aldb.modem_aldb import ModemALDB
from .modem_base import ModemBase


class PLM(ModemBase):
    """Insteon PLM class."""

    def __init__(
        self,
        address="000000",
        cat=0x03,
        subcat=0x00,
        firmware=0x00,
        description="",
        model="",
    ):
        """Init the Modem class."""
        super().__init__(address, cat, subcat, firmware, description, model)
        if subcat in [0x05, 0x06, 0x0B, 0x10, 0x13, 0x14]:
            mem_addr = 0x3FFF
        else:
            mem_addr = 0x1FFF
        self._aldb = ModemALDB(self._address, mem_addr=mem_addr)
