"""Insteon Powerline Modem (PLM)."""

from ..aldb.modem_aldb import ModemALDB
from .modem_base import ModemBase


class MockModem(ModemBase):
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
        self._aldb = ModemALDB(self._address, mem_addr=0x1FFF)
