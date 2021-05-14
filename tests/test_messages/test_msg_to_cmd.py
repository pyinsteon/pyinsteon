"""Test the sending and receiving of messages using the MockPLM and receive topics."""
import asyncio
import json
import unittest
from binascii import unhexlify

import aiofiles

from pyinsteon import pub
from tests import set_log_levels
from tests.utils import (
    DataItem,
    async_case,
    async_protocol_manager,
    create_std_ext_msg,
    random_address,
    send_data,
)

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
    return DataItem(msg, 0.02)


class TestDirectMsgToTopic(unittest.TestCase):
    """Test direct messages mapped to topics."""

    def setUp(self):
        """Set up the tests."""
        self._test_lock = asyncio.Lock()
        self._topic = None
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="debug",
            logger_topics=True,
        )

    def tearDown(self):
        """Tear down the test."""
        pub.unsubAll("send")
        pub.unsubAll("send_message")

    def capture_topic(
        self, cmd1, cmd2, target, user_data, hops_left, topic=pub.AUTO_TOPIC
    ):
        """Save the last topic."""
        self._topic = topic
        if self._test_lock.locked():
            self._test_lock.release()

    @async_case
    async def test_message_to_topic(self):
        """Test converting a message to a topic."""

        async with async_protocol_manager() as protocol:
            tests = await import_commands()

            for test_info in tests:
                self._topic = None
                address = repr(random_address())
                curr_test = tests[test_info]
                if curr_test.get("address"):
                    curr_test["address"] = address
                msgs = [create_message(curr_test)]
                curr_topic = curr_test["topic"].format(address)
                pub.subscribe(self.capture_topic, curr_topic)
                send_data(msgs, protocol.read_queue)
                await self._test_lock.acquire()
                try:
                    await asyncio.wait_for(self._test_lock.acquire(), 2)
                    assert self._topic.name == curr_topic

                except asyncio.TimeoutError:
                    raise AssertionError(
                        "Failed timed out {} with test topic {}".format(
                            test_info, curr_test.get("topic")
                        )
                    )
                except (AssertionError, AttributeError):
                    raise AssertionError(
                        "Failed test {} with test topic {}".format(
                            test_info, curr_test.get("topic")
                        )
                    )
                finally:
                    pub.unsubscribe(self.capture_topic, curr_topic)
                    if self._test_lock.locked():
                        self._test_lock.release()
