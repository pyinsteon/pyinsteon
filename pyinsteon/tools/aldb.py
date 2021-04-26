"""Command line tools to interact with the Insteon devices."""

from .. import devices
from ..constants import ALDBStatus, DeviceCategory, RAMP_RATES
from ..managers.scene_manager import async_add_device_to_scene
from ..utils import seconds_to_ramp_rate
from .tools_base import ToolsBase
from .advanced import AdvancedTools


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

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=True, match_device=True
        )
        if not addresses:
            return

        if devices[addresses[0]] != devices.modem or len(addresses) > 1:
            if not refresh_yn:
                refresh_yn = await self._get_char(
                    "Clear existing records and reload (y/n)",
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

        if battery_devices:
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
                await devices[address].aldb.async_load(refresh=refresh)

    async def do_print_aldb(self, *args, **kwargs):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb <ADDRESS>|all
        """
        await self._print_aldb(*args)

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

        addresses = await self._get_addresses(
            address=address, allow_all=False, allow_cancel=True, match_device=True
        )
        if not addresses:
            return
        device = devices[addresses[0]]
        self._log_command(f"add_default_links {addresses[0]}")
        await device.async_add_default_links()

    async def do_add_device_to_scene(self, *args, **kwargs):
        """Add a device to a scene.

        Usage:
            add_device_to_scene <ADDRESS> <SCENE NUMBER> [<ON LEVEL>] [<RAMP RATE>] [<BUTTON>] | [Data1] [Data2] [Data3]
        <ADDRESS>: The device address such as 1a.2b.3c
        <SCENE NUMBER>: Value from 25 to 255.

        For Device type 1:
        <ON LEVEL>: (Optional) Value from 0 (off) - 255 (full on).
                    For dimmable devices any number from 0 to 255 is allowable.
                    Default is 255.
        <RAMP RATE>: 0.1 seconds to 480 seconds (8 minutes)
                     Default is 0.5 seconds
        <BUTTON>: (Optional) The button or group number of the device to change as part of the scene.
                    Valid values are device dependant.
                    Default is 1.

        for Device type 2:
        <Data1>: (Optional) Value from 0 (off) - 255 (full on).
                    For on/off devices only 0 and 255 are allowed.
                    Default is 255.
        <Data2>: Data field 2. Default is 0. Typically, this is not used by device type 2.
        <BUTTON>: (Optional) The button or group number of the device to change as part of the scene.
                    Valid values are device dependant.
                    Default is 1.

        For all other device types:
        <Data1>: Data field 1. Any value from 0 - 255 are allowed. Default is 255.
        <Data2>: Data field 2 Any value from 0 - 255 are allowed. Default is 0.
        <Data3>: Data field 3  Any value from 0 - 255 are allowed. Default is 1.

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
            data2 = int(args[3])
        except (IndexError, ValueError):
            data2 = None

        try:
            data3 = int(args[4])
        except (IndexError, ValueError):
            data3 = None

        addresses = await self._get_addresses(
            address=address, allow_all=False, allow_cancel=True, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]

        if not scene:
            scene = await self._get_int(
                "Scene number or blank to cancel", values=range(25, 256),
            )
            if not scene:
                return

        if data1 is None:
            if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                data1 = await self._get_int(
                    "On level", default=255, values=range(0, 256)
                )
            elif device.cat == DeviceCategory.SWITCHED_LIGHTING_CONTROL:
                data1 = await self._get_int("On level", default=255, values=[0, 255])
            else:
                data1 = await self._get_int("Data1", default=255, values=range(0, 255))

        if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
            if data2 is None:
                try:
                    data2_seconds = float(args[3])
                except (IndexError, ValueError):
                    data2_seconds = None
                if data2_seconds is None:
                    data2_seconds = await self._get_float(
                        "Ramp rate", default=0.5, maximum=480, minimum=0.1,
                    )
            else:
                data2_seconds = data2

            data2 = seconds_to_ramp_rate(data2_seconds)
            if RAMP_RATES[data2] != data2_seconds:
                self._log_stdout(
                    f"Ramp rate rounded to {RAMP_RATES[data2]} to conform to standard values."
                )

        elif data2 is None:
            data2 = await self._get_int("Data2", default=0, values=range(0, 255))

        if data3 is None:
            if device.cat in [
                DeviceCategory.DIMMABLE_LIGHTING_CONTROL,
                DeviceCategory.SWITCHED_LIGHTING_CONTROL,
            ]:
                data3 = await self._get_int("Button", default=1, values=range(0, 255))
            else:
                data3 = await self._get_int("Data3", default=0, values=range(0, 255))

        await async_add_device_to_scene(device, scene, data1, data2, data3)

    def do_print_aldb_load_status(self, *args, **kwargs):
        """Print the All-Link databbase load status for all devices."""
        self._log_stdout("")
        self._log_stdout("Device   Status")
        self._log_stdout("-------- ---------------")
        for address in devices:
            self._log_stdout(f"{address} {str(devices[address].aldb.status)}")

    async def do_advanced(self, *args, **kwargs):
        """Enter advanced ALDB menu."""
        self._log_command("advanced")
        await self._call_next_menu(AdvancedTools, "advanced")
