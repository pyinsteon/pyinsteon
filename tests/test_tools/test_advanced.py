"""Test the advanced Advanced commands."""
import asyncio
import os
import random
import sys
from binascii import unhexlify
from unittest import skipIf

try:
    from unittest.mock import AsyncMock, MagicMock, patch
except ImportError:
    from unittest.mock import MagicMock, patch
    from .asyncmock_patch import AsyncMock

import pyinsteon
from pyinsteon.address import Address
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus, AllLinkMode
from pyinsteon.device_types import ClimateControl_WirelessThermostat
from pyinsteon.tools.advanced import AdvancedTools
from tests.utils import async_case, random_address

from .tools_utils import (
    MockDevices,
    ToolsTestBase,
    clean_buffer,
    get_bad_address,
    get_curr_dir,
    get_good_address,
    log_file_lines,
    remove_log_file,
)

devices = MockDevices()
bad_address = get_bad_address(devices)
good_address = get_good_address(devices)
good_device = devices[good_address]

battery_address = random_address()
battery_device = ClimateControl_WirelessThermostat(battery_address, 0x07, 0x00)
battery_device.aldb.remove = MagicMock()
battery_device.aldb.async_write = AsyncMock(return_value=(0, 0))
devices[battery_address] = battery_device

curr_dir = get_curr_dir(__file__)


def check_output(
    mode,
    input_index,
    inline_index,
    input_text,
    background_index,
    background_text,
    stdout_buffer,
    curr_dir,
):
    """Check the output of the command."""
    if mode != "background":
        buffer = clean_buffer(stdout_buffer)
        index = input_index if mode == "input" else inline_index
        assert buffer[index] == input_text
        return

    buffer = log_file_lines(curr_dir)
    assert buffer[background_index] == background_text


def create_tools_commands(mode, command, *inputs, curr_dir=None):
    """Create the mock user input for a tools command."""
    input_args = []
    if mode == "background" and curr_dir:
        input_args.append(f"log_to_file y {curr_dir}")
    if mode == "input":
        input_args.append(command)
        for arg in inputs:
            found_eq = arg.find("=")
            if found_eq >= 0:
                input_args.append(arg[0:found_eq])
                input_args.append(arg[found_eq + 1 :])
            else:
                input_args.append(arg)
            if arg == "":
                break
    append_blank = False
    if mode == "inline" or mode == "background":
        command_in = command
        if mode == "background":
            command_in = f"{command_in} -b"
        for arg in inputs:
            if arg == "":
                if mode == "inline":
                    append_blank = True
                continue
            command_in = f"{command_in} {arg}"
        input_args.append(command_in)
    if append_blank:
        input_args.append("")
    input_args.append("exit")
    return input_args


class TestToolsAdvancedMenu(ToolsTestBase):
    """Test the tools Advanced menu."""

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_enter_linking_mode(self):
        """Test the enter_linking_mode command of the tools function."""
        mock_enter_linking_mode = AsyncMock()
        linking_modes = ["r", "c", "e"]
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ), patch.object(
                pyinsteon.tools.advanced,
                "async_enter_linking_mode",
                mock_enter_linking_mode,
            ):
                for mode in ["input", "inline", "background"]:
                    # Happy path
                    link_mode_in = linking_modes[random.randint(0, 2)]
                    if link_mode_in == "r":
                        link_mode = AllLinkMode.RESPONDER
                    elif link_mode_in == "c":
                        link_mode = AllLinkMode.CONTROLLER
                    else:
                        link_mode = AllLinkMode.EITHER

                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "enter_linking_mode", link_mode_in, str(group)
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    mock_enter_linking_mode.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_enter_linking_mode.call_count == 1
                    mock_enter_linking_mode.assert_called_with(
                        link_mode=link_mode, group=group, address=None
                    )

                    # Add link with no linking mode
                    inputs = create_tools_commands(
                        mode, "enter_linking_mode", "", curr_dir=curr_dir
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    mock_enter_linking_mode.call_count = 0
                    stdout.buffer = []
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    check_output(
                        mode,
                        1,
                        1,
                        "Linking mode is required\n",
                        0,
                        "Missing arguments required to run in background\n",
                        stdout.buffer,
                        curr_dir,
                    )
                    assert mock_enter_linking_mode.call_count == 0

                    # Add default links with no group
                    inputs = create_tools_commands(
                        mode, "enter_linking_mode", link_mode_in, "", curr_dir=curr_dir
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools, inputs, allow_logging=True
                    )
                    mock_enter_linking_mode.call_count = 0
                    stdout.buffer = []
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    check_output(
                        mode,
                        2,
                        2,
                        "Group is required\n",
                        0,
                        "Missing arguments required to run in background\n",
                        stdout.buffer,
                        curr_dir,
                    )
                    assert mock_enter_linking_mode.call_count == 0

                    # Add link with an invalid linking mode
                    inputs = create_tools_commands(
                        mode,
                        "enter_linking_mode",
                        "x",
                        "",
                        str(group),
                        curr_dir=curr_dir,
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                    )
                    mock_enter_linking_mode.call_count = 0
                    stdout.buffer = []
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    check_output(
                        mode,
                        2,
                        2,
                        "Linking mode is required\n",
                        1,
                        "Invalid linking mode\n",
                        stdout.buffer,
                        curr_dir,
                    )
                    assert mock_enter_linking_mode.call_count == 0

                    # Add default links with background mode with an invalid group
                    inputs = create_tools_commands(
                        mode,
                        "enter_linking_mode",
                        link_mode_in,
                        "x",
                        "",
                        curr_dir=curr_dir,
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                    )
                    mock_enter_linking_mode.call_count = 0
                    stdout.buffer = []
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    check_output(
                        mode,
                        3,
                        2,
                        "Group is required\n",
                        1,
                        "Invalid group number\n",
                        stdout.buffer,
                        curr_dir,
                    )
                    assert mock_enter_linking_mode.call_count == 0

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_remove_link(self):
        """Test the remove link command."""
        rec_1 = ALDBRecord(
            0x0FFF, False, 0, devices.modem.address, 3, 2, 1, True, False
        )
        rec_2 = ALDBRecord(0x0FF7, True, 0, good_address, 4, 3, 2, True, False)
        records = {rec_1.mem_addr: rec_1, rec_2.mem_addr: rec_2}

        good_device.aldb.remove = MagicMock()

        mem_addr = "0x0ff7"
        mem_addr_int = int.from_bytes(unhexlify(mem_addr[2:]), byteorder="big")
        bad_mem_addr = "0ff1"

        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "inline", "background"]:
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    # Happy path
                    inputs = create_tools_commands(
                        mode, "remove_link", str(good_address), "0x0ff7"
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 1
                    assert good_device.aldb.async_write.call_count == 1
                    good_device.aldb.remove.assert_called_with((mem_addr_int))

                    # Bad address
                    inputs = create_tools_commands(
                        mode, "remove_link", str(bad_address), "", mem_addr
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Bad memory address
                    inputs = create_tools_commands(
                        mode, "remove_link", str(bad_address), bad_mem_addr, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid address
                    inputs = create_tools_commands(
                        mode, "remove_link", "not.an.address", "", mem_addr
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid memory address
                    inputs = create_tools_commands(
                        mode, "remove_link", str(good_address), "gfcd", ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # No address
                    inputs = create_tools_commands(mode, "remove_link", "")
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # No memory address
                    inputs = create_tools_commands(
                        mode, "remove_link", str(good_address), ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Write fails
                    good_device.aldb.async_write = AsyncMock(return_value=(0, 1))
                    inputs = create_tools_commands(
                        mode,
                        "remove_link",
                        str(good_address),
                        mem_addr,
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 1
                    assert good_device.aldb.async_write.call_count == 1

                    # ALDB not loaded
                    good_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
                    inputs = create_tools_commands(
                        mode,
                        "remove_link",
                        str(good_address),
                        mem_addr,
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.remove.call_count = 0
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert good_device.aldb.remove.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Battery device
                    inputs = create_tools_commands(
                        mode,
                        "remove_link",
                        str(battery_address),
                        mem_addr,
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )

                    battery_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    battery_device.aldb.remove.call_count = 0
                    battery_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert battery_device.aldb.remove.call_count == 1
                    assert battery_device.aldb.async_write.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_export_replace_aldb(self):
        """Test exporting and replacing the ALDB."""
        rec_1 = ALDBRecord(
            0x0FFF, False, 0, devices.modem.address, 3, 2, 1, True, False
        )
        rec_2 = ALDBRecord(0x0FF7, True, 0, good_address, 4, 3, 2, True, False)
        records = {rec_1.mem_addr: rec_1, rec_2.mem_addr: rec_2}
        good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
        default_filename = f"{good_device.address.id}_aldb.json"
        default_file = os.path.join(curr_dir, default_filename)
        aldb_filename = "aldb_export.json"
        aldb_file = os.path.join(curr_dir, aldb_filename)

        def cleanup_files():
            """Remove the temp files."""
            if os.path.isfile(default_file):
                os.remove(default_file)
            if os.path.isfile(aldb_file):
                os.remove(aldb_file)

        async def run_export_tests(mode):
            """Run the export tests."""
            # happy path
            inputs = create_tools_commands(
                mode, "export_aldb", str(good_address), curr_dir, aldb_filename
            )
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=True,
            )
            stdout.buffer = []
            remove_log_file(curr_dir)
            cleanup_files()
            await cmd_mgr.async_cmdloop()
            await asyncio.sleep(0.1)
            assert os.path.isfile(aldb_file)

            # No address
            inputs = create_tools_commands(
                mode, "export_aldb", "", aldb_filename, curr_dir=curr_dir
            )
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=True,
            )
            cleanup_files()
            stdout.buffer = []
            remove_log_file(curr_dir)
            await cmd_mgr.async_cmdloop()
            check_output(
                mode,
                0,
                0,
                "Address is required\n",
                0,
                "Invalid device address or device not found\n",
                stdout.buffer,
                curr_dir,
            )

            # No location
            inputs = create_tools_commands(
                mode, "export_aldb", str(good_address), "", curr_dir=curr_dir
            )
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            cleanup_files()
            stdout.buffer = []
            remove_log_file(curr_dir)
            await cmd_mgr.async_cmdloop()
            await asyncio.sleep(0.1)
            if mode == "background":
                assert os.path.isfile(default_file)
                os.remove(default_file)
            else:
                check_output(
                    mode,
                    2,
                    2,
                    "File location is required\n",
                    None,
                    None,
                    stdout.buffer,
                    None,
                )

            # No filename
            inputs = create_tools_commands(
                mode,
                "export_aldb",
                str(good_address),
                curr_dir,
                "",
                curr_dir=curr_dir,
            )
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            cleanup_files()
            stdout.buffer = []
            remove_log_file(curr_dir)
            cmd_mgr.workdir = None
            await cmd_mgr.async_cmdloop()
            await asyncio.sleep(0.1)
            assert os.path.isfile(default_file)
            os.remove(default_file)

            # Filename is "." (cwd)
            inputs = create_tools_commands(
                mode,
                "export_aldb",
                str(good_address),
                ".",
                aldb_filename,
                curr_dir=curr_dir,
            )
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            cleanup_files()
            stdout.buffer = []
            remove_log_file(curr_dir)
            cmd_mgr.workdir = None
            await cmd_mgr.async_cmdloop()
            await asyncio.sleep(0.1)
            cwd_dir = os.getcwd()
            cwd_file = os.path.join(cwd_dir, aldb_filename)
            assert os.path.isfile(cwd_file)
            os.remove(cwd_file)

        async def run_replace_tests(mode):
            """Run the replace aldb tests."""
            # Happy path
            inputs = create_tools_commands(
                mode,
                "replace_aldb",
                str(new_address),
                curr_dir,
                aldb_filename,
                curr_dir=curr_dir,
            )
            inputs.insert(len(inputs) - 1, "y")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 3  # Includes new HWM

            # Do not confirm
            inputs = create_tools_commands(
                mode,
                "replace_aldb",
                str(new_address),
                curr_dir,
                aldb_filename,
                curr_dir=curr_dir,
            )
            inputs.insert(len(inputs) - 1, "n")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 0

            # No address
            inputs = create_tools_commands(mode, "replace_aldb", "")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 0

            # No location  (No file exists so fail)
            inputs = create_tools_commands(
                mode, "replace_aldb", str(new_address), "", ""
            )
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 0

            # No filename  (No file exists so fail)
            inputs = create_tools_commands(
                mode, "replace_aldb", str(new_address), curr_dir, ""
            )
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 0

            # location is "."  (No file exists so fail)
            inputs = create_tools_commands(
                mode, "replace_aldb", str(new_address), ".", ""
            )
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 0

            # Writing failes fully
            inputs = create_tools_commands(
                mode,
                "replace_aldb",
                str(new_address),
                curr_dir,
                aldb_filename,
                curr_dir=curr_dir,
            )
            inputs.insert(len(inputs) - 1, "y")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            new_device.aldb.async_write = AsyncMock(return_value=(0, 3))
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 3  # Includes new HWM

            # Writing failes partially
            inputs = create_tools_commands(
                mode,
                "replace_aldb",
                str(new_address),
                curr_dir,
                aldb_filename,
                curr_dir=curr_dir,
            )
            inputs.insert(len(inputs) - 1, "y")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            new_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            new_device.aldb.async_write = AsyncMock(return_value=(1, 2))
            await cmd_mgr.async_cmdloop()
            assert len(new_device.aldb.pending_changes) == 3  # Includes new HWM

            # Battery device
            inputs = create_tools_commands(
                mode,
                "replace_aldb",
                str(battery_address),
                curr_dir,
                aldb_filename,
                curr_dir=curr_dir,
            )
            inputs.insert(len(inputs) - 1, "y")
            cmd_mgr, _, _ = self.setup_cmd_tool(
                AdvancedTools,
                inputs,
                allow_logging=False,
            )
            battery_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
            battery_device.aldb.async_write = AsyncMock(return_value=(2, 0))
            await cmd_mgr.async_cmdloop()
            assert len(battery_device.aldb.pending_changes) == 3

        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "inline", "background"]:
                    try:
                        await run_export_tests(mode)
                    finally:
                        if os.path.isfile(default_file):
                            os.remove(default_file)
                        if os.path.isfile(aldb_file):
                            os.remove(aldb_file)

                # Create a new ALDB export to use with importing
                inputs = create_tools_commands(
                    "inline", "export_aldb", str(good_address), curr_dir, aldb_filename
                )
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    AdvancedTools,
                    inputs,
                    allow_logging=False,
                )
                await cmd_mgr.async_cmdloop()
                await asyncio.sleep(0.1)
                assert os.path.isfile(aldb_file)
                new_address = random_address()
                new_device = type(good_device)(new_address, 0x00, 0x00)
                devices[new_address] = new_device

                try:
                    for mode in ["input", "inline"]:
                        await run_replace_tests(mode)
                finally:
                    if os.path.isfile(default_file):
                        os.remove(default_file)
                    if os.path.isfile(aldb_file):
                        os.remove(aldb_file)

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_link(self):
        """Test adding a link."""
        rec_1 = ALDBRecord(
            0x0FFF, False, 0, devices.modem.address, 3, 2, 1, True, False
        )
        rec_2 = ALDBRecord(0x0FF7, True, 0, good_address, 4, 3, 2, True, False)
        records = {rec_1.mem_addr: rec_1, rec_2.mem_addr: rec_2}

        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "inline", "background"]:
                    # happy path
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        str(group),
                        str(target),
                        link_mode,
                        "",
                        "",
                        "",
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 1
                    for mem_addr in good_device.aldb.pending_changes:
                        assert good_device.aldb.pending_changes[mem_addr].group == group
                        assert (
                            good_device.aldb.pending_changes[mem_addr].target == target
                        )
                        assert (
                            good_device.aldb.pending_changes[mem_addr].is_controller
                            == is_controller
                        )
                        assert good_device.aldb.pending_changes[mem_addr].data1 == 0
                        assert good_device.aldb.pending_changes[mem_addr].data2 == 0
                        assert good_device.aldb.pending_changes[mem_addr].data3 == 0

                    # with data values
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    data1 = random.randint(0, 255)
                    data2 = random.randint(0, 255)
                    data3 = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        str(group),
                        str(target),
                        link_mode,
                        str(data1),
                        str(data2),
                        str(data3),
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 1
                    for mem_addr in good_device.aldb.pending_changes:
                        assert good_device.aldb.pending_changes[mem_addr].group == group
                        assert (
                            good_device.aldb.pending_changes[mem_addr].target == target
                        )
                        assert (
                            good_device.aldb.pending_changes[mem_addr].is_controller
                            == is_controller
                        )
                        if mode == "input":
                            assert good_device.aldb.pending_changes[mem_addr].data1 == 0
                            assert good_device.aldb.pending_changes[mem_addr].data2 == 0
                            assert good_device.aldb.pending_changes[mem_addr].data3 == 0
                        else:
                            assert (
                                good_device.aldb.pending_changes[mem_addr].data1
                                == data1
                            )
                            assert (
                                good_device.aldb.pending_changes[mem_addr].data2
                                == data2
                            )
                            assert (
                                good_device.aldb.pending_changes[mem_addr].data3
                                == data3
                            )

                    # No address
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode, "add_link", "", str(group), str(target), link_mode
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # No group
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode, "add_link", str(good_address), ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0

                    # No target
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode, "add_link", str(good_address), str(group), "", link_mode
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0

                    # No link mode
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode, "add_link", str(good_address), str(group), str(target), ""
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid Address
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        "not.an.address",
                        "",
                        str(group),
                        str(target),
                        link_mode,
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid group
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        "x",
                        "",
                        str(target),
                        link_mode,
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # invalid link mode
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        str(group),
                        str(target),
                        "x",
                        "",
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Empty ALDB
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        str(group),
                        str(target),
                        "x",
                        "",
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.EMPTY, {})
                    good_device.aldb.async_write = AsyncMock(return_value=(0, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 0
                    assert good_device.aldb.async_write.call_count == 0

                    # Write error
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(good_address),
                        str(group),
                        str(target),
                        link_mode,
                        "",
                        "",
                        "",
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(0, 1))
                    await cmd_mgr.async_cmdloop()
                    assert len(good_device.aldb.pending_changes) == 1
                    assert good_device.aldb.async_write.call_count == 1

                    # Battery device
                    group = random.randint(0, 255)
                    target = random_address()
                    link_mode = ["c", "r"][random.randint(0, 1)]
                    is_controller = link_mode == "c"
                    inputs = create_tools_commands(
                        mode,
                        "add_link",
                        str(battery_address),
                        str(group),
                        str(target),
                        link_mode,
                        "",
                        "",
                        "",
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    battery_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    battery_device.aldb.async_write = AsyncMock(return_value=(0, 0))
                    await cmd_mgr.async_cmdloop()
                    assert len(battery_device.aldb.pending_changes) == 1
                    assert battery_device.aldb.async_write.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_find_broken_links(self):
        """Test the fine broken links command."""
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "background"]:

                    inputs = create_tools_commands(
                        mode, "find_broken_links", curr_dir=curr_dir
                    )
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    stdout.buffer = []
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    check_output(
                        mode,
                        1,
                        None,
                        "Device   Mem Addr Target    Group Mode Status\n",
                        0,
                        "Device   Mem Addr Target    Group Mode Status\n",
                        stdout.buffer,
                        curr_dir,
                    )

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_cancel_linking_mode(self):
        """Test the cancel_linking_mode command."""
        mock_cancel_linking_mode = AsyncMock()
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced,
                "async_cancel_linking_mode",
                mock_cancel_linking_mode,
            ):
                for mode in ["input", "background"]:

                    inputs = create_tools_commands(mode, "cancel_linking_mode")
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    mock_cancel_linking_mode.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_cancel_linking_mode.call_count == 1

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_find_im_records(self):
        """Test the find_im_records command."""
        call_count = 0

        rec_1 = ALDBRecord(
            0x0FFF, False, 0, devices.modem.address, 3, 2, 1, True, False
        )
        rec_2 = ALDBRecord(0x0FF7, True, 0, good_address, 4, 3, 2, True, False)

        async def mock_find_records(address, group):
            """Mock the find records method."""
            nonlocal call_count, records
            call_count += 1
            for record in records:
                yield record

        devices.modem.aldb.async_find_records = mock_find_records
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "inline", "background"]:
                    # Happy path
                    records = [rec_1, rec_2]
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", str(good_address), str(group)
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 1

                    # No records found
                    records = []
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", str(good_address), str(group)
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 1

                    # No address
                    records = [rec_1, rec_2]
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", "", str(group)
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 0

                    # No group
                    records = [rec_1, rec_2]
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", str(good_address), ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 0

                    # Invalid address
                    records = [rec_1, rec_2]
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", "not.an.address", "", str(group)
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 0

                    # Invalid group
                    records = [rec_1, rec_2]
                    group = random.randint(0, 255)
                    inputs = create_tools_commands(
                        mode, "find_im_records", str(good_address), "x", ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert call_count == 0

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_change_link(self):
        """Test the change_link command.

        "in_use",
        "link_mode",
        "hwm",
        "target",
        "group",
        "data1",
        "data2",
        "data3",
        "force",

        """

        def create_random_change_args():
            """Create the args used in changes."""
            return {
                "in_use": bool(random.randint(0, 1)),
                "is_controller": bool(random.randint(0, 1)),
                "is_hwm": bool(random.randint(0, 1)),
                "target": random_address(),
                "group": random.randint(0, 255),
                "data1": random.randint(0, 255),
                "data2": random.randint(0, 255),
                "data3": random.randint(0, 255),
            }

        def create_random_arg_str(
            in_use, is_controller, is_hwm, target, group, data1, data2, data3
        ):
            bool_options = {True: "y", False: "n"}
            controller_options = {True: "c", False: "r"}
            args = []
            if in_use is not None:
                args.append(f"in_use={bool_options[in_use]}")

            if is_controller is not None:
                args.append(f"link_mode={controller_options[is_controller]}")

            if is_hwm is not None:
                args.append(f"hwm={bool_options[is_hwm]}")

            if target is not None:
                args.append(f"target={target}")

            if group is not None:
                args.append(f"group={group}")

            if data1 is not None:
                args.append(f"data1={data1}")

            if data2 is not None:
                args.append(f"data2={data2}")

            if data3 is not None:
                args.append(f"data3={data3}")

            return args

        rec_1 = ALDBRecord(
            0x0FFF, False, 0, devices.modem.address, 3, 2, 1, True, False
        )
        rec_2 = ALDBRecord(0x0FF7, True, 0, good_address, 4, 3, 2, True, False)
        rec_2 = ALDBRecord(0x0FEF, False, 0, Address("00.00.00"), 0, 0, 0, False, True)
        records = {rec_1.mem_addr: rec_1, rec_2.mem_addr: rec_2}
        async with self.test_lock:
            with patch.object(
                pyinsteon.tools.advanced, "devices", devices
            ), patch.object(pyinsteon.tools.tools_base, "devices", devices):
                for mode in ["input", "inline", "background"]:
                    # Happy path
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0fff", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 1

                    # Write failure
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0fff", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(0, 1))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 1

                    # No address
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", "", "0x0fff", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # No mem_addr
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # No kwargs
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0ff7", ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid address
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", "not.an.address", "0x0fff", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid mem_addr
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "nope", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid kwarg key
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0fff", "bad_arg=1"
                    )
                    if mode == "input":
                        inputs.insert(-2, "")
                    if mode == "inline":
                        inputs.insert(-1, "")
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # Invalid kwarg value
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0fff", "link_mode=1"
                    )
                    if mode == "input":
                        inputs.insert(-2, "")
                    if mode == "inline":
                        inputs.insert(-1, "")
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0

                    # Battery device
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode,
                        "change_link",
                        str(battery_address),
                        "0x0fff",
                        *str_args,
                        "",
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    battery_device.aldb.load_saved_records(ALDBStatus.LOADED, records)
                    battery_device.aldb.async_write = AsyncMock(return_value=(0, 0))
                    battery_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert battery_device.aldb.async_write.call_count == 1

                    # ALDB not loaded
                    kwargs = create_random_change_args()
                    str_args = create_random_arg_str(**kwargs)
                    inputs = create_tools_commands(
                        mode, "change_link", str(good_address), "0x0fff", *str_args, ""
                    )
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        AdvancedTools,
                        inputs,
                        allow_logging=True,
                    )
                    good_device.aldb.load_saved_records(ALDBStatus.PARTIAL, records)
                    good_device.aldb.async_write = AsyncMock(return_value=(1, 0))
                    good_device.aldb.async_write.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_write.call_count == 0
