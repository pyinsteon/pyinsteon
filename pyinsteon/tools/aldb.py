"""Command line tools to interact with the Insteon devices."""

from .. import devices
from ..constants import ALDBStatus, DeviceCategory
from ..managers.link_manager import async_link_devices
from ..utils import seconds_to_ramp_rate
from .tools_base import ToolsBase

SHOW_ADVANCED = True


class ToolsAldb(ToolsBase):
    """Command class to test interactivity."""

    async def do_load_aldb(
        self, address, clear=None, log_stdout=None, background=False
    ):
        """Load the All-Link Database of a device.

        Usage:
            load_aldb [--background | -b] address [clear]

        address: Insteon address of a device or `all` for all devices
        clear: Clear the current ALDB records from memory to ensure a full DB read
            y | n  Default n
        """
        ask_clear = address is None and not background
        try:
            addresses = await self._ensure_address(
                address=address,
                name="Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=True,
                match_device=True,
            )
            if not addresses:
                return
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        try:
            refresh = await self._ensure_bool(
                clear, "Clear current records", ask_clear, log_stdout, default=False
            )
        except ValueError:
            log_stdout("An invalid value for `clear` was received")
            return

        battery_devices = []
        for device_address in addresses:
            if devices[device_address].is_battery:
                battery_devices.append(device_address)
            # Only load the modem ALDB if explicitly asked
            if devices[device_address] == devices.modem and len(addresses) == 1:
                await devices.modem.aldb.async_load()
            elif devices[device_address].cat == 0x03:
                pass
            else:
                # tasks.append(devices[device_address].aldb.async_load(refresh=refresh))
                await devices[device_address].aldb.async_load(refresh=refresh)

        if battery_devices:
            log_stdout("The following devices are battery operated.")
            log_stdout("They will load in the background when they wake up.")
        for device_address in battery_devices:
            log_stdout(f"    - {device_address}")

        # if the device did not load the first time, try one more time with refresh
        for device_address in addresses:
            if (
                devices[device_address] != devices.modem
                and devices[device_address].aldb.status != ALDBStatus.LOADED
                and not devices[device_address].is_battery
            ):
                await devices[device_address].aldb.async_load(refresh=True)

    async def do_print_aldb(
        self, address, unused=None, log_stdout=None, background=False
    ):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb  [--background | -b] address | all unused

        address: Insteon address of a device or `all` for all devices
        unused (optional): y | n
        """
        try:
            addresses = await self._ensure_address(
                address=address,
                name="Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addresses:
                return

        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        try:
            unused = await self._ensure_bool(
                unused, "Show Unused", not background, log_stdout, default=False
            )
        except ValueError:
            unused = False
        self._print_aldb_out(addresses, unused, log_stdout)

    async def do_add_default_links(self, address, log_stdout=None, background=False):
        """Add default links between a device and the modem.

        Usage:
            add_default_links [--background | -b] address

        address: Insteon address of a device
        """

        try:
            addresses = await self._ensure_address(
                address=address,
                name="Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addresses:
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        device = devices[address]
        await device.async_add_default_links()

    async def do_add_device_to_scene(
        self,
        address,
        scene,
        data1=None,
        data2=None,
        data3=None,
        log_stdout=None,
        background=False,
    ):
        """Add a device to a scene.

        Usage:
            add_device_to_scene [--background | -b] <ADDRESS> <SCENE NUMBER> [<ON LEVEL>] [<RAMP RATE>] [<BUTTON>] | [Data1] [Data2] [Data3]

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

        for Device type 0x02 (Dimmable lights):
        <ON LEVEL>: (Optional) Value from 0 (off) - 255 (full on).
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

        ask_data_vals = address is None and not background

        try:
            addresses = await self._ensure_address(
                address=address,
                name="Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addresses:
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        device = devices[address]

        try:
            scene = await self._ensure_byte(
                scene, "Scene Number", not background, log_stdout
            )
        except ValueError:
            log_stdout("Invalid scene number")
            return

        # Get data1 value
        try:
            if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                name = "On Level"
                data1 = await self._ensure_byte(
                    data1, name, ask_data_vals, log_stdout, default=255
                )
            elif device.cat == DeviceCategory.SWITCHED_LIGHTING_CONTROL:
                name = "On Level"
                data1 = await self._ensure_int(
                    data1, [0, 255], name, ask_data_vals, log_stdout, default=255
                )
            else:
                name = "Data1"
                data1 = await self._ensure_byte(
                    data1, name, ask_data_vals, log_stdout, default=255
                )
        except ValueError:
            log_stdout(f"Invalid value for {name}")
            return

        # Get data2 value
        if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
            name = "Ramp Rate"
            try:
                data2 = await self._ensure_float(
                    data2, 0, 240, name, ask_data_vals, log_stdout, default=0.5
                )
            except ValueError:
                log_stdout("Invalid value for ramp rate")
                return
            data2 = seconds_to_ramp_rate(data2)

        else:
            try:
                data2 = await self._ensure_byte(
                    data2, "Data2", ask_data_vals, log_stdout, default=0
                )
            except ValueError:
                log_stdout("Invalid value for Data2")
                return

        # Get data3
        if device.cat in [
            DeviceCategory.DIMMABLE_LIGHTING_CONTROL,
            DeviceCategory.SWITCHED_LIGHTING_CONTROL,
        ]:
            name = "Button"
        else:
            name = "Data3"
        try:
            data3 = await self._ensure_byte(
                data3, name, ask_data_vals, log_stdout, default=1
            )
        except ValueError:
            log_stdout(f"Invalid value for {name}")
            return

        await async_link_devices(devices.modem, device, scene, data1, data2, data3)

    # pylint: disable=no-self-use
    def do_print_aldb_load_status(self, log_stdout=None, background=False):
        """Print the All-Link databbase load status for all devices.

        Useage:
            print_aldb_load_status [--background | -b]

        """
        log_stdout("")
        log_stdout("Device   Status")
        log_stdout("-------- ---------------")
        for address in devices:
            log_stdout(f"{address} {str(devices[address].aldb.status)}")

    async def menu_advanced(self):
        """Enter advanced ALDB menu."""
        # pylint: disable=import-outside-toplevel
        from .advanced import AdvancedTools

        if not isinstance(self, AdvancedTools):
            await self._call_next_menu(AdvancedTools, "advanced")
