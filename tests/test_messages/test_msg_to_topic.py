"""Test converting a message to a topic."""

import json
from unittest import TestCase

import aiofiles

from pyinsteon.protocol.msg_to_topic import convert_to_topic
from tests import set_log_levels
from tests.utils import async_case, hex_to_inbound_message

FILE = "msg_to_topic.json"


async def import_commands(file_name):
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, file_name)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


class TestMsgToTopic(TestCase):
    """Test messages mapped to topics."""

    def setUp(self):
        """Set up the tests."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="debug",
            logger_messages="debug",
            logger_topics=True,
        )

    @async_case
    async def test_message_to_topic(self):
        """Test converting a message to a topic."""

        tests = await import_commands(FILE)

        for test_info in tests:
            self._topic = None
            msg_hex = tests[test_info]["message"]
            expected_topic = tests[test_info]["topic"]
            msg, _ = hex_to_inbound_message(msg_hex)
            topics = []
            for topic, _ in convert_to_topic(msg):
                topics.extend((topic.split(".")))
            try:
                assert expected_topic in topics
            except AssertionError:
                raise AssertionError(
                    f"Error in test {test_info}: Received {topic}  Expected: {expected_topic}"
                )
