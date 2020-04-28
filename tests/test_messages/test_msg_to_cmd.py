"""Test the sending and receiving of messages using the MockPLM and receive topics."""
import json
import unittest
from asyncio import Queue, sleep
from binascii import unhexlify
from functools import partial

import aiofiles

from pyinsteon import pub
from pyinsteon.protocol.protocol import Protocol
from tests import async_connect_mock, set_log_levels
from tests.utils import DataItem, async_case, create_std_ext_msg, send_data

FILE = "msg_to_cmd.json"


async def import_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


def create_message(msg_dict):
    """Create a message from a dictionary."""
    address = msg_dict.get("address")
    flags = int.from_bytes(unhexlify(msg_dict.get("flags")), "big")
    cmd1 = int.from_bytes(unhexlify(msg_dict.get("cmd1")), "big")
    cmd2 = int.from_bytes(unhexlify(msg_dict.get("cmd2")), "big")
    if msg_dict.get("user_data") == "":
        user_data = None
    else:
        user_data = int.from_bytes(unhexlify(msg_dict.get("user_data")), "big")
    if msg_dict.get("ack") == "":
        ack = None
    else:
        ack = int.from_bytes(unhexlify(msg_dict.get("ack")), "big")
    if msg_dict.get("target") == "":
        target = None
    else:
        target = msg_dict.get("target")
    msg = create_std_ext_msg(
        address, flags, cmd1, cmd2, user_data=user_data, target=target, ack=ack
    )
    return DataItem(msg, 0.1)


class TestDirectMsgToTopic(unittest.TestCase):
    """Test direct messages mapped to topics."""

    def setUp(self):
        """Set up the tests."""
        self._topic = None

    def capture_topic(
        self, cmd1, cmd2, target, user_data, hops_left, topic=pub.AUTO_TOPIC
    ):
        """Save the last topic."""
        self._topic = topic
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    @async_case
    async def test_message_to_topic(self):
        """Test converting a message to a topic."""
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
        await sleep(0.01)

        for test_info in tests:
            self._topic = None
            curr_test = tests[test_info]

            msgs = [create_message(curr_test)]
            pub.subscribe(self.capture_topic, curr_test.get("topic"))
            send_data(msgs, read_queue)
            await sleep(0.13)
            try:
                assert self._topic.name == curr_test.get("topic")
            except AssertionError:
                raise AssertionError(
                    "Failed test {} with message topic {} and test topic {}".format(
                        test_info, self._topic.name, curr_test.get("topic")
                    )
                )
            finally:
                pub.subscribe(self.capture_topic, curr_test.get("topic"))
