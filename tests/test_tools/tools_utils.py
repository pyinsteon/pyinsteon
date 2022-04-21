"""Utilities used to test tools functions."""
import asyncio
import os
import sys
from io import StringIO
from unittest import TestCase

try:
    from unittest.mock import AsyncMock, MagicMock
except ImportError:
    from unittest.mock import MagicMock
    from .asyncmock_patch import AsyncMock

from pyinsteon.address import Address
from pyinsteon.device_types import (
    PLM,
    ClimateControl_Thermostat,
    DimmableLightingControl,
    DimmableLightingControl_KeypadLinc_8,
    SensorsActuators_IOLink,
)
from pyinsteon.tools.tools_base import _LOGGING, LOG_FILE_NAME
from tests.utils import random_address


class StdInStream(StringIO):
    """Stream to redirect stdin."""

    def __init__(self):
        """Init the StdInStream."""
        super().__init__()
        self.stdin = self

    def not_tty(self):
        """Indicate that this is not a tty device."""

    # pylint: disable=invalid-overridden-method
    async def readline(self):
        """Read a line."""
        await asyncio.sleep(0.5)
        return ""


class StdOutStream:
    """Stream to redirect stdout."""

    def __init__(self):
        """Init the Win32StdoutWriter class."""
        self.buffer = []
        self.stdout = StringIO()

    def write(self, data):
        """Write to standard out."""
        self.buffer.append(data)

    async def drain(self):
        """Drain method used to make StdOutStream look like a stream."""


STDOUT = StdOutStream()


def clean_buffer(buffer, start=0):
    """Remove lines not directed to stdout."""
    new_buffer = []
    for line in buffer:
        line = line[start:]
        if not line.startswith("pyinsteon") and not line.startswith("INPUT"):
            if not new_buffer or line != new_buffer[-1]:
                new_buffer.append(line)
    return new_buffer


def create_device(device_type, address, cat, subcat):
    """Create a device from a device type."""
    return device_type(address, cat, subcat)


def get_curr_dir(curr_file):
    """Return the directory of the current file."""
    return os.path.dirname(os.path.realpath(curr_file))


def remove_log_file(curr_dir):
    """Remove the log file if it exists in the current directory."""
    log_file = os.path.join(curr_dir, LOG_FILE_NAME)
    if os.path.isfile(log_file):
        os.remove(log_file)


def log_file_lines(curr_dir):
    """Return the log file as an array."""
    log_file = os.path.join(curr_dir, LOG_FILE_NAME)
    assert os.path.isfile(log_file)
    with open(log_file) as lfile:
        lines = lfile.readlines()
    return clean_buffer(lines, 48)


async def mock_remove_device_timeout(*args, **kwargs):
    """Mock remove device."""
    raise asyncio.TimeoutError


def get_good_address(devices):
    """Get a good address from devices."""
    for good_address in devices:
        if good_address != devices.modem.address:
            return good_address


def get_bad_address(devices):
    """Get a good address from devices."""
    while True:
        bad_address = random_address()
        if bad_address not in devices:
            return bad_address


class ToolsTestBase(TestCase):
    """Base class for tools tests."""

    test_lock = asyncio.Lock()

    def setup_cmd_tool(
        self, menu, input_values, stdin=None, stdout=None, allow_logging=False
    ):
        """Set up a new instance of the command tools."""

        async def mock_input(*args, **kwargs):
            """Mock the tools _input function."""
            nonlocal input_values
            val = input_values.pop(0)
            if isinstance(val, int):
                await asyncio.sleep(val)
                self.log_to_file("Sending: ")
                return ""
            self.log_to_file(f"Sending: {val}")
            return val

        if allow_logging:
            input_values.insert(0, "log_to_file y .")
            input_values.insert(0, "set_log_level v")

        if stdin is None:
            stdin = StdInStream()
        if stdout is None:
            stdout = STDOUT

        loop = asyncio.get_event_loop()
        cmd_mgr = menu(loop=loop, stdin=stdin, stdout=stdout)
        # pylint: disable=protected-access
        cmd_mgr._input = mock_input
        return cmd_mgr, stdin, stdout

    def log_to_file(self, line, prompt="pyinsteon: "):
        """Log output to log file only."""
        line = f"{prompt}{line}"
        _LOGGING.info(line)


class MockDevices:
    """Mock devices class."""

    def __init__(self):
        """Init the MockDevices class."""

        self._devices = {}
        self.devices_to_add = []

        self.modem = create_device(PLM, "11.22.33", 0x03, 0x01)
        self._devices[self.modem.address] = self.modem

        device1 = create_device(DimmableLightingControl, random_address(), 0x01, 0x02)
        self._devices[device1.address] = device1

        device2 = create_device(
            DimmableLightingControl_KeypadLinc_8, random_address(), 0x01, 0x03
        )
        self._devices[device2.address] = device2

        device3 = create_device(SensorsActuators_IOLink, random_address(), 0x02, 0x04)
        self._devices[device3.address] = device3

        device4 = create_device(ClimateControl_Thermostat, random_address(), 0x07, 0x05)
        self._devices[device4.address] = device4

        # Do not set methods to AyncMock if python version < 3.8
        if sys.version_info[0:2] < (3, 8):
            return

        for addr in self._devices:
            self._devices[addr].aldb.async_load = AsyncMock()

        self.async_save = AsyncMock()
        self.async_load = AsyncMock()
        self.set_id = MagicMock()
        self.async_remove_device = AsyncMock()
        self.add_x10_device = MagicMock()

    def __getitem__(self, address):
        """Return a a device from the device address."""
        return self._devices.get(address)

    def __iter__(self):
        """Return an iterator of device addresses."""
        for address in self._devices:
            yield address

    def __setitem__(self, address, device):
        """Add a device to the device list."""
        if device is None:
            return
        self._devices[Address(address)] = device

    def __len__(self):
        """Return the number of devices."""
        return len(self._devices)

    def get(self, address):
        """Return a device from an address."""
        return self._devices.get(address)

    def pop(self, address):
        """Remove a device from the device list."""
        self._devices.pop(address)

    async def async_add_device(self, *args, address=None, multiple=False, **kwargs):
        """Add devices mock up."""
        if not self.devices_to_add:
            raise asyncio.TimeoutError

        while True:
            yield self.devices_to_add.pop(0)
            await asyncio.sleep(0.1)
            if not self.devices_to_add:
                break


class MockAldb:
    """Mock ALDB."""

    def __init__(self, load_status, *args, **kwargs):
        """Init the MockAldb class."""
        self.records = {}
        self.status = load_status
        self.async_load = AsyncMock()

    def __getitem__(self, mem_addr):
        """Return a record."""
        return self.records.get(mem_addr)

    def __iter__(self):
        """Return an iterator of memory addresses."""
        for mem_addr in self.records:
            yield mem_addr

    def __setitem__(self, mem_addr, record):
        """Add a device to the device list."""
        if record is None:
            return
        self.records[mem_addr] = record

    def __len__(self):
        """Return the number of devices."""
        return len(self.records)

    def get(self, mem_addr):
        """Return a device from an address."""
        return self.records.get(mem_addr)
