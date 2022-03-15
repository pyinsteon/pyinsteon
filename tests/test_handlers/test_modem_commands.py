"""Test the sending and receiving of direct commands using the MockPLM."""
import json
import unittest
from asyncio import sleep
from binascii import unhexlify

import aiofiles

import pyinsteon.handlers as commands
from pyinsteon import pub
from pyinsteon.address import Address

# pylint: disable=unused-import
# flake8: noqa: F401
from pyinsteon.handlers.cancel_all_linking import CancelAllLinkingCommandHandler
from pyinsteon.handlers.get_first_all_link_record import GetFirstAllLinkRecordHandler
from pyinsteon.handlers.get_im_configuration import GetImConfigurationHandler
from pyinsteon.handlers.get_im_info import GetImInfoHandler
from pyinsteon.handlers.get_next_all_link_record import GetNextAllLinkRecordHandler
from pyinsteon.handlers.manage_all_link_record import ManageAllLinkRecordCommand
from pyinsteon.handlers.read_eeprom import ReadEepromHandler
from pyinsteon.handlers.send_all_link import SendAllLinkCommandHandler
from pyinsteon.handlers.send_all_link_off import SendAllLinkOffCommandHandler
from pyinsteon.handlers.send_all_link_on import SendAllLinkOnCommandHandler
from pyinsteon.handlers.set_im_configuration import SetImConfigurationHandler
from pyinsteon.handlers.start_all_linking import StartAllLinkingCommandHandler
from pyinsteon.handlers.write_eeprom import WriteEepromHandler

# pylint: enable=unused-import
from tests import set_log_levels
from tests.utils import (
    DataItem,
    async_case,
    async_protocol_manager,
    create_std_ext_msg,
    get_class_or_method,
    random_address,
    send_data,
)

FILE = "modem_commands.json"


async def import_modem_commands():
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


def create_message(msg_dict, delay=0.1):
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
        """Set up the tests."""
        self._assert_tests = []
        self._current_test = None
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
                    if assert_test == "address":
                        self._assert_tests[assert_test] = Address(
                            self._assert_tests[assert_test]
                        )
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
    async def test_modem_command(self):
        """Test direct command."""
        async with async_protocol_manager(auto_ack=False) as protocol:

            tests = await import_modem_commands()
            pub.subscribe(self.validate_values, pub.ALL_TOPICS)

            for test_info in tests:
                self._current_test = test_info
                test_command = tests[test_info]
                command = test_command.get("command")
                cmd_class = command.get("class")
                params = command.get("params")
                if command.get("ack_response"):
                    ack_nak_response = command["ack_response"]["data"]
                    ack_nak_data = unhexlify(f"02{ack_nak_response}06")
                else:
                    ack_nak_response = command["nak_response"]["data"]
                    ack_nak_data = unhexlify(f"02{ack_nak_response}15")
                send_params = command.get("send_params")
                test_response = test_command.get("response")
                self._assert_tests = test_command.get("assert_tests")
                obj = get_class_or_method(commands, cmd_class)
                cmd = obj(**params)
                ack_nak_response_item = DataItem(ack_nak_data, 0.1)
                send_data([ack_nak_response_item], protocol.read_queue)
                try:
                    response = await cmd.async_send(**send_params)
                except Exception as ex:
                    raise Exception(
                        "Failed test {} with error: {}".format(
                            self._current_test, str(ex)
                        )
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


if __name__ == "__main__":
    unittest.main()
