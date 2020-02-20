"""Utilities for the tools commands."""
import asyncio
import logging
import os
import sys

from .. import devices

_LOGGING = logging.getLogger(__name__)
_DEFAULT_LIMIT = 2 ** 16  # 64kb


def get_int(prompt, default=None, values=None):
    """Get an integer value."""
    value = None
    if default:
        prompt = f"{prompt} (Default {default}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
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
                _LOGGING.info(response)
        elif default is not None:
            value = default
            break
        else:
            response = "A number is required."
            if values:
                response = f"{response} Acceptable values {values}."
            _LOGGING.info(response)
    return value


def get_float(prompt, default=None, maximum=None, minimum=None):
    """Get an integer value."""
    value = None
    if default:
        prompt = f"{prompt} (Default {default}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
        if value:
            try:
                value = float(value)
                if value < maximum or value > maximum:
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
                _LOGGING.info(response)
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
            _LOGGING.info(response)
    return value


def get_char(prompt, default=None, values=None):
    """Get an integer value."""
    if default:
        prompt = f"{prompt} (Default {default.upper()}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
        if value:
            if not values or value.lower() in values:
                break
            _LOGGING.error("Acceptable values %s.", values)
        elif default is not None:
            value = default
            break
        else:
            response = "A response is required."
            if values:
                response = f"{response} Acceptable values {values}."
            _LOGGING.info(response)
    return value


def get_workdir():
    """Input the valeu for the workdir."""
    _LOGGING.info("The working directory stores the lsit of identified devices.")
    _LOGGING.info(
        "Enter a working directory where the saved file is (and will be saved to after loading.)"
    )
    workdir = input(f"Working directory (enter . for current director): ")
    if workdir == ".":
        return os.getcwd()
    return workdir


def get_addresses(address=None, allow_cancel=False, allow_all=True):
    """Get the address of a device or all devices."""
    prompt_addr = "Enter device address"
    prompt_cancel = "Enter device address or blank to cancel"
    prompt_all = "Enter device address or all for all devices"
    prompt_all_cancel = "Enter device address, all for all devices, or blank to cancel"

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
        if not address:
            address = input(prompt)
        if not address:
            if allow_cancel:
                return addresses
        elif str(address).strip("'\"").lower() == "all":
            for addr in devices:
                addresses.append(addr)
            return addresses
        elif devices[address]:
            addresses.append(address)
            return addresses
        else:
            _LOGGING.info("Device %s not found in device list.", address)
            return []


def print_aldb(device):
    """Print the All-Link Database to the log."""
    _LOGGING.info("")
    _LOGGING.info("RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3")
    _LOGGING.info("----- ------ ---- --- ----- -------- ------ ------ ------")
    for mem_addr in device.aldb:
        rec = device.aldb[mem_addr]
        in_use = "Y" if rec.is_in_use else "N"
        mode = "C" if rec.is_controller else "R"
        hwm = "Y" if rec.is_high_water_mark else "N"
        line = f" {rec.mem_addr:04x}    {in_use:s}     {mode:s}   {hwm:s}    {rec.group:3d} {rec.target}   {rec.data1:3d}   {rec.data2:3d}   {rec.data3:3d}"
        _LOGGING.info(line)
    _LOGGING.info("")


async def stdio(limit=_DEFAULT_LIMIT, loop=None):
    """Create async standard in/out handlers."""
    if loop is None:
        loop = asyncio.get_event_loop()

    if sys.platform == "win32":
        return _win32_stdio(loop)

    reader = asyncio.StreamReader(limit=limit, loop=loop)
    reader_protocol = asyncio.StreamReaderProtocol(reader, loop=loop)

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        lambda: asyncio.streams.FlowControlMixin(loop=loop), os.fdopen(1, "wb")
    )
    writer = asyncio.streams.StreamWriter(writer_transport, writer_protocol, None, loop)

    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)
    return reader, writer


def patch_stdin_stdout(stdin, stdout):
    """Patch sys.stdout.write to ensure proper encoding."""
    write_orig = stdout.write
    read_orig = stdin.readline

    async def decode_read():
        """Decode the input line."""
        line = await read_orig()
        return line.decode("UTF-8")

    def encode_write(line: str):
        """Encode line before passing to write method."""
        write_orig(line.encode("UTF-8"))

    stdin.readline = decode_read
    stdout.write = encode_write


def _win32_stdio(loop):
    # no support for asyncio stdio yet on Windows, see https://bugs.python.org/issue26832
    # use an executor to read from stdio and write to stdout
    # note: if nothing ever drains the writer explicitly, no flushing ever takes place!
    class Win32StdinReader:
        """Windows standard in Reader."""

        def __init__(self):
            """Init the Win32StdinReader class."""
            self.stdin = sys.stdin.buffer

        async def readline(self):
            """Read a line."""
            # a single call to sys.stdin.readline() is thread-safe
            return await loop.run_in_executor(None, sys.stdin.readline)

    class Win32StdoutWriter:
        """Windows standard out writer."""

        def __init__(self):
            """Init the Win32StdoutWriter class."""
            self.buffer = []
            self.stdout = sys.stdout.buffer

        def write(self, data):
            """Write to standard out."""
            self.buffer.append(data)

        async def drain(self):
            """Flush the output to standard out."""
            data, self.buffer = self.buffer, []
            # a single call to sys.stdout.writelines() is thread-safe
            return await loop.run_in_executor(None, sys.stdout.writelines, data)

    return Win32StdinReader(), Win32StdoutWriter()


def set_loop() -> None:
    """Attempt to use different loop."""
    from asyncio.events import BaseDefaultEventLoopPolicy

    if sys.platform == "win32":
        if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
            # pylint: disable=no-member
            policy = asyncio.WindowsProactorEventLoopPolicy()
        else:

            class ProactorPolicy(BaseDefaultEventLoopPolicy):
                """Event loop policy to create proactor loops."""

                _loop_factory = asyncio.ProactorEventLoop

            policy = ProactorPolicy()

        asyncio.set_event_loop_policy(policy)
