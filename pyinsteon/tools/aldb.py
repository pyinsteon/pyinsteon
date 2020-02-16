"""Command line tools to interact with the Insteon devices."""

import asyncio
import logging
from .. import devices
from ..constants import LinkStatus
from .cmd_base import ToolsBase
from ..managers.link_manager import async_create_default_links, find_broken_links
from ..managers.scene_manager import (
    async_add_device_to_scene,
    async_trigger_scene_on,
    async_trigger_scene_off,
)
from .utils import get_addresses, get_char, get_float, get_int, print_aldb
from ..utils import seconds_to_ramp_rate

_LOGGING = logging.getLogger(__name__)


class ToolsAldb(ToolsBase):
    """Command class to test interactivity."""

    def do_load_aldb(self, *args, **kwargs):
        """Load the All-Link Database of a device.

        Usage:
            load_aldb <ADDRESS> y|n  Load one device (can be the modem address)
            load_aldb all y|n        Load all devices (including the modem)
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
            refresh_yn = None

        tasks = []
        addresses = get_addresses(address=address, allow_cancel=True, allow_all=True)
        if not addresses:
            return

        if devices[addresses[0]] != devices.modem or len(addresses) > 1:
            if not refresh_yn:
                refresh_yn = get_char(
                    "Clear existing records and reload (y/n)",
                    default="n",
                    values=["y", "n"],
                )
        refresh = refresh_yn.lower() == "y"

        for address in addresses:
            if devices[address] == devices.modem:
                self._async_run(devices.modem.aldb.async_load)
            elif devices[address].cat == 0x03:
                pass
            else:
                tasks.append(devices[address].aldb.async_load(refresh=refresh))
        if tasks:
            self._async_run(asyncio.gather, *tasks)

    # pylint: disable=no-self-use
    def do_print_aldb(self, *args, **kwargs):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = get_addresses(address=address, allow_all=True, allow_cancel=True)
        if not addresses:
            return
        self._log_command(f"print_aldb {'all' if len(addresses) > 1 else addresses[0]}")
        for address in addresses:
            device = devices[address]
            print_aldb(device)

    def do_create_default_links(self, *args, **kwargs):
        """Create default links between a device and the modem.

        Usage:
            create_default_links <ADDRESS>
        """

        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = get_addresses(address=address, allow_all=False, allow_cancel=True)
        if not addresses:
            _LOGGING.info("Exiting")
            return
        device = devices[addresses[0]]
        self._log_command(f"create_default_links {addresses[0]}")
        self._async_run(async_create_default_links, device)

    def do_add_device_to_scene(self, *args, **kwargs):
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

        addresses = get_addresses(address=address, allow_all=False, allow_cancel=True)
        if not addresses:
            return
        if not scene:
            scene = get_int("Scene number or blank to cancel", values=range(25, 256))
            if not scene:
                return

        if not data1:
            data1 = get_int("On level", default=255, values=range(25, 256))

        if not data2_seconds:
            data2_seconds = get_float(
                "Ramp rate", default=0.5, maximum=480, minimum=0.1
            )

        if not data3:
            data2_seconds = get_int("Button", default=1)

        data2 = seconds_to_ramp_rate(data2_seconds)
        device = devices[addresses[0]]
        self._async_run(async_add_device_to_scene, device, scene, data1, data2, data3)

    def do_test_scene_on(self, *args, **kwargs):
        """Test a scene."""

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = get_int("Scene number or blank to cancel", range(25, 256))

        if not scene:
            return

        self._async_run(async_trigger_scene_on, scene)

    def do_test_scene_off(self, *args, **kwargs):
        """Test a scene."""

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = get_int("Scene number or blank to cancel", range(25, 256))

        if not scene:
            return

        self._async_run(async_trigger_scene_off, scene)

    def do_find_broken_links(self, *args, **kwargs):
        """Find broken links between devices."""
        broken_links = find_broken_links()
        _LOGGING.info("Device   Target    Group Mode Status")
        _LOGGING.info(
            "-------- --------- ----- ---- ----------------------------------------"
        )
        for address in broken_links:
            for rec, status in broken_links[address]:
                if status == LinkStatus.MISSING_CONTROLLER:
                    status_txt = "Missing controller"
                elif status == LinkStatus.MISSING_RESPONDER:
                    status_txt = "Missing responder"
                elif status == LinkStatus.MISSING_TARGET:
                    status_txt = "Target device not found"
                elif status == LinkStatus.TARGET_DB_NOT_LOADED:
                    status_txt = "Cannot verify - Target ALDB not loaded"
                if rec.is_controller:
                    mode = "C"
                else:
                    mode = "R"
                _LOGGING.info(
                    "%s %s %5d   %s %.40s",
                    address,
                    rec.target,
                    rec.group,
                    mode,
                    status_txt,
                )

    def do_print_aldb_load_status(self, *args, **kwargs):
        """Print the All-Link databbase load status for a device."""
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = get_addresses(address=address, allow_cancel=True, allow_all=True)
        if not addresses:
            return

        _LOGGING.info("")
        _LOGGING.info("Device   Status")
        _LOGGING.info("-------- ---------------")
        for address in addresses:
            _LOGGING.info("%s %s", address, devices[address].aldb.status)
