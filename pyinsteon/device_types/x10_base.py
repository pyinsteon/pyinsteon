"""X10 device types."""

from ..aldb.no_aldb import NoALDB
from ..constants import ResponseStatus
from ..x10_address import create


class X10DeviceBase:
    """X10 device base class."""

    def __init__(self, housecode, unitcode):
        """Init the X10DeviceBase class."""

        self._address = create(housecode, unitcode)
        self._aldb = NoALDB(self._address)
        self._description = "Generic X10 device"
        self._model = ""

        self._groups = {}
        self._handlers = {}
        self._managers = {}
        self._events = {}

        self._register_handlers_and_managers()
        self._register_groups()
        self._register_events()
        self._subscribe_to_handelers_and_managers()

    # Public properties
    @property
    def address(self):
        """Return the INSTEON device address."""
        return self._address

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
    def cat(self):
        """Return a fake Insteon device category."""
        return 0xFF

    @property
    def subcat(self):
        """Return a fake Insteon device subcategory."""
        return 0xFF

    @property
    def firmware(self):
        """Return a fake Insteon device firmware."""
        return 0xFF

    @property
    def groups(self):
        """Return the device groups/groups."""
        return self._groups

    @property
    def aldb(self):
        """Return the device All-Link Database."""
        return self._aldb

    @property
    def operating_flags(self):
        """Return the Operating Flags."""
        return {}

    @property
    def properties(self):
        """Return the Extended Properties."""
        return {}

    @property
    def default_links(self):
        """Return the list of default links."""
        return []

    @property
    def is_battery(self):
        """Return True if the device is battery operated."""
        return False

    @property
    def engine_version(self):
        """Return an engine version."""
        return 0

    def status(self, group=None):
        """Get the status of the device."""

    async def async_status(self, group=None):
        """Get the status of the device."""
        return ResponseStatus.SUCCESS

    async def async_read_config(self):
        """Get all configuration settings.

        This command does nothing for X10 devices.

        """
        return ResponseStatus.SUCCESS

    async def async_read_op_flags(self, group=None):
        """Read the device operating flags."""
        return ResponseStatus.SUCCESS

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        return ResponseStatus.SUCCESS

    async def async_read_ext_properties(self):
        """Get the device extended properties."""
        return ResponseStatus.SUCCESS

    async def async_write_ext_properties(self):
        """Write the extended properties."""
        return ResponseStatus.SUCCESS

    async def async_read_product_id(self):
        """Get the product ID."""
        return ResponseStatus.SUCCESS

    async def async_add_default_links(self):
        """Add the default links betweent he modem and the device."""
        return ResponseStatus.SUCCESS

    def _register_handlers_and_managers(self):
        """Register handlers and managers."""

    def _register_groups(self):
        """Register groups."""

    def _register_events(self):
        """Register events."""

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe groups and events to handlers and managers."""
