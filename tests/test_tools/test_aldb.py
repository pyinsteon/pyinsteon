"""Test the ALDB commands."""
import random
import sys
from unittest import skipIf

try:
    from unittest.mock import AsyncMock, patch
except ImportError:
    from unittest.mock import patch
    from .asyncmock_patch import AsyncMock

import pyinsteon
from pyinsteon.constants import ALDBStatus, DeviceCategory
from pyinsteon.device_types import (
    ClimateControl_Thermostat,
    DimmableLightingControl,
    SensorsActuators_IOLink,
    SwitchedLightingControl,
)
from pyinsteon.tools.aldb import ToolsAldb
from pyinsteon.utils import seconds_to_ramp_rate
from tests.utils import async_case, random_address

from .tools_utils import (
    MockAldb,
    MockDevices,
    ToolsTestBase,
    clean_buffer,
    create_device,
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


class TestToolsAldbMenu(ToolsTestBase):
    """Test the tools main menu."""

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_default_links(self):
        """Test the add_default_links command of the tools function."""
        good_device.async_add_default_links = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools.aldb, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Add default links with input mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, ["add_default_links", str(good_address), "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 1

                # Add default links with input mode and a bad device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, ["add_default_links", str(bad_address), "", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 1

                # Add default links with command line mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, [f"add_default_links {good_address}", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 2

                # Add default links with command line mode and a bad device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, [f"add_default_links {bad_address}", "", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 2

                # Add default links with background mode
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, [f"add_default_links -b {good_address}", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 3

                # Add default links with background mode and a bad device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, [f"add_default_links -b {bad_address}", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 3

                # Add default links with background mode and a no device
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, ["add_default_links -b", "exit"]
                )
                await cmd_mgr.async_cmdloop("")
                assert good_device.async_add_default_links.call_count == 3

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_add_device_to_scene(self):
        """Test the add_device_to_scene command of the tools function."""
        device_01 = create_device(DimmableLightingControl, random_address(), 0x01, 0x01)
        device_02 = create_device(SwitchedLightingControl, random_address(), 0x02, 0x02)
        device_05 = create_device(
            ClimateControl_Thermostat, random_address(), 0x05, 0x04
        )
        device_07 = create_device(SensorsActuators_IOLink, random_address(), 0x07, 0x03)
        devices[device_01.address] = device_01
        devices[device_02.address] = device_02
        devices[device_05.address] = device_05
        devices[device_07.address] = device_07

        mock_add_device_to_scene = AsyncMock()
        async with self.test_lock:
            with patch.object(pyinsteon.tools.aldb, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ), patch.object(
                pyinsteon.tools.aldb,
                "async_add_device_to_scene",
                mock_add_device_to_scene,
            ):
                # Add default links with input mode and default values for data1, data2, data3
                for device in [device_01, device_02, device_05, device_07]:
                    scene = random.randint(0, 255)
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsAldb,
                        [
                            "add_device_to_scene",
                            str(device.address),
                            str(scene),
                            "",
                            "",
                            "",
                            "exit",
                        ],
                    )
                    mock_add_device_to_scene.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_add_device_to_scene.call_count == 1
                    if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                        mock_add_device_to_scene.assert_called_with(
                            device, scene, 255, 28, 1
                        )
                    else:
                        mock_add_device_to_scene.assert_called_with(
                            device, scene, 255, 0, 1
                        )

                # Add default links with command line and background mode and default values for data1, data2, data3
                for device in [device_01, device_02, device_05, device_07]:
                    for command in ["add_device_to_scene", "add_device_to_scene -b"]:
                        scene = random.randint(0, 255)
                        cmd_mgr, _, stdout = self.setup_cmd_tool(
                            ToolsAldb,
                            [
                                f"{command} {str(device.address)} {scene}",
                                "exit",
                            ],
                        )
                        mock_add_device_to_scene.call_count = 0
                        await cmd_mgr.async_cmdloop("")
                        assert mock_add_device_to_scene.call_count == 1
                        if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                            mock_add_device_to_scene.assert_called_with(
                                device, scene, 255, 28, 1
                            )
                        else:
                            mock_add_device_to_scene.assert_called_with(
                                device, scene, 255, 0, 1
                            )

                # Add default links with input mode with inputs for data1, data2, data3
                for device in [device_01, device_02, device_05, device_07]:
                    scene = random.randint(0, 255)
                    if device.cat == 0x02:
                        vals = [0, 255]
                        data1 = vals[random.randint(0, 1)]
                    else:
                        data1 = random.randint(0, 255)
                    if device.cat == 0x01:
                        data2 = random.randint(0, 2400) / 10
                    else:
                        data2 = random.randint(0, 255)
                    data3 = random.randint(0, 255)
                    cmd_mgr, _, stdout = self.setup_cmd_tool(
                        ToolsAldb,
                        [
                            "add_device_to_scene",
                            str(device.address),
                            str(scene),
                            str(data1),
                            str(data2),
                            str(data3),
                            "exit",
                        ],
                    )
                    mock_add_device_to_scene.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_add_device_to_scene.call_count == 1
                    if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                        mock_add_device_to_scene.assert_called_with(
                            device, scene, data1, seconds_to_ramp_rate(data2), data3
                        )
                    else:
                        mock_add_device_to_scene.assert_called_with(
                            device, scene, data1, data2, data3
                        )

                # Add default links with command line and background mode with inputs for data1, data2, data3
                for device in [device_01, device_02, device_05, device_07]:
                    for command in ["add_device_to_scene", "add_device_to_scene -b"]:
                        scene = random.randint(0, 255)
                        if device.cat == 0x02:
                            vals = [0, 255]
                            data1 = vals[random.randint(0, 1)]
                        else:
                            data1 = random.randint(0, 255)
                        if device.cat == 0x01:
                            data2 = random.randint(0, 2400) / 10
                        else:
                            data2 = random.randint(0, 255)
                        data3 = random.randint(0, 255)
                        cmd_mgr, _, stdout = self.setup_cmd_tool(
                            ToolsAldb,
                            [
                                f"{command} {device.address} {scene} {data1}  {data2} {data3}",
                                "exit",
                            ],
                        )
                        mock_add_device_to_scene.call_count = 0
                        await cmd_mgr.async_cmdloop("")
                        assert mock_add_device_to_scene.call_count == 1
                        if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                            mock_add_device_to_scene.assert_called_with(
                                device, scene, data1, seconds_to_ramp_rate(data2), data3
                            )
                        else:
                            mock_add_device_to_scene.assert_called_with(
                                device, scene, data1, data2, data3
                            )

                # Add default links with background mode with bad data for data1, data2, data3
                for device in [device_01, device_02, device_05, device_07]:
                    scene = random.randint(0, 255)
                    data1 = ["x", 255, 255]
                    data2 = [255, "x", 255]
                    data3 = [255, 200, "x"]
                    data4 = [300, 255, 255]
                    data5 = [255, 3000, 255]
                    data6 = [255, 255, 300]
                    for data in [data1, data2, data3, data4, data5, data6]:
                        cmd_mgr, _, stdout = self.setup_cmd_tool(
                            ToolsAldb,
                            [
                                f"add_device_to_scene -b {device.address} {scene} {data[0]}  {data[1]} {data[2]}",
                                "exit",
                            ],
                        )
                        mock_add_device_to_scene.call_count = 0
                        await cmd_mgr.async_cmdloop("")
                        assert mock_add_device_to_scene.call_count == 0

                # Add device to scene with no address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb,
                    [
                        "add_device_to_scene",
                        "",
                        "exit",
                    ],
                )
                mock_add_device_to_scene.call_count = 0
                await cmd_mgr.async_cmdloop("")
                assert mock_add_device_to_scene.call_count == 0

                # Add device to scene in background mode with bad address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb,
                    [
                        f"add_device_to_scene -b {bad_address}",
                        "exit",
                    ],
                )
                mock_add_device_to_scene.call_count = 0
                await cmd_mgr.async_cmdloop("")
                assert mock_add_device_to_scene.call_count == 0

                # Add device to scene in background mode with invalid address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb,
                    [
                        "add_device_to_scene -b not.an.address 100",
                        "exit",
                    ],
                )
                mock_add_device_to_scene.call_count = 0
                await cmd_mgr.async_cmdloop("")
                assert mock_add_device_to_scene.call_count == 0

                # Add device to scene in background mode with invalid scene
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb,
                    [
                        f"add_device_to_scene -b {good_address} x",
                        "exit",
                    ],
                )
                mock_add_device_to_scene.call_count = 0
                await cmd_mgr.async_cmdloop("")
                assert mock_add_device_to_scene.call_count == 0

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_print_aldb(self):
        """Test the print_aldb command of the tools function."""
        curr_dir = get_curr_dir(__file__)
        async with self.test_lock:
            with patch.object(pyinsteon.tools.aldb, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Print ALDB with input mode
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsAldb, ["print_aldb", str(good_address), "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert (
                    buffer[2]
                    == "RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3\n"
                )

                # Print ALDB with command line mode
                cmd_mgr, _, stdout = self.setup_cmd_tool(
                    ToolsAldb, [f"print_aldb {good_address}", "exit"]
                )
                stdout.buffer = []
                await cmd_mgr.async_cmdloop("")
                buffer = clean_buffer(stdout.buffer)
                assert (
                    buffer[2]
                    == "RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3\n"
                )

                # Print ALDB with command line and background mode with bad address
                for command in ["print_aldb", "print_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb,
                        [
                            f"log_to_file y {curr_dir}",
                            f"{command} {bad_address}",
                            "",
                            "exit",
                        ],
                    )
                    remove_log_file(curr_dir)
                    await cmd_mgr.async_cmdloop("")
                    buffer = log_file_lines(curr_dir)
                    assert buffer[0].startswith("No device found with address")

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_load_aldb(self):
        """Test the load_aldb command of the tools function."""

        class MockDevice:
            """Mock device with mock ALDB."""

            def __init__(self):
                """Init the MockDevice class."""
                self.address = random_address()
                self.aldb = MockAldb(ALDBStatus.LOADED)
                self.is_battery = True
                self.cat = 0x01
                self.subcat = 0x02

        async with self.test_lock:
            with patch.object(pyinsteon.tools.aldb, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Load ALDB with input mode and default clear
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, ["load_aldb", str(good_address), "", "exit"]
                )
                good_device.aldb.async_load = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert (
                    good_device.aldb.async_load.call_count == 2
                )  # a retry happens when the laod status is not LOADED
                assert good_device.aldb.async_load.await_args_list[0].kwargs == {
                    "refresh": False
                }
                good_device.aldb.async_load.assert_called_with(refresh=True)

                # Load ALDB with input mode and with clear
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, ["load_aldb", str(good_address), "y", "exit"]
                )
                good_device.aldb.async_load = AsyncMock()
                await cmd_mgr.async_cmdloop("")
                assert (
                    good_device.aldb.async_load.call_count == 2
                )  # a retry happens when the laod status is not LOADED
                assert good_device.aldb.async_load.await_args_list[0].kwargs == {
                    "refresh": True
                }
                good_device.aldb.async_load.assert_called_with(refresh=True)

                # Load ALDB with command line and background mode and with default clear
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {good_address}", "exit"]
                    )
                    good_device.aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert (
                        good_device.aldb.async_load.call_count == 2
                    )  # a retry happens when the laod status is not LOADED
                    assert good_device.aldb.async_load.await_args_list[0].kwargs == {
                        "refresh": False
                    }
                    good_device.aldb.async_load.assert_called_with(refresh=True)

                # Load ALDB with command line and background mode and without clear
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {good_address} n", "exit"]
                    )
                    good_device.aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert (
                        good_device.aldb.async_load.call_count == 2
                    )  # a retry happens when the laod status is not LOADED
                    assert good_device.aldb.async_load.await_args_list[0].kwargs == {
                        "refresh": False
                    }
                    good_device.aldb.async_load.assert_called_with(refresh=True)

                # Load ALDB with command line and background mode and with clear
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {good_address} y", "exit"]
                    )
                    good_device.aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert (
                        good_device.aldb.async_load.call_count == 2
                    )  # a retry happens when the laod status is not LOADED
                    assert good_device.aldb.async_load.await_args_list[0].kwargs == {
                        "refresh": True
                    }
                    good_device.aldb.async_load.assert_called_with(refresh=True)

                # Load ALDB with command line and background mode and a bad address
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {bad_address}", "", "exit"]
                    )
                    good_device.aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_load.call_count == 0

                # Load ALDB with command line and background mode and an invalid clear
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {good_address} x", "", "exit"]
                    )
                    good_device.aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    assert good_device.aldb.async_load.call_count == 0

                # Load ALDB with command line and background mode and all devices
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} all", "exit"]
                    )
                    for addr in devices:
                        devices[addr].aldb.async_load = AsyncMock()
                    await cmd_mgr.async_cmdloop("")
                    for addr in devices:
                        if addr == devices.modem.address:
                            assert devices[addr].aldb.async_load.call_count == 0
                        elif devices[addr].aldb.status == ALDBStatus.LOADED:
                            assert devices[addr].aldb.async_load.call_count == 1
                        else:
                            assert devices[addr].aldb.async_load.call_count == 2

                # Load ALDB with command line and background mode and with clear
                mock_device = MockDevice()
                devices[mock_device.address] = mock_device
                for command in ["load_aldb", "load_aldb -b"]:
                    cmd_mgr, _, _ = self.setup_cmd_tool(
                        ToolsAldb, [f"{command} {mock_device.address} y", "exit"]
                    )
                    mock_device.aldb.async_load.call_count = 0
                    await cmd_mgr.async_cmdloop("")
                    assert mock_device.aldb.async_load.call_count == 1  # no retry

                # Load ALDB with modem address
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb, [f"load_aldb {devices.modem.address}", "exit"]
                )
                devices.modem.aldb.async_load.call_count = 0
                await cmd_mgr.async_cmdloop("")
                assert devices.modem.aldb.async_load.call_count == 1
                devices.modem.aldb.async_load.assert_called_with()

    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @skipIf(sys.version_info[0:2] < (3, 8), reason="AsyncMock does not exist for 3.7")
    @async_case
    async def test_print_aldb_load_status(self):
        """Test the print_aldb_load_status command of the tools function."""
        async with self.test_lock:
            with patch.object(pyinsteon.tools.aldb, "devices", devices), patch.object(
                pyinsteon.tools.tools_base, "devices", devices
            ):
                # Print ALDB load status using input and bachground mode
                curr_dir = get_curr_dir(__file__)
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsAldb,
                    [
                        "set_log_level i",
                        f"log_to_file y {curr_dir}",
                        "print_aldb_load_status",
                        "exit",
                    ],
                )
                good_device.aldb.async_load = AsyncMock()
                remove_log_file(curr_dir)
                await cmd_mgr.async_cmdloop("")
                buffer = log_file_lines(curr_dir)
                assert buffer[1] == "Device   Status\n"
