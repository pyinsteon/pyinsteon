"""Test the config commands."""
import random
import sys
from unittest import skipIf

try:
    from unittest.mock import AsyncMock, patch
except ImportError:
    from unittest.mock import patch
    from .asyncmock_patch import AsyncMock

import pyinsteon
from pyinsteon.config import LED_OFF, ON_LEVEL
from pyinsteon.constants import RelayMode, ResponseStatus, ToggleMode
from pyinsteon.device_types import (
    ClimateControl_Thermostat,
    DimmableLightingControl_KeypadLinc_6,
    DimmableLightingControl_LampLinc,
    SensorsActuators_IOLink,
    SwitchedLightingControl,
    SwitchedLightingControl_SwitchLinc,
)
from pyinsteon.tools.config import ToolsConfig
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
device_01_kpl = create_device(
    DimmableLightingControl_KeypadLinc_6, random_address(), 0x01, 0x02
)
device_02 = create_device(
    SwitchedLightingControl_SwitchLinc, random_address(), 0x02, 0x02
)
device_02_no_config = create_device(
    SwitchedLightingControl, random_address(), 0x02, 0x05
)
device_05 = create_device(ClimateControl_Thermostat, random_address(), 0x05, 0x04)
device_07 = create_device(SensorsActuators_IOLink, random_address(), 0x07, 0x03)
devices[device_01.address] = device_01
devices[device_01_kpl.address] = device_01_kpl
devices[device_02.address] = device_02
devices[device_02_no_config.address] = device_02_no_config
devices[device_05.address] = device_05
devices[device_07.address] = device_07


class TestToolsConfigMenu(ToolsTestBase):
    """Test the tools config menu."""

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_config_value(self):
        """Test the set_config_value command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Set property value with input mode
                on_level = random.randint(0, 255)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        "set_config_value",
                        str(device_01.address),
                        ON_LEVEL,
                        str(on_level),
                        "exit",
                    ],
                )
                device_01.properties[ON_LEVEL].load(0)
                await cmd_mgr.async_cmdloop("")
                assert device_01.properties[ON_LEVEL].new_value == on_level

                # Set operating flag value with input mode
                led_off = bool(random.randint(0, 1))
                led_off_char = "y" if led_off else "n"
                device_01.operating_flags[LED_OFF].load(not led_off)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        "set_config_value",
                        str(device_01.address),
                        LED_OFF,
                        led_off_char,
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert device_01.operating_flags[LED_OFF].new_value == led_off

                # Set property value with command line mode
                on_level = random.randint(0, 255)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"set_config_value {device_01.address} {ON_LEVEL} {on_level}",
                        "exit",
                    ],
                )
                device_01.properties[ON_LEVEL].load(0)
                await cmd_mgr.async_cmdloop("")
                assert device_01.properties[ON_LEVEL].new_value == on_level

                # Set operating flag value with command line mode
                led_off = bool(random.randint(0, 1))
                led_off_char = "y" if led_off else "n"
                device_01.operating_flags[LED_OFF].load(not led_off)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"set_config_value {device_01.address} {LED_OFF} {led_off_char}",
                        "exit",
                    ],
                )
                await cmd_mgr.async_cmdloop("")
                assert device_01.operating_flags[LED_OFF].new_value == led_off

                # Set property value with input mode and bad perperty name
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        "set_config_value",
                        str(device_01.address),
                        "not_a_prop",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1].startswith("Acceptable values")

                # Set property value with input mode and bad perperty value
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        "set_config_value",
                        str(device_01.address),
                        ON_LEVEL,
                        "x",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1].startswith("Invalid Property value")

                # Set property value with input mode with a device without properties
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_config_value", str(device_02_no_config.address), "exit"],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert (
                    buffer[1]
                    == f"Device {device_02_no_config.address} has no configurable settings.\n"
                )

                # Set property value with input mode without an address
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_config_value", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address is required.\n"

                # Set property value with background mode with a bad address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "set_config_value -b not.an.address some_prop y",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Set property value with background mode with a bad property name
                bad_prop = "not_a_prop"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_config_value -b {device_01.address} {bad_prop} y",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert (
                    buffer[1]
                    == f"Flag {bad_prop} not found in device {device_01.address}\n"
                )

                # Set property value with background mode with a bad property value
                bad_prop = "not_a_prop"
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_config_value -b {device_01.address} {ON_LEVEL} y",
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == f"Invalid value for {ON_LEVEL}\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_iolinc_delay(self):
        """Test the set_iolinc_delay command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Set IOLinc delay with input mode
                seconds = random.randint(0, 255)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_iolinc_delay", str(device_07.address), str(seconds), "exit"],
                )
                device_07.async_set_momentary_delay = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert device_07.async_set_momentary_delay.call_count == 1
                device_07.async_set_momentary_delay.assert_called_with(seconds=seconds)

                # Set IOLinc delay with command line and background mode
                for command in ["set_iolinc_delay", "set_iolinc_delay -b"]:
                    seconds = random.randint(0, 255)
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsConfig,
                        [f"{command} {device_07.address} {seconds}", "exit"],
                    )
                    device_07.async_set_momentary_delay = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert device_07.async_set_momentary_delay.call_count == 1
                    device_07.async_set_momentary_delay.assert_called_with(
                        seconds=seconds
                    )

                # Set IOLinc delay with command line mode with no address
                seconds = random.randint(0, 255)
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_iolinc_delay", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address is required\n"

                # Set IOLinc delay with command line mode with no seconds
                seconds = random.randint(0, 255)
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_iolinc_delay", str(device_07.address), "", "exit"],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[2] == "Value for seconds is required\n"

                # Set IOLinc delay with command line mode with a non-IOLinc device
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_iolinc_delay", str(device_01.address), "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Device is not an IOLinc device\n"

                # Set IOLinc delay with background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "set_iolinc_delay -b not.an.address 100",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Set IOLinc delay with background mode with an invalid number for seconds
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_iolinc_delay -b {device_07.address} 300",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid number for seconds\n"

                # Set IOLinc delay with background mode with an invalid number for seconds
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_iolinc_delay -b {device_07.address} x",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid number for seconds\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_get_engine_version(self):
        """Test the get_engine_version command of the tools function."""
        device_01.async_get_engine_version = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Get engine version using input mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig, ["get_engine_version", str(device_01.address), "exit"]
                )
                device_01.async_get_engine_version = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert device_01.async_get_engine_version.call_count == 1

                # Get engine version using background mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig, [f"get_engine_version -b {device_01.address}", "exit"]
                )
                device_01.async_get_engine_version = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert device_01.async_get_engine_version.call_count == 1

                # Get engine version using input mode with failure
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig, ["get_engine_version", str(device_01.address), "exit"]
                )
                device_01.async_get_engine_version = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert device_01.async_get_engine_version.call_count == 1

                # Get engine version using input mode with no address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [f"log_to_file y {curr_dir}", "get_engine_version", "", "exit"],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Address is required\n"

                # Get engine version using background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "get_engine_version -b not.an.address",
                        "",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Get engine version using background mode with all addresses
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "get_engine_version -b all",
                        "",
                        "exit",
                    ],
                )
                for addr in devices:
                    devices[addr].async_get_engine_version = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                for addr in devices:
                    if addr != devices.modem.address:
                        assert devices[addr].async_get_engine_version.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_print_config(self):
        """Test the print_config command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Print config with input mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "print_config",
                        str(device_01.address),
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                device_01.operating_flags[LED_OFF].load(False)
                device_01.operating_flags[LED_OFF].new_value = True
                device_01.properties[ON_LEVEL].load(255)
                device_01.properties[ON_LEVEL].new_value = 100
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[3] == "Operating Flag                  Value\n"
                assert (
                    len(buffer)
                    == len(device_01.operating_flags) + len(device_01.properties) + 9
                )
                for line in buffer:
                    if line.startswith(ON_LEVEL):
                        assert line[len(ON_LEVEL)] == "*"
                    if line.startswith(LED_OFF):
                        assert line[len(LED_OFF)] == "*"

                # Print config with command line and background mode
                for command in ["print_config", "print_config -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsConfig,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{command} {device_02.address}",
                            "exit",
                        ],
                    )
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[2] == "Operating Flag                  Value\n"
                    assert (
                        len(buffer)
                        == len(device_01.operating_flags)
                        + len(device_01.properties)
                        + 7
                    )

                # Print config with command line mode with invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "print_config not.an.address",
                        "",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Address is required\n"

                # Print config with command line mode with invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "print_config -b not.an.address",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_iolinc_mode(self):
        """Test the set_iolinc_mode command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Set IOLinc mode with input mode for all modes
                latching_modes = [0, 1, 2, 3]
                for latching_mode in latching_modes:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsConfig,
                        [
                            "set_iolinc_mode",
                            str(device_07.address),
                            str(latching_mode),
                            "exit",
                        ],
                    )
                    device_07.async_set_relay_mode = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert device_07.async_set_relay_mode.call_count == 1
                    device_07.async_set_relay_mode.assert_called_with(
                        latching_mode=RelayMode(latching_mode)
                    )

                # Set IOLinc mode with command line and background mode
                for command in ["set_iolinc_mode", "set_iolinc_mode -b"]:
                    latching_mode = 1
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsConfig,
                        [f"{command} {device_07.address} {latching_mode}", "exit"],
                    )
                    device_07.async_set_relay_mode = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert device_07.async_set_relay_mode.call_count == 1
                    device_07.async_set_relay_mode.assert_called_with(
                        latching_mode=RelayMode(latching_mode)
                    )

                # Set IOLinc mode with command line mode with no address
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_iolinc_mode", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address is required\n"

                # Set IOLinc mode with command line mode with no latching_mode
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_iolinc_mode", str(device_07.address), "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Value for latching mode is required\n"

                # Set IOLinc mode with command line mode with a non-IOLinc device
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_iolinc_mode", str(device_01.address), "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Device is not an IOLinc device\n"

                # Set IOLinc mode with background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "set_iolinc_mode -b not.an.address 100",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Set IOLinc mode with background mode with an invalid number for seconds
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_iolinc_mode -b {device_07.address} 300",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid value for latching mode\n"

                # Set IOLinc mode with background mode with an invalid number for seconds
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_iolinc_mode -b {device_07.address} x",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid value for latching mode\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_write_config(self):
        """Test the write_config command of the tools function."""
        mock_write_ext_properties_success = AsyncMock(
            return_value=ResponseStatus.SUCCESS
        )
        mock_write_ext_properties_failure = AsyncMock(
            return_value=ResponseStatus.FAILURE
        )
        mock_write_op_flags_success = AsyncMock(return_value=ResponseStatus.SUCCESS)
        mock_write_op_flags_failure = AsyncMock(return_value=ResponseStatus.FAILURE)
        device_01.async_write_ext_properties = mock_write_ext_properties_success
        device_01.async_write_op_flags = mock_write_op_flags_success

        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Write config using input mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "write_config",
                        str(device_01.address),
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Operating flags written\n"
                assert buffer[2] == "Extended properties written\n"

                # Write config using background mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"write_config -b {device_01.address}",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Operating flags written\n"
                assert buffer[1] == "Extended properties written\n"

                # Write config using input mode with failure
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "write_config",
                        str(device_01.address),
                        "exit",
                    ],
                )
                device_01.async_write_ext_properties = mock_write_ext_properties_failure
                device_01.async_write_op_flags = mock_write_op_flags_failure
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Operating flags write error\n"
                assert buffer[2] == "Extended properties write error\n"

                # Write config using input mode with no address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [f"log_to_file y {curr_dir}", "write_config", "", "exit"],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Address is required\n"

                # Write config using background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "write_config -b not.an.address",
                        "",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Write config using background mode with all addresses
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [f"log_to_file y {curr_dir}", "write_config -b all", "", "exit"],
                )
                for addr in devices:
                    devices[addr].async_write_ext_properties = AsyncMock(
                        return_value=ResponseStatus.SUCCESS
                    )
                    devices[addr].async_write_op_flags = AsyncMock(
                        return_value=ResponseStatus.SUCCESS
                    )
                await cmd_mgr.async_cmdloop("")
                for addr in devices:
                    if addr != devices.modem.address:
                        assert devices[addr].async_write_ext_properties.call_count == 1
                        assert devices[addr].async_write_op_flags.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_read_config(self):
        """Test the read_config command of the tools function."""
        mock_read_config_success = AsyncMock(return_value=ResponseStatus.SUCCESS)
        mock_read_config_failure = AsyncMock(return_value=ResponseStatus.FAILURE)
        device_01.async_read_op_flags = mock_read_config_success
        device_01.async_read_ext_properties = mock_read_config_success

        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Write config using input mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "read_config",
                        str(device_01.address),
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[2] == "Operating flags read\n"
                assert buffer[3] == "Extended properties read\n"

                # Write config using background mode with success
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"read_config -b {device_01.address}",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Operating flags read\n"
                assert buffer[2] == "Extended properties read\n"

                # Write config using input mode with failure
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "read_config",
                        str(device_01.address),
                        "exit",
                    ],
                )
                device_01.async_read_op_flags = mock_read_config_failure
                device_01.async_read_ext_properties = mock_read_config_failure
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[2] == "Operating flags read error\n"
                assert buffer[3] == "Extended properties read error\n"

                # Write config using input mode with no address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [f"log_to_file y {curr_dir}", "read_config", "", "exit"],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Address is required\n"

                # Write config using background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "read_config -b not.an.address",
                        "",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Write config using background mode with all addresses
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [f"log_to_file y {curr_dir}", "read_config -b all", "", "exit"],
                )
                for addr in devices:
                    devices[addr].async_read_op_flags = AsyncMock(
                        ResponseStatus.SUCCESS
                    )
                    devices[addr].async_read_ext_properties = AsyncMock(
                        ResponseStatus.SUCCESS
                    )
                await cmd_mgr.async_cmdloop("")
                for addr in devices:
                    if addr != devices.modem.address:
                        assert devices[addr].async_read_ext_properties.call_count == 1
                        assert devices[addr].async_read_op_flags.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_kpl_radio_buttons(self):
        """Test the set_kpl_radio_buttons command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Set toggle mode with input mode for all modes
                button_set = [
                    [3, 4],
                    [3, 5, 6],
                    [3, 4, 5, 6],
                ]
                for buttons in button_set:
                    for button in buttons:
                        input_buttons = [str(button_num) for button_num in buttons]
                        cmd_mgr, _, _ = self.setup_cmd_tool(
                            ToolsConfig,
                            [
                                "set_kpl_radio_buttons",
                                str(device_01_kpl.address),
                                *input_buttons,
                                "",
                                "exit",
                            ],
                        )
                        device_01_kpl.async_set_radio_buttons = AsyncMock()
                        await cmd_mgr.async_cmdloop("")
                        assert device_01_kpl.async_set_radio_buttons.call_count == 1
                        device_01_kpl.async_set_radio_buttons.assert_called_with(
                            buttons=buttons
                        )

                # Set toggle mode with command line and background mode
                for command in ["set_kpl_radio_buttons", "set_kpl_radio_buttons -b"]:
                    for buttons in button_set:
                        input_buttons_str = ""
                        for button in buttons:
                            input_buttons_str = f"{input_buttons_str}{button} "
                        cmd_mgr, _, _ = self.setup_cmd_tool(
                            ToolsConfig,
                            [
                                f"{command} {device_01_kpl.address} {input_buttons_str}",
                                "exit",
                            ],
                        )
                        device_01_kpl.async_set_radio_buttons = AsyncMock()
                        await cmd_mgr.async_cmdloop("")
                        assert device_01_kpl.async_set_radio_buttons.call_count == 1
                        device_01_kpl.async_set_radio_buttons.assert_called_with(
                            buttons=buttons
                        )

                # Set toggle mode with command line mode with no address
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_kpl_radio_buttons", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address is required\n"

                # Set toggle mode with command line mode with no button
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_kpl_radio_buttons", str(device_01_kpl.address), "", "exit"],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "At least two buttons are required\n"

                # Set toggle mode with command line mode with a non-KPL device
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_kpl_radio_buttons", str(device_01.address), "exit"],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Device is not a KeypadLinc\n"

                # Set toggle mode with background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "set_kpl_radio_buttons -b not.an.address 3 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Set toggle mode with background mode with an address without a device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_radio_buttons -b {get_bad_address(devices)} 3 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid device address or device not found\n"

                # Set toggle mode with background mode with an invalid value for button
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_radio_buttons -b {device_01_kpl.address} 300 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid button number\n"

                # Set toggle mode with background mode with an invalid number for button 1
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_radio_buttons -b {device_01_kpl.address} x 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid button number\n"

                # Set toggle mode with background mode with an invalid number for button 2
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_radio_buttons -b {device_01_kpl.address} 3 x",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid button number\n"

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_set_kpl_toggle_mode(self):
        """Test the kpl_toggle_mode command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.config, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Set toggle mode with input mode for all modes
                for toggle_mode in ToggleMode:
                    for button in device_01_kpl.groups:
                        cmd_mgr, _, _ = self.setup_cmd_tool(
                            ToolsConfig,
                            [
                                "set_kpl_toggle_mode",
                                str(device_01_kpl.address),
                                str(button),
                                str(toggle_mode.value),
                                "exit",
                            ],
                        )
                        device_01_kpl.async_set_toggle_mode = AsyncMock()
                        await cmd_mgr.async_cmdloop("")
                        assert device_01_kpl.async_set_toggle_mode.call_count == 1
                        device_01_kpl.async_set_toggle_mode.assert_called_with(
                            button=button, toggle_mode=toggle_mode
                        )

                # Set toggle mode with command line and background mode
                for command in ["set_kpl_toggle_mode", "set_kpl_toggle_mode -b"]:
                    toggle_mode = ToggleMode.TOGGLE
                    button = 3
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsConfig,
                        [
                            f"{command} {device_01_kpl.address} {button} {int(toggle_mode)}",
                            "exit",
                        ],
                    )
                    device_01_kpl.async_set_toggle_mode = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert device_01_kpl.async_set_toggle_mode.call_count == 1
                    device_01_kpl.async_set_toggle_mode.assert_called_with(
                        button=button, toggle_mode=toggle_mode
                    )

                # Set toggle mode with command line mode with no address
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_kpl_toggle_mode", "", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Address is required\n"

                # Set toggle mode with command line mode with no button
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    ["set_kpl_toggle_mode", str(device_01_kpl.address), "", "exit"],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "A button number is required\n"

                # Set toggle mode with command line mode with no toggle mode
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        "set_kpl_toggle_mode",
                        str(device_01_kpl.address),
                        str(button),
                        "",
                        "exit",
                    ],
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "A toggle mode is required\n"

                # Set toggle mode with command line mode with a non-KPL device
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsConfig, ["set_kpl_toggle_mode", str(device_01.address), "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert buffer[1] == "Device is not a KeypadLinc\n"

                # Set toggle mode with background mode with an invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        "set_kpl_toggle_mode -b not.an.address 3 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[0] == "Invalid device address or device not found\n"

                # Set toggle mode with background mode with an address without a device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_toggle_mode -b {get_bad_address(devices)} 3 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid device address or device not found\n"

                # Set toggle mode with background mode with an invalid value for button
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_toggle_mode -b {device_01_kpl.address} 300 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid button number\n"

                # Set toggle mode with background mode with an invalid number for button
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_toggle_mode -b {device_01_kpl.address} x 1",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid button number\n"

                # Set toggle mode with background mode with an invalid number for toggle mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_toggle_mode -b {device_01_kpl.address} 3 x",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid toggle mode\n"

                # Set toggle mode with background mode with an invalid value for toggle mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsConfig,
                    [
                        f"log_to_file y {curr_dir}",
                        f"set_kpl_toggle_mode -b {device_01_kpl.address} 3 7",
                        "exit",
                    ],
                )
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Invalid toggle mode\n"
