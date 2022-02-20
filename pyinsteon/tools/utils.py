"""Utilities for the tools commands."""
import asyncio
import os
import sys
from asyncio.events import BaseDefaultEventLoopPolicy

_DEFAULT_LIMIT = 2**16  # 64kb


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

        # pylint: disable=no-self-use
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
