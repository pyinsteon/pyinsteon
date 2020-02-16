"""Base object for all command line menues."""

import argparse
from collections import namedtuple
import asyncio
import cmd
import getpass
import logging
import os
import sys

from .. import devices
from .log_filter import CommandFilter
from .utils import get_addresses, get_char, get_int, get_workdir

_LOGGING = logging.getLogger(__name__)
LOG_FILE_NAME = "pyinsteon_tools.log"
STDOUT_LOG_HANDLER = "stdout_handler"
FILE_LOG_HANDLER = "file_handler"
CmdArgs = namedtuple("CmdArgs", "workdir device username host hub_version port")


class ToolsBase(cmd.Cmd):
    """Base class for all tools menues."""

    def __init__(self, loop, args=None, menu=None):
        """Init the InsteonCmd class."""
        super().__init__()
        prompt = "pyinsteon"
        if menu:
            self.prompt = f"{prompt} - {menu}: "
        else:
            self.prompt = f"{prompt}: "
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

        if hasattr(args, "verbose"):
            if args.verbose:
                self._setup_logging(logging.DEBUG)
            else:
                self._setup_logging(logging.INFO)
        self._add_filter()

        if hasattr(args, "workdir"):
            self.workdir = args.workdir
            if hasattr(args, "logging") and self.workdir:
                self.do_log_to_file("y", self.workdir)

    def _log_command(self, line):
        """Log the command to the log file if the log file is active."""
        output = f"{self.prompt}{line}"
        _LOGGING.info(output)

    @classmethod
    def start(cls, loop=None, args=None, menu=None):
        """Start the tools menu."""

        if not loop:
            cls._start_loop()
        else:
            cls(loop, args, menu).cmdloop()

    # pylint: disable=no-self-use
    def emptyline(self):
        """Change default empty line to do nothing."""
        return

    @classmethod
    def _start_loop(cls):
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

        loop = asyncio.get_event_loop()

        intro = "\nThe command line module for pyinsteon is designed to test devices and perform certain common functions.\nTo see the list of commands enter `help`\n."

        try:
            cls(loop, args).cmdloop(intro=intro)
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

    # pylint: disable=no-self-use
    def do_list_devices(self, *args, **kwargs):
        """List all devices.

        Usage:
            list_devices
        """
        self._log_command("list_devices")
        _LOGGING.info("Address   Cat   Subcat Description")
        _LOGGING.info(
            "--------  ----- ------ ------------------------------------------------------------------------"
        )
        for addr in devices:
            device = devices[addr]
            _LOGGING.info(
                "%s  0x%02x  0x%02x   %s",
                addr,
                device.cat,
                device.subcat,
                device.description,
            )
        _LOGGING.info("Total devices: %d", len(devices))

    def do_log_to_file(self, *args, **kwargs):
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
            mode = get_char("Log to file (y/n)", values=["y", "n"])

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
            self.workdir = get_workdir()

        if self.workdir == "":
            _LOGGING.error("A value for the working directory is required.")
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

    def do_save_devices(self, *args, **kwargs):
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
            self.workdir = get_workdir()

        if self.workdir == "":
            _LOGGING.error("A value for the working directory is required.")
            return

        self._log_command(f"save_devices {self.workdir}")
        self._async_run(devices.async_save, workdir=self.workdir)

    def do_exit(self, *args, **kwargs):
        """Exit the current menu.

        Usage:
            exit
        """
        self._log_command("exit")
        return -1

    def do_set_log_level(self, *args, **kwargs):
        """Set the log level to INFO (i) or VERBOSE (v).

        Usage:
            set_log_level i|v|
        i: Info
        v: Debug
        m: Show messages
        t: Show topics
        n: No messages or topics
        """
        args = args[0].split()
        try:
            mode = args[0].lower()
        except IndexError:
            mode = None

        options = ["i", "v", "m", "t", "n"]
        if mode not in options:
            mode = get_char(
                "Log level (i=info, v=verbose, m=messages, t=topics, n=no messages or topics)",
                values=options,
            )

        self._log_command(f"set_log_level {mode}")
        root_logger = logging.getLogger()
        if mode == "i":
            root_logger.setLevel(logging.INFO)
        elif mode == "v":
            root_logger.setLevel(logging.DEBUG)
        elif mode == "m":
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.DEBUG)
        elif mode == "t":
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.DEBUG)
        elif mode == "n":
            message_logger = logging.getLogger("pyinsteon.messages")
            message_logger.setLevel(logging.ERROR)
            topic_logger = logging.getLogger("pyinsteon.topics")
            topic_logger.setLevel(logging.ERROR)

    def do_device_status(self, *args, **kwargs):
        """Display device statis.

        Usage:
            device_status
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
        addresses = get_addresses(allow_all=True, allow_cancel=True)
        if not addresses:
            return

        for address in addresses:
            if devices[address] != devices.modem:
                if not refresh_yn:
                    refresh_yn = get_char(
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
            self._async_run(asyncio.gather, *tasks)

        for address in addresses:
            if devices[address] != devices.modem:
                self._print_device_status(address)

    def _print_device_status(self, address):
        """Print device status to log."""
        device = devices[address]
        _LOGGING.info("Address  Group State Name      Value")
        _LOGGING.info("-------- ----- --------------- -----")
        for group_id in device.groups:
            group = device.groups[group_id]
            _LOGGING.info(
                "%s %5d %.15s %5d", device.address, group_id, group.name, group.value
            )

    def _async_run(self, func, *args, **kwargs):
        """Run a function in the event loop."""
        self.loop.run_until_complete(func(*args, **kwargs))

    def _get_connection_params(self):
        """Ensure connectoin parameters are filled."""
        password = None
        if not self.device and not self.host:
            self.device = input(
                "USB Device (i.e. /dev/ttyUSB0 or COM5) press enter if Hub: "
            )
        if not self.device:
            if not self.host:
                self.host = input("Hub IP address or hostname: ")
            if not self.username:
                self.username = input("Hub usernme: ")
            password = getpass.getpass(prompt="Hub password: ")
            if not self.hub_version:
                self.hub_version = get_int("Hub version", 2, [1, 2])
            if not self.port:
                self.port = get_int(
                    "Hub port", 25105 if self.hub_version == 2 else 9761
                )
        return password

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
        _LOGGING.info("Set log level to %s", level)

    def _call_next_menu(self, menu, name=None):
        """Start the next menu."""
        cmd_args = CmdArgs(
            self.workdir,
            self.device,
            self.username,
            self.host,
            self.hub_version,
            self.port,
        )
        menu.start(self.loop, cmd_args, name)

    def _add_filter(self):
        """Add a filter for the current menu."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if handler.get_name() == STDOUT_LOG_HANDLER:
                for my_filter in handler.filters:
                    if hasattr(my_filter, "prompt") and my_filter.prompt == self.prompt:
                        return
                handler.addFilter(CommandFilter(self.prompt))
