"""Base device object."""

from abc import ABC
from datetime import datetime
import logging

from ..address import Address
from ..aldb import ALDB
from ..managers.get_set_op_flag_manager import GetSetOperatingFlagsManager
from ..managers.get_set_ext_property_manager import GetSetExtendedPropertyManager
from ..operating_flag import OperatingFlag


_LOGGER = logging.getLogger(__name__)


class Device(ABC):
    """INSTEON Device Class."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
    ):
        """Init the Device class."""
        self._address = Address(address)
        self._cat = cat
        self._subcat = subcat
        if self._subcat is None:
            self._subcat = 0x00
        self._firmware = firmware if firmware is not None else 0x00
        self._description = description
        self._model = model
        self._product_id = None

        self._last_communication_received = datetime(1, 1, 1, 1, 1, 1)
        self._product_data_in_aldb = False
        self._states = {}
        self._handlers = {}
        self._managers = {}
        self._events = {}

        self._aldb = ALDB(self._address)
        self._default_links = []
        self._operating_flags = {}
        self._properties = {}
        self._op_flags_manager = GetSetOperatingFlagsManager(
            self._address, self._operating_flags
        )
        self._ext_property_manager = GetSetExtendedPropertyManager(self._address)

        self._register_handlers_and_managers()
        self._register_states()
        self._register_events()
        self._subscribe_to_handelers_and_managers()
        self._register_default_links()
        self._register_operating_flags()

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
    def firmware(self):
        """Return the INSTEON product key."""
        return self._firmware

    @property
    def description(self):
        """Return the INSTEON device description."""
        return self._description

    @property
    def model(self):
        """Return the INSTEON device model number."""
        return self._model

    @property
    def product_id(self):
        """Return the INSTEON product ID."""
        return self._product_id

    @property
    def id(self):
        """Return the ID of the device."""
        return self._address.id

    @property
    def states(self):
        """Return the device states/groups."""
        return self._states

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

    @property
    def operating_flags(self):
        """Return the Operating Flags."""
        return self._operating_flags

    @property
    def properties(self):
        """Return the Extended Properties."""
        return self._properties

    @property
    def default_links(self):
        """Return the list of default links."""
        return self._default_links

    @property
    def is_battery(self):
        """Return True if the device is battery operated."""
        return False

    def status(self, group=None):
        """Get the status of the device."""

    async def async_status(self, group=None):
        """Get the status of the device."""

    async def async_read_config(self):
        """Get all configuration settings.

        This includes:
        - Operating flags
        - Extended properties
        - All-Link Database records.
        """
        await self.async_read_op_flags()
        await self.async_read_ext_properties()
        await self._aldb.async_load()

    async def async_read_op_flags(self, group=None):
        """Read the device operating flags."""
        return await self._op_flags_manager.async_read(group=group)

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        return await self._op_flags_manager.async_write()

    async def async_read_ext_properties(self):
        """Get the device extended properties."""
        return await self._ext_property_manager.async_read()

    async def async_write_ext_properties(self):
        """Write the extended properties."""
        return await self._ext_property_manager.async_write()

    async def async_read_product_id(self):
        """Get the product ID."""
        from ..handlers.to_device.product_data_request import ProductDataRequestCommand

        return await ProductDataRequestCommand(self._address).async_send()

    async def async_add_default_links(self):
        """Add the default links betweent he modem and the device."""
        from ..managers.link_manager import async_add_default_links

        return await async_add_default_links(self)

    def _register_states(self):
        """Add the states to the device."""

    def _register_handlers_and_managers(self):
        """Add all handlers to the device and register listeners."""

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe states and events to handlers and managers."""

    def _register_default_links(self):
        """Add default links for linking the device to the modem."""
        from ..default_link import DefaultLink

        link_0 = DefaultLink(
            is_controller=False,
            group=0,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0,
            modem_data1=self.cat,
            modem_data2=self.subcat,
            modem_data3=self.firmware,
        )
        link_0 = self._default_links.append(link_0)

    def _register_events(self):
        """Add events that are triggered when events are fired from the device."""

    def _register_operating_flags(self):
        """Add operating flags to the device."""

    def _add_operating_flag(self, name, group, bit, set_cmd, unset_cmd):
        flag_type = bool if bit is not None else int
        self._operating_flags[name] = OperatingFlag(self._address, name, flag_type)
        self._op_flags_manager.subscribe(name, group, bit, set_cmd, unset_cmd)

    def _add_property(self, name, data_field, set_cmd, group=1, bit=None):
        self._properties[name] = self._ext_property_manager.create(
            name, group, data_field, bit, set_cmd
        )

    def _remove_operating_flag(self, name, group=None):
        self._op_flags_manager.unsubscribe(name)
        self._operating_flags.pop(name)

    def _handle_product_data(self, product_id, cat, subcat):
        """Receive and set the product data information."""
        self._product_id = product_id
        # self._cat = cat
        # self._subcat = subcat
