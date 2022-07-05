"""Test device commands outbound."""
import json
import unittest
from asyncio import sleep
from binascii import unhexlify

import aiofiles

import pyinsteon
import pyinsteon.device_types as device_types
from pyinsteon.address import Address
from pyinsteon.data_types.user_data import create_from_dict
from tests import _LOGGER, set_log_levels
from tests.utils import (
    TopicItem,
    async_case,
    async_protocol_manager,
    random_address,
    send_topics,
)

FILE = "device_commands.json"


def convert_to_int(value):
    """Convert a string hex value to int."""
    if isinstance(value, int):
        return value
    return int.from_bytes(unhexlify(value), byteorder="big")


def convert_response(response, address):
    """Convert a response dict to a topic."""
    topic = str(response["topic"])
    topic = topic.replace("<address>", repr(address))
    cmd1 = convert_to_int(response["cmd1"])
    cmd2 = convert_to_int(response["cmd2"])
    target = Address(response["target"])
    userdata = response["userdata"]
    if userdata:
        userdata_dict = {k: convert_to_int(v) for k, v in userdata.items()}
        userdata = create_from_dict(userdata_dict)

    kwargs = {
        "cmd1": cmd1,
        "cmd2": cmd2,
        "target": target,
        "user_data": userdata,
        "hops_left": 3,
    }
    topic_item = TopicItem(topic, kwargs, 0.02)
    return topic_item


async def import_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


def test_results(device, results):
    """Test the results of a command."""
    for result in results:
        group = result.get("group")
        if group:
            value = convert_to_int(result.get("value"))
            assert device.groups[group].value == value
        property = result.get("property")
        if property:
            value = convert_to_int(property.get("value"))
            name = property.get("name")
            assert device.properties[name].value == value
        config = result.get("config")
        if config:
            value = convert_to_int(config.get("value"))
            name = config.get("name")
            assert device.configuration[name].value == value
        op_flag = result.get("op_flag")
        if op_flag:
            value = convert_to_int(op_flag.get("value"))
            name = op_flag.get("name")
            assert device.operating_flags[name].value == value


class TestDeviceCommands(unittest.TestCase):
    """Test device commands outbound."""

    def setUp(self):
        """Set up the test."""
        self._topic = None
        self._last_value = None
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def tearDown(self):
        """Tear down the test."""
        pyinsteon.pub.unsubAll("send")

    @async_case
    async def test_device_commands(self):
        """Test sending a command from a device."""
        async with async_protocol_manager():
            tests = await import_commands()
            await sleep(0.1)

            for device_type in tests:  # ["SwitchedLightingControl_DinRail"]:
                test_configs = tests[device_type]
                for command in test_configs:
                    await self._execute_command(
                        device_type, command, test_configs[command]
                    )

    async def _execute_command(self, device_type, command, config):
        address = random_address()
        params = config["params"]
        for param in params:
            if isinstance(params[param], int):
                continue
            params[param] = convert_to_int(params[param])
        topic_items = []
        for response in config.get("response", []):
            topic_items.append(convert_response(response, address))

        device_class = getattr(device_types, device_type)

        try:
            device = device_class(
                address=address, cat=0x01, subcat=0x02, description=device_type
            )
            method = getattr(device, command)
            for topic_item in topic_items:
                send_topics([topic_item])
            result = await method(**params)
            assert int(result) == 1
            test_results(device, config.get("result"))

        # pylint: disable=broad-except
        except Exception as ex:
            _LOGGER.error("Failed: device: %s  command: %s", device_type, command)
            _LOGGER.error(ex)
            assert False

    @async_case
    async def test_x10_commands(self):
        """Test X10 commands."""
        async with async_protocol_manager():
            x10_types = ["X10OnOff", "X10Dimmable"]
            for device_type in x10_types:
                device_class = getattr(device_types, device_type)
                device = device_class("A", 3)
                result = await device.async_on()
                assert int(result) == 1
                assert device.groups[1].value == 255
                result = await device.async_off()
                assert int(result) == 1
                assert device.groups[1].value == 0


if __name__ == "__main__":
    unittest.main()
