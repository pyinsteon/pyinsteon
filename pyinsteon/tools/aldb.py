"""Command line tools to interact with the Insteon devices."""

from .. import devices
from ..constants import ALDBStatus
from .tools_base import ToolsBase
from ..managers.link_manager import async_add_default_links
from ..managers.scene_manager import (
    async_add_device_to_scene,
    async_trigger_scene_on,
    async_trigger_scene_off,
)
from .utils import get_addresses, get_char, get_float, get_int, print_aldb
from ..utils import seconds_to_ramp_rate


class ToolsAldb(ToolsBase):
    """Command class to test interactivity."""

    async def do_load_aldb(self, *args, **kwargs):
        """Load the All-Link Database of a device.

        Usage:
            load_aldb <ADDRESS>|all y|n  Load one or all devices (can be the modem address)
        To clear the current ALDB and reload from the device, enter `y` as the second argment.
        Otherwise enter `n`.
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        try:
            refresh_yn = args[1]
            refresh = refresh_yn.lower() == "y"
        except IndexError:
            refresh_yn = ""

        addresses = get_addresses(
            address=address,
            print_stdout=self._log_stdout,
            allow_cancel=True,
            allow_all=True,
        )
        if not addresses:
            return

        if devices[addresses[0]] != devices.modem or len(addresses) > 1:
            if not refresh_yn:
                refresh_yn = get_char(
                    "Clear existing records and reload (y/n)",
                    print_stdout=self._log_stdout,
                    default="n",
                    values=["y", "n"],
                )
        refresh = refresh_yn.lower() == "y"

        battery_devices = []
        for address in addresses:
            if devices[address].is_battery:
                battery_devices.append(address)
            # Only load the modem ALDB if explicitly asked
            if devices[address] == devices.modem and len(addresses) == 1:
                await devices.modem.aldb.async_load()
            elif devices[address].cat == 0x03:
                pass
            else:
                # tasks.append(devices[address].aldb.async_load(refresh=refresh))
                await devices[address].aldb.async_load(refresh=refresh)

        self._log_stdout("The following devices are battery operated.")
        self._log_stdout("They will load in the background when they wake up.")
        for address in battery_devices:
            self._log_stdout(f"    - {address}")

        # if the device did not load the first time, try one more time with refresh
        for address in addresses:
            if (
                devices[address] != devices.modem
                and devices[address].aldb.status != ALDBStatus.LOADED
                and not devices[address].is_battery
            ):
                await devices[address].aldb.async_load(refresh=True)

    def do_print_aldb(self, *args, **kwargs):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb <ADDRESS>|all
        """
        print_aldb(args, self._log_command, self._log_stdout)

    async def do_add_default_links(self, *args, **kwargs):
        """Add default links between a device and the modem.

        Usage:
            add_default_links <ADDRESS>
        """

        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = get_addresses(
            address=address,
            print_stdout=self._log_stdout,
            allow_all=False,
            allow_cancel=True,
        )
        if not addresses:
            return
        device = devices[addresses[0]]
        self._log_command(f"add_default_links {addresses[0]}")
        await async_add_default_links(device)

    async def do_add_device_to_scene(self, *args, **kwargs):
        """Add a device to a scene.

        Usage:
            add_device_to_scene <ADDRESS> <SCENE NUMBER> [<ON LEVEL>] [<RAMP RATE>] [<BUTTON>]
        <ADDRESS>: The device address such as 1a.2b.3c
        <SCENE NUMBER>: Value from 25 to 255.
        <ON LEVEL>: (Optional) Value from 0 (off) - 255 (full on).
                    For dimmable devices any number from 0 to 255 is allowable.
                    For on/off devices only 0 and 255 are allowed.
                    Default is 255.
        <RAMP RATE>: (Only valid for dimmable devices) 0.1 seconds to 480 seconds (8 minutes)
                    Default is 0.5 seconds
        <BUTTON>: (Optional) The button or group number of the device to change as part of the scene.
                    Valid values are device dependant.
                    Default is 1.

        KeyPadLinc devices will not respond correctly to scenes in this way other than the main power.
        """

        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        try:
            scene = int(args[1])
        except (IndexError, ValueError):
            scene = None

        try:
            data1 = int(args[2])
        except (IndexError, ValueError):
            data1 = None

        try:
            data2_seconds = int(args[3])
        except (IndexError, ValueError):
            data2_seconds = None

        try:
            data3 = int(args[4])
        except (IndexError, ValueError):
            data3 = None

        addresses = get_addresses(
            address=address,
            print_stdout=self._log_stdout,
            allow_all=False,
            allow_cancel=True,
        )
        if not addresses:
            return
        if not scene:
            scene = get_int(
                "Scene number or blank to cancel",
                print_stdout=self._log_stdout,
                values=range(25, 256),
            )
            if not scene:
                return

        if not data1:
            data1 = get_int(
                "On level",
                print_stdout=self._log_stdout,
                default=255,
                values=range(25, 256),
            )

        if not data2_seconds:
            data2_seconds = get_float(
                "Ramp rate",
                print_stdout=self._log_stdout,
                default=0.5,
                maximum=480,
                minimum=0.1,
            )

        if not data3:
            data2_seconds = get_int("Button", print_stdout=self._log_stdout, default=1)

        data2 = seconds_to_ramp_rate(data2_seconds)
        device = devices[addresses[0]]
        await async_add_device_to_scene(device, scene, data1, data2, data3)

    async def do_test_scene_on(self, *args, **kwargs):
        """Test a scene."""

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = get_int(
                "Scene number or blank to cancel",
                print_stdout=self._log_stdout,
                values=range(25, 256),
            )

        if not scene:
            return

        await async_trigger_scene_on(scene)

    async def do_test_scene_off(self, *args, **kwargs):
        """Test a scene."""

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = get_int(
                "Scene number or blank to cancel",
                print_stdout=self._log_stdout,
                values=range(25, 256),
            )

        if not scene:
            return

        await async_trigger_scene_off(scene)

    def do_print_aldb_load_status(self, *args, **kwargs):
        """Print the All-Link databbase load status for a device."""
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = get_addresses(
            address=address,
            print_stdout=self._log_stdout,
            allow_cancel=True,
            allow_all=True,
        )
        if not addresses:
            return

        self._log_stdout("")
        self._log_stdout("Device   Status")
        self._log_stdout("-------- ---------------")
        for address in addresses:
            self._log_stdout(f"{address} {str(devices[address].aldb.status)}")
