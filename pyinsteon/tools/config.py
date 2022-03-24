"""Command line interface for Operation Flag and Extended Properites Management."""

from .. import devices
from ..constants import RelayMode, ResponseStatus
from .tools_base import ToolsBase


class ToolsConfig(ToolsBase):
    """Command line interface for Operation Flag and Extended Properites Management."""

    async def do_read_config(self, address, log_stdout=None, background=False):
        """Read the operating flags and extended properties of a device.

        Usage:
            read_config <ADDRESS>|all
        """
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
                log_stdout("Address is required")
                return
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        for device_address in addresses:
            device = devices[device_address]
            if not device == devices.modem:
                log_stdout(f"Reading configuration for: {device.address}")
                if await device.async_read_op_flags() == ResponseStatus.SUCCESS:
                    log_stdout("Operating flags read")
                else:
                    log_stdout("Operating flags read error")
                if await device.async_read_ext_properties() == ResponseStatus.SUCCESS:
                    log_stdout("Extended properties read")
                else:
                    log_stdout("Extended properties read error")

    async def do_print_config(self, address, log_stdout=None, background=False):
        """Write the operating flags and extended properties to a device.

        Usage:
            read_ops_flags <ADDRESS>|all
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
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        for device_address in addresses:
            device = devices[device_address]
            if device and not device == devices.modem:
                log_stdout("")
                log_stdout(f"Device: {device_address}")
                log_stdout("Operating Flag                  Value")
                log_stdout("------------------------------  -----")
                for name in device.operating_flags:
                    op_flag = device.operating_flags[name]
                    if op_flag.is_dirty:
                        name_out = f"{name}*"
                    else:
                        name_out = name
                    log_stdout(f"{name_out:30s}  {bool(op_flag.value)}")
                log_stdout("")
                log_stdout("Property                        Value")
                log_stdout("------------------------------  ----------")
                for name in device.properties:
                    prop = device.properties[name]
                    if prop.is_dirty:
                        name_out = f"{name}*"
                    else:
                        name_out = name
                    if isinstance(prop.value, bool):
                        log_stdout(f"{name_out:30s}  {prop.value}")
                    else:
                        prop_value = prop.value if prop.value is not None else 0
                        log_stdout(
                            f"{name_out:30s}  0x{prop_value:02x} ({prop_value:d})"
                        )
                log_stdout("")

    async def do_set_config_value(
        self, address, name, value, log_stdout=None, background=False
    ):
        """Set an operating flag or extended property for a device.

        Usage:
            set_config_value <ADDRESS> flag y|n
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
                log_stdout("Address is required.")
                return
            address = addresses[0]
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        device = devices[address]

        prop_names = []
        for prop_name in device.operating_flags:
            prop_names.append(prop_name)
        for prop_name in device.properties:
            prop_names.append(prop_name)

        if not prop_names:
            log_stdout(f"Device {address} has no configurable settings.")
            return

        try:
            name = await self._ensure_string(
                name, prop_names, "Property name", not background, log_stdout
            )
            if name is None:
                log_stdout("Property name is required.")
                return
        except ValueError:
            log_stdout(f"Flag {name} not found in device {address}")

        if device.operating_flags.get(name):
            prop = device.operating_flags[name]
        else:
            prop = device.properties[name]

        try:
            if prop.value_type is bool:
                value = await self._ensure_bool(
                    value, "Property value", not background, log_stdout
                )
            else:
                value = await self._ensure_byte(
                    value, "Property value", not background, log_stdout
                )
            if value is None:
                log_stdout("Property value is required.")
                return
        except ValueError:
            log_stdout(f"Invalid value for {name}")
            return

        prop.new_value = value
        log_stdout(f"Changed property {prop.name} value to {value}")
        log_stdout("Use `write_config command to write changes to the device")

    async def do_write_config(self, address, log_stdout=None, background=False):
        """Write the device config.

        Usage:
            write_config <ADDRESS>|all
        """
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
                log_stdout("Address is required")
                return
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        for device_address in addresses:
            device = devices[device_address]
            if device != devices.modem:
                if await device.async_write_op_flags() == ResponseStatus.SUCCESS:
                    log_stdout("Operating flags written")
                else:
                    log_stdout("Operating flags write error")
                if await device.async_write_ext_properties() == ResponseStatus.SUCCESS:
                    log_stdout("Extended properties written")
                else:
                    log_stdout("Extended properties write error")

    async def do_set_kpl_toggle_mode(
        self, address, button, toggle_mode, log_stdout=None, background=False
    ):
        """Set the toggle mode of a KeypadLinc button.

        Usage:
            set_kpl_toggle_mode address button toggle_mode

        address: Address of a KeypadLinc device
        button: Button number to set (2-8 on an 8 button KPL, 3-6 on a 6 button KPL)
        toggle_mode: Button toggle mode (0: toggle on/off, 1: On only, 2: Off only)
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
        if not hasattr(device, "async_set_toggle_mode"):
            log_stdout("Device is not a KeypadLinc")
            return

        try:
            button = await self._ensure_int(
                button,
                device.groups.keys(),
                "Button",
                not background,
                log_stdout,
            )
            if button is None:
                log_stdout("A button number is required")
                return
        except ValueError:
            log_stdout("Invalid button number")
            return

        try:
            toggle_mode = await self._ensure_int(
                toggle_mode,
                [0, 1, 2],
                "Toggle mode",
                not background,
                log_stdout,
            )
            if toggle_mode is None:
                log_stdout("A toggle mode is required")
                return
        except ValueError:
            log_stdout("Invalid toggle mode")

        return await device.async_set_toggle_mode(
            button=button, toggle_mode=toggle_mode
        )

    async def do_set_kpl_radio_buttons(
        self, address, button1, button2, *args, log_stdout=None, background=False
    ):
        """Set the toggle mode of a KeypadLinc button.

        Usage:
            set_kpl_radio_buttons address button1 button2 [button3 button4 button5 button6 button7]

        address: Address of a KeypadLinc device
        button: Button number to set (2-8 on an 8 button KPL, 3-6 on a 6 button KPL)
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
        if not hasattr(device, "async_set_radio_buttons"):
            log_stdout("Device is not a KeypadLinc")
            return

        input_buttons = [button1, button2, *args]
        ask_values = button2 is None and not background
        buttons = []
        for button in range(0, len(device.groups)):
            try:
                input_button = input_buttons[button]
            except IndexError:
                input_button = None
            try:
                button = await self._ensure_int(
                    value=input_button,
                    values=device.groups.keys(),
                    name="Button",
                    ask_value=ask_values,
                    log_stdout=log_stdout,
                )
            except ValueError:
                if input_button is None and len(buttons) >= 2:
                    break
                log_stdout("Invalid button number")
                return
            if button is None and len(buttons) < 2:
                log_stdout("At least two buttons are required")
                return
            if button is None:
                break
            buttons.append(button)

        await device.async_set_radio_buttons(buttons=buttons)

    async def do_set_iolinc_mode(
        self, address, latching_mode, log_stdout=None, background=False
    ):
        """Set the relay mode of an IO Linc device.

        Usage:
            set_iolinc_mode address latching_mode

        address: IOLinc device address
        latching_mode: Trigger or Momentary A, B or C
            0 - Latching (Continuous)
            1 - Momentary A
            2 - Momentary B
            3 - Momentary C

        for more information see the IOLinc user manual.
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
        if not hasattr(device, "async_set_relay_mode"):
            log_stdout("Device is not an IOLinc device")
            return

        try:
            latching_mode = await self._ensure_int(
                latching_mode, [0, 1, 2, 3], "Latching mode", not background, log_stdout
            )
            if latching_mode is None:
                log_stdout("Value for latching mode is required")
                return
        except ValueError:
            log_stdout("Invalid value for latching mode")
            return
        await device.async_set_relay_mode(latching_mode=RelayMode(latching_mode))

    async def do_set_iolinc_delay(
        self, address, seconds, log_stdout=None, background=False
    ):
        """Set the delay of an IO Linc device when in momentary mode.

        Usage:
            set_iolinc_delay address seconds

        address: IOLinc device address
        seconds: Integer number of seconds to delay before the relay is turned off

        For more information see the IOLinc user manual.
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
        if not hasattr(device, "async_set_momentary_delay"):
            log_stdout("Device is not an IOLinc device")
            return

        try:
            seconds = await self._ensure_byte(
                seconds, "Delay (seconds)", not background, log_stdout
            )
            if seconds is None:
                log_stdout("Value for seconds is required")
        except ValueError:
            log_stdout("Invalid number for seconds")
            return

        await device.async_set_momentary_delay(seconds=seconds)

    async def do_get_engine_version(self, address, log_stdout=None, background=False):
        """Get the engine version of the device.

        Usage:
            get_engine_version <ADDRESS>|all
        """
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
                log_stdout("Address is required")
                return
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        for device_address in addresses:
            device = devices[device_address]
            if not device == devices.modem and device.cat != 0x03:
                await device.async_get_engine_version()
