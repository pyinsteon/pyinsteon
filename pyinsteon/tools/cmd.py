"""Tools to run device commands."""

import inspect
from types import MethodType

from .tools_base import ToolsBase
from .. import devices
from ..managers.scene_manager import (
    async_trigger_scene_off,
    async_trigger_scene_on,
)


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
    if val == "True":
        return True
    if val == "False":
        return False
    return val


def _parse_cmd(*args):
    try:
        address = args[0]
        if not devices[address]:
            raise IndexError
    except IndexError:
        return None, None, {}

    try:
        cmd = args[1]
        if not hasattr(devices[address], cmd):
            raise AttributeError
    except IndexError:
        return address, None, {}

    kwargs = {}
    for arg in args[2:]:
        kwarg, val = arg.split("=")
        val = _convert_val(val)
        kwargs[kwarg] = val

    return address, cmd, kwargs


class CmdTools(ToolsBase):
    """Tools to run device commands."""

    async def do_on(self, *args, **kwargs):
        """Test turning a device on.

        Usage:
            on <address>

        This method calls `async_on` with default values.
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not hasattr(device, "async_on"):
            self._log_stdout("Device cannot be turned on.")

        await device.async_on()

    async def do_off(self, *args, **kwargs):
        """Test turning a device off.

        Usage:
            on <address>

        This method calls `async_off` with default values.
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not hasattr(device, "async_off"):
            self._log_stdout("Device cannot be turned off.")

        await device.async_off()

    async def do_scene_on(self, *args, **kwargs):
        """Test a scene.

        Usage:
            scene_on scene
        """

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = await self._get_int(
                "Scene number or blank to cancel", values=range(25, 256),
            )

        if not scene:
            return

        await async_trigger_scene_on(scene)

    async def do_scene_off(self, *args, **kwargs):
        """Test a scene.

        Usage:
            scene_off scene
        """

        args = args[0].split()
        try:
            scene = int(args[0])
        except (IndexError, ValueError):
            scene = None

        if not scene:
            scene = await self._get_int(
                "Scene number or blank to cancel", values=range(25, 256),
            )

        if not scene:
            return

        await async_trigger_scene_off(scene)

    async def do_cmd(self, *args, **kwargs):
        """Run a general device command.

        Usage:
            cmd address command [arg1=value1 arg2=value2 ...]

        Examples:
            cmd 1a2b3c async_on on_level=100
            cmd 1a2b3c async_off

        No spaces between argument, '=' and value are allowed.
        If an enumerator is required (i.e. ThermostatMode) use the integer represenation of the enum.

        Example:
            cmd 1a2b3c async_set_mode mode=3

        where ThermostatMode.AUTO equals 3.

        """

        args = args[0].split()
        try:
            address, cmd, kwargs = _parse_cmd(*args)
        except AttributeError:
            self._log_stdout(f"Device command not found.")
            return

        addresses = await self._get_addresses(
            address=address, allow_cancel=True, allow_all=False, match_device=True
        )
        if not addresses:
            return

        device = devices[addresses[0]]
        if not device:
            self._log_stdout("Device not found.")
            return

        if cmd is None:
            cmd = await self._get_char("Device command")
            if not hasattr(device, cmd):
                self._log_stdout("Device command not found.")

            if not kwargs:
                while True:
                    arg = self._get_char(
                        "Enter argument (eg. on_level=255). Press enter for last argument"
                    )
                    if arg == "":
                        break
                    kwarg, val = arg.split("=")
                    val = _convert_val(val)
                    kwargs[kwarg] = val

        self._log_stdout(f"cmd {address} {cmd} {kwargs}")

        func = getattr(device, cmd)
        if inspect.iscoroutinefunction(func) or inspect.isawaitable(func):
            result = await func(**kwargs)
        else:
            result = func(**kwargs)
        self._log_stdout(f"Result: {str(result)}")

    def do_help(self, arg):
        """List available commands with "help" or detailed help with "help cmd".

        You can also get a list of device commands to run with the "cmd" method.
        Example 1:
            help cmd 1a2b3c

        This will show the available commands that can be run against device 1A.2B.3C.

        Example 2:
            help cmd 1a2b3c async_off

        This will show the parameters available to the async_off method.
        """
        arg_set = arg.split()
        try:
            cmd = arg_set[0]
            if cmd != "cmd":
                return super().do_help(arg)

        except IndexError:
            return super().do_help(arg)

        try:
            address = arg_set[1]
        except IndexError:
            return super().do_help(arg)

        device = devices[address]
        if device:
            try:
                method = arg_set[2]
                if not hasattr(device, method):
                    self._log_stdout("Method not found for device.")
                    return
                func = getattr(device, method)
                arguments = str(inspect.signature(func)).strip("(").strip(")")
                self._log_stdout("")
                self._log_stdout(
                    f"Device {str(device.address)} {method} method arguments: {arguments}"
                )
            except IndexError:
                all_methods = dir(device)
                methods = []
                for method in all_methods:
                    if method[0] != "_":
                        func = getattr(device, method)
                        if isinstance(func, MethodType):
                            methods.append(method)
                self._log_stdout("")
                header = f"Available commands for device {str(device.address)}:"
                self.print_topics(header, methods, 15, 80)
