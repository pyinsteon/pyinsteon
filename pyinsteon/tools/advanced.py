"""Advanced ALDB tools."""
import json
import os

import aiofiles

from .. import devices
from ..aldb.aldb_record import ALDBRecord
from ..constants import ALDBStatus, AllLinkMode, LinkStatus
from ..managers.link_manager import (
    async_cancel_linking_mode,
    async_enter_linking_mode,
    find_broken_links,
)
from ..managers.saved_devices_manager import aldb_rec_to_dict, dict_to_aldb_record
from .aldb import ToolsAldb

LINK_MODE_MAP = {
    "c": AllLinkMode.CONTROLLER,
    "r": AllLinkMode.RESPONDER,
    "e": AllLinkMode.EITHER,
}


class AdvancedTools(ToolsAldb):
    """Advanced ALDB tools."""

    async def do_add_link(
        self,
        address,
        group,
        target,
        link_mode,
        data1=0,
        data2=0,
        data3=0,
        log_stdout=None,
        background=False,
    ):
        """Add a link to a device All-Link Database.

        For modems use the add_im_link command.

        Usage:
            add_device_link [--background | -b] address group target link_mode [data1 data2 data3]

        address: Address of the device to add the link [0 - 255]
        group: Group number of the link [0 - 255]
        target: The device target the link refers to
        link_mode: c or r   Controller or responder link type (c=Controller, r=Responder)
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

        if device.aldb.status != ALDBStatus.LOADED:
            log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        record = {
            "link_mode": link_mode,
            "hwm": "n",
            "in_use": "y",
            "group": group,
            "target": target,
            "data1": data1,
            "data2": data2,
            "data3": data3,
        }
        try:
            record = await self._parse_record(log_stdout, not background, **record)
        except ValueError:
            return

        device.aldb.add(
            group=record["group"],
            target=record["target"],
            controller=record["is_controller"],
            data1=record["data1"],
            data2=record["data2"],
            data3=record["data3"],
        )
        success, _ = await device.aldb.async_write()
        if device.is_battery:
            log_stdout(
                f"Device {device.address} is battery operated. The record will be written when the device wakes up."
            )
            return

        if success:
            log_stdout(f"The record was successfully writen to device {device.address}")
            return

        log_stdout(
            f"An issue occured writing to the database of device {device.address}"
        )

    async def do_remove_link(
        self, address, mem_addr, log_stdout=None, background=False
    ):
        """Remove a link from the All-Link Database.

        Usage:
            remove_link [--background | -b] address mem_addr

            address: Address of the device
            mem_addr: Memory address of the link to remove (i.e. 0f7f)
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
                log_stdout("Address is required")
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        device = devices[address]
        if device.aldb.status != ALDBStatus.LOADED:
            log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        try:
            mem_addr = await self._ensure_hex_byte(
                mem_addr,
                "Memory address",
                not background,
                log_stdout,
                values=device.aldb,
            )
            if mem_addr is None:
                log_stdout("Record memory address is required")
                return

        except (IndexError, ValueError):
            log_stdout("Invalid record memory address")
            return

        device.aldb.remove(mem_addr)
        success, _ = await device.aldb.async_write()
        if device.is_battery:
            log_stdout(
                f"Device {device.address} is battery operated. The record will be removed when the device wakes up."
            )
        elif success:
            log_stdout(
                f"The record was successfully removed from the device {device.address}"
            )
        else:
            log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )

    # pylint: disable=no-self-use
    def do_find_broken_links(self, log_stdout=None, background=False):
        """Find broken links between devices.

        Useage:
            find_broken_links [--background | -b]
        """
        broken_links = find_broken_links(devices)
        log_stdout("Device   Mem Addr Target    Group Mode Status")
        log_stdout(
            "-------- -------- --------- ----- ---- ----------------------------------------"
        )
        for address, broken_link in broken_links.items():
            for mem_addr, rec, status in broken_link:
                if status == LinkStatus.MISSING_CONTROLLER:
                    status_txt = "Missing controller"
                elif status == LinkStatus.MISSING_RESPONDER:
                    status_txt = "Missing responder"
                elif status == LinkStatus.MISSING_TARGET:
                    status_txt = "Target device not found"
                elif status == LinkStatus.TARGET_DB_NOT_LOADED:
                    status_txt = "Cannot verify - Target ALDB not loaded"
                if rec.is_controller:
                    link_mode = "C"
                else:
                    link_mode = "R"
                log_stdout(
                    f"{str(address)}     {mem_addr:04x} {str(rec.target)} {rec.group:5d}   {link_mode:s} {status_txt:.40s}"
                )

    async def do_change_link(
        self, address, mem_addr, log_stdout=None, background=False, **kwargs
    ):
        """Add a link to a device All-Link Database.

        For modems use the add_im_link command.

        Usage:
            add_device_link [--background | -b] address rec_id field=value [field=value field=value] [force]


        address: Address of the device to add the link [0 - 255]
        rec_id: ALDB record id (i.e. 1fff. Can be found with the print_aldb command)

        Field can be any of the following:
            in_use: Should the record be in use
                y: record is active
                n: record is inactive (same as deleting the record)
            link_mode: Controller or responder link type
                c: Controller
                r: Responder)
            hwm: Is the record the high water mark
                y: record is hwm
                n: record is not hwm
            group: Group number of the link [0 - 255]
            target: The address of the device target the link refers to
            data1: Data field 1 [0 - 255]
            data2: Data field 2 [0 - 255]
            data3: Data feild 3 [0 - 255]

        force: Force the write to happen (overrides ALDB load status)
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
        if device.aldb.status != ALDBStatus.LOADED:
            log_stdout(
                f"The All-Link Database for device {device.address} must be loaded first."
            )
            return

        try:
            mem_addr = await self._ensure_hex_byte(
                mem_addr, "Record ID", not background, log_stdout, values=device.aldb
            )
            if mem_addr is None:
                log_stdout("Record ID is required")
                return
        except (ValueError):
            log_stdout("Invalid record ID")
            return

        key_values = [
            "in_use",
            "link_mode",
            "hwm",
            "target",
            "group",
            "data1",
            "data2",
            "data3",
            "force",
        ]

        kwargs_found = bool(kwargs)
        changes = {}
        while True:
            if kwargs_found:
                try:
                    arg, value = kwargs.popitem()
                except KeyError:
                    break

            else:
                value = None
                arg = None

            try:
                arg = await self._ensure_string(
                    arg,
                    key_values,
                    "Record value to change (i.e. in_use, data1, etc.)",
                    not background,
                    log_stdout,
                )
            except ValueError:
                log_stdout(f"Invalid record value to change: {arg}")
                return

            if arg is None:
                break

            try:
                if arg in ["in_use", "hwm", "force"]:
                    value = await self._ensure_bool(
                        value, arg, not background, log_stdout=log_stdout
                    )
                if arg == "link_mode":
                    value = await self._ensure_bool(
                        value,
                        arg,
                        not background,
                        log_stdout=log_stdout,
                        true_val="c",
                        values=["c", "r"],
                    )
                if arg == "target":
                    values = await self._ensure_address(
                        value,
                        arg,
                        not background,
                        log_stdout=log_stdout,
                        allow_all=False,
                        match_device=False,
                    )
                    if not values:
                        log_stdout(f"Value is required for {arg}")
                        return
                    value = values[0]

                if arg in ["group", "data1", "data2", "data3"]:
                    value = await self._ensure_byte(
                        value, arg, not background, log_stdout=log_stdout
                    )
            except ValueError:
                log_stdout(f"Invalid value for {arg}")
                return

            if value is None:
                log_stdout(f"Value is required for {arg}")
                return

            changes[arg] = value

        if not changes or ("force" in changes and len(changes) == 1):
            log_stdout("At least one value must be changed")
            return

        device.aldb.modify(
            mem_addr=mem_addr,
            group=changes.get("group"),
            target=changes.get("target"),
            in_use=changes.get("in_use"),
            controller=changes.get("link_mode"),
            high_water_mark=changes.get("hwm"),
            data1=changes.get("data1"),
            data2=changes.get("data2"),
            data3=changes.get("data3"),
        )
        success, _ = await device.aldb.async_write(force=changes.get("force"))
        if device.is_battery:
            log_stdout(
                f"Device {device.address} is battery operated. The record will be written when the device wakes up."
            )
        elif success:
            log_stdout(f"The record was successfully writen to device {device.address}")
        else:
            log_stdout(
                f"An issue occured writing to the database of device {device.address}"
            )
            device.aldb.clear_pending()

    async def do_export_aldb(
        self, address, location=None, filename=None, log_stdout=None, background=False
    ):
        """Export the All-Link Database for a device to a file.

        Usage:
            export_aldb [--background | -b] address [location] [filename]

        address: Address of the device to export
        location: Directory location of where to place the file (default is the current directory).
        filename: Filename of the device. The default file name is `<address>_aldb.json`
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
                log_stdout("Address is required")
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        device = devices[address]

        if location is None and not background:
            location = await self._get_workdir()
            if location is None:
                log_stdout("File location is required")
                return

        if location is None and self.workdir:
            location = self.workdir

        if location is None:
            log_stdout("File location is required")
            return

        if location == ".":
            location = os.getcwd()

        default_filename = f"{device.address.id}_aldb.json"
        filename = await self._ensure_string(
            filename,
            None,
            "Filename",
            not background,
            self._log_stdout,
            default=default_filename,
        )

        aldb_dict = {}
        for mem in device.aldb:
            rec = device.aldb[mem]
            rec_dict = aldb_rec_to_dict(rec)
            aldb_dict[mem] = rec_dict
        await self._write_aldb_file(log_stdout, aldb_dict, location, filename)

    async def do_replace_aldb(self, address, location, filename):
        """Read and replace the device ALDB with the contents of a file.

        Reads a JSON formated file with All-Link Database records and replaces
        the current records in the device. To create the JSON file use the
        `export_aldb` command.

        WARNING: This method is very dangerous and can make your device non-responsive.

        Usage:
            replace_aldb address [location [filename]]

        address: Address of the device
        location: Directory location of the file (default is the current directory).
        filename: Name of the file to use (default is <address>_aldb.json)
        """

        addresses = await self._ensure_address(
            address=address,
            name="Address",
            ask_value=True,
            log_stdout=self._log_stdout,
            allow_all=False,
            match_device=True,
        )
        if not addresses:
            return
        address = addresses[0]

        device = devices[address]

        if location is None:
            location = await self._get_workdir()
            if location is None:
                self._log_stdout("File location is required")
                return

        if location == ".":
            location = os.getcwd()

        default_filename = f"{device.address.id}_aldb.json"
        filename = await self._ensure_string(
            filename, None, "Filename", True, self._log_stdout, default=default_filename
        )

        try:
            aldb_dict = await self._read_aldb_file(self._log_stdout, location, filename)
        except ValueError:
            self._log_stdout(f"Could not load the file {location}/{filename}")
            return
        aldb_recs = dict_to_aldb_record(aldb_dict)
        aldb_array = [rec for _, rec in aldb_recs.items()]
        self._log_stdout("Preview of changes:")
        self._print_aldb_output(self._log_stdout, device, aldb_array)
        confirm = await self._ensure_bool(
            None, "Do you want to proceed", True, self._log_stdout
        )
        if not confirm:
            return

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
        done, not_done = await device.aldb.async_write(force=True)

        if device.is_battery:
            self._log_stdout(
                "This device is battery operated. The ALDB will be written when the device wakes up."
            )
            return

        if not done:
            self._log_stdout("No records were written")
        elif not_done:
            self._log_stdout("Some records not written")
        else:
            self._log_stdout("All records written succesfully")

    async def do_enter_linking_mode(
        self, link_mode, group, log_stdout=None, background=False
    ):
        """Put the modem into linking mode.

        Useage:
            enter_linking_mode [--background | -b] link_mode group

        link_mode: c | r | e  (c = Modem is controller, r = Modem is responder, e = Either)
        group: 0 - 255
        """
        try:
            link_mode = await self._ensure_string(
                value=link_mode,
                values=["c", "r", "e"],
                name="Link mode",
                ask_value=not background,
                log_stdout=log_stdout,
            )
            if link_mode is None:
                log_stdout("Linking mode is required")
                return
        except ValueError:
            log_stdout("Invalid linking mode")
            return

        try:
            group = await self._ensure_byte(group, "Group", not background, log_stdout)
            if group is None:
                log_stdout("Group is required")
                return
        except ValueError:
            log_stdout("Invalid group number")
            return

        await async_enter_linking_mode(
            link_mode=LINK_MODE_MAP[link_mode], group=group, address=None
        )

    async def do_cancel_linking_mode(self):
        """Take the modem out of linking mode.

        Useage:
            cancel_linking_mode
        """
        await async_cancel_linking_mode()

    async def do_find_im_records(
        self, address, group, log_stdout=None, background=False
    ):
        """Find one or more records in the Modem All-Link Database.

        This command does read the Insteon modem rather than read what is currently in memory.

        Useage:
            find_im_records [--background | -b] address group

        address: Insteon address of a device
        group: 0 - 255
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
                log_stdout("Address is required")
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        try:
            group = await self._ensure_byte(group, "Group", not background, log_stdout)
            if group is None:
                log_stdout("Group number is required")
                return
        except ValueError:
            log_stdout("Invalid group number")
            return

        recs = [
            rec async for rec in devices.modem.aldb.async_find_records(address, group)
        ]
        if not recs:
            log_stdout("No records found")
            return

        self._print_aldb_output(log_stdout, devices.modem, recs)

    async def _write_aldb_file(self, log_stdout, aldb_dict, location, filename):
        device_file = os.path.join(location, filename)
        try:
            async with aiofiles.open(device_file, "w") as afp:
                out_json = json.dumps(aldb_dict, indent=2)
                await afp.write(out_json)
                await afp.flush()
        except FileNotFoundError as ex:
            log_stdout(f"Cannot write to file {device_file}")
            log_stdout(f"Exception: {str(ex)}")

    async def _read_aldb_file(self, log_stdout, location, filename):
        """Load device information from the device info file."""
        aldb_dict = []
        try:
            device_file = os.path.join(location, filename)
            async with aiofiles.open(device_file, "r") as afp:
                json_file = ""
                json_file = await afp.read()
            try:
                aldb_dict = json.loads(json_file)
            except json.decoder.JSONDecodeError:
                log_stdout("Loading ALDB file failed")
        except FileNotFoundError:
            log_stdout("ALDB file not found")
            raise ValueError
        return aldb_dict

    async def _parse_record(self, log_stdout, ask_values, **kwargs):
        """Create a dict of ALDB record values.

        Sets the value to `None` if the value is not received and `ask_values` is `False`.
        Returns `None` if bad values are received and ask_values is `False`.
        """
        link_mode = kwargs.get("link_mode")
        group = kwargs.get("group")
        target = kwargs.get("target")
        data1 = kwargs.get("data1")
        data2 = kwargs.get("data2")
        data3 = kwargs.get("data3")

        name = ""
        try:
            name = "Group"
            group = await self._ensure_byte(group, name, ask_values, log_stdout)
            if group is None:
                log_stdout("Group is required")
                raise ValueError
            name = "Target"

            targets = await self._ensure_address(
                target,
                name,
                ask_values,
                log_stdout,
                allow_all=False,
                match_device=False,
            )
            if not targets:
                log_stdout("Target address is required")
                raise ValueError
            target = targets[0]

            name = "Link mode"
            is_controller = await self._ensure_bool(
                link_mode, name, ask_values, log_stdout, "c", ["r", "c"]
            )
            if is_controller is None:
                log_stdout("Link mode is required")
                raise ValueError

            name = "Data1"
            data1 = await self._ensure_byte(
                data1, name, ask_values, log_stdout, default=0
            )
            name = "Data2"
            data2 = await self._ensure_byte(
                data2, name, ask_values, log_stdout, default=0
            )
            name = "Data3"
            data3 = await self._ensure_byte(
                data3, name, ask_values, log_stdout, default=0
            )

        except ValueError:
            log_stdout(f"Invalid value for {name}")
            raise ValueError

        return {
            "is_in_use": True,
            "is_controller": is_controller,
            "is_high_water_mark": False,
            "group": group,
            "target": target,
            "data1": data1,
            "data2": data2,
            "data3": data3,
        }
