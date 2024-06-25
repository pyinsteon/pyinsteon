"""Test device status commands."""

from asyncio import sleep
from binascii import unhexlify
import json
from os import path
from random import randint
from typing import Union
import unittest

import aiofiles

import pyinsteon
from pyinsteon.data_types.user_data import create_from_dict
import pyinsteon.device_types.ipdb as device_types

from tests import _LOGGER, set_log_levels
from tests.utils import (
    TopicItem,
    async_case,
    async_protocol_manager,
    random_address,
    send_topics,
)

FILE = "status_commands.json"


def convert_to_int(value: Union[str, int]) -> tuple[int, Union[str, None]]:
    """Convert a string hex value to int."""
    if isinstance(value, int):
        return value, None

    if len(value) == 2:
        return int.from_bytes(unhexlify(value), byteorder="big"), None

    return randint(1, 255), value


def convert_topic_data(
    topic: str, response_data: dict, response_values: dict, delay: float
) -> tuple[TopicItem, dict[str, int]]:
    """Convert a topic data dict to a TopicItem."""
    response_data_out = response_data.copy()
    for param, value in response_data_out.items():
        if isinstance(value, int):
            continue

        if param == "target":
            if target := response_values.get("target"):
                response_data_out["target"] = target
            else:
                response_values["target"] = response_data_out[
                    "target"
                ] = random_address()
            continue

        if param == "user_data":
            if value:
                userdata_dict = {}
                for ud_key, ud_value in value.items():
                    if existing_value := response_values.get(ud_key):
                        userdata_dict[ud_key] = existing_value
                    else:
                        new_value, value_name = convert_to_int(ud_value)
                        userdata_dict[ud_key] = new_value
                        if value_name:
                            response_values[value_name] = new_value
                response_data_out["user_data"] = create_from_dict(userdata_dict)
            continue

        new_value, value_name = convert_to_int(value)
        response_data_out[param] = new_value
        if value_name:
            response_values[value_name] = new_value

    return TopicItem(topic, response_data_out, delay), response_values


async def import_commands():
    """Import and parse the commands to test."""

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


def _test_results(device, results, results_values):
    """Test the results of a command."""
    for result in results:
        group = result["group"]
        value = result["value"]
        if not isinstance(value, int):
            value = results_values[value]
        if device.groups[group].is_dimmable:
            assert device.groups[group].value == value
        elif device.groups[group].is_reversed:
            assert bool(device.groups[group].value) != bool(value)
        else:
            assert bool(device.groups[group].value) == bool(value)


class TestDeviceStatusCommands(unittest.TestCase):
    """Test device status commands outbound."""

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
    async def test_device_status_commands(self):
        """Test sending a command from a device."""
        async with async_protocol_manager():
            tests: dict[str, dict] = await import_commands()
            await sleep(0.1)

            for test_name, test in tests.items():
                if test_name.startswith("skip"):
                    continue
                for device_type in test["device_types"]:
                    groups = test["groups"]
                    response_topics = test["response_topics"]
                    results = test["results"]
                    for group in groups:
                        _LOGGER.info(
                            "Running: test_name: %s   device: %s   group: %s",
                            test_name,
                            device_type,
                            str(group),
                        )
                        await self._execute_command(
                            test_name,
                            device_type,
                            group,
                            response_topics,
                            results,
                        )

    async def _execute_command(
        self,
        test_name: str,
        device_type: str,
        group: int,
        response_topics_data: list[dict],
        results: dict,
    ):
        address = random_address()
        results_values = {"target": random_address()}
        topic_items = []
        for response_topic_data in response_topics_data:
            cmd1 = response_topic_data["cmd1"]
            resp_type = response_topic_data["type"]
            topic_data = {
                key: value
                for key, value in response_topic_data.items()
                if key != "type"
            }
            if cmd1 == "2e" and resp_type == "direct_ack":
                direct_ack_topic = f"{address.id}.extended_get_set.{resp_type}"
            elif cmd1 == "2e" and resp_type == "direct":
                direct_ack_topic = f"{address.id}.extended_get_response.{resp_type}"
            else:
                direct_ack_topic = f"{address.id}.some_topic.{resp_type}"
            direct_ack_topic_item, results_values = convert_topic_data(
                direct_ack_topic, topic_data, results_values, 0.1
            )
            topic_items.append(direct_ack_topic_item)

        device_class = getattr(device_types, device_type)

        try:
            device = device_class(
                address=address, cat=0x01, subcat=0x02, description=device_type
            )
            send_topics(topic_items)
            result = await device.async_status(group=group)
            assert int(result) == 1
            _test_results(device, results, results_values)

        # pylint: disable=broad-except
        except Exception as ex:
            _LOGGER.error(
                "Failed: test_name: %s   device: %s   group: %s",
                test_name,
                device_type,
                str(group),
            )
            _LOGGER.error(ex)
            assert False
