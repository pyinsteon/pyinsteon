"""Base device object."""

from abc import ABC
import asyncio
from datetime import datetime
from functools import partial
import logging

from .. import pub
from ..address import Address
from ..aldb import ALDB
from ..managers.get_set_op_flag_manager import GetSetOperatingFlagsManager
from ..managers.get_set_ext_property_manager import GetSetExtendedPropertyManager
from ..handlers.to_device.extended_set import ExtendedSetCommand
from ..operating_flag import OperatingFlag
from ..extended_property import ExtendedProperty
from .commands import (EXTENDED_GET_COMMAND, EXTENDED_SET_COMMAND,
                       GET_OPERATING_FLAGS_COMMAND,
                       SET_OPERATING_FLAGS_COMMAND,
                       EXTENDED_GET_RESPONSE, ON_ALL_LINK_CLEANUP,
                       OFF_ALL_LINK_CLEANUP)

_LOGGER = logging.getLogger(__name__)

class Device(ABC):
    """INSTEON Device Class."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=None):
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
        self._op_flags_manager = GetSetOperatingFlagsManager(self._address)
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

    async def async_get_configuration(self):
        """Get all configuration settings.

        This includes:
        - Operating flags
        - Extended properties
        - All-Link Database records.
        """
        await self.async_get_operating_flags()
        await self.async_get_extended_properties()
        await self._aldb.async_load()

    async def async_get_operating_flags(self, group=None):
        """Read the device operating flags."""
        return await self._op_flags_manager.async_get(group=group)

    async def async_set_operating_flags(self, group=None, force=False):
        """Write the operating flags to the device."""
        return await self._op_flags_manager.async_set(group=group, force=force)

    async def async_get_extended_properties(self, group=None):
        """Get the device extended properties."""
        return await self._ext_property_manager.async_get(group=group)

    async def async_get_product_id(self):
        """Get the product ID."""
        from ..handlers.to_device.product_data_request import ProductDataRequestCommand
        return await ProductDataRequestCommand(self._address).async_send()

    def _register_states(self):
        """Add the states to the device."""

    def _register_handlers_and_managers(self):
        """Add all handlers to the device and register listeners."""

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe states and events to handlers and managers."""

    def _register_default_links(self):
        """Add default links for linking the device to the modem."""

    def _register_events(self):
        """Add events that are triggered when events are fired from the device."""

    def _register_operating_flags(self):
        """Add operating flags to the device."""
        self._add_operating_flag('bit0', 0, 0, 0, 1)
        self._add_operating_flag('bit1', 0, 1, 2, 3)
        self._add_operating_flag('bit2', 0, 2, 4, 5)
        self._add_operating_flag('bit3', 0, 3, 6, 7)
        self._add_operating_flag('bit4', 0, 4, 8, 9)
        self._add_operating_flag('bit5', 0, 5, 10, 11)
        self._add_operating_flag('bit6', 0, 6, 12, 13)
        self._add_operating_flag('bit7', 0, 6, 14, 15)

    def _add_operating_flag(self, name, group, bit, set_cmd, unset_cmd):
        flag_type = bool if bit is not None else int
        self._operating_flags[name] = OperatingFlag(self._address, name, flag_type)
        flag = self._operating_flags[name]
        self._op_flags_manager.subscribe(flag, flag.load, group, bit,
                                         set_cmd, unset_cmd)

    def _add_property(self, name, data_field, set_cmd, group=0, bit=None):
        prop_type = bool if bit is not None else int
        self._properties[name] = ExtendedProperty(self._address, name, prop_type)
        prop = self._properties[name]
        self._ext_property_manager.subscribe(prop, prop.load, group, data_field, bit, set_cmd)

    def _remove_operating_flag(self, name, group):
        self._op_flags_manager.unsubscribe(name, group)
        self._operating_flags.pop(name)

    def _handle_product_data(self, product_id, cat, subcat):
        """Receive and set the product data information."""
        self._product_id = product_id
        # self._cat = cat
        # self._subcat = subcat


#pylint: disable=no-member
class BatteryDeviceBase():
    """Base class for battery operated devices."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', **kwargs):
        """Init the DeviceBattery class."""
        from ..aldb.aldb_battery import ALDBBattery

        # The super class is the non-battery base class such as OnOffControllerBase
        super(BatteryDeviceBase, self).__init__(address=address, cat=cat, subcat=subcat,
                                                firmware=0x00, description='', model='',
                                                **kwargs)
        self._aldb = ALDBBattery(address=address)
        self._commands_queue = asyncio.Queue()
        pub.subscribe(self._device_awake, self._address.id)
        pub.subscribe(self._load_aldb, '{}.aldb.load'.format(self._address.id))
        pub.subscribe(self._write_aldb, '{}.aldb.write'.format(self._address.id))

    def _run_on_wake(self, command, **kwargs):
        cmd = partial(command, **kwargs)
        self._commands_queue.put_nowait(cmd)

    async def async_get_operating_flags(self):
        """Read the device operating flags."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_get_operating_flags)

    async def async_set_operating_flags(self):
        """Write the operating flags to the device."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_set_operating_flags)

    async def async_get_extended_properties(self):
        """Get the device extended properties."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_get_extended_properties)

    async def async_keep_awake(self, awake_time=0xff):
        """Keep the device awake to ensure commands are heard."""
        cmd = ExtendedSetCommand(self._address)
        return await cmd.async_send(group=0, action=0x04, data3=awake_time)

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Execute the commands that were requested while sleeping."""
        asyncio.ensure_future(self._run_commands())

    async def _run_commands(self):
        from inspect import iscoroutinefunction, iscoroutine
        if not self._commands_queue.empty():
            _LOGGER.debug('Sending commands to battery operated device %s', self._address)
            await self.async_keep_awake()
        while not self._commands_queue.empty():
            command = await self._commands_queue.get()
            if isinstance(command, partial):
                if iscoroutine(command.func) or iscoroutinefunction(command.func):
                    await command()
                else:
                    command()
            elif iscoroutine(command) or iscoroutinefunction(command):
                await command()
            else:
                command()

    def _load_aldb(self, mem_addr, num_recs, refresh, callback):
        cmd = partial(self._aldb.async_load, mem_addr=mem_addr, num_recs=num_recs,
                      refresh=refresh, callback=callback)
        self._commands_queue.put_nowait(cmd)

    def _write_aldb(self):
        cmd = partial(self._aldb.async_write_records)
        self._commands_queue.put_nowait(cmd)
