"""Tools to run device commands."""

import inspect
from types import MethodType

from .. import (
    async_x10_all_lights_off,
    async_x10_all_lights_on,
    async_x10_all_units_off,
    devices,
)
from ..constants import HC_LOOKUP
from ..managers.scene_manager import async_trigger_scene_off, async_trigger_scene_on
from .tools_base import ToolsBase


class ToolsCommands(ToolsBase):
    """Tools to run device commands."""

    async def do_on(self, address, log_stdout=None, background=False):
        """Test turning a device on.

        Usage:
            on [--background | -b] <address> [group]

        This method calls `async_on` with default values.
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
        if not hasattr(device, "async_on"):
            log_stdout("Device cannot be turned on.")
            return

        await device.async_on()

    async def do_off(self, address, log_stdout=None, background=False):
        """Test turning a device off.

        Usage:
            on [--background | -b] <address> [group]

        This method calls `async_off` with default values.
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
        if not hasattr(device, "async_off"):
            log_stdout("Device cannot be turned off.")
            return

        await device.async_off()

    async def do_scene_on(self, scene, log_stdout=None, background=False):
        """Test a scene.

        Usage:
            scene_on [--background | -b] scene
        """

        try:
            scene = await self._ensure_byte(scene, "Scene", not background, log_stdout)
            if scene is None:
                log_stdout("Scene number is required")
                return
        except ValueError:
            log_stdout("Invalid scene number")
            return

        await async_trigger_scene_on(scene)

    async def do_scene_off(self, scene, log_stdout=None, background=False):
        """Test a scene.

        Usage:
            scene_off [--background | -b] scene
        """

        try:
            scene = await self._ensure_byte(scene, "Scene", not background, log_stdout)
            if scene is None:
                log_stdout("Scene number is required")
                return
        except ValueError:
            log_stdout("Invalid scene number")
            return

        await async_trigger_scene_off(scene)

    async def do_cmd(self, address, command):
        """Run a general device command.

        Usage:
            cmd address command

        Examples:
            cmd 1a2b3c async_on
            cmd 1a2b3c async_off

        You will be prompted for any arguments to the command. To see a list of available commands for a device use:
            help cmd address

        This command cannot be run in the background.
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
            self._log_stdout("Address is required")
            return

        address = addresses[0]
        device = devices[address]

        device_commands = []
        for device_method in dir(device):
            if not device_method.startswith("_"):
                device_commands.append(device_method)

        command = await self._ensure_string(
            command, device_commands, "Command", True, self._log_stdout
        )
        if not command:
            self._log_stdout("A device command is required")
            return

        func = getattr(device, command)
        signature = inspect.signature(func)
        func_args = [arg for arg, _ in signature.parameters.items()]
        kwargs = {}
        if func_args:
            args_defaults = {
                k: v.default
                for k, v in signature.parameters.items()
                if v.default is not inspect.Parameter.empty
            }
            print_args = ""
            for arg, _ in signature.parameters.items():
                if print_args != "":
                    print_args += ", "
                print_args += arg
                arg_def = args_defaults.get(arg, inspect.Parameter.empty)
                if arg_def != inspect.Parameter.empty:
                    print_args += f"={arg_def}"

            # self._log_stdout(f"Command arguments: {print_args}")
            self._log_stdout(f"Command arguments: {signature}")
            while True:
                arg = await self._ensure_string(
                    None, func_args, "Argument", True, self._log_stdout
                )
                if arg is None:
                    break
                arg_default = args_defaults.get(arg)
                value = await self._ensure_arg_value(
                    arg, None, True, self._log_stdout, arg_default
                )
                kwargs[arg] = value
            for arg in func_args:
                if arg not in kwargs and arg not in args_defaults:
                    self._log_stdout(f"Missing value for required argument {arg}")
                    return
                kwargs[arg] = kwargs.get(arg, args_defaults.get(arg))

        if inspect.iscoroutinefunction(func) or inspect.isawaitable(func):
            result = await func(**kwargs)
        else:
            result = func(**kwargs)
        self._log_stdout(f"Result: {str(result)}")

    async def do_x10_all_lights_on(
        self, housecode: str, log_stdout=None, background=False
    ):
        """Run the X10 All Lights On command.

        Usage:
          x10_all_lights_on housecode
        """
        housecode = await self._ensure_string(
            str(housecode).lower(),
            list(HC_LOOKUP.keys()),
            "Housecode",
            True,
            log_stdout,
        )
        await async_x10_all_lights_on(housecode=housecode)

    async def do_x10_all_lights_off(
        self, housecode: str, log_stdout=None, background=False
    ):
        """Run the X10 All Lights Off command.

        Usage:
          x10_all_lights_off housecode
        """
        housecode = await self._ensure_string(
            str(housecode).lower(),
            list(HC_LOOKUP.keys()),
            "Housecode",
            True,
            log_stdout,
        )
        await async_x10_all_lights_off(housecode=housecode)

    async def do_x10_all_units_off(
        self, housecode: str, log_stdout=None, background=False
    ):
        """Run the X10 All Units Off command.

        Usage:
          x10_all_units_off housecode
        """
        housecode = await self._ensure_string(
            str(housecode).lower(),
            list(HC_LOOKUP.keys()),
            "Housecode",
            True,
            log_stdout,
        )
        await async_x10_all_units_off(housecode=housecode)

    # pylint: disable=arguments-renamed
    # pylint: disable=invalid-overridden-method
    async def do_help(self, cmd=None, address=None, method=None):
        """List available commands with "help" or detailed help with "help cmd".

        You can also get a list of device commands to run with the "cmd" method.
        Example 1:
            help cmd 1a2b3c

        This will show the available commands that can be run against device 1A.2B.3C.

        Example 2:
            help cmd 1a2b3c async_off

        This will show the parameters available to the async_off method.
        """

        if cmd != "cmd":
            return super().do_help(cmd)

        try:
            addresses = await self._ensure_address(
                address,
                "Device address",
                False,
                self._log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addresses:
                return super().do_help(cmd)

            address = addresses[0]
        except ValueError:
            self._log_stdout("Invalid device address")
            return

        device = devices[address]
        if method:
            if not hasattr(device, method):
                self._log_stdout(f"Method {method} not found for device {address}.")
                return
            func = getattr(device, method)
            doc = func.__doc__
            if doc:
                self._log_stdout(doc)
            arguments = str(inspect.signature(func)).strip("(").strip(")")
            self._log_stdout("")
            self._log_stdout(
                f"Device {str(device.address)} {method} method arguments: {arguments}"
            )
            return

        all_methods = dir(device)
        methods = []
        for func_method in all_methods:
            if func_method[0] != "_":
                func = getattr(device, func_method)
                if isinstance(func, MethodType):
                    methods.append(func_method)
        self._log_stdout("")
        header = f"Available commands for device {str(device.address)}:"
        self.print_topics(header, methods, 15, 80)
