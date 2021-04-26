"""Base object for all command line menues."""

import argparse
import asyncio
import getpass
import inspect
import logging
import os
import sys
from cmd import Cmd
from collections import namedtuple
import traceback

from .. import devices
from .log_filter import CommandFilter, StdoutFilter
from .utils import patch_stdin_stdout, set_loop, stdio

_LOGGING = logging.getLogger(__name__)
LOG_FILE_NAME = "pyinsteon_tools.log"
STDOUT_LOG_HANDLER = "stdout_handler"
FILE_LOG_HANDLER = "file_handler"
CmdArgs = namedtuple("CmdArgs", "workdir device username host hub_version port")


class ToolsBase(Cmd):
    """Base class for all tools menues."""

    def __init__(self, loop, args=None, menu=None, stdin=None, stdout=None):
        """Init the InsteonCmd class."""
        super().__init__()
        self.stdin = stdin
        self.stdout = stdout
        prompt = "pyinsteon"
        if menu:
            self.prompt = f"{prompt} - {menu}: "
        else:
            self.prompt = f"{prompt}: "
        self._log_prefix = "STDOUT: "
        self.loop = loop
        self.workdir = None

        # connection variables
        self.device = args.device
        self.username = args.username
        self.host = args.host
        self.hub_version = args.hub_version
        def_port = {}
        def_port[1] = 9761
        def_port[2] = 25105
        self.port = args.port if args.port else def_port.get(self.hub_version)

        if hasattr(args, "verbose") and args.verbose:
            self._setup_logging(logging.DEBUG)
        else:
            self._setup_logging(logging.INFO)
        self._add_filter()

        if hasattr(args, "workdir"):
            self.workdir = args.workdir
            if hasattr(args, "logging") and self.workdir:
                self.do_log_to_file("y", self.workdir)

    async def cmdloop(self, intro=None):
        """Override standard cmdloop to make this async.

        Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if not self.stdin and not self.stdout:
            self.stdin, self.stdout = await stdio(loop=self.loop)
            if sys.platform != "win32":
                patch_stdin_stdout(self.stdin, self.stdout)

        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(self.intro + "\n")
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
                    stop = await self.onecmd(line)
                # pylint: disable=broad-except
                except Exception as ex:
                    self._log_stdout("An error occured executing command.")
                    self._log_stdout(str(ex))
                    _LOGGING.debug(traceback.format_exc())
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            pass

    async def onecmd(self, line):
        """Override the method to make it async.

        Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line

        if line == "EOF":
            return

        if cmd == "":
            return self.default(line)

        try:
            func = getattr(self, "do_" + cmd)
        except AttributeError:
            return self.default(line)
        if inspect.iscoroutinefunction(func) or inspect.isawaitable(func):
            return await func(arg)
        return func(arg)

    # pylint: disable=no-self-use
    def emptyline(self):
        """Change default empty line to do nothing."""
        return

    @classmethod
    def start(cls):
        """Start the loop and the current command set."""
        parser = argparse.ArgumentParser(description=__doc__)
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

        intro = "The command line module for pyinsteon is designed to test devices and perform certain common functions."

        try:
            loop.run_until_complete(cls(loop, args).cmdloop(intro=intro))
        except KeyboardInterrupt:
            loop.stop()
            pending = asyncio.Task.all_tasks(loop=loop)
            for task in pending:
                task.cancel()
                try:
                    loop.run_until_complete(task)
                except asyncio.CancelledError:
                    pass
                except KeyboardInterrupt:
                    pass
            loop.close()

    async def start_menu(self):
        """Start the menu."""
        await self.cmdloop()

    # pylint: disable=no-self-use
    def do_list_devices(self, *args, **kwargs):
        """List all devices.

        Usage:
            list_devices
        """
        self._log_command("list_devices")
        self._log_stdout("Address   Cat   Subcat Description")
        self._log_stdout(
            "--------  ----- ------ ------------------------------------------------------------------------"
        )
        for addr in devices:
            device = devices[addr]
            self._log_stdout(
                f"{addr}  {device.cat!r}  0x{int(device.subcat):02x}   {device.description}"
            )
        self._log_stdout(f"Total devices: {len(devices)}")

    async def do_log_to_file(self, *args, **kwargs):
        """Start logging to file.

        Usage:
            log_to_file y|n
        """
        args = args[0].split()
        try:
            mode = args[0].lower()
        except IndexError:
            mode = None
        if mode not in ["y", "n"]:
            mode = await self._get_char("Log to file (y/n)", values=["y", "n"])

        try:
            if args[1] != "":
                self.workdir = args[1]
        except IndexError:
            pass

        root_logger = logging.getLogger()

        if mode == "n":
            self._log_command("log_to_file n")
            for handler in root_logger.handlers:
                if handler.get_name() == FILE_LOG_HANDLER:
                    root_logger.removeHandler(handler)
            return

        if not self.workdir:
            self.workdir = await self._get_workdir()

        if self.workdir == "":
            self._log_stdout("A value for the working directory is required.")
            return

        log_file = os.path.join(self.workdir, LOG_FILE_NAME)
        self._log_command(f"log_to_file y {self.workdir}")
        file_formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        )
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(file_formatter)
        file_handler.set_name(FILE_LOG_HANDLER)
        root_logger.addHandler(file_handler)

    async def do_save_devices(self, *args, **kwargs):
        """Save devices to the working directory.

        Usage:
            save_devices workdir

        workdir: Directory where the saved device file is located
        """
        args = args[0].split()
        try:
            if args[0] != "":
                self.workdir = args[0]
        except IndexError:
            pass

        if not self.workdir:
            self.workdir = await self._get_workdir()

        if self.workdir == "":
            self._log_stdout("A value for the working directory is required.")
            return

        self._log_command(f"save_devices {self.workdir}")
        await devices.async_save(workdir=self.workdir)

    def do_exit(self, *args, **kwargs):
        """Exit the current menu.

        Usage:
            exit
        """
        self._log_command("exit")
        return -1

    async def do_set_log_level(self, *args, **kwargs):
        """Set the log level to INFO (i) or VERBOSE (v).

        Usage:
            set_log_level i|v|
        i: Info
        v: Debug
        m: Show messages
        t: Show topics
        """
        args = args[0].split()
        try:
            mode = args[0].lower()
        except IndexError:
            mode = None

        options = ["i", "v", "m", "t", "n"]
        if mode not in options:
            mode = await self._get_char(
                "Log level (i=info, v=verbose, m=messages, t=topics, n=no messages or topics)",
                values=options,
            )

        self._log_command(f"set_log_level {mode}")
        root_logger = logging.getLogger()
        if mode == "i":
            root_logger.setLevel(logging.INFO)
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.ERROR)
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.ERROR)
        elif mode == "v":
            root_logger.setLevel(logging.DEBUG)
        elif mode == "m":
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.DEBUG)
        elif mode == "t":
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.DEBUG)

    async def do_status(self, *args, **kwargs):
        """Display the status of a device.

        Usage:
            status <address>|all y|n

        address: Enter a single address or all for all devices
        reload: y to request the device to send status or
                n to use the current known status
        """
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None
        try:
            refresh_yn = args[1].lower()
            if refresh_yn not in ["y", "n"]:
                refresh_yn = None
        except IndexError:
            refresh_yn = None

        tasks = []
        addresses = await self._get_addresses(
            address=address, allow_all=True, allow_cancel=True, match_device=True
        )
        if not addresses:
            return

        for address in addresses:
            if devices[address] != devices.modem:
                if not refresh_yn:
                    refresh_yn = await self._get_char(
                        "Clear existing records and reload (y/n)",
                        default="n",
                        values=["y", "n"],
                    )
                refresh_current = refresh_yn.lower()
                if refresh_current == "n":
                    for group in devices[address].groups:
                        if devices[address].groups[group].value is None:
                            refresh_current = "y"
                            break
                if refresh_current == "y":
                    tasks.append(devices[address].async_status())
        if tasks:
            await asyncio.gather(*tasks)

        for address in addresses:
            if devices[address] != devices.modem:
                self._print_device_status(address)

    async def do_monitor_mode(self, *args, **kwargs):
        """Enter monitoring mode.

        Usage:
            monitor_mode
        """
        self._log_stdout("Press enter to exit monitor mode")
        self._remove_filter()
        await self.stdin.readline()
        self._add_filter()

    def _print_device_status(self, address):
        """Print device status to log."""
        device = devices[address]
        self._log_stdout("Address  Group State Name      Value")
        self._log_stdout("-------- ----- --------------- -----")
        for group_id in device.groups:
            group = device.groups[group_id]
            self._log_stdout(
                f"{device.address} {group_id:>3d}   {group.name:15.15s} {str(group.value):>5s}"
            )

    def _async_run(self, func, *args, **kwargs):
        """Run a function in the event loop."""
        self.loop.run_until_complete(func(*args, **kwargs))

    async def _get_connection_params(self):
        """Ensure connectoin parameters are filled."""
        password = None
        if not self.device and not self.host:
            self.device = await self._input(
                "USB Device (i.e. /dev/ttyUSB0 or COM5) press enter if Hub: "
            )
        if not self.device:
            if not self.host:
                self.host = await self._input("Hub IP address or hostname: ")
            if not self.username:
                self.username = await self._input("Hub usernme: ")
            password = getpass.getpass(prompt="Hub password: ")
            if not self.hub_version:
                self.hub_version = await self._get_int(
                    "Hub version", default=2, values=[1, 2],
                )
            if not self.port:
                self.port = await self._get_int(
                    "Hub port", default=25105 if self.hub_version == 2 else 9761,
                )
        return password

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
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(stdout_formatter)
        console_handler.set_name(STDOUT_LOG_HANDLER)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(level)
        self._log_stdout(f"Set log level to {level}")

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
        for handler in root_logger.handlers:
            if handler.get_name() == STDOUT_LOG_HANDLER:
                for my_filter in handler.filters:
                    if hasattr(my_filter, "prompt") and my_filter.prompt == self.prompt:
                        found_prompt = True
                    if (
                        hasattr(my_filter, "prefix")
                        and my_filter.prefix == self._log_prefix
                    ):
                        found_prefix = True
                if not found_prompt:
                    handler.addFilter(CommandFilter(self.prompt))
                if not found_prefix:
                    handler.addFilter(StdoutFilter(self._log_prefix))

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
        output = f"{self.prompt}{line}"
        _LOGGING.info(output)

    def _log_stdout(self, line):
        """Log a message to standard out."""
        output = f"{self._log_prefix}{line}"
        _LOGGING.info(output)

    async def _get_int(self, prompt, default=None, values=None):
        """Get an integer value."""
        value = None
        if default is not None:
            prompt = f"{prompt} (Default {default}): "
        else:
            prompt = f"{prompt}: "
        while True:
            value = await self._input(prompt)
            if value:
                try:
                    value = int(value)
                    if values and value not in values:
                        raise ValueError()
                    break
                except ValueError:
                    response = "Must be a number."
                    if values:
                        response = f"{response} Acceptable values {values}."
                    self._log_stdout(response)
            elif default is not None:
                value = default
                break
            else:
                response = "A number is required."
                if values:
                    response = f"{response} Acceptable values {values}."
                self._log_stdout(response)
        return value

    async def _get_float(self, prompt, default=None, maximum=None, minimum=None):
        """Get a floating point value."""
        value = None
        if default is not None:
            prompt = f"{prompt} (Default {default}): "
        else:
            prompt = f"{prompt}: "
        while True:
            value = await self._input(prompt)
            if value:
                try:
                    value = float(value)
                    if value < minimum or value > maximum:
                        raise ValueError()
                    break
                except ValueError:
                    response = "Must be a number."
                    if maximum and minimum:
                        response = f"{response} (Max: {maximum}  Min: {minimum})."
                    elif maximum:
                        response = f"{response} (Max: {maximum})."
                    elif maximum and minimum:
                        response = f"{response} (Min: {minimum})."
                    self._log_stdout(response)
            elif default is not None:
                value = default
                break
            else:
                response = "Must be a number."
                if maximum and minimum:
                    response = f"{response} (Max: {maximum}  Min: {minimum})."
                elif maximum:
                    response = f"{response} (Max: {maximum})."
                elif maximum and minimum:
                    response = f"{response} (Min: {minimum})."
                self._log_stdout(response)
        return value

    async def _get_char(self, prompt, default=None, values=None):
        """Get a character string value."""
        if default is not None:
            prompt = f"{prompt} (Default {default.upper()}): "
        else:
            prompt = f"{prompt}: "
        while True:
            value = await self._input(prompt)
            if value:
                if not values or value.lower() in values:
                    break
                self._log_stdout(f"Acceptable values {values}")
            elif default is not None:
                value = default
                break
            else:
                response = "A response is required."
                if values:
                    response = f"{response} Acceptable values {values}."
                self._log_stdout(response)
        return value

    async def _get_workdir(self):
        """Input the valeu for the workdir."""
        self._log_stdout("The working directory stores the lsit of identified devices.")
        self._log_stdout(
            "Enter a working directory where the saved file is (and will be saved to after loading.)"
        )
        workdir = await self._input(
            f"Working directory (enter . for current director): "
        )
        if workdir == ".":
            return os.getcwd()
        return workdir

    async def _get_addresses(
        self,
        address=None,
        allow_cancel=False,
        allow_all=True,
        match_device=True,
        prompt="Enter device address",
    ):
        """Get the address of a device or all devices."""
        prompt_addr = prompt
        prompt_cancel = f"{prompt} or blank to cancel"
        prompt_all = f"{prompt} or all for all devices"
        prompt_all_cancel = f"{prompt}, all for all devices, or blank to cancel"

        addresses = []
        if allow_all and allow_cancel:
            prompt = f"{prompt_all_cancel}: "
        elif allow_all:
            prompt = f"{prompt_all}: "
        elif allow_cancel:
            prompt = f"{prompt_cancel}: "
        else:
            prompt = prompt_addr

        while True:
            try:
                if not address:
                    address = await self._input(prompt)
                if not address:
                    if allow_cancel:
                        return addresses
                elif str(address).strip("'\"").lower() == "all":
                    for addr in devices:
                        addresses.append(addr)
                    return addresses
                elif devices[address] or not match_device:
                    addresses.append(address)
                    return addresses
                else:
                    self._log_stdout(f"Device {address} not found in device list.")
                    return []
            except ValueError:
                self._log_stdout("Invalid address entered.")
                address = None

    async def _print_aldb(self, *args):
        """Print the All-Link Database to the log."""
        args = args[0].split()
        try:
            address = args[0]
        except IndexError:
            address = None

        addresses = await self._get_addresses(
            address=address, allow_all=True, allow_cancel=True, match_device=True
        )
        if not addresses:
            return
        self._log_command(f"print_aldb {'all' if len(addresses) > 1 else addresses[0]}")
        self._print_aldb_out(addresses)

    def _print_aldb_out(self, addresses):
        """Print the ALDB to the log."""
        for address in addresses:
            device = devices[address]
            self._log_stdout("")
            self._log_stdout(
                f"Device: {device.address}  Load Status: {str(device.aldb.status)}"
            )
            self._log_stdout(
                "RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3"
            )
            self._log_stdout(
                "----- ------ ---- --- ----- -------- ------ ------ ------"
            )
            for mem_addr in device.aldb:
                rec = device.aldb[mem_addr]
                in_use = "Y" if rec.is_in_use else "N"
                mode = "C" if rec.is_controller else "R"
                hwm = "Y" if rec.is_high_water_mark else "N"
                line = f" {rec.mem_addr:04x}    {in_use:s}     {mode:s}   {hwm:s}    {rec.group:3d} {rec.target}   {rec.data1:3d}   {rec.data2:3d}   {rec.data3:3d}"
                self._log_stdout(line)
            self._log_stdout("")
