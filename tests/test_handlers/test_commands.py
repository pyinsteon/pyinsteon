"""Test the sending and receiving of direct commands using the MockPLM."""
from asyncio import Queue, sleep
import unittest
from functools import partial
import json
from aiofile import AIOFile

import pyinsteon.handlers.to_device as commands
from pyinsteon import pub
from pyinsteon.protocol.protocol import Protocol

# pylint: disable=unused-import
from pyinsteon.handlers.to_device.enter_linking_mode import EnterLinkingModeCommand
from pyinsteon.handlers.to_device.enter_unlinking_mode import EnterUnlinkingModeCommand
from pyinsteon.handlers.to_device.extended_get import ExtendedGetCommand
from pyinsteon.handlers.to_device.extended_set import ExtendedSetCommand
from pyinsteon.handlers.to_device.get_operating_flags import GetOperatingFlagsCommand
from pyinsteon.handlers.to_device.id_request import IdRequestCommand
from pyinsteon.handlers.to_device.off_all_link_broadcast import (
    OffAllLinkBroadcastCommand,
)
from pyinsteon.handlers.to_device.off_all_link_cleanup import OffAllLinkCleanupCommand
from pyinsteon.handlers.to_device.off_fast import OffFastCommand
from pyinsteon.handlers.to_device.off import OffCommand
from pyinsteon.handlers.to_device.on_fast import OnFastCommand
from pyinsteon.handlers.to_device.on_level_all_link_broadcast import (
    OnLevelAllLinkBroadcastCommand,
)
from pyinsteon.handlers.to_device.on_level_all_link_cleanup import (
    OnLevelAllLinkCleanupCommand,
)
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from pyinsteon.handlers.to_device.product_data_request import ProductDataRequestCommand
from pyinsteon.handlers.to_device.read_aldb import ReadALDBCommandHandler
from pyinsteon.handlers.to_device.set_operating_flags import SetOperatingFlagsCommand
from pyinsteon.handlers.to_device.status_request import StatusRequestCommand
from pyinsteon.handlers.to_device.write_aldb import WriteALDBCommandHandler

# pylint: enable=unused-import
from tests import async_connect_mock, set_log_levels
from tests.utils import (
    create_std_ext_msg,
    async_case,
    send_data,
    DataItem,
    get_class_or_method,
)


FILE = "commands.json"


async def import_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with AIOFile(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


def create_message(msg_dict, delay=.1):
    """Create a message from a dictionary."""
    address = msg_dict.get("address")
    flags = msg_dict.get("flags")
    cmd1 = msg_dict.get("cmd1")
    cmd2 = msg_dict.get("cmd2")
    user_data = msg_dict.get("user_data")
    ack = msg_dict.get("ack")
    target = msg_dict.get("target")
    msg = create_std_ext_msg(
        address, flags, cmd1, cmd2, user_data=user_data, target=target, ack=ack
    )
    return DataItem(msg, delay)


class TestDirectCommands(unittest.TestCase):
    """Test a set of handlers that handle direct commands."""

    def setUp(self):
        """Setup the tests."""
        self._assert_tests = []
        self._read_queue = Queue()
        self._write_queue = Queue()
        self._current_test = None
        self._connect_method = partial(
            async_connect_mock,
            read_queue=self._read_queue,
            write_queue=self._write_queue,
            random_nak=False,
        )
        self._protocol = Protocol(connect_method=self._connect_method)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def validate_values(self, topic=pub.ALL_TOPICS, **kwargs):
        """Validate what should be returned from the handler."""
        for assert_test in self._assert_tests:
            if kwargs.get(assert_test) is not None:
                try:
                    assert kwargs.get(assert_test) == self._assert_tests[assert_test]
                except AssertionError:
                    raise AssertionError(
                        "Failed test '{}' with argument '{}' value {} vs expected value {}".format(
                            self._current_test,
                            assert_test,
                            kwargs.get(assert_test),
                            self._assert_tests[assert_test],
                        )
                    )

    @async_case
    async def test_command(self):
        """Test direct command."""
        msgs = []
        def listen_for_ack():
            send_data(msgs, self._read_queue)

        tests = await import_commands()
        pub.subscribe(self.validate_values, pub.ALL_TOPICS)
        pub.subscribe(listen_for_ack, 'ack')
        await self._protocol.async_connect()

        for test_info in tests:
            self._current_test = test_info
            test_command = tests[test_info]
            command = test_command.get("command")
            cmd_class = command.get("class")
            params = command.get("params")
            send_params = command.get("send_params")
            test_response = test_command.get("response")
            obj = get_class_or_method(commands, cmd_class)
            cmd = obj(**params)

            messages = test_command.get("messages")
            msgs = []
            for message in messages:
                msg_dict = messages[message]
                msgs.append(create_message(msg_dict))
            self._assert_tests = test_command.get("assert_tests")

            # send_data(msgs, self._read_queue)
            try:
                response = await cmd.async_send(**send_params)
            except Exception as e:
                raise Exception(
                    "Failed test {} with error: {}".format(self._current_test, str(e))
                )
            if test_response:
                try:
                    assert int(response) == test_response
                except AssertionError:
                    raise AssertionError(
                        "Failed test: {} command response: {}".format(
                            self._current_test, response
                        )
                    )
            await sleep(0.1)
        pub.unsubscribe(self.validate_values, pub.ALL_TOPICS)
        self._protocol.close()
        await sleep(0.1)


if __name__ == "__main__":
    unittest.main()