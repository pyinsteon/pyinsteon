"""Base object for all command line menues."""

from argparse import ArgumentParser
import asyncio
from binascii import Error as BinasciiError, unhexlify
from cmd import Cmd
from collections import namedtuple
import getpass
import inspect
import logging
import os
import signal
import sys
import traceback
from typing import List

from .. import devices
from ..address import Address
from ..constants import RelayMode, ThermostatMode, ToggleMode
from ..x10_address import X10Address
from .log_filter import NoStdoutFilter, StdoutFilter, StripPrefixFilter
from .utils import patch_stdin_stdout, set_loop, stdio

_LOGGING = logging.getLogger(__name__)
LOG_FILE_NAME = "pyinsteon_tools.log"
STDOUT_LOG_HANDLER = "stdout_handler"
FILE_LOG_HANDLER = "file_handler"
CmdArgs = namedtuple("CmdArgs", "workdir device username host hub_version port")
ARG_TYPES = {
    "auto_led": bool,
    "awake_time": bytes,
    "button": range(1, 9),
    "buttons": [range(1, 9)],
    "deadman": bool,
    "disable_auto_linking": bool,
    "fast": bool,
    "force": bool,
    "group": bytes,
    "humidity": bytes,
    "link_mode": bool,
    "logging_mode": bool,
    "master": Address,
    "monitor_mode": bool,
    "on_level": bytes,
    "open_level": bytes,
    "relay_mode": RelayMode,
    "seconds": bytes,
    "temperature": bytes,
    "thermostat_mode": ThermostatMode,
    "toggle_mode": ToggleMode,
}
DEFAULT_HUB_PORT = {1: 9761, 2: 25105}


def validate_address(address, allow_all, match_device, log_stdout) -> List[Address]:
    """Check that an address value is valid.

    Returns `[address]` if `address` is a valid `Address` or if `address` eq `all`.

    Raises `ValueError` if:
        - `address` is not a valid `Address`
        - `address` eq `all` and `allow_all` is `False`
        - `address` does not match an existing device and `match_device` is `True`
    """
    if not address:
        raise ValueError("No address provided")

    if address != "all":
        try:
            address = Address(address)
        except ValueError:
            address = X10Address(address)
        if not match_device or address in devices:
            return [address]
        log_stdout(f"No device found with address {address}")
        raise ValueError(f"No device found with address {address}")

    if allow_all:
        return list(devices)
    log_stdout("A single address is expected")
    raise ValueError("A single address is expected")


class ToolsBase(Cmd):
    """Base class for all tools menues."""

    _active_task = None

    def __init__(self, loop, args=None, menu=None, stdin=None, stdout=None):
        """Init the InsteonCmd class."""
        super().__init__()
        self.stdin = stdin
        self.stdout = stdout
        self._prompt_base = "pyinsteon"
        if menu:
            self.prompt = f"{self._prompt_base} - {menu}: "
        else:
            self.prompt = f"{self._prompt_base}: "
        self._log_prefix = "STDOUT: "
        self._input_prefix = "INPUT"
        self._background_prefix = "BACKGROUND"
        self.loop = loop
        self.workdir = None

        self.device = None
        self.host = None
        self.username = None
        self.hub_version = 2
        self.port = 25105
        self.mock = False

        self._set_command_line_values(args)

        self._add_filter()

        if hasattr(args, "workdir"):
            self.workdir = args.workdir
            if hasattr(args, "logging") and self.workdir:
                self.do_log_to_file("y", self.workdir)

    def _set_command_line_values(self, args):
        """Set up the connection values from the command line arguments."""
        try:
            self.device = args.device if args.device else None
        except AttributeError:
            pass
        try:
            self.username = args.username if args.username else None
        except AttributeError:
            pass
        try:
            self.host = args.host if args.host else None
        except AttributeError:
            pass
        try:
            self.hub_version = args.hub_version if args.hub_version else 2
        except AttributeError:
            pass
        try:
            self.port = (
                args.port if args.port else DEFAULT_HUB_PORT.get(self.hub_version)
            )
        except AttributeError:
            pass

        if hasattr(args, "verbose") and args.verbose:
            self._setup_logging(logging.DEBUG)
        else:
            self._setup_logging(logging.INFO)

    async def async_cmdloop(self, *intro):
        """Replace standard cmdloop to make this async.

        Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        Can be called with `async_cmdloop()` or `async_cmdloop("intro string")` or
        `async_cmdloop(*["intro line 1", "intro_line2", ...])`
        """

        self.preloop()
        if not self.stdin and not self.stdout:
            self.stdin, self.stdout = await stdio(loop=self.loop)
            if sys.platform != "win32":
                patch_stdin_stdout(self.stdin, self.stdout)

        try:
            for intro_str in intro:
                self.stdout.write(intro_str + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    line = await self._input(prompt=self.prompt)
                    if not line:
                        line = "EOF"
                line = self.precmd(line)
                try:
                    active_task = asyncio.create_task(self.async_onecmd(line))
                    self._set_active_task(active_task)
                    try:
                        stop = await active_task
                    except asyncio.CancelledError:
                        stop = None
                    self._set_active_task(None)
                # pylint: disable=broad-except
                except Exception as ex:
                    self._log_stdout("An error occured executing command.")
                    self._log_stdout(str(ex))
                    _LOGGING.debug(traceback.format_exc())
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            pass

    def parseline(self, line):
        """Parse the full command line."""
        cmd, args, line = super().parseline(line)
        if args:
            args = args.split(" ")
            while "" in args:
                args.remove("")
        else:
            args = []
        return cmd, args, line

    async def async_onecmd(self, line):
        """Replace the onecmd method to make it async.

        Interpret the argument as though it had been typed in response
        to the prompt.
        """

        if not line:
            return self.emptyline()

        cmd, all_args, line = self.parseline(line)
        self._log_command(line)

        self.lastcmd = line

        try:
            func = getattr(self, "do_" + cmd)
        except AttributeError:
            try:
                func = getattr(self, "menu_" + cmd)
            except AttributeError:
                self._log_stdout(f"Invalid command: {cmd}")
                return
        args, kwargs, args_valid = self._parse_args(func, all_args)

        if not args_valid:
            return

        background = kwargs.get("background")
        if background:
            return asyncio.ensure_future(func(*args, **kwargs))
        if inspect.iscoroutinefunction(func) or inspect.isawaitable(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    # pylint: disable=no-self-use
    def emptyline(self):
        """Change default empty line to do nothing."""
        return

    @classmethod
    def start(cls):
        """Start the loop and the current command set."""
        parser = ArgumentParser(description=__doc__)
        parser.add_argument("--device", default="", help="Path to PLM device")
        parser.add_argument("--host", default="", help="Hostname or IP address of Hub")
        parser.add_argument("--username", default="", help="Username of Hub")
        parser.add_argument(
            "--hub_version", default="", help="Version of the Hub (1 or 2)"
        )
        parser.add_argument(
            "--port",
            default="",
            help="Hub IP port (Default 25105 for version 2 or 9761 for version 1)",
        )
        parser.add_argument(
            "-v", "--verbose", action="count", help="Set logging level to verbose"
        )
        parser.add_argument("-l", "--logging", action="count", help="Log to file")
        parser.add_argument(
            "--workdir",
            default="",
            help="Working directory for reading and saving device information.",
        )
        args = parser.parse_args()

        set_loop()
        loop = asyncio.get_event_loop()

        intro = [
            "",
            "The command line module for pyinsteon is designed to test devices and perform certain common functions.",
            "",
            "Enter `help` to see a list of commands.",
            "Most commands can be called with `--background` or `-b` as the first parameter to run the command asyncronously in the background."
            "For example:",
            "      status --backround aa.bb.cc",
            "",
        ]

        try:
            loop.add_signal_handler(signal.SIGINT, cls._cancel_active_task)
        except NotImplementedError:
            signal.signal(signal.SIGINT, cls._cancel_active_task)

        loop.run_until_complete(cls(loop, args).async_cmdloop(*intro))

    async def start_menu(self):
        """Start the menu."""
        await self.async_cmdloop()

    # pylint: disable=arguments-differ
    def do_help(self, arg=""):
        """List available commands with "help" or detailed help with "help cmd"."""
        menus = self._get_menus()
        if arg and arg in self._get_menus():
            try:
                func = getattr(self, "help_" + arg)
            except AttributeError:
                try:
                    doc = getattr(self, "menu_" + arg).__doc__
                    if doc:
                        self.stdout.write(f"{doc}\n")
                        return
                except AttributeError:
                    pass
                # pylint: disable=consider-using-f-string
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
            return
        if arg:
            self.stdout.write("\n")

        super().do_help(arg)
        if arg:
            try:
                func = getattr(self, "do_" + arg)
                full_args_spec = inspect.getfullargspec(func)
                if "background" in full_args_spec.args:
                    self.stdout.write(
                        "        --background | -b: Run in the background\n"
                    )
            except AttributeError:
                pass
            self.stdout.write("\n")
            return

        self.stdout.write("\n")
        menu_header = "List of available submenues:"
        self.print_topics(menu_header, menus, 15, 80)
        self.stdout.write("\n")

    # pylint: disable=no-self-use
    def do_list_devices(self, log_stdout=None, background=False):
        """List all devices.

        Usage:
            list_devices [--background | -b]
        """
        log_stdout("Address   Cat   Subcat Description")
        log_stdout(
            "--------  ----- ------ ------------------------------------------------------------------------"
        )
        for addr in devices:
            device = devices[addr]
            log_stdout(
                f"{addr}  {device.cat!r}  0x{int(device.subcat):02x}   {device.description}"
            )
        log_stdout(f"Total devices: {len(devices)}")

    async def do_log_to_file(self, logging_mode, workdir=None):
        """Start logging to file.

        Usage:
            log_to_file logging_mode [location]

        logging_mode: y | n
        location: Location to store the log file (default is current directory)

        The log file name is `pyinsteon_tools.log`.
        """
        try:
            logging_mode = await self._ensure_bool(
                logging_mode, "Log mode", True, self._log_stdout
            )
        except ValueError:
            self._log_stdout("A valid value for log mode is required")
            return

        root_logger = logging.getLogger()
        if not logging_mode:
            for handler in root_logger.handlers:
                if handler.get_name() == FILE_LOG_HANDLER:
                    root_logger.removeHandler(handler)
            return

        if workdir:
            self.workdir = workdir

        if not self.workdir and not workdir:
            self.workdir = await self._get_workdir()

        log_file = os.path.join(self.workdir, LOG_FILE_NAME)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        )
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(file_formatter)
        file_handler.set_name(FILE_LOG_HANDLER)
        file_handler.addFilter(StripPrefixFilter(self._input_prefix))
        file_handler.addFilter(StripPrefixFilter(self._background_prefix))
        root_logger.addHandler(file_handler)

    async def do_save_devices(self, workdir=None, log_stdout=None, background=False):
        """Save devices to the working directory.

        Usage:
            save_devices [--background | -b] workdir

        workdir: Directory where the saved device file is located
        """
        if workdir is None:
            workdir = self.workdir if self.workdir else "."

        self.workdir = workdir

        if not self.workdir:
            if background:
                log_stdout("A value for the working directory is required.")
                return
            self.workdir = await self._get_workdir()

        if not self.workdir:
            return

        await devices.async_save(workdir=self.workdir)

    async def do_back(self):
        """Go back to the previous menu.

        Usage:
            back
        """
        if self.prompt[:-2] != self._prompt_base:
            return -1

    async def do_exit(self):
        """Exit the tool.

        Usage:
            exit
        """
        await self.do_log_to_file("n")
        return True

    async def do_set_log_level(self, level):
        """Set the log level to INFO (i) or VERBOSE (v).

        Usage:
            set_log_level level

        level: Can be one of the following:
            i: Info
            v: Debug
            m: Show messages
            t: Show topics
        """

        options = ["i", "v", "m", "t", "n"]
        if level is not None:
            level = level.lower()

        level = await self._ensure_string(
            level,
            options,
            "Log level (i=info, v=verbose, m=messages, t=topics)",
            True,
            self._log_stdout,
        )

        root_logger = logging.getLogger()
        if level == "i":
            root_logger.setLevel(logging.INFO)
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.ERROR)
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.ERROR)
        elif level == "v":
            root_logger.setLevel(logging.DEBUG)
        elif level == "m":
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.DEBUG)
        elif level == "t":
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.DEBUG)

    async def do_debug_device(self, address, logging_mode=True):
        """Place a device into debug mode to log all topics for the device.

        usage:
            debug_device address [logging_mode]

        logging_mode: y | n  (default is y)

        """
        try:
            addresses = await self._ensure_address(
                address=address,
                name="Address",
                ask_value=True,
                log_stdout=self._log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addresses:
                raise ValueError
            address = addresses[0]
        except ValueError:
            self._log_stdout("Invalid device address or device not found")
            return
        try:
            logging_mode = await self._ensure_bool(
                logging_mode, "Log mode", True, self._log_stdout
            )
        except ValueError:
            self._log_stdout("A valid value for log mode is required")
            return

        logger = logging.getLogger(f"pyinsteon.{address.id}")
        log_level = logging.DEBUG if logging_mode else logging.INFO
        logger.setLevel(log_level)

    async def do_status(self, address, reload, log_stdout=None, background=False):
        """Display the status of a device.

        Usage:
            status [--background | -b] <address>|all y|n

        address: Enter a single address or all for all devices
        reload: y to request the device to send status or
                n to use the current known status
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
                if background:
                    raise ValueError
                return
        except ValueError:
            log_stdout("Invalid device address or device not found")
            return

        try:
            refresh_current = await self._ensure_bool(
                reload, "Reload", not background, log_stdout
            )
            if refresh_current is None:
                if background:
                    raise ValueError
                return
        except ValueError:
            log_stdout("Invalid value for reload")
            return

        tasks = []

        for device_address in addresses:
            if devices[device_address] != devices.modem:
                if not refresh_current:
                    for group in devices[device_address].groups:
                        if devices[device_address].groups[group].value is None:
                            refresh_current = True
                            break
                if refresh_current:
                    tasks.append(devices[device_address].async_status())
        if tasks:
            await asyncio.gather(*tasks)

        for device_address in addresses:
            if devices[device_address] != devices.modem:
                self._print_device_status(log_stdout, device_address)

    async def do_monitor_mode(self):
        """Enter monitoring mode.

        Usage:
            monitor_mode
        """
        self._log_stdout("Press enter to exit monitor mode")
        self._remove_filter()
        await self.stdin.readline()
        self._add_filter()

    def _print_device_status(self, log_stdout, address):
        """Print device status to log."""
        device = devices[address]
        log_stdout("Address  Group State Name      Value")
        log_stdout("-------- ----- --------------- -----")
        for group_id in device.groups:
            group = device.groups[group_id]
            log_stdout(
                f"{device.address} {group_id:>3d}   {group.name:15.15s} {str(group.value):>5s}"
            )

    def _async_run(self, func, *args, **kwargs):
        """Run a function in the event loop."""
        self.loop.run_until_complete(func(*args, **kwargs))

    async def _get_connection_params(self, password):
        """Ensure connectoin parameters are filled."""
        if self.host:
            modem_type = "hub"
        elif self.device:
            modem_type = "plm"
        else:
            modem_type = None

        modem_type = await self._ensure_string(
            modem_type,
            ["plm", "hub"],
            "Modem type (plm or hub)",
            True,
            self._log_stdout,
        )
        if not modem_type:
            return None

        if modem_type == "plm":
            self.device = await self._ensure_string(
                self.device,
                None,
                "Device (i.e. /dev/ttyUSB0 or COM5)",
                True,
                self._log_stdout,
            )
            self._log_input(f"    Device: {self.device}")
            return

        self.host = await self._ensure_string(
            self.host, None, "Hub IP address or hostname", True, self._log_stdout
        )
        if not self.host:
            return

        self.username = await self._ensure_string(
            self.username, None, "Username", True, self._log_stdout
        )
        if not self.username:
            return

        self._log_command(f"Password in: {password}")
        if not password:
            self._log_command("Need password")
            if hasattr(self.stdin, "not_tty"):
                self._log_command("Using standard input method")
                # Used for test purposes to allow input via a stream vs a tty device
                password = await self._input("Password")
            else:
                password = getpass.getpass(prompt="Hub password: ")
            if not password:
                raise ValueError("Password is required")

        self.hub_version = await self._ensure_int(
            self.hub_version,
            [1, 2],
            "Hub version",
            True,
            self._log_stdout,
            default=2,
        )

        self.port = await self._ensure_int(
            self.port,
            None,
            "Hub port",
            True,
            self._log_stdout,
            default=DEFAULT_HUB_PORT[self.hub_version],
        )
        return password

    def postcmd(self, stop, line):
        """Perform post command execution."""
        if line == "exit":
            return True
        return False

    async def _input(self, prompt=""):
        """Asyncronous input of a line."""
        self.stdout.write(prompt)
        await self.stdout.drain()
        line = await self.stdin.readline()
        return line.strip("\r\n")

    def _setup_logging(self, level):
        """Set up the initial console logging."""

        root_logger = logging.getLogger()

        # remove any existing logging that are not our handlers
        # add filter to existing stdout handler
        found_our_handlers = False
        for handler in root_logger.handlers:
            if handler.get_name() not in [STDOUT_LOG_HANDLER, FILE_LOG_HANDLER]:
                logging.getLogger().removeHandler(handler)
            else:
                found_our_handlers = True

        if found_our_handlers:
            return

        stdout_formatter = logging.Formatter("%(message)s")
        console_handler = logging.StreamHandler(self.stdout)
        console_handler.setFormatter(stdout_formatter)
        console_handler.set_name(STDOUT_LOG_HANDLER)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(level)

    async def _call_next_menu(self, menu, name=None):
        """Start the next menu."""
        cmd_args = CmdArgs(
            self.workdir,
            self.device,
            self.username,
            self.host,
            self.hub_version,
            self.port,
        )
        await menu(
            self.loop, cmd_args, name, stdin=self.stdin, stdout=self.stdout
        ).start_menu()

    def _add_filter(self):
        """Add a filter for the current menu."""
        root_logger = logging.getLogger()
        found_prompt = False
        found_prefix = False
        found_input = False
        found_background = False
        for handler in root_logger.handlers:
            if handler.get_name() == STDOUT_LOG_HANDLER:
                for my_filter in handler.filters:
                    if hasattr(my_filter, "prefix") and my_filter.prefix == self.prompt:
                        found_prompt = True
                    if (
                        hasattr(my_filter, "prefix")
                        and my_filter.prefix == self._log_prefix
                    ):
                        found_prefix = True
                    if (
                        hasattr(my_filter, "input_prefix")
                        and my_filter.prefix == self._input_prefix
                    ):
                        found_input = True
                    if (
                        hasattr(my_filter, "prefix")
                        and my_filter.prefix == self._background_prefix
                    ):
                        found_background = True
                if not found_prompt:
                    handler.addFilter(NoStdoutFilter(self.prompt))
                if not found_prefix:
                    handler.addFilter(StdoutFilter(self._log_prefix))
                if not found_input:
                    handler.addFilter(NoStdoutFilter(self._input_prefix))
                if not found_background:
                    handler.addFilter(NoStdoutFilter(self._background_prefix))

    def _remove_filter(self):
        """Remove the stdout filter to enable log output."""
        root_logger = logging.getLogger()
        found_prefix_filter = False
        for handler in root_logger.handlers:
            if handler.get_name() == STDOUT_LOG_HANDLER:
                for my_filter in handler.filters:
                    if (
                        hasattr(my_filter, "prefix")
                        and my_filter.prefix == self._log_prefix
                    ):
                        found_prefix_filter = True
                        stdout_filter = my_filter
                        break
            if found_prefix_filter:
                handler.removeFilter(stdout_filter)

    def _log_command(self, line):
        """Log the command to the log file if the log file is active."""
        # This works because there is a filter on stdout for
        # any string begining with self.prompt
        output = f"{self.prompt}{line}"
        _LOGGING.info(output)

    def _log_background(self, line):
        """Log the command to the log file if the log file is active."""
        # This works because there is a filter on stdout for
        # any string begining with self.prompt
        output = f"{self._background_prefix}{line}"
        _LOGGING.info(output)

    def _log_stdout(self, line):
        """Log a message to standard out."""
        output = f"{self._log_prefix}{line}"
        _LOGGING.info(output)

    def _log_input(self, line):
        """Log a message to standard out."""
        output = f"{self._input_prefix}{line}"
        _LOGGING.info(output)

    async def _get_int(self, prompt, default=None, values=None):
        """Get an integer value."""
        if default is not None:
            prompt = f"{prompt} (Default {default}): "
        else:
            prompt = f"{prompt}: "
        while True:
            value = await self._input(prompt)
            self._log_input(f"    {prompt}: {value}")
            if value == "":
                return default
            try:
                value = int(value)
                if values and value not in values:
                    raise ValueError
                return value
            except ValueError:
                response = "Must be a number."
                if values:
                    response = f"{response} Acceptable values {values}."
                self._log_stdout(response)

    async def _get_float(self, prompt, default=None, maximum=None, minimum=None):
        """Get a floating point value."""
        if default is not None:
            prompt = f"{prompt} (Default {default}): "
        else:
            prompt = f"{prompt}: "
        while True:
            value = await self._input(prompt)
            self._log_input(f"    {prompt}: {value}")
            if value == "":
                return default
            try:
                value = float(value)
                if minimum is not None and value < minimum:
                    raise ValueError
                if maximum is not None and value > maximum:
                    raise ValueError
                return value
            except ValueError:
                response = "Must be a number."
                if maximum is not None and minimum is not None:
                    response = f"{response} (Max: {maximum}  Min: {minimum})."
                elif maximum is not None:
                    response = f"{response} (Max: {maximum})."
                elif minimum is not None:
                    response = f"{response} (Min: {minimum})."
                self._log_stdout(response)

    async def _get_char(
        self, prompt, default=None, values=None, ignore_case=True, hex_string=False
    ):
        """Get a character string value."""
        if default is not None:
            prompt = f"{prompt} (Default {default.upper()}): "
        else:
            prompt = f"{prompt}: "
        if ignore_case and values:
            values = [val.lower() for val in values]

        while True:
            value = await self._input(prompt)
            self._log_input(f"    {prompt}: {value}")
            if hex_string and value.startswith("0x"):
                value = value[2:]

            if value == "":
                return default

            if not values:
                return value

            if ignore_case and value.lower() in values:
                return value.lower()

            if value in values:
                return value

            self._log_stdout(f"Acceptable values {values}.")

    async def _get_workdir(self):
        """Input the value for the workdir."""
        self._log_stdout("The working directory stores the list of identified devices.")
        self._log_stdout(
            "Enter a working directory where the saved file is (and will be saved to after loading.)"
        )
        while True:
            workdir = await self._input(
                "Working directory (enter . for current director): "
            )
            self._log_input(f"    Working Directory: {workdir}")

            if workdir == "":
                return None

            if workdir == ".":
                return os.getcwd()

            if os.path.exists(workdir):
                return workdir

            self._log_stdout("Directory does not exist")

    async def _get_address(
        self,
        allow_all=True,
        match_device=True,
        prompt="Address",
    ):
        """Get the address of a device or all devices."""
        if allow_all:
            input_prompt = f"{prompt} or all for all device addresses: "
        else:
            input_prompt = prompt

        while True:
            address = await self._input(input_prompt)
            self._log_input(f"    {input_prompt}: {address}")

            if address == "":
                return []

            try:
                addresses = validate_address(
                    address, allow_all, match_device, self._log_stdout
                )
                return addresses
            except ValueError:
                address = None

    def _print_aldb_out(self, addresses, unused, log_stdout):
        """Print the ALDB to the log."""
        for address in addresses:
            device = devices[address]
            records = [
                device.aldb[mem_addr]
                for mem_addr in device.aldb
                if (unused or device.aldb[mem_addr].is_in_use)
            ]
            self._print_aldb_output(log_stdout, device, records)

    def _print_aldb_output(self, log_stdout, device="", records=1, **kwargs):
        log_stdout("")
        log_stdout(f"Device: {device.address}  Load Status: {str(device.aldb.status)}")
        log_stdout("RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3")
        log_stdout("----- ------ ---- --- ----- -------- ------ ------ ------")
        for rec in records:
            in_use = "Y" if rec.is_in_use else "N"
            link_mode = "C" if rec.is_controller else "R"
            hwm = "Y" if rec.is_high_water_mark else "N"
            line = f" {rec.mem_addr:04x}    {in_use:s}     {link_mode:s}   {hwm:s}    {rec.group:3d} {rec.target}   {rec.data1:3d}   {rec.data2:3d}   {rec.data3:3d}"
            log_stdout(line)
        log_stdout("")

    @classmethod
    def _set_active_task(cls, task):
        """Set the active task."""
        cls._active_task = task

    @classmethod
    def _cancel_active_task(cls, *args, **kwargs):
        """Cancel the active task."""
        if cls._active_task is not None:
            cls._active_task.cancel()

    async def _ensure_byte(self, value, name, ask_value, log_stdout, default=None):
        """Ensure a given `value` is a single bite between 0 - 255.

        Returns `None` or default if value is `None` and `ask_value` is `False`.
        Raises `ValueError` if `value` is not a valid byte and `ask_value` is `False`.
        """
        if value is None and not ask_value:
            return default

        try:
            value = int(value) if value is not None else None
            if value not in range(0, 256):
                raise ValueError
        except ValueError as ex:
            log_stdout(f"Invalid {name} value")
            if not ask_value:
                raise ValueError from ex
            value = None
        if value is None:
            value = await self._get_int(name, default=default, values=range(0, 256))
        return value

    async def _ensure_bool(
        self,
        value,
        name,
        ask_value,
        log_stdout,
        true_val=None,
        values=None,
        default=None,
    ):
        """Compare a given `value` against `true_val`.

        Returns `None` if value is `None` and `ask_value` is `False`.
        Raises `ValueError` if `value` is not in the list of acceptable values
        and `ask_value` is `False`.
        """

        if value is None and not ask_value:
            return default

        if true_val is None:
            true_val = "y"

        if values is None:
            values = ["y", "n"]

        if value is not None:
            if str(value).lower() in values:
                return str(value).lower() == true_val
            log_stdout(f"Invalid {name} value")
            if not ask_value:
                raise ValueError
            value = None

        default_char = true_val if default else ""
        val = await self._get_char(name, values=values, default=default_char)
        if val == "":
            return default
        return val == true_val

    async def _ensure_int(
        self, value, values, name, ask_value, log_stdout, default=None
    ):
        """Ensure a value is an int within the acceptable values`.

        Returns `default` if value is `None` and `ask_value` is `False`.
        Raises `ValueError` if `value` is not in the list of acceptable values
        and `ask_value` is `False`.
        """
        if value is None and not ask_value:
            return default

        if value is not None:
            try:
                value = int(value)
                if not values or value in values:
                    return value
                raise ValueError
            except (ValueError, TypeError):
                log_stdout(f"Invalid {name} value")
                value = None

        if not ask_value:
            raise ValueError

        return await self._get_int(name, values=values, default=default)

    async def _ensure_float(
        self, value, minimum, maximum, name, ask_value, log_stdout, default=None
    ):
        """Ensure a value is a floting point number within the acceptable values`.

        Returns `None` if value is `None` and `ask_value` is `False`.
        Raises `ValueError` if `value` is not in the list of acceptable values
        and `ask_value` is `False`.
        """
        if value is None and not ask_value:
            return default

        if value is not None:
            try:
                value = float(value)
                if minimum is not None and value < minimum:
                    raise ValueError
                if maximum is not None and value > maximum:
                    raise ValueError
                return value
            except (ValueError, TypeError):
                log_stdout(f"Invalid {name} value")
                value = None

        if not ask_value:
            raise ValueError

        return await self._get_float(
            name, default=default, minimum=minimum, maximum=maximum
        )

    async def _ensure_string(
        self, value, values, name, ask_value, log_stdout, default=None
    ):
        """Ensure a value is a string within the acceptable values`.

        Returns `default` if `default` is set and value is `None` and `ask_value` is `False`.

        Raises `ValueError` if
        - `value` is not in the list of acceptable values and `ask_value` is `False`.
        - `value` is `None` and `default` is not set and `ask_value` is `False`
        """
        if value is None and not ask_value:
            return default

        if value is not None:
            value = str(value)
            if not values or value in values:
                return value
            log_stdout(f"Invalid {name} value")
            value = None

        if not ask_value:
            raise ValueError

        return await self._get_char(name, values=values, default=default)

    async def _ensure_address(
        self,
        address,
        name,
        ask_value,
        log_stdout,
        allow_all=True,
        match_device=True,
    ) -> List[Address]:
        """Ensure a value is a proper device address.

        Returns `[]` if the value is `None` and `ask_value` is `False`

        Returns a list of addresses if value is `all` and allow_all is `True`

        Raises `ValueError` if
        - `value` is not a valid address and `ask_value` is `False`
        - `value` does not match a known device and `match_device` is `True` and `ask_value` is `False`
        - `value` is `all` and `allow_all` is `False` and `ask_value` is `False`
        """
        if address is None and not ask_value:
            return []

        try:
            return validate_address(address, allow_all, match_device, log_stdout)
        except ValueError:
            if not ask_value:
                raise

        return await self._get_address(
            allow_all=allow_all,
            match_device=match_device,
            prompt=name,
        )

    def _get_menus(self):
        """Return the list of menu commands."""
        menus = []
        for method in self.get_names():
            if method.startswith("menu_"):
                menus.append(method[len("menu_") :])
        return menus

    def _parse_args(self, func, all_args):
        def to_args_kwargs(arg_in, f_args, args, kwargs, found_kwarg):
            loc_eq = arg_in.find("=")
            if loc_eq != -1:
                found_kwarg = True
                key = arg_in[:loc_eq]
                val = arg_in[loc_eq + 1 :]
                kwargs[key] = val

            # We found a kwarg previously and now we don't have a kwarg
            # That is an issue!
            elif found_kwarg:
                raise ValueError
            else:
                args.append(arg_in)
                try:
                    f_args.pop(0)
                except IndexError:
                    pass
            return f_args, args, kwargs, found_kwarg

        full_args_spec = inspect.getfullargspec(func)
        f_args = full_args_spec.args
        f_kwargs = full_args_spec.kwonlyargs
        has_vargs = full_args_spec.varargs is not None
        has_kwargs = full_args_spec.varkw is not None
        len_defaults = len(full_args_spec.defaults or [])
        if "self" in f_args:
            f_args.remove("self")

        found_kwarg = False
        args = []
        kwargs = {}
        background = False
        for item in ["--background", "-b"]:
            try:
                all_args.remove(item)
                background = True
            except ValueError:
                pass
        # Set up background and log_stdout kwargs if possible
        if "background" in f_args or "background" in f_kwargs:
            kwargs["background"] = background
            if len_defaults >= 2:
                len_defaults -= 2
            if background:
                kwargs["log_stdout"] = self._log_background
            else:
                kwargs["log_stdout"] = self._log_stdout
            if "background" in f_args:
                f_args.remove("background")
            if "log_stdout" in f_args:
                f_args.remove("log_stdout")

        elif background:
            self._log_stdout("Command cannot be run in the background.")
            background = False

        len_f_args = len(f_args)
        for _ in range(0, len_f_args):
            try:
                arg_in = all_args[0]
                f_args, args, kwargs, found_kwarg = to_args_kwargs(
                    arg_in, f_args, args, kwargs, found_kwarg
                )
                all_args.pop(0)
            except IndexError:
                break
            except ValueError:
                self._log_stdout("Keyword argument before non-keyword argument")
                return args, kwargs, False

        vargs = []
        for arg_in in all_args:
            try:
                f_args, vargs, kwargs, found_kwarg = to_args_kwargs(
                    arg_in, f_args, vargs, kwargs, found_kwarg
                )
            except ValueError:
                self._log_stdout("Keyword argument before non-keyword argument")
                return args, kwargs, False

        if vargs and not has_vargs:
            self._log_stdout("Too many arguements")
            return args, kwargs, False

        args += vargs

        # Test if there are items in kwargs that cannot be handled
        for arg in kwargs:
            if arg in ["background", "log_stdout"]:
                continue
            if arg not in f_args and not has_kwargs:
                self._log_stdout(f"Invalid keyword argument {arg}")
                return args, kwargs, False
            if arg in f_args:
                f_args.remove(arg)

        # Test if we have enough args to continue
        if len(f_args) > len_defaults and background:
            self._log_stdout("Missing arguments required to run in background")
            return args, kwargs, False

        # Pad missing args with `None`.
        for _ in range(0, max(0, len(f_args) - len_defaults)):
            args.append(None)

        return args, kwargs, True

    async def _ensure_arg_value(
        self,
        arg,
        value,
        ask_value,
        log_stdout,
        values=None,
        default=None,
        true_val=None,
        require_two=True,
    ):
        """Convert an argument value from string to argument type.

        Ensures a value for an argument is valid. Uses the ARG_TYPE list to determine the argument type.

        If the argument is `buttons`, the `requires_two` argument determines if two or more buttons is required.
        """

        arg_type = ARG_TYPES.get(arg)
        # pylint: disable=too-many-nested-blocks
        if arg_type is not None:
            try:
                if arg_type == bool:
                    return await self._ensure_bool(
                        value,
                        arg,
                        ask_value,
                        log_stdout,
                        default=default,
                        values=values,
                        true_val=true_val,
                    )

                if arg_type == bytes:
                    return await self._ensure_byte(
                        value, arg, ask_value, log_stdout, default=default
                    )

                if isinstance(arg_type, range):
                    values = values if values is not None else arg_type
                    return await self._ensure_int(
                        value=value,
                        values=values,
                        name=arg,
                        ask_value=ask_value,
                        log_stdout=log_stdout,
                        default=default,
                    )

                if arg.lower() == "buttons":
                    if value is None and not ask_value:
                        return default

                    buttons = []
                    values = values if values else arg_type[0]
                    for button in range(0, len(values)):
                        input_button = None
                        if value:
                            try:
                                input_button = value[button]
                            except IndexError:
                                pass
                        try:
                            button = await self._ensure_int(
                                value=input_button,
                                values=values,
                                name="Button",
                                ask_value=ask_value,
                                log_stdout=log_stdout,
                            )
                        except ValueError as ex:
                            log_stdout("Invalid button number")
                            if not ask_value:
                                raise ValueError from ex
                        if button is None and len(buttons) < 2 and require_two:
                            log_stdout("At least two buttons are required")
                            if not ask_value:
                                raise ValueError
                        if button is None:
                            break
                        buttons.append(button)
                    return buttons

                if arg_type == Address:
                    return await self._ensure_address(
                        address=value,
                        name=arg,
                        ask_value=ask_value,
                        log_stdout=log_stdout,
                        allow_all=False,
                        match_device=False,
                    )

                # enum type:
                log_stdout("\nValid values are:")
                options = []
                for option in arg_type:
                    log_stdout(f"    {option}: {int(option)}")
                    options.append(option)
                return await self._ensure_int(
                    value, options, arg, ask_value, log_stdout, default=default
                )

            except (TypeError, ValueError) as ex:
                log_stdout(f"Invalid value for {arg}")
                raise ValueError from ex
        return value

    async def _ensure_hex_byte(self, value, name, ask_value, log_stdout, values=None):
        """Ensure a value is a hex byte string.

        Returns a bytes value equivalent of the hex string.

        byte_len is the number of bytes. Default is 1 byte (i.e. 0x01, 0xff).
        """

        def hex_str_to_int(value):
            """Convert a hex string into an integer."""
            if value and value.startswith("0x"):
                value = value[2:]
            byte_val = unhexlify(value)
            return int.from_bytes(byte_val, byteorder="big")

        convert_length = {
            range(0, 256): 2,
            range(256, 65536): 4,
            range(65536, 16777216): 6,
        }
        if value is None and not ask_value:
            raise ValueError

        values_text = []

        # pylint: disable=too-many-nested-blocks
        while True:
            if value is not None:
                try:
                    int_value = hex_str_to_int(value)
                    if not values or int_value in values:
                        return int_value
                    value = None
                except (BinasciiError, TypeError, ValueError, IndexError):
                    log_stdout(f"Invalid value for {name}")
                    value = None
            if ask_value:
                if values and not values_text:
                    val_length = 6
                    for val in values:
                        for val_range, convert_len in convert_length.items():
                            if val in val_range:
                                val_length = convert_len
                                break
                        if val_length == 2:
                            values_text.append(f"{val:02x}")
                        elif val_length == 4:
                            values_text.append(f"{val:04x}")
                        else:
                            values_text.append(f"{val:06x}")
                value = await self._get_char(name, values=values_text, hex_string=True)
                if value is None:
                    return None
            else:
                raise ValueError
