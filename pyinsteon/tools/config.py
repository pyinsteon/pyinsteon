"""Command line interface for Operation Flag and Extended Properites Management."""

from .tools_base import ToolsBase
from .. import devices
from ..constants import ResponseStatus, RelayMode


class ToolsConfig(ToolsBase):
    """Command line interface for Operation Flag and Extended Properites Management."""

    async def do_read_config(self, *args, **kwargs):
        """Read the operating flags and extended properties of a device.

        Usage:
            read_config <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=True, match_device=True
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
        """Write the operating flags and extended properties to a device.

        Usage:
            update_config <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True, match_device=True
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
        """Write the operating flags and extended properties to a device.

        Usage:
            read_ops_flags <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True, match_device=True
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
                        prop_value = prop.value if prop.value is not None else 0
                        self._log_stdout(
                            f"{name_out:30s}  0x{prop_value:02x} ({prop_value:d})"
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
            address, allow_cancel=True, allow_all=False, match_device=True
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
            return

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
        self._log_stdout(f"Value {value} writen to property {prop.name}")

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
            address, allow_cancel=True, allow_all=True, match_device=True
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

    async def do_set_kpl_toggle_mode(self, *args, **kwargs):
        """Set the toggle mode of a KeypadLinc button.

        Usage:
            set_kpl_toggle_mode address button mode

        address: Address of a KeypadLinc device
        button: Button number to set (2-8 on an 8 button KPL, 3-6 on a 6 button KPL)
        mode: Button mode (0: toggle on/off, 1: On only, 2: Off only)
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not hasattr(device, "async_set_toggle_mode"):
            self._log_stdout("Device is not a KeypadLinc")
            return

        try:
            button = int(args[1])
        except (IndexError, ValueError):
            button = await self._get_int("Buttom number", values=device.groups.keys())

        try:
            mode = int(args[2])
        except (IndexError, ValueError):
            mode = await self._get_int(
                "Toggle mode (0: toggle on/off, 1: On only, 2: Off only)",
                values=[0, 1, 2],
            )
        await device.async_set_toggle_mode(button=button, mode=mode)

    async def do_set_kpl_radio_buttons(self, *args, **kwargs):
        """Set the toggle mode of a KeypadLinc button.

        Usage:
            set_kpl_radio_buttons address button1 button2 [button3 button4 button5 button6 button7]

        address: Address of a KeypadLinc device
        button: Button number to set (2-8 on an 8 button KPL, 3-6 on a 6 button KPL)
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not hasattr(device, "async_set_radio_buttons"):
            self._log_stdout("Device is not a KeypadLinc")
            return

        item = 1
        buttons = []
        while True:
            try:
                buttons.append(int(args[item]))
                item += 1
            except (IndexError, ValueError):
                break

        possible_buttons = [0]
        _ = [possible_buttons.append(k) for k in device.groups]
        if len(buttons) < 2:
            while True:
                for button in buttons:
                    if button in possible_buttons:
                        possible_buttons.remove(button)
                button = await self._get_int(
                    "Button number (enter 0 for last button)", values=possible_buttons
                )
                if button != 0:
                    buttons.append(button)
                else:
                    break
        if len(buttons) < 2:
            self._log_stdout("At least two buttons are required")
            return

        await device.async_set_radio_buttons(buttons=buttons)

    async def do_set_iolinc_mode(self, *args, **kwargs):
        """Set the mode of an IO Linc device.

        Usage:
            set_iolinc_mode address mode

        address: IOLinc device address
        mode: Trigger or Momentary A, B or C
            0 - Latching (Continuous)
            1 - Momentary A
            2 - Momentary B
            3 - Momentary C

        for more information see the IOLinc user manual.
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
        if not hasattr(device, "async_set_relay_mode"):
            self._log_stdout("Device is not an IOLinc device")
            return

        try:
            mode = int(args[1])
            if mode not in [0, 1, 2, 3]:
                raise ValueError
        except (IndexError, ValueError):
            mode = await self._get_int("Mode", values=[0, 1, 2, 3])

        await device.async_set_relay_mode(mode=RelayMode(mode))

    async def do_set_iolinc_delay(self, *args, **kwargs):
        """Set the delay of an IO Linc device when in momentary mode.

        Usage:
            set_iolinc_delay address seconds

        address: IOLinc device address
        seconds: Integer number of seconds to delay before the relay is turned off

        For more information see the IOLinc user manual.
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not hasattr(device, "async_set_momentary_delay"):
            self._log_stdout("Device is not an IOLinc device")
            return

        try:
            seconds = int(args[1])
        except (IndexError, ValueError):
            seconds = await self._get_int("Delay (seconds)")

        await device.async_set_momentary_delay(seconds=seconds)

    async def do_get_engine_version(self, *args, **kwargs):
        """Get the engine version of the device.

        Usage:
            get_engine_version <ADDRESS>|all
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address, allow_cancel=True, allow_all=True, match_device=True
        )
        if not addresses:
            return

        for address in addresses:
            device = devices[address]
            if not device == devices.modem and device.cat != 0x03:
                await device.async_get_engine_version()
