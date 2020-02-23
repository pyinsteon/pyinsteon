"""Advanced ALDB tools."""
from binascii import unhexlify

from .. import devices
from ..constants import ALDBStatus, ResponseStatus, LinkStatus
from .tools_base import ToolsBase
from ..managers.link_manager import find_broken_links


class AdvancedTools(ToolsBase):
    """Advanced ALDB tools."""

    async def do_print_aldb(self, *args, **kwargs):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb <ADDRESS>|all
        """
        await self._print_aldb(*args)

    async def do_add_device_link(self, *args, **kwargs):
        """Add a link to a device All-Link Database.

        For modems use the add_im_link command.

        Usage:
            add_device_link address group target c|r [data1 data2 data3]

        address: Address of the device to add the link [0 - 255]
        group: Group number of the link [0 - 255]
        target: The device target the link refers to
        c|r: Controller or responder link type (c=Controller, r=Responder)
        """

        args = args[0].split()
        address = None
        group = None
        target = None
        controller = None
        data1 = None
        data2 = None
        data3 = None
        try:
            address = args[0]
            group = int(args[1])
            target = args[2]
            if args[3].lower() in ["r", "c"]:
                controller = args[3].lower() == "c"
            else:
                controller = None
            data1 = int(args[4])
            data2 = int(args[5])
            data3 = int(args[6])
        except (IndexError, ValueError):
            pass

        address = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False
        )
        if not address:
            return
        device = devices[address]
        if device.aldb.status != ALDBStatus.LOADED:
            self._log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        if not group:
            group = await self._get_int("Group number", values=range(0, 256))

        target = await self._get_addresses(
            address=target,
            allow_cancel=True,
            allow_all=False,
            prompt="Enter link target address",
        )
        if not target:
            return
        if controller is None:
            controller = bool(
                await self._get_char(
                    "Controller or responder (c=Controller, r=Responder)",
                    values=["c", "r"],
                )
                == "c"
            )
        if data1 is None:
            data1 = await self._get_int("Data 1", default=0, values=range(0, 256))
        if data2 is None:
            data2 = await self._get_int("Data 2", default=0, values=range(0, 256))
        if data3 is None:
            data3 = await self._get_int("Data 3", default=0, values=range(0, 256))

        c_r = "c" if controller else "r"
        self._log_command(
            f"add_device_link {address} {group} {target} {c_r} {data1} {data2} {data3}"
        )

        device.aldb.add(
            group=group,
            target=target,
            controller=controller,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        result = await device.aldb.write()
        if device.is_battery:
            self._log_command(
                f"Device {device.address} is battery operated. The record will be written when the device wakes up."
            )
        elif result != ResponseStatus.SUCCESS:
            self._log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )
        else:
            self._log_stdout(
                f"The record was successfully writen to device {device.address}"
            )

    async def do_remove_link(self, *args, **kwargs):
        """Remove a link from the All-Link Database."""
        args = args[0].split()
        address = None
        mem_addr = None
        try:
            address = args[0]
            mem_addr_str = args[1]
            mem_addr = int.from_bytes(unhexlify(mem_addr_str), byteorder="big")
        except (IndexError, ValueError):
            pass

        address = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False
        )
        if not address:
            return
        device = devices[address]
        if device.aldb.status != ALDBStatus.LOADED:
            self._log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        if mem_addr is None:
            mem_addr_str = await self._get_int(
                "Memory address of the record to remove (Be very careful!)"
            )
            if mem_addr == "":
                return
            mem_addr = int.from_bytes(unhexlify(mem_addr_str), byteorder="big")

        if device.aldb[mem_addr] is None:
            self._log_stdout(
                f"Record {mem_addr:04x} was not found in the ALDB of device {device.address}."
            )
            return

        self._log_command(f"remove_device_link {address} {mem_addr:04x}")
        device.aldb.remove(mem_addr)
        result = await device.aldb.write()
        if device.is_battery:
            self._log_command(
                f"Device {device.address} is battery operated. The record will be removed when the device wakes up."
            )
        elif result != ResponseStatus.SUCCESS:
            self._log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )
        else:
            self._log_stdout(
                f"The record was successfully removed from the device {device.address}"
            )

    async def do_add_im_link(self, *args, **kwargs):
        """Add a link to the Insteon Modem (IM)."""
        args = args[0].split()
        group = None
        target = None
        controller = None
        data1 = None
        data2 = None
        data3 = None
        try:
            group = int(args[0])
            target = args[1]
            if args[3].lower() in ["r", "c"]:
                controller = args[2].lower() == "c"
            else:
                controller = None
            data1 = int(args[3])
            data2 = int(args[4])
            data3 = int(args[5])
        except (IndexError, ValueError):
            pass

        if devices.modem.aldb.status != ALDBStatus.LOADED:
            self._log_stdout(
                f"The All-Link Database for the Insteon Modem (IM) must be loaded first."
            )
            return

        if not group:
            group = await self._get_int("Group number", values=range(0, 256))

        target = await self._get_addresses(
            address=target,
            allow_cancel=True,
            allow_all=False,
            prompt="Enter link target address",
        )
        if not target:
            return
        if controller is None:
            controller = bool(
                await self._get_char(
                    "Controller or responder (c=Controller, r=Responder)",
                    values=["c", "r"],
                )
                == "c"
            )
        if data1 is None:
            data1 = await self._get_int("Data 1", default=0, values=range(0, 256))
        if data2 is None:
            data2 = await self._get_int("Data 2", default=0, values=range(0, 256))
        if data3 is None:
            data3 = await self._get_int("Data 3", default=0, values=range(0, 256))

        c_r = "c" if controller else "r"
        self._log_command(f"add_im_link {group} {target} {c_r} {data1} {data2} {data3}")

        devices.modem.aldb.add(
            group=group,
            target=target,
            controller=controller,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        result = await devices.modem.aldb.write()
        if result != ResponseStatus.SUCCESS:
            self._log_stdout(
                f"An issue occured writing to the database of the Insteon Modem (IM)."
            )
        else:
            self._log_stdout(
                f"The record was successfully writen to the Insteon Modem (IM)."
            )

    async def do_remove_im_link(self, *args, **kwargs):
        """Remove a link from the Insteon Modem (IM)."""
        args = args[0].split()
        group = None
        target = None
        controller = None
        try:
            group = int(args[0])
            target = args[1]
            if args[3].lower() in ["r", "c"]:
                controller = args[2].lower() == "c"
            else:
                controller = None
        except (IndexError, ValueError):
            pass

        if devices.modem.aldb.status != ALDBStatus.LOADED:
            self._log_stdout(
                f"The All-Link Database for the Insteon Modem (IM) must be loaded first."
            )
            return

        if not group:
            group = await self._get_int("Group number", values=range(0, 256))

        target = await self._get_addresses(
            address=target,
            allow_cancel=True,
            allow_all=False,
            prompt="Enter link target address",
        )
        if not target:
            return
        if controller is None:
            controller = bool(
                await self._get_char(
                    "Controller or responder (c=Controller, r=Responder)",
                    values=["c", "r"],
                )
                == "c"
            )

        c_r = "c" if controller else "r"
        self._log_command(f"remove_im_link {group} {target} {c_r}")

        devices.modem.aldb.remove(group=group, target=target, controller=controller)
        result = await devices.modem.aldb.write()
        if result != ResponseStatus.SUCCESS:
            self._log_stdout(
                f"An issue occured writing to the database of the Insteon Modem (IM)."
            )
        else:
            self._log_stdout(
                f"The record was successfully writen to the Insteon Modem (IM)."
            )

    def do_find_broken_links(self, *args, **kwargs):
        """Find broken links between devices."""
        broken_links = find_broken_links()
        self._log_stdout("Device   Mem Addr Target    Group Mode Status")
        self._log_stdout(
            "-------- -------- --------- ----- ---- ----------------------------------------"
        )
        for address in broken_links:
            for mem_addr in broken_links[address]:
                rec, status = broken_links[address][mem_addr]
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
                self._log_stdout(
                    f"{address:s}     {mem_addr:04x} {rec.target:s} {rec.group:5d}   {mode:s} {status_txt:.40s}"
                )
