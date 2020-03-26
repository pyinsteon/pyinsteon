"""Insteon Powerline Modem (PLM)."""

from ..aldb.plm_aldb import PlmALDB
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
        self._aldb = PlmALDB(self._address)
