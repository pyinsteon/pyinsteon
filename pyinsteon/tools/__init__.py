"""Command line tools to interact with the Insteon devices."""
import logging
import os
from .. import async_connect, async_close, devices
from .cmd_base import ToolsBase, get_int, get_workdir
from .op_flags import ToolsOpFlags
from .aldb import ToolsAldb

_LOGGING = logging.getLogger(__name__)


class InsteonCmd(ToolsBase):
    """Command class to test interactivity."""

    async def do_connect(self, *args, **kwargs):
        """Connect to the Insteon modem.

        Usage:
            connect device
            connect host username [hub_version port]
        """
        args = args[0].split()
        try:
            self.username = args[1]
            self.host = args[0]
            self.hub_version = int(args[2])
            self.port = int(args[3])
        except IndexError:
            try:
                self.device = args[0]
            except IndexError:
                pass
            params = self.device
        except ValueError:
            self.hub_version = None
            self.port = None

        password = self._get_connection_params()

        if self.username:
            params = f"{self.host} {self.username} {'*' * len(password)} {self.hub_version} {self.port}"
        self._log_command(f"connect {params}")
        await async_connect(
            device=self.device,
            host=self.host,
            port=self.port,
            username=self.username,
            password=password,
            hub_version=self.hub_version,
        )

    async def do_disconnect(self, *args, **kwargs):
        """Close the connection to the modem.

        Usage:
            disconnect
        """
        self._log_command("disconnect")
        await async_close()

    async def do_load_devices(self, *args, **kwargs):
        """Load the devices.

        Usage:
            load_devices workdir id_devices

        workdir: Directory where the saved device file is located (Enter . for current directory)
        id_devices: Option for handling unknown devices
            0 - Do not ID devices
            1 - ID unknown devices only (default)
            2 - ID all devices
        """

        args = args[0].split()
        try:
            if args[0] != "":
                self.workdir = args[0]
                if self.workdir == ".":
                    self.workdir = os.getcwd()
        except IndexError:
            pass

        if not self.workdir:
            self.workdir = get_workdir()

        try:
            id_devices = int(args[1])
        except (IndexError, ValueError):
            id_devices = None
        if id_devices not in [0, 1, 2]:
            id_devices = get_int(
                "Identify devices (0=None, 1=Unknown Only, 2=All", 1, [0, 1, 2]
            )
        self._log_command(f"load_devices {self.workdir} {id_devices}")
        await devices.async_load(workdir=self.workdir, id_devices=id_devices)
        self._log_stdout(f"Total devices: {len(devices)}")

    def do_manage_aldb(self, *args, **kwargs):
        """Manage device All-Link database."""
        self._log_command("manage_aldb")
        self._call_next_menu(ToolsAldb, "aldb")

    def do_manage_op_flags(self, *args, **kwargs):
        """Manage operational flags."""
        self._log_command("manage_op_flags")
        self._call_next_menu(ToolsOpFlags, "op_flags")


def tools():
    """Start insteon tools."""
    InsteonCmd.start()
