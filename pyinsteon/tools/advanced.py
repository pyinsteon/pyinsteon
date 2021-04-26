"""Advanced ALDB tools."""
import json
from binascii import unhexlify
from os import path

import aiofiles

from .. import devices
from ..constants import ALDBStatus, LinkStatus
from ..managers.link_manager import find_broken_links
from ..managers.saved_devices_manager import aldb_rec_to_dict, dict_to_aldb_record
from .tools_base import ToolsBase
from ..aldb.aldb_record import ALDBRecord


def _convert_val(val):
    if '"' not in val and "'" not in val:
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                val = val.strip('"').strip("'")
    else:
        val = val.strip('"').strip("'")
    if val in ["y", "c"]:
        return True
    if val in ["n", "r"]:
        return False
    return val


def _parse_record(*args):
    try:
        address = args[0]
        if not devices[address]:
            raise IndexError
    except IndexError:
        return None, None, {}

    try:
        rec_id = args[1]
        mem_addr = int.from_bytes(unhexlify(rec_id), byteorder="big")
    except IndexError:
        return address, None, {}
    except ValueError:
        return address, -1, {}

    kwargs = {}
    for arg in args[2:]:
        kwarg, val = arg.split("=")
        val = _convert_val(val)
        kwargs[kwarg] = val

    return address, mem_addr, kwargs


class AdvancedTools(ToolsBase):
    """Advanced ALDB tools."""

    async def do_print_aldb(self, *args, **kwargs):
        """Print the records in an All-Link Database.

        Usage:
            print_aldb <ADDRESS>|all
        """
        await self._print_aldb(*args)

    async def do_add_link(self, *args, **kwargs):
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

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True,
        )
        if not addresses:
            return
        device = devices[addresses[0]]
        if device.aldb.status != ALDBStatus.LOADED:
            self._log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        if not group:
            group = await self._get_int("Group number", values=range(0, 256))

        targets = await self._get_addresses(
            address=target,
            allow_cancel=True,
            allow_all=False,
            match_device=False,
            prompt="Enter link target address",
        )
        if not targets:
            return
        target = targets[0]
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
        success, _ = await device.aldb.async_write()
        if device.is_battery:
            self._log_command(
                f"Device {device.address} is battery operated. The record will be written when the device wakes up."
            )
        elif success:
            self._log_stdout(
                f"The record was successfully writen to device {device.address}"
            )
        else:
            self._log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )

    async def do_remove_link(self, *args, **kwargs):
        """Remove a link from the All-Link Database.

        Usage:
            remove_link address mem_addr

            address: Address of the device
            mem_addr: Memory address of the link to remove (i.e. 0f7f)
        """
        args = args[0].split()
        address = None
        mem_addr = None
        try:
            address = args[0]
            mem_addr_str = args[1]
            mem_addr = int.from_bytes(unhexlify(mem_addr_str), byteorder="big")
        except (IndexError, ValueError):
            pass

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True,
        )
        if not addresses:
            return
        device = devices[addresses[0]]
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

        self._log_command(f"remove_link {address} {mem_addr:04x}")
        device.aldb.remove(mem_addr)
        success, _ = await device.aldb.async_write()
        if device.is_battery:
            self._log_command(
                f"Device {device.address} is battery operated. The record will be removed when the device wakes up."
            )
        elif success:
            self._log_stdout(
                f"The record was successfully removed from the device {device.address}"
            )
        else:
            self._log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )

    def do_find_broken_links(self, *args, **kwargs):
        """Find broken links between devices."""
        broken_links = find_broken_links(devices)
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
                    f"{str(address)}     {mem_addr:04x} {str(rec.target)} {rec.group:5d}   {mode:s} {status_txt:.40s}"
                )

    async def do_change_link(self, *args, **kwargs):
        """Add a link to a device All-Link Database.

        For modems use the add_im_link command.

        Usage:
            add_device_link address rec_id field=value [field=value field=value]


        address: Address of the device to add the link [0 - 255]
        rec_id: ALDB record id (i.e. 1fff. Can be found with the print_aldb command)

        Field can be any of the following:
            in_use: Should the record be in use
                y: record is active
                n: record is inactive (same as deleting the record)
            mode: Controller or responder link type
                c: Controller
                r: Responder)
            group: Group number of the link [0 - 255]
            target: The address of the device target the link refers to
            data1: Data field 1 [0 - 255]
            data2: Data field 2 [0 - 255]
            data3: Data feild 3 [0 - 255]
            force: Force the write to happen (overrides ALDB load status)
        """

        args = args[0].split()
        address, mem_addr, kwargs = _parse_record(*args)
        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False
        )
        if not addresses:
            return

        if mem_addr is None:
            rec_id = await self._get_char("Record ID (eg. 1fff)")
            try:
                mem_addr = int.from_bytes(unhexlify(rec_id), byteorder="big")
            except ValueError:
                self._log_stdout("Invalid record id")

        device = devices[addresses[0]]
        rec = device.aldb[mem_addr]
        if not rec:
            self._log_stdout(f"All-Link record not found")
            return

        if not kwargs:
            while True:
                arg = await self._get_char(
                    "Enter argument (eg. mode=c). Press enter for last argument",
                    default="",
                )
                if arg == "":
                    break
                kwarg, val = arg.split("=")
                val = _convert_val(val)
                kwargs[kwarg] = val

        for kwarg in kwargs:
            if kwarg not in [
                "in_use",
                "mode",
                "target",
                "group",
                "data1",
                "data2",
                "data3",
            ]:
                self._log_stdout(f"Invalid argument: {kwarg}")
                return

        in_use = (
            kwargs.get("in_use") if kwargs.get("in_use") is not None else rec.is_in_use
        )
        controller = (
            kwargs.get("mode") if kwargs.get("mode") is not None else rec.is_controller
        )
        target = (
            kwargs.get("target") if kwargs.get("target") is not None else rec.target
        )
        group = kwargs.get("group") if kwargs.get("group") is not None else rec.group
        data1 = kwargs.get("data1") if kwargs.get("data1") is not None else rec.data1
        data2 = kwargs.get("data2") if kwargs.get("data2") is not None else rec.data2
        data3 = kwargs.get("data3") if kwargs.get("data3") is not None else rec.data3
        force = kwargs.get("force", False)

        device.aldb.modify(
            mem_addr=mem_addr,
            group=group,
            target=target,
            in_use=in_use,
            controller=controller,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        success, _ = await device.aldb.async_write(force=force)
        if device.is_battery:
            self._log_command(
                f"Device {device.address} is battery operated. The record will be written when the device wakes up."
            )
        elif success:
            self._log_stdout(
                f"The record was successfully writen to device {device.address}"
            )
        else:
            self._log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )

    async def do_export_aldb(self, *args, **kwargs):
        """Export the All-Link Database for a device to a file.

        Usage:
            export_aldb address location [filename]

        address: Address of the device to export
        location: Directory location of where to place the file (use `.` for the current directory).
        filename: Filename of the device. The default file name is address_aldb.json
        """
        args = args[0].split()
        location = None
        filename = None
        try:
            address = args[0]
            try:
                location = args[1]
                filename = args[2]
            except IndexError:
                pass
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True,
        )
        if not addresses:
            return

        address = addresses[0]
        device = devices[address]

        if location is None:
            location = self._get_workdir()

        if filename is None:
            filename = f"{device.address.id}_aldb.json"
            filename = await self._get_char("Filename", default=filename)

        aldb_dict = {}
        for mem in device.aldb:
            rec = device.aldb[mem]
            rec_dict = aldb_rec_to_dict(rec)
            aldb_dict[mem] = rec_dict
        await self._write_aldb_file(aldb_dict, location, filename)

    async def do_replace_aldb(self, *args, **kwargs):
        """Read and replace the device ALDB with the contents of a file.

        Reads a JSON formated file with All-Link Database records and replaces
        the current records in the device. To create the JSON file use the
        `export_aldb` command.

        WARNING: This method is very dangerous and can make your device non-responsive.

        Usage:
            replace_aldb address location [filename]

        address: Address of the device
        location: Directory location of the file (use `.` for the current directory).
        filename: Name of the file to use (default is address_aldb.json)
        """
        args = args[0].split()
        location = None
        filename = None
        try:
            address = args[0]
            try:
                location = args[1]
                filename = args[2]
            except IndexError:
                pass
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True
        )

        if not addresses:
            return

        address = addresses[0]
        device = devices[address]

        if location is None:
            location = self._get_workdir()

        if filename is None:
            filename = f"{device.address.id}_aldb.json"
            filename = await self._get_char("Filename", default=filename)

        aldb_dict = await self._read_device_aldb(location, filename)
        aldb_recs = dict_to_aldb_record(aldb_dict)
        device.aldb.load_saved_records(ALDBStatus.LOADED, aldb_recs)
        last_rec = None
        for mem in device.aldb:
            rec = device.aldb[mem]
            device.aldb[mem] = rec
            last_rec = rec
        if last_rec and not last_rec.is_high_water_mark:
            mem = last_rec.mem_addr - 8
            new_rec = ALDBRecord(mem, False, 0, "00.00.00", 0, 0, 0, False, True, 0, 0)
            device.aldb[mem] = new_rec
        self._log_stdout("Preview of changes:")
        self._print_aldb_out([device.address])
        confirm = await self._get_char("Continue", default="n", values=["y", "n"])
        if confirm == "y":
            done, not_done = await device.aldb.async_write(force=True)

        if not done:
            self._log_stdout("No records were written")
        elif not_done:
            self._log_stdout("Some records not written")
        else:
            self._log_stdout("All records written succesfully")

    async def _write_aldb_file(self, aldb_dict, location, filename):
        device_file = path.join(location, filename)
        try:
            async with aiofiles.open(device_file, "w") as afp:
                out_json = json.dumps(aldb_dict, indent=2)
                await afp.write(out_json)
                await afp.flush()
        except FileNotFoundError as ex:
            self._log_stdout(f"Cannot write to file {device_file}")
            self._log_stdout(f"Exception: {str(ex)}")

    async def _read_device_aldb(self, location, filename):
        """Load device information from the device info file."""
        aldb_dict = []
        try:
            device_file = path.join(location, filename)
            async with aiofiles.open(device_file, "r") as afp:
                json_file = ""
                json_file = await afp.read()
            try:
                aldb_dict = json.loads(json_file)
            except json.decoder.JSONDecodeError:
                self._log_stdout("Loading ALDB file failed")
        except FileNotFoundError:
            self._log_stdout("ALDB file not found")
        return aldb_dict
