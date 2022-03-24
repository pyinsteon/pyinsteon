"""Test the main menu commands."""
import logging
import os
import sys
from unittest import skipIf

try:
    from unittest.mock import AsyncMock, patch
except ImportError:
    from unittest.mock import patch
    from .asyncmock_patch import AsyncMock

import pyinsteon
from pyinsteon.tools import InsteonCmd
from pyinsteon.x10_address import create as create_x10_address
from tests.utils import async_case, random_address

from .tools_utils import (
    MockDevices,
    ToolsTestBase,
    clean_buffer,
    get_bad_address,
    get_curr_dir,
    get_good_address,
    log_file_lines,
    mock_remove_device_timeout,
    remove_log_file,
)

devices = MockDevices()
bad_address = get_bad_address(devices)
good_address = get_good_address(devices)


class TestToolsMainMenu(ToolsTestBase):
    """Test the tools main menu."""

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_help(self):
        """Test the help command of the tools function."""
        async with self.test_lock:
            cmd_mgr, _, stdout = self.setup_cmd_tool(InsteonCmd, ["help", "exit"])
            stdout.buffer = []
            await cmd_mgr.async_cmdloop("")
            buffer = clean_buffer(stdout.buffer)
            assert buffer[1] == "Documented commands (type help <topic>):\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_connect(self):
        """Test the connect command of the tools function."""

        async def mock_failed_connection(*args, **kwargs):
            """Return a failed connection."""
            raise ConnectionError("Connection failed")

        mock_connect = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "async_connect", mock_connect):

                # Failed connection due to no input
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["connect", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Modem information required.\n"
                assert mock_connect.call_count == 0

                # Standard PLM connection using input method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect",
                        "plm",
                        "/some_serial_port_0",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device == "/some_serial_port_0"
                assert mock_connect.call_count == 1

                # PLM connection using command line method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect /some_serial_port_1",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device == "/some_serial_port_1"
                assert mock_connect.call_count == 2

                # Hub connection using prompts method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect",
                        "hub",
                        "myhost",
                        "myusername",
                        "mypassword",
                        "",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert cmd_mgr.port == 25105
                assert mock_connect.call_count == 3

                # Hub connection using command line method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect myhost myusername",
                        "mypassword",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert mock_connect.call_count == 4

                # Hub connection using command line with hub_version method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect myhost myusername 1",
                        "mypassword",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert mock_connect.call_count == 5
                mock_connect.assert_called_with(
                    device=None,
                    host="myhost",
                    port=9761,
                    username="myusername",
                    password="mypassword",
                    hub_version=1,
                )

                # Hub connection using command line method with hub_version and port
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect myhost myusername 1 123",
                        "mypassword",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert mock_connect.call_count == 6
                mock_connect.assert_called_with(
                    device=None,
                    host="myhost",
                    port=123,
                    username="myusername",
                    password="mypassword",
                    hub_version=1,
                )

                # Hub connection using command line method with bad hub_version without port
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect myhost myusername a",
                        "mypassword",
                        "1",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert mock_connect.call_count == 7
                mock_connect.assert_called_with(
                    device=None,
                    host="myhost",
                    port=9761,
                    username="myusername",
                    password="mypassword",
                    hub_version=1,
                )

                # Hub connection using command line method with bad hub_version
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect myhost myusername a 345",
                        "mypassword",
                        "1",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device is None
                assert cmd_mgr.host == "myhost"
                assert mock_connect.call_count == 8
                mock_connect.assert_called_with(
                    device=None,
                    host="myhost",
                    port=345,
                    username="myusername",
                    password="mypassword",
                    hub_version=1,
                )

            with patch.object(
                pyinsteon.tools,
                "async_connect",
                mock_failed_connection,
            ):
                # Failed connection
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "connect /dev/some_device",
                        "exit",
                    ],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                assert cmd_mgr.device == "/dev/some_device"
                buffer = clean_buffer(stdout.buffer)
                assert (
                    buffer[1]
                    == "Connection failed. Please review connection information.\n"
                )

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_disconnect(self):
        """Test the disconnect command."""
        mock_close = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "async_close", mock_close):
                # Failed connection
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "disconnect",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert mock_close.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_device(self):
        """Test adding a device."""
        mock_cancel_linking_mode = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools, "async_cancel_linking_mode", mock_cancel_linking_mode
            ):
                # Add device with manually pressing the set button
                devices.devices_to_add = ["11.22.33"]
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["add_device", "", 10, "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[3] == "Device 11.22.33 was added.\n"

                # Add device with address entered in command line mode
                devices.devices_to_add = ["44.55.66"]
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device 44.55.66",
                        1,
                        "exit",
                    ],
                    stdout=stdout,
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[4] == "Device 44.55.66 was added.\n"

                # Add device with multiple addresses in command line mode
                stdout.buffer = []
                devices.devices_to_add = ["AA.BB.CC", "DD.EE.FF"]
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device m",
                        1,
                        "exit",
                    ],
                    stdout=stdout,
                )
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[3] == "Device AA.BB.CC was added.\n"
                assert buffer[4] == "Device DD.EE.FF was added.\n"

                # Add multiple devices with input mode
                devices.devices_to_add = ["66.77.88", "99.88.77"]
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["add_device", "y", 10, "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[3] == "Device 66.77.88 was added.\n"
                assert buffer[4] == "Device 99.88.77 was added.\n"

                # Add multiple devices with input mode
                devices.devices_to_add = ["66.55.44"]
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["add_device not.a.device", "", 10, "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[3] == "Device 66.55.44 was added.\n"

                # Add devices with timeout error
                devices.devices_to_add = []
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["add_device m", 10, "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[3] == "All-Linking has timed out.\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_list_devices(self):
        """Test the list_devices command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices):
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["list_devices", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address   Cat   Subcat Description\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_log_to_file(self):
        """Test the log_to_file command of the tools function."""
        curr_dir = get_curr_dir(__file__)
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"log_to_file y {curr_dir}", "list_devices", "exit"]
                )
                stdout.buffer = []
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Address   Cat   Subcat Description\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_log_level(self):
        """Test set_log_level tools command."""

        root_logger = logging.getLogger()
        message_logger = logging.getLogger("pyinsteon.messages")
        topic_logger = logging.getLogger("pyinsteon.topics")

        async with self.test_lock:
            # Set log level with input method
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                InsteonCmd, ["set_log_level", "v", "exit"]
            )
            await cmd_mgr.async_cmdloop()
            buffer = clean_buffer(stdout.buffer)
            assert root_logger.level == logging.DEBUG

            # Set invalid value for logging
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                InsteonCmd, ["set_log_level g", "i", "exit"]
            )
            stdout.buffer = []
            await cmd_mgr.async_cmdloop()
            buffer = clean_buffer(stdout.buffer)
            assert buffer[0].startswith("Invalid")
            assert root_logger.level == logging.INFO

            # Set verbose logging
            cmd_mgr, _, _ = self.setup_cmd_tool(InsteonCmd, ["set_log_level v", "exit"])
            await cmd_mgr.async_cmdloop()
            assert root_logger.level == logging.DEBUG

            # Set message logging
            cmd_mgr, _, _ = self.setup_cmd_tool(InsteonCmd, ["set_log_level m", "exit"])
            await cmd_mgr.async_cmdloop()
            assert message_logger.level == logging.DEBUG

            # Set topic logging
            cmd_mgr, _, _ = self.setup_cmd_tool(InsteonCmd, ["set_log_level t", "exit"])
            await cmd_mgr.async_cmdloop()
            assert topic_logger.level == logging.DEBUG

            # Set all logging then clear all logging
            cmd_mgr, _, _ = self.setup_cmd_tool(
                InsteonCmd,
                [
                    "set_log_level v",
                    "set_log_level m",
                    "set_log_level t",
                    "set_log_level i",
                    "exit",
                ],
            )
            await cmd_mgr.async_cmdloop()
            assert root_logger.level == logging.INFO
            assert topic_logger.level == logging.ERROR
            assert message_logger.level == logging.ERROR

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_save_devices(self):
        """Test save_devices tools command."""
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"save_devices {curr_dir}", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert cmd_mgr.workdir == curr_dir
                assert devices.async_save.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_status(self):
        """Test the status tools command."""

        good_device = devices[good_address]
        good_device.groups[1].value = 100

        for address in devices:
            devices[address].async_status = AsyncMock()

        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Get status of good_address using input method without refresh
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["status", str(good_address), "n", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 0

                # Get status of good_address using input method with refresh
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["status", str(good_address), "y", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 1

                # Get status of good_address using input method with refresh=n but value=None
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["status", str(good_address), "n", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = None
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                print(
                    "Here is the buffer \n --------------------------",
                    buffer,
                    "\n--------------------------------",
                )
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 2

                # Get status of good_address using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"status {str(good_address)}", "n", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 2

                # Get status of good_address using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"status {str(good_address)}", "y", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 3

                # Get status of good_address using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"status {str(good_address)} n", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 3

                # Get status of good_address using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"status {str(good_address)} y", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "Address  Group State Name      Value\n"
                assert good_device.async_status.call_count == 4

                # Get status of a bad address using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"status {str(bad_address)} y", "", "exit"]
                )
                stdout.buffer = []
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0].startswith("No device found")
                assert good_device.async_status.call_count == 4

                # Get status of a bad address in background mode
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"log_to_file y {curr_dir}",
                        f"status -b {str(bad_address)} y",
                        "exit",
                    ],
                )
                stdout.buffer = []
                remove_log_file(curr_dir)
                good_device.groups[1].value = 0
                await cmd_mgr.async_cmdloop()
                buffer = log_file_lines(curr_dir)
                assert buffer[0].startswith("No device found")
                assert buffer[1] == "Invalid device address or device not found\n"
                assert good_device.async_status.call_count == 4

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_load_devices(self):
        """Test the load_devices tools command."""
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Load from current dir using inline method
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"load_devices {curr_dir}", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert cmd_mgr.workdir == curr_dir
                assert devices.async_load.call_count == 1

                # Load from bad dir
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices bad_dir", curr_dir, "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert cmd_mgr.workdir == curr_dir
                assert devices.async_load.call_count == 2
                assert buffer[0] == "Invalid working directory\n"
                devices.async_load.assert_called_with(
                    workdir=curr_dir, id_devices=1, load_modem_aldb=1
                )

                # Load from current dir using input method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices", curr_dir, "exit"]
                )
                stdout.buffer = []
                assert cmd_mgr.workdir is None
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert cmd_mgr.workdir == curr_dir
                assert devices.async_load.call_count == 3
                assert buffer[0].startswith("The working directory stores")
                devices.async_load.assert_called_with(
                    workdir=curr_dir, id_devices=1, load_modem_aldb=1
                )

                # Load from current dir passing load_aldb and id_devices using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"load_devices {curr_dir} 0 2", "exit"]
                )
                stdout.buffer = []
                assert cmd_mgr.workdir is None
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert cmd_mgr.workdir == curr_dir
                assert devices.async_load.call_count == 4
                devices.async_load.assert_called_with(
                    workdir=curr_dir, id_devices=0, load_modem_aldb=2
                )

                # Load from current dir passing load_aldb and id_devices using inline method
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices . 0 2", "exit"]
                )
                work_dir = os.getcwd()
                stdout.buffer = []
                assert cmd_mgr.workdir is None
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert cmd_mgr.workdir == work_dir
                assert devices.async_load.call_count == 5
                devices.async_load.assert_called_with(
                    workdir=work_dir, id_devices=0, load_modem_aldb=2
                )

                # Load in background mode with no parameters
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices -b", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert devices.async_load.call_count == 5

                # Load in background mode with bad load_devices
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices -b . 7 0", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert devices.async_load.call_count == 5

                # Load in background mode with bad load_aldb
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, ["load_devices -b . 0 5", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert devices.async_load.call_count == 5

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_device_manually(self):
        """Test the add_device_manually tools command."""
        address = random_address()
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # add device using inline method
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [f"add_device_manually {address} 0x01 0x02 0x03", "exit"],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 1
                devices.set_id.assert_called_with(address, 1, 2, 3)

                # add device using input method
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        str(address),
                        "0x04",
                        "0x05",
                        "0x06",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 2
                devices.set_id.assert_called_with(address, 4, 5, 6)

                # add device using input method
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        str(address),
                        "0x07",
                        "0x08",
                        "0x09",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 3
                devices.set_id.assert_called_with(address, 7, 8, 9)

                # add device using input method with a bad cat value
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        str(address),
                        "p",
                        "0x0a",
                        "0x0b",
                        "0x0c",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 4
                devices.set_id.assert_called_with(address, 10, 11, 12)

                # add device using input method with a bad subcat value
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        str(address),
                        "0x0d",
                        "p",
                        "0x0e",
                        "0x0f",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 5
                devices.set_id.assert_called_with(address, 13, 14, 15)

                # add device using input method with a bad firmware value
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        str(address),
                        "0x10",
                        "0x11",
                        "p",
                        "0x12",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                devices.set_id.assert_called_with(address, 16, 17, 18)

                # add device in background with a bad device cat value
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        f"add_device_manually -b {str(address)} 0x0q 0x01",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0].startswith("Invalid device cat")

                # add device in background with a bad device address
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        "add_device_manually -b not.an.address 0x0a 0x01",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0].startswith("Address required.\n")

                # add device in background without a device cat
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        f"add_device_manually -b {str(address)}",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0].startswith(
                    "Missing arguments required to run in background"
                )

                # add device in background without a device subcat
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        f"add_device_manually -b {str(address)} 0x01",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0].startswith(
                    "Missing arguments required to run in background"
                )

                # add device without address
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_device_manually",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0].startswith("Address required.\n")

                # add device with bad subcat
                address = random_address()
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        f"add_device_manually -b {address} 0x01 xy 0x03",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device subcategory.\n"

                # add device with bad firmware
                address = random_address()
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "set_log_level v",
                        f"log_to_file y {curr_dir}",
                        f"add_device_manually -b {address} 0x01 0x02 xy",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device firmware.\n"

                # add device with input mode and not cat
                address = random_address()
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_device_manually {address}",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6

                # add device with input mode and not subcat
                address = random_address()
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_device_manually {address} 0x02",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6

                # add device with input mode and not firmware
                address = random_address()
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_device_manually {address}",
                        "0x02",
                        "0x03",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.set_id.call_count == 6

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_remove_device(self):
        """Test the add_device_manually tools command."""
        mock_unlink_devices = AsyncMock()
        mock_cancel_linking_mode = AsyncMock()

        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ), patch.object(
                pyinsteon.tools, "async_unlink_devices", mock_unlink_devices
            ), patch.object(
                pyinsteon.tools, "async_cancel_linking_mode", mock_cancel_linking_mode
            ):
                # Remove dead device using command line mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device {str(bad_address)} f", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 1

                # Remove dead device using input mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, ["remove_device", str(bad_address), "f", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 2

                # Enter dead device using input mode but without force (nothing should happen)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, ["remove_device", str(bad_address), "", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 2

                # Enter dead device using background mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device -b {str(bad_address)} f", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 3

                # Enter dead device using background mode without address (Nothing should happen)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, ["remove_device -b", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 3

                # Enter dead device using background mode without force (Nothing should happen)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device -b {str(bad_address)}", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 3

                mock_unlink_devices.call_count = 0
                # Remove known device using command line mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device {str(good_address)}", 1, "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 0
                assert devices.async_remove_device.call_count == 1

                mock_unlink_devices.call_count = 0
                # Remove known device using input mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, ["remove_device", str(good_address), 1, "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 0
                assert devices.async_remove_device.call_count == 2

                mock_unlink_devices.call_count = 0
                # Remove known device using bakcground mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device -b {str(good_address)}", 1, "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 0
                assert devices.async_remove_device.call_count == 3

                mock_unlink_devices.call_count = 0
                # Remove known device using command line mode with force
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device {str(good_address)} f", 1, "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 1
                assert devices.async_remove_device.call_count == 3

                # Remove known device using command line mode with force
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd, ["remove_device -b not.a.device", "exit"]
                )
                await cmd_mgr.async_cmdloop()
                assert mock_unlink_devices.call_count == 1
                assert devices.async_remove_device.call_count == 3

                # Remove known device with timeout
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    InsteonCmd, [f"remove_device {str(good_address)}", 1, "exit"]
                )
                stdout.buffer = []
                devices.async_remove_device = mock_remove_device_timeout
                await cmd_mgr.async_cmdloop()
                buffer = clean_buffer(stdout.buffer)
                assert buffer[0] == "No device was removed due to a timeout error.\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_x10_device(self):
        """Test the add_device_manually tools command."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # add dimmable x10 device using input method
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                steps = 10
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        addr.housecode,
                        str(addr.unitcode),
                        x10_type,
                        str(steps),
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 1
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, steps, 255
                )

                # add on_off x10 device using input method
                addr = create_x10_address("a", 3)
                x10_type = "on_off"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        addr.housecode,
                        str(addr.unitcode),
                        x10_type,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 2
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add sensor x10 device using input method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        addr.housecode,
                        str(addr.unitcode),
                        x10_type,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 3
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add incorrect x10 device type using input method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        addr.housecode,
                        str(addr.unitcode),
                        "not_a_type",
                        x10_type,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 4
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add incorrect x10 device housecode us1ing input method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        "z",
                        addr.housecode,
                        str(addr.unitcode),
                        x10_type,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 5
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add incorrect x10 device unitcode us1ing input method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        addr.housecode,
                        "300",
                        str(addr.unitcode),
                        x10_type,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 6
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add incorrect x10 device housecode us1ing background method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [f"add_x10_device -b z {str(addr.unitcode)} {x10_type}", "exit"],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 6

                # add incorrect x10 device unitcode us1ing background method
                addr = create_x10_address("a", 3)
                x10_type = "sensor"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [f"add_x10_device -b {addr.housecode} 300 {x10_type}", "exit"],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 6

                # add dimmable x10 device us1ing background method witout steps
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_x10_device -b {addr.housecode} {str(addr.unitcode)} {x10_type}",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 7
                devices.add_x10_device.assert_called_with(
                    addr.housecode.lower(), addr.unitcode, x10_type, 22, 255
                )

                # add x10 device us1ing input method without housecode
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        "add_x10_device",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 7

                # add x10 device us1ing input method without unitcode
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_x10_device {addr.housecode}",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 7

                # add x10 device us1ing input method without device type
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_x10_device {addr.housecode} {addr.unitcode}",
                        "",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 7

                # add x10 device us1ing background method without device type
                addr = create_x10_address("a", 3)
                x10_type = "dimmable"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    InsteonCmd,
                    [
                        f"add_x10_device -b {addr.housecode} {addr.unitcode} bad_device_type",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop()
                assert devices.add_x10_device.call_count == 7
