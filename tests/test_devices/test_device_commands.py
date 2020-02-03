"""Test device commands outbound."""
import json
import unittest
from asyncio import Queue, sleep
from binascii import unhexlify
from functools import partial
from random import randint

from aiofile import AIOFile

from pyinsteon.address import Address
import pyinsteon.device_types as device_types
from pyinsteon.protocol.protocol import Protocol

from tests import async_connect_mock, set_log_levels, _LOGGER
from tests.utils import async_case, TopicItem, send_topics


FILE = "device_commands.json"


def convert_to_int(str_value):
    """Convert a string hex value to int."""
    return int.from_bytes(unhexlify(str_value), byteorder="big")


def random_address():
    """Generate a random address."""
    address = ""
    for _ in range(0, 3):
        rand_int = randint(1, 255)
        if address:
            address = f"{address}."
        address = f"{address}{rand_int:02x}"
    return Address(address)


def convert_response(response, address):
    """Convert a response dict to a topic."""
    topic = str(response["topic"])
    topic = topic.replace("<address>", repr(address))
    cmd1 = convert_to_int(response["cmd1"])
    cmd2 = convert_to_int(response["cmd2"])
    target = Address(response["target"])
    kwargs = {"cmd1": cmd1, "cmd2": cmd2, "target": target, "user_data": None}
    topic_item = TopicItem(topic, kwargs, 2)
    return topic_item


async def import_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with AIOFile(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


class TestDeviceCommands(unittest.TestCase):
    """Test device commands outbound."""

    def setUp(self):
        """Set up the test."""
        self._topic = None
        self._last_value = None
        set_log_levels("info", "info", "info", True)

    @async_case
    async def test_device_commands(self):
        """Test sending a command from a device."""
        read_queue = Queue()
        write_queue = Queue()
        connect_method = partial(
            async_connect_mock,
            read_queue=read_queue,
            write_queue=write_queue,
            random_nak=False,
        )
        protocol = Protocol(connect_method=connect_method)

        tests = await import_commands()
        await protocol.async_connect()
        await sleep(0.1)

        for device_type in tests:  # ["SwitchedLightingControl_DinRail"]:
            test_configs = tests[device_type]
            for command in test_configs:
                await self._execute_command(device_type, command, test_configs[command])

    async def _execute_command(self, device_type, command, config):
        address = random_address()
        params = config["params"]
        for param in params:
            params[param] = convert_to_int(params[param])
        topic_item = convert_response(config["response"], address)

        device_class = getattr(device_types, device_type)

        try:
            device = device_class(
                address=address, cat=0x01, subcat=0x02, description=device_type
            )
            method = getattr(device, command)
            send_topics([topic_item])
            result = await method(**params)
            assert int(result) == 1
        # pylint: disable=broad-except
        except Exception as ex:
            print("Something failed")
            _LOGGER.error("Failed: device: %s  command: %s", device_type, command)
            _LOGGER.error(ex)
            assert False


if __name__ == "__main__":
    unittest.main()
