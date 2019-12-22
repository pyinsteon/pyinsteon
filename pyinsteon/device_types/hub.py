"""Insteon Hub version 2."""

from .modem_base import ModemBase
from ..aldb.hub_aldb import HubALDB


class Hub(ModemBase):
    """Insteon Hub class."""

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
        self._aldb = HubALDB(self._address)
