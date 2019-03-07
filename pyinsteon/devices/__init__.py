"""Base device object."""

from abc import ABC, abstractmethod
from datetime import datetime

from ..aldb import ALDB
from ..address import Address

class Device(ABC):
    """INSTEON Device Class."""

    def __init__(self, address, cat, subcat, product_key=0x00,
                 description='', model=''):
        """Init the Device class."""
        self._address = Address(address)
        self._cat = cat
        self._subcat = subcat
        if self._subcat is None:
            self._subcat = 0x00
        self._product_key = product_key
        if self._product_key is None:
            self._product_key = 0x00
        self._description = description
        self._model = model

        self._last_communication_received = datetime(1, 1, 1, 1, 1, 1)
        self._product_data_in_aldb = False
        self._stateList = {}

        self._aldb = ALDB(self._address)
        self._default_links = []

        self._register_states()
        self._register_handlers()
        self._register_default_links()

    # Public properties
    @property
    def address(self):
        """Return the INSTEON device address."""
        return self._address

    @property
    def cat(self):
        """Return the INSTEON device category."""
        return self._cat

    @property
    def subcat(self):
        """Return the INSTEON device subcategory."""
        return self._subcat

    @property
    def product_key(self):
        """Return the INSTEON product key."""
        return self._product_key

    @property
    def description(self):
        """Return the INSTEON device description."""
        return self._description

    @property
    def model(self):
        """Return the INSTEON device model number."""
        return self._model

    @property
    def id(self):
        """Return the ID of the device."""
        return self._address.id

    @property
    def states(self):
        """Return the device states/groups."""
        return self._stateList

    @property
    def prod_data_in_aldb(self):
        """Return if the PLM use the ALDB data to setup the device.

        True if Product data (cat, subcat) is stored in the PLM ALDB.
        False if product data must be acquired via a Device ID message or from
        a Product Data Request command.

        The method of linking determines if product data in the ALDB,
        therefore False is the default. The common reason to store product data
        in the ALDB is for one way devices or battery opperated devices where
        the ability to send a command request is limited.
        """
        return self._product_data_in_aldb

    @property
    def aldb(self):
        """Return the device All-Link Database."""
        return self._aldb

    @abstractmethod
    def _register_states(self):
        """Add the states to the device."""

    @abstractmethod
    def _register_handlers(self):
        """Add all handlers to the device and register listeners."""

    @abstractmethod
    def _register_default_links(self):
        """Add default links for linking the device to the modem."""
