"""Test the commands menu of tools."""
import random
import sys

from unittest import skipIf
try:
    from unittest.mock import patch, AsyncMock
except ImportError:
    from unittest.mock import patch
    from .asyncmock_patch import AsyncMock
import pyinsteon
from pyinsteon.device_types import (
    UnknownDevice,
    DimmableLightingControl_LampLinc,
    SwitchedLightingControl_SwitchLinc,
    SensorsActuators_IOLink,
    ClimateControl_Thermostat,
)
from pyinsteon.tools.commands import ToolsCommands
from tests.utils import async_case, random_address
from .tools_utils import (
    MockDevices,
    ToolsTestBase,
    clean_buffer,
    create_device,
    get_bad_address,
    get_curr_dir,
    log_file_lines,
    remove_log_file,
)

curr_dir = get_curr_dir(__file__)
devices = MockDevices()
device_01 = create_device(
    DimmableLightingControl_LampLinc, random_address(), 0x01, 0x01
)
device_unknown = create_device(UnknownDevice, random_address(), 0x00, 0x00)
device_02 = create_device(
    SwitchedLightingControl_SwitchLinc, random_address(), 0x02, 0x02
)
device_05 = create_device(ClimateControl_Thermostat, random_address(), 0x05, 0x04)
device_07 = create_device(SensorsActuators_IOLink, random_address(), 0x07, 0x03)
devices[device_01.address] = device_01
devices[device_02.address] = device_02
devices[device_05.address] = device_05
devices[device_07.address] = device_07
devices[device_unknown.address] = device_unknown


class TestToolsCommandsMenu(ToolsTestBase):
    """Test the tools commands menu"""

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_on_off(self):
        """Test the on and off commands of the tools function."""
        cmds = ["on", "off"]
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.commands, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for cmd in cmds:
                    # Test on command with input mode
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            cmd,
                            str(device_01.address),
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    if cmd == "on":
                        assert device_01.async_on.call_count == 1
                        device_01.async_on.assert_called_with()
                    else:
                        assert device_01.async_off.call_count == 1
                        device_01.async_off.assert_called_with()

                    # Test on command with command line and background mode
                    for command in [cmd, f"{cmd} -b"]:
                        cmd_mgr, _, _ = self.setup_cmd_tool(
                            ToolsCommands,
                            [
                                f"{command} {device_01.address}",
                                "exit",
                            ],
                        )

                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    if cmd == "on":
                        assert device_01.async_on.call_count == 1
                        device_01.async_on.assert_called_with()
                    else:
                        assert device_01.async_off.call_count == 1
                        device_01.async_off.assert_called_with()

                    # Test on command with input mode with no address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            cmd,
                            "",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1] == "Address is required\n"
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with no address
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b",
                            "",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0].startswith("Missing arguments required to run in background")
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with an address without a device
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b {get_bad_address(devices)}",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0].startswith("No device found with address")
                    assert buffer[1] == "Invalid device address or device not found\n"
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with a bad address
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b not.an.address",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0] == "Invalid device address or device not found\n"
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with a device without on/off commands
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b {device_unknown.address}",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0].startswith("Device cannot be turned")
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_scene_on_off(self):
        """Test the scene_on and scene_off commands of the tools function."""
        cmds = ["scene_on", "scene_off"]
        mock_trigger_scene_on = AsyncMock()
        mock_trigger_scene_off = AsyncMock()
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.commands, "devices", devices
            ), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ), patch.object(
                pyinsteon.tools.commands,
                "async_trigger_scene_on",
                mock_trigger_scene_on,
            ), patch.object(
                pyinsteon.tools.commands,
                "async_trigger_scene_off",
                mock_trigger_scene_off,
            ):
                for cmd in cmds:
                    # Test on command with input mode
                    scene = random.randint(0, 255)
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            cmd,
                            str(scene),
                            "exit",
                        ],
                    )
                    mock_trigger_scene_on.call_count = 0
                    mock_trigger_scene_off.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    if cmd == "scene_on":
                        assert mock_trigger_scene_on.call_count == 1
                        mock_trigger_scene_on.assert_called_with(scene)
                    else:
                        assert mock_trigger_scene_off.call_count == 1
                        mock_trigger_scene_off.assert_called_with(scene)

                    # Test on command with command line and background mode
                    for command in [cmd, f"{cmd} -b"]:
                        scene = random.randint(0, 255)
                        cmd_mgr, _, _ = self.setup_cmd_tool(
                            ToolsCommands,
                            [
                                f"{command} {scene}",
                                "exit",
                            ],
                        )
                        mock_trigger_scene_on.call_count = 0
                        mock_trigger_scene_off.call_count = 0
                        await cmd_mgr.async_cmdloop("")
                        if cmd == "scene_on":
                            assert mock_trigger_scene_on.call_count == 1
                            mock_trigger_scene_on.assert_called_with(scene)
                        else:
                            assert mock_trigger_scene_off.call_count == 1
                            mock_trigger_scene_off.assert_called_with(scene)


                    # Test on command with input mode with no scene number
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            cmd,
                            "",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    stdout.buffer = []
                    mock_trigger_scene_on.call_count = 0
                    mock_trigger_scene_off.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[2] == "Scene number is required\n"
                    assert mock_trigger_scene_on.call_count == 0
                    assert mock_trigger_scene_off.call_count == 0

                    # Test on command with background mode with no scene number
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0].startswith("Missing arguments required to run in background")
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with an invalid scene number
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b x",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0] == "Invalid Scene value\n"
                    assert buffer[1] == "Invalid scene number\n"
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

                    # Test on command with background mode with an invalid scene number
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{cmd} -b 300",
                            "exit",
                        ],
                    )
                    device_01.async_on = AsyncMock()
                    device_01.async_off = AsyncMock()
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0] == "Invalid Scene value\n"
                    assert buffer[1] == "Invalid scene number\n"
                    assert device_01.async_on.call_count == 0
                    assert device_01.async_off.call_count == 0

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_help_commands_menu(self):
        """Test the help command of the commands tools function."""
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.commands, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                    # Test help command with no parameters
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "help",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1] == 'Documented commands (type help <topic>):\n'
                    assert len(buffer) == 8

                    # Test help on the cmd command
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "help cmd",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1].startswith("Run a general device command.")
                    assert len(buffer) == 3

                    # Test help command with a device address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"help cmd {device_01.address}",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1].startswith("Available commands for device")

                    # Test help command with a device address and a method
                    method = "async_on"
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"help cmd {device_01.address} {method}",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[-1].startswith(f"Device {device_01.address} {method} method arguments:")

                    # Test help command with a invalid device address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"help cmd {get_bad_address(devices)}",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1].startswith("No device found with address")
                    assert buffer[2].startswith("Invalid device address")

                    # Test help command with a invalid device address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "help cmd not.an.address",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1].startswith("Invalid device address")

                    # Test help command with a device address and a bad method
                    method = "not_a_method"
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"help cmd {device_01.address} {method}",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[-1] == f"Method {method} not found for device {device_01.address}.\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_cmd(self):
        """Test the cmd command of the commands tools function."""
        mock_method = AsyncMock()

        async def mock_async_on(on_level: int = 0xFF, group: int = 0, fast: bool = False):
            """Mock the async_on command."""
            nonlocal mock_method
            await mock_method(on_level=on_level, group=group, fast=fast)

        async def mock_missing_arg(on_level: int, group: int = 0, fast: bool = False):
            """Mock a command with a required argument."""
            nonlocal mock_method
            await mock_method(on_level=on_level, group=group, fast=fast)

        device_01.async_on = mock_async_on
        device_01.async_off = mock_missing_arg

        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.commands, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                    # Test help command with default arguments
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd",
                            str(device_01.address),
                            "async_on",
                            "",
                            "exit",
                        ],
                    )
                    mock_method.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_method.call_count == 1
                    mock_method.assert_called_with(on_level=255, group=0, fast=False)

                    # Test help command with modified on_level argument
                    on_level = random.randint(0, 255)
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd",
                            str(device_01.address),
                            "async_on",
                            "on_level",
                            str(on_level),
                            "",
                            "exit",
                        ],
                    )
                    mock_method.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_method.call_count == 1
                    mock_method.assert_called_with(on_level=on_level, group=0, fast=False)

                    # Test help command with modified fast argument
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd",
                            str(device_01.address),
                            "async_on",
                            "fast",
                            "y",
                            "",
                            "exit",
                        ],
                    )
                    mock_method.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_method.call_count == 1
                    mock_method.assert_called_with(on_level=255, group=0, fast=True)

                    # Test help command with no address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd",
                            "",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1] == 'Address is required\n'

                    # Test help command with a bad address
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd not.an.address",
                            "",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1] == 'Address is required\n'


                    # Test help command with a bad method
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            f"cmd {device_01.address} not_a_method",
                            "",
                            "exit",
                        ],
                    )
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert buffer[1] == 'Invalid Command value\n'
                    assert buffer[2] == 'A device command is required\n'

                    # Test cmd command with missing required argumetn
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsCommands,
                        [
                            "cmd",
                            str(device_01.address),
                            "async_off",
                            "",
                            "exit",
                        ],
                    )
                    mock_method.call_count = 0
                    stdout.buffer = []
                    await cmd_mgr.async_cmdloop("")
                    buffer = clean_buffer(stdout.buffer)
                    assert mock_method.call_count == 0
                    assert buffer[1].startswith("Command arguments")
                    assert buffer[2].startswith("Missing value for required argument")
