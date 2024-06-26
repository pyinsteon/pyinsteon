"""Base device object."""

from abc import ABC
from datetime import datetime
import logging
from typing import Dict

from ..address import Address
from ..aldb.aldb import ALDB
from ..config.extended_property import ExtendedProperty
from ..config.operating_flag import OperatingFlag
from ..constants import DeviceCategory, EngineVersion, PropertyType, ResponseStatus
from ..default_link import DefaultLink
from ..device_types.device_commands import STATUS_COMMAND
from ..handlers.to_device.engine_version_request import EngineVersionRequest
from ..handlers.to_device.ping import PingCommand
from ..handlers.to_device.product_data_request import ProductDataRequestCommand
from ..managers.get_set_ext_property_manager import GetSetExtendedPropertyManager
from ..managers.get_set_op_flag_manager import GetSetOperatingFlagsManager
from ..managers.link_manager.default_links import async_add_default_links
from ..managers.status_manager import StatusManager
from ..topics import ENGINE_VERSION
from ..utils import multiple_status, publish_topic

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
        self._cat = DeviceCategory(0xFF) if cat is None else DeviceCategory(int(cat))
        self._subcat = subcat
        if self._subcat is None:
            self._subcat = 0x00
        self._firmware = firmware if firmware is not None else 0x00
        self._description = description
        self._model = model
        self._product_id = None
        self._is_battery = False
        self._engine_version = EngineVersion.UNKNOWN

        self._last_communication_received = datetime(1, 1, 1, 1, 1, 1)
        self._product_data_in_aldb = False
        self._groups = {}
        self._handlers = {}
        self._managers = {}
        self._events = {}

        self._aldb = ALDB(self._address)
        self._default_links = []
        self._operating_flags: Dict[str, OperatingFlag] = {}
        self._properties: Dict[str, ExtendedProperty] = {}
        self._config = {}

        self._op_flags_manager = GetSetOperatingFlagsManager(
            self._address, self._operating_flags
        )
        self._ext_property_manager = GetSetExtendedPropertyManager(self._address)

        self._register_groups()
        self._register_events()
        self._register_op_flags_and_props()
        self._register_handlers_and_managers()
        self._subscribe_to_handelers_and_managers()
        self._register_default_links()
        self._register_config()

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
    def groups(self):
        """Return the device groups / buttons."""
        return self._groups

    @property
    def events(self):
        """Return the device events."""
        return self._events

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
    def configuration(self):
        """Return the configuration properties."""
        return self._config

    @property
    def default_links(self):
        """Return the list of default links."""
        return self._default_links

    @property
    def is_battery(self):
        """Return True if the device is battery operated."""
        return self._is_battery

    @property
    def engine_version(self):
        """Return device engine version."""
        return self._engine_version

    @engine_version.setter
    def engine_version(self, value: EngineVersion):
        """Set the device engine version."""
        try:
            version = EngineVersion(value)
        except ValueError:
            version = EngineVersion.UNKNOWN
        if version in [EngineVersion.I2, EngineVersion.I2CS]:
            self._op_flags_manager.extended_write = True
        self._engine_version = version
        publish_topic(
            f"{self._address.id}.{ENGINE_VERSION}", version=self._engine_version
        )

    async def async_status(self, group=None):
        """Get the status of the device."""
        return ResponseStatus.SUCCESS

    async def async_read_config(self, read_aldb: bool = True):
        """Get all configuration settings.

        This includes:
        - Engine Version
        - Operating flags
        - Extended properties
        - All-Link Database records.
        """
        result_engine = await self.async_get_engine_version()
        result_op_flags = await self.async_read_op_flags()
        result_ext_prop = await self.async_read_ext_properties()
        if read_aldb:
            result_aldb = await self._aldb.async_load()
        else:
            result_aldb = ResponseStatus.SUCCESS
        return multiple_status(
            result_engine, result_ext_prop, result_op_flags, result_aldb
        )

    async def async_write_config(self):
        """Write the device configuration to the physical device."""
        result1 = await self.async_write_op_flags()
        result2 = await self.async_write_ext_properties()
        return multiple_status(result1, result2)

    async def async_read_op_flags(self, group=None):
        """Read the device operating flags."""
        return await self._op_flags_manager.async_read(group=group)

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        return await self._op_flags_manager.async_write()

    async def async_read_ext_properties(self, group=None):
        """Get the device extended properties."""
        return await self._ext_property_manager.async_read(group=group)

    async def async_write_ext_properties(self):
        """Write the extended properties."""
        return await self._ext_property_manager.async_write()

    async def async_read_product_id(self):
        """Get the product ID."""
        return await self._handlers["product_data_cmd"].async_send()

    async def async_add_default_links(self):
        """Add the default links betweent he modem and the device."""
        return await async_add_default_links(self)

    async def async_get_engine_version(self):
        """Read the device engine version."""
        return await self._handlers["engine_version_cmd"].async_send()

    async def async_ping(self):
        """Ping the device."""
        cmd = PingCommand(self.address)
        return await cmd.async_send()

    def _register_groups(self):
        """Add the groups to the device."""

    def _register_handlers_and_managers(self):
        """Add all handlers to the device and register listeners."""
        self._handlers["product_data_cmd"] = ProductDataRequestCommand(self._address)
        self._handlers["engine_version_cmd"] = EngineVersionRequest(self._address)
        self._managers[STATUS_COMMAND] = StatusManager(self._address)

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe groups and events to handlers and managers."""
        self._handlers["product_data_cmd"] = ProductDataRequestCommand(self._address)
        self._handlers["engine_version_cmd"].subscribe(self._engine_version_received)

    def _register_default_links(self):
        """Add default links for linking the device to the modem."""
        link_0 = DefaultLink(
            is_controller=False,
            group=0,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0,
            modem_data1=int(self.cat),
            modem_data2=self.subcat,
            modem_data3=self.firmware,
        )
        self._default_links.append(link_0)

    def _register_events(self):
        """Add events that are triggered when events are fired from the device."""

    def _register_op_flags_and_props(self):
        """Add operating flags to the device."""

    def _register_config(self):
        """Set up the configuration properties."""
        for name, prop in self._operating_flags.items():
            if prop.property_type == PropertyType.STANDARD:
                self._config[name] = prop

        for name, prop in self._properties.items():
            if prop.property_type == PropertyType.STANDARD:
                self._config[name] = prop

    def _add_operating_flag(
        self,
        name,
        group,
        bit,
        set_cmd,
        unset_cmd,
        is_reversed=False,
        prop_type=PropertyType.STANDARD,
    ):
        self._op_flags_manager.check_duplicate(name, group, bit, set_cmd, unset_cmd)
        read_only = set_cmd is None or unset_cmd is None
        value_type = bool if bit is not None else int
        self._operating_flags[name] = OperatingFlag(
            self._address, name, value_type, is_reversed, read_only, prop_type
        )
        self._op_flags_manager.subscribe(name, group, bit, set_cmd, unset_cmd)

    def _add_property(
        self,
        name,
        data_field,
        set_cmd,
        group=1,
        bit=None,
        is_reversed=False,
        prop_type=PropertyType.STANDARD,
    ):
        self._ext_property_manager.check_duplicate(group, data_field, bit, set_cmd)
        self._properties[name] = self._ext_property_manager.create(
            name, group, data_field, bit, set_cmd, is_reversed, prop_type
        )

    def _remove_operating_flag(self, name, group=None):
        self._op_flags_manager.unsubscribe(name)
        self._operating_flags.pop(name)

    def _handle_product_data(self, product_id, cat, subcat):
        """Receive and set the product data information."""
        self._product_id = product_id

    def _engine_version_received(self, engine_version):
        """Receive engine version response."""
        self.engine_version = engine_version

    def _product_data_received(self, product_id, cat, subcat):
        """Receive product data response."""
        self._product_id = product_id
        self._cat = cat
        self._subcat = subcat
