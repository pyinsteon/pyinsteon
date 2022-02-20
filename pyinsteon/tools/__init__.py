"""Command line tools to interact with the Insteon devices."""
import asyncio
import os
from binascii import Error as BinasciiError
from binascii import unhexlify
from functools import partial

from .. import async_close, async_connect, devices
from ..address import Address
from ..constants import HC_LOOKUP, UC_LOOKUP
from ..managers.link_manager import async_cancel_linking_mode, async_unlink_devices
from .aldb import ToolsAldb
from .commands import ToolsCommands
from .config import ToolsConfig
from .tools_base import DEFAULT_HUB_PORT, ToolsBase

DEFAULT_HUB_VERSION = 2


async def _add_device_with_yield(log_stdout, address: Address, multiple: bool):
    """Act as a frontend to devices.async_add_device to capture the yielding of addresses."""
    async for address in devices.async_add_device(address=address, multiple=multiple):
        log_stdout(f"Device {str(address)} was added.")


class InsteonCmd(ToolsBase):
    """Command class to test interactivity."""

    def __init__(self, loop, args=None, menu=None, stdin=None, stdout=None):
        """Init the InsteonCmd class."""
        super().__init__(loop, args=args, menu=menu, stdin=stdin, stdout=stdout)
        self._link_mode_lock = asyncio.Lock()
        self._link_queue = asyncio.Queue()

    async def do_connect(
        self,
        device_or_host,
        username=None,
        hub_version=None,
        port=None,
        password=None,
    ):
        """Connect to the Insteon modem.

        Usage:
            connect
            connect device
            connect host username [hub_version [port [password]]]
        """
        if not device_or_host:
            self.device = None
            self.host = None
            self.username = None
            self.hub_version = None
            self.port = None
            password = None
            password = await self._get_connection_params(password)

        elif username is not None:
            self.host = device_or_host
            self.username = username
            if hub_version is not None:
                try:
                    self.hub_version = int(hub_version)
                except ValueError:
                    self._log_stdout("Invalid Hub version")
                    self.hub_version = None
            else:
                self.hub_version = DEFAULT_HUB_VERSION
            if port is not None:
                self.port = port
            elif self.hub_version in [1, 2]:
                self.port = DEFAULT_HUB_PORT[self.hub_version]
            else:
                self.port = None
            if password is None:
                password = await self._get_connection_params(password)
        else:
            self.device = device_or_host

        if not self.device and not self.host:
            self._log_stdout("Modem information required.")
            return

        try:
            await async_connect(
                device=self.device,
                host=self.host,
                port=self.port,
                username=self.username,
                password=password,
                hub_version=self.hub_version,
            )
            connected_to = self.device if self.device else self.host
            self._log_stdout(f"Connected to {connected_to}")
        except ConnectionError:
            self._log_stdout("Connection failed. Please review connection information.")

    # pylint: disable=no-self-use
    async def do_disconnect(self):
        """Close the connection to the modem.

        Usage:
            disconnect
        """
        await async_close()

    async def do_load_devices(
        self,
        workdir=None,
        id_devices=1,
        load_modem_aldb=1,
        log_stdout=None,
        background=False,
    ):
        """Load the devices.

        Usage:
            load_devices [--background | -b] workdir id_devices load_modem_aldb

        workdir: Directory where the saved device file is located (Default is current directory)
        id_devices: Option for handling unknown devices
            0 - Do not ID devices
            1 - ID unknown devices only (default)
            2 - ID all devices
        load_modem_aldb: Option for loading the Modem ALDB
            0 - Do not load
            1 - Load if not loaded from saved file (default)
            2 - Always load
        """

        self.workdir = workdir
        if self.workdir == ".":
            self.workdir = os.getcwd()

        if self.workdir:
            if not os.path.exists(self.workdir):
                log_stdout("Invalid working directory")
                self.workdir = None

        if not self.workdir:
            if background:
                log_stdout("Working directory is required in background mode.")
                return
            self.workdir = await self._get_workdir()

        try:
            id_devices = await self._ensure_int(
                id_devices,
                [0, 1, 2],
                "ID Devices",
                ask_value=not background,
                log_stdout=log_stdout,
                default=1,
            )
        except ValueError:
            log_stdout("Invalid value for `id_devices`")
            return

        try:
            load_modem_aldb = await self._ensure_int(
                load_modem_aldb,
                [0, 1, 2],
                "Load modem ALDB",
                ask_value=not background,
                log_stdout=log_stdout,
                default=1,
            )
        except ValueError:
            log_stdout("Invalid value for `load_modem_aldb`")
            return

        await devices.async_load(
            workdir=self.workdir, id_devices=id_devices, load_modem_aldb=load_modem_aldb
        )
        log_stdout(f"Total devices: {len(devices)}")

    async def menu_aldb(self):
        """Manage device All-Link database."""
        await self._call_next_menu(ToolsAldb, "aldb")

    async def menu_config(self):
        """Manage operational flags and extended properties."""
        await self._call_next_menu(ToolsConfig, "config")

    async def menu_commands(self):
        """Execute device commands."""
        await self._call_next_menu(ToolsCommands, "commands")

    async def do_add_device(self, address_or_multiple=None):
        """Link a device to the modem.

        Usage:
            add_device [<address> | multiple | m]

        <address> (Optional): Insteon address of the device to link
        multiple | m (optional): Add multiple devices at in one session.

        If an address is not provided the device must be put into link mode manually.
        This is done by pressing the set button on the device.

        If the word `multiple` or `m` are provided then the modem will stay in linking mode until
        the `cancel_lihnking` command is entered at the command line or for 3 minutes after
        the last device is linked.

        NOTE: Not all devices respond to a request to link using thier address. For
        any device that does not respond, the device must be put into linking mode
        manually.

        This command cannot be run in the background.
        """
        multiple = address_or_multiple is not None and address_or_multiple[:1] == "m"
        address = None

        if address_or_multiple is None:
            multiple = await self._ensure_bool(
                None,
                "Multiple devices",
                ask_value=True,
                log_stdout=self._log_stdout,
                default="n",
            )

        if not multiple:
            addresses = await self._ensure_address(
                address_or_multiple,
                "Address (optional)",
                ask_value=True,
                log_stdout=self._log_stdout,
                allow_all=False,
                match_device=False,
            )
            if addresses:
                address = addresses[0]

        if address is not None:
            self._log_stdout(f"Attempting to place device {address} into linking mode.")
            self._log_stdout(
                "If the device does not link with the modem within a minute, press the set button on the device."
            )
        else:
            self._log_stdout(
                "Press the set button on the device. Linking will occur in the background."
            )

        self._log_stdout("Press enter to stop linking.")
        link_function = partial(
            _add_device_with_yield,
            log_stdout=self._log_stdout,
            address=address,
            multiple=multiple,
        )
        try:
            await self._start_all_linking(link_function)
        except asyncio.TimeoutError:
            self._log_stdout("All-Linking has timed out.")

    async def do_add_device_manually(
        self, address, cat, subcat, firmware="0x00", log_stdout=None, background=None
    ):
        """Add a device using a cat and subcat.

        Usage:
           add_device_manually [--background | -b] address cat subcat [firmware]

        address: Device address
        cat: Device category (i.e. 05 or 0x05)
        subcat: Device subcategory (i.e. 1f or 0x1f)

        Note: Device cat and subcat are the hex representation and should be at
        least 2 digits. They can be written with or without the hex prefix 0x.

        The cat and subcat can be found in the user manual for the device. The values
        in the user manual are in hex.
        """

        def hex_str_to_int(value):
            """Convert a hex string into an integer."""
            if value[0:2] == "0x":
                value = value[2:]
            byte_val = unhexlify(value)
            return int.from_bytes(byte_val, byteorder="big")

        if subcat is None and not background:
            firmware = None

        try:
            addresses = await self._ensure_address(
                address,
                "Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=False,
                match_device=False,
            )
            if not addresses:
                raise ValueError
            address = addresses[0]
        except (IndexError, ValueError):
            log_stdout("Address required.")
            return

        while True:
            if cat is not None:
                try:
                    cat = hex_str_to_int(cat)
                    break
                except (BinasciiError, TypeError, IndexError, ValueError):
                    if background:
                        log_stdout("Invalid device category.")
                        return
                    cat = None
            cat = await self._input("Device category or enter to cancel (eg: 0x02)")
            if cat == "":
                return

        while True:
            if subcat is not None:
                try:
                    subcat = hex_str_to_int(subcat)
                    break
                except (BinasciiError, TypeError, IndexError, ValueError):
                    if background:
                        log_stdout("Invalid device subcategory.")
                        return
                    subcat = None
            subcat = await self._input(
                "Device subcategory or enter to cancel (eg: 0x02)"
            )
            if subcat == "":
                return

        while True:
            if firmware is not None:
                try:
                    firmware = hex_str_to_int(firmware)
                except (BinasciiError, TypeError, IndexError, ValueError):
                    if background:
                        log_stdout("Invalid device firmware.")
                        return
                    firmware = None
                else:
                    break
            firmware = await self._input(
                "Device firmware or enter to cancel (eg: 0x02)"
            )
            if firmware == "":
                return

        self._log_background(f"Calling with {address} {cat} {subcat} {firmware}")

        devices.set_id(address, cat, subcat, firmware)

    async def do_remove_device(
        self, address=None, force=None, log_stdout=None, background=False
    ):
        """Remove a device.

        Usage:
          remove_device [--background | -b] [address [f|force]]

        address (optional): Device address
        f or force (optional): Force removal.

        This command will perform the following steps:
          - Remove all modem links from the device
          - Unlink the device from the modem
          - Remove all device links from the modem

        The force option is used when the device is no longer available, for example, if it has been removed from the network.
        If the force option is used,  all links will be removed from the modem. This will not attempt to unlink the device or
        remove modem links from the device.
        """

        try:
            addresses = await self._ensure_address(
                address,
                "Address",
                ask_value=not background,
                log_stdout=log_stdout,
                allow_all=False,
                match_device=False,
            )
            if not addresses:
                log_stdout("Device address is required.")
                return
            address = addresses[0]
        except (IndexError, ValueError):
            log_stdout("Invalid Insteon address.")
            return

        device = devices[address]
        if device is None and force is None:
            log_stdout(
                f"Device with address {address} not found. Use force mode to remove links from the modem."
            )
            if background:
                return

        if device is not None and force is None:
            force = ""

        force = await self._ensure_bool(
            force[:1] if force is not None else None,
            "Force",
            ask_value=not background,
            log_stdout=log_stdout,
            true_val="f",
            values=["f", ""],
            default=False,
        )

        if force:
            await async_unlink_devices(devices.modem, address)
            devices[address] = None
            return

        if device is None:
            log_stdout(
                f"Device with address {address} not found. Use force mode to remove links from the modem."
            )
            return

        link_function = partial(devices.async_remove_device, address=address)
        try:
            linked_address = await self._start_all_linking(
                link_function=link_function, background=background
            )
            if linked_address:
                log_stdout(f"Device {linked_address} was removed.")
        except asyncio.TimeoutError:
            log_stdout("No device was removed due to a timeout error.")

    async def do_add_x10_device(
        self, housecode, unitcode, x10_type, steps=22, log_stdout=None, background=False
    ):
        """Add an X10 device.

        Usage:
            add_x10_device [--background | -b] housecode unitcode type [steps]

        houscode: The device housecode (a - p)
        unitcode: The device unitcode (1 - 16)
        type: The device type (on_off, dimmable, sensor)
        steps: Number of steps from off to full on (dimmable only)
        """
        x10_types = ["dimmable", "on_off", "sensor"]
        if housecode is not None:
            housecode = housecode.lower()
        if x10_type is not None:
            x10_type = x10_type.lower()

        if background:
            log_stdout("In background mode")

        try:
            housecode = await self._ensure_string(
                housecode,
                list(HC_LOOKUP.keys()),
                "Housecode",
                ask_value=not background,
                log_stdout=log_stdout,
            )
            if housecode is None:
                return
        except ValueError:
            if background:
                log_stdout("Housecode is required")
            return

        try:
            unitcode = await self._ensure_int(
                unitcode,
                list(UC_LOOKUP.keys()),
                "Unitcode",
                ask_value=not background,
                log_stdout=log_stdout,
            )
            if unitcode is None:
                return
        except ValueError:
            if background:
                log_stdout("Unitcode is required")
            return

        ask_steps = x10_type is None

        try:
            x10_type = await self._ensure_string(
                x10_type,
                x10_types,
                "X10 device type",
                ask_value=not background,
                log_stdout=log_stdout,
            )
            if x10_type is None:
                return
        except ValueError:
            if background:
                log_stdout("X10 devuce type is required")
            return

        if x10_type == "dimmable" and ask_steps:
            steps = await self._ensure_byte(
                None,
                "Dimmer steps",
                ask_value=not background,
                log_stdout=log_stdout,
                default=22,
            )

        devices.add_x10_device(housecode, unitcode, x10_type, steps, 255)

    async def _start_all_linking(self, link_function, background=False):
        """Put the modem into linking mode repeatedly or cancel on timeout."""
        unfinished = []
        result = ""
        if background:
            return await link_function()

        try:
            link_func_task = asyncio.create_task(link_function())
            input_task = asyncio.create_task(self._input())
            finished, unfinished = await asyncio.wait(
                [link_func_task, input_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in finished:
                return task.result()
        finally:
            for task in unfinished:
                task.cancel()
            if unfinished:
                await asyncio.wait(unfinished)
            if result == "":
                self._log_command("Sending cancel command")
                await async_cancel_linking_mode()
            await asyncio.sleep(0.1)


def tools():
    """Start insteon tools."""
    InsteonCmd.start()
