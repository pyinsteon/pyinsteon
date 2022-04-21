"""Test outbound SD and ED messages."""
import asyncio
import json
from binascii import hexlify, unhexlify
from unittest import TestCase

import aiofiles

from pyinsteon.protocol.command_to_msg import register_command_handlers
from pyinsteon.protocol.messages.outbound import (
    outbound_write_manager,
    register_outbound_handlers,
)
from pyinsteon.utils import publish_topic

from ... import set_log_levels
from ...utils import async_case, random_address

FILE = "outbound_commands.json"


async def import_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


class TestOuboundCommands(TestCase):
    """Test outbound SD and ED messages."""

    def setUp(self) -> None:
        """Set up the test."""
        self.msg = None
        self.call_count = 0
        register_outbound_handlers()
        register_command_handlers()
        outbound_write_manager.protocol_write = self.receive_message
        set_log_levels(logger_topics=True)

    def receive_message(self, msg, priority):
        """Receive the outbound message."""
        self.msg = msg
        self.call_count += 1

    @async_case
    async def test_oubound_commands(self):
        """Test outbound SD and ED messages."""
        register_outbound_handlers()
        test_cases = await import_commands()

        for test_case in test_cases:
            address = random_address()
            self.call_count = 0
            self.msg = None
            main_topic = test_cases[test_case]["topic"]
            topic = f"send.{main_topic}.direct"
            args = test_cases[test_case]["args"]
            for k, v in args.items():
                if str(v).startswith("0x"):
                    v = int.from_bytes(unhexlify(v[2:]), "big")
                    args[k] = v
            args["address"] = address
            result = str(test_cases[test_case]["result"])
            result = result.replace("aaaaaa", address.id)
            publish_topic(topic, **args)
            await asyncio.sleep(0.1)
            assert self.msg is not None
            msg_str = str(hexlify(bytes(self.msg)))[2:-1]
            test_msg = msg_str[: len(result)]
            try:
                assert test_msg.lower() == result.lower()
            except AssertionError:
                raise AssertionError(
                    f"Error in {test_case}: Result: {msg_str.lower()} ({test_msg.lower()})  Expected: {result.lower()}"
                )
