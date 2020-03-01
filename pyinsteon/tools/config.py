"""Command line interface for Operation Flag and Extended Properites Management."""

from .tools_base import ToolsBase
from .. import devices
from ..constants import ResponseStatus


class ToolsConfig(ToolsBase):
    """Command line interface for Operation Flag and Extended Properites Management."""

    async def do_read_config(self, *args, **kwargs):
        """Read the operating flags and extended properties of a device.""

        Usage:
            read_config <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True
        )
        if not addresses:
            return

        for address in addresses:
            device = devices[address]
            if not device == devices.modem:
                self._log_stdout(f"Reading configuration for: {device.address}")
                if await device.async_read_op_flags() == ResponseStatus.SUCCESS:
                    self._log_stdout("Operating flags read")
                else:
                    self._log_stdout("Operating flags read error")
                if await device.async_read_ext_properties() == ResponseStatus.SUCCESS:
                    self._log_stdout("Extended properties read")
                else:
                    self._log_stdout("Extended properties read error")


    async def do_update_config(self, *args, **kwargs):
        """Write the operating flags and extended properties to a device.""

        Usage:
            update_config <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True
        )
        if not addresses:
            return

        for address in addresses:
            device = devices[address]
            if not device == devices.modem:
                if await device.async_write_op_flags() == ResponseStatus.SUCCESS:
                    self._log_stdout("Operating flags writen successfully")
                else:
                    self._log_stdout("Operating flags not writen")
                if await device.async_write_ext_properties() == ResponseStatus:
                    self._log_stdout("Extended properties writen successfully")
                else:
                    self._log_stdout("Extended properties not writen")

    async def do_print_config(self, *args, **kwargs):
        """Write the operating flags and extended properties to a device.""

        Usage:
            read_ops_flags <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True
        )
        if not addresses:
            return

        for address in addresses:
            device = devices[address]
            if device and not device == devices.modem:
                self._log_stdout("")
                self._log_stdout(f"Device: {address}")
                self._log_stdout("Operating Flag                  Value")
                self._log_stdout("------------------------------  -----")
                for name in device.operating_flags:
                    op_flag = device.operating_flags[name]
                    if op_flag.is_dirty:
                        name_out = f"{name}*"
                    else:
                        name_out = name
                    self._log_stdout(f"{name_out:30s}  {bool(op_flag.value)}")
                self._log_stdout("")
                self._log_stdout("Property                        Value")
                self._log_stdout("------------------------------  ----------")
                for name in device.properties:
                    prop = device.properties[name]
                    if prop.is_dirty:
                        name_out = f"{name}*"
                    else:
                        name_out = name
                    if isinstance(prop.value, bool):
                        self._log_stdout(f"{name_out:30s}  {prop.value}")
                    else:
                        self._log_stdout(
                            f"{name_out:30s}  0x{prop.value:02x} ({prop.value:d})"
                        )
                self._log_stdout("")

    async def do_set_config_value(self, *args, **kwargs):
        """Set an operating flag or extended property for a device.

        Usage:
            set_config_value <ADDRESS> flag y|n
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=False
        )
        if not addresses:
            return
        device = devices[addresses[0]]

        try:
            name = args[1]
        except IndexError:
            name = None

        if name is None:
            name = await self._get_char("Enter property name")

        if not name:
            self._log_stdout("A name is required")

        if not device.operating_flags.get(name) and not device.properties.get(name):
            self._log_stdout(f"Flag {name} not found in device {addresses[0]}")

        if device.operating_flags.get(name):
            prop = device.operating_flags[name]
        else:
            prop = device.properties[name]

        try:
            value = args[2]
            if isinstance(prop.value, bool):
                if value not in ["y", "n"]:
                    self._log_stdout("Value must be y or n")
                    return
                value = value == "y"
            else:
                value = int(value)
                if value not in range(0, 256):
                    self._log_stdout("Value must be between 0 and 255")
                    return
        except IndexError:
            value = None
        except TypeError:
            self._log_stdout("Value must be an integer between 0 and 255")
            return

        if value is None:
            if isinstance(prop.value, bool):
                yn_value = await self._get_char(
                    "Property is set (y/n)", values=["y", "n"]
                )
                value = yn_value == "y"
            else:
                value = await self._get_int("Property value", values=range(0, 256))

        prop.new_value = value

    async def do_write_config(self, *args, **kwargs):
        """Write the device config.
        
        Usage:
            write_config <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True
        )
        if not addresses:
            return

        for address in addresses:
            device = devices[address]
            if device != devices.modem:
                if await device.async_write_op_flags() == ResponseStatus.SUCCESS:
                    self._log_stdout("Operating flags written")
                else:
                    self._log_stdout("Operating flags write error")
                if await device.async_write_ext_properties() == ResponseStatus.SUCCESS:
                    self._log_stdout("Extended properties written")
                else:
                    self._log_stdout("Extended properties write error")
