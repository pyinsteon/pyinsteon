"""Test the sending and receiving of direct commands using the MockPLM."""

from asyncio import sleep
from binascii import unhexlify
import json
from os import path
import unittest

import aiofiles

from pyinsteon import pub
from pyinsteon.address import Address
import pyinsteon.handlers as commands

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
from tests import _LOGGER, set_log_levels
from tests.utils import (
    DataItem,
    async_case,
    async_protocol_manager,
    create_std_ext_msg,
    get_class_or_method,
    send_data,
)

FILE = "modem_inbound.json"


async def import_modem_commands():
    """Import and parse the commands to test."""
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


class TestModemInbound(unittest.TestCase):
    """Test a set of handlers that handle direct commands."""

    def setUp(self):
        """Set up the tests."""
        self._assert_tests = []
        self._current_test = None
        self._test_result = True
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="debug",
            logger_topics=True,
        )

    def validate_values(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Validate what should be returned from the handler."""
        if str(topic).startswith("handler"):
            return
        for assert_test in self._assert_tests:
            if kwargs.get(assert_test) is not None:
                try:
                    self._test_result = True
                    if assert_test == "address" or assert_test == "target":
                        self._assert_tests[assert_test] = Address(
                            self._assert_tests[assert_test]
                        )
                    if isinstance(self._assert_tests[assert_test], int):
                        kwargs_assert_test = int(kwargs.get(assert_test))
                    else:
                        kwargs_assert_test = kwargs.get(assert_test)
                    assert kwargs_assert_test == self._assert_tests[assert_test]
                except (AssertionError, TypeError) as ex:
                    self._test_result = False
                    raise AssertionError(
                        "Failed test '{}' with argument '{}' value {} vs expected value {}".format(
                            self._current_test,
                            assert_test,
                            kwargs.get(assert_test),
                            self._assert_tests[assert_test],
                        )
                    ) from ex

    @async_case
    async def test_modem_inbound(self):
        """Test direct command."""
        async with async_protocol_manager(auto_ack=False) as protocol:
            tests = await import_modem_commands()

            for test_info in tests:
                self._current_test = test_info
                _LOGGER.info("Starting Test: %s", test_info)
                test_command = tests[test_info]
                command = test_command.get("command")
                cmd_class = command.get("class")
                inbound_message = command.get("inbound_message")["data"]
                self._assert_tests = test_command.get("assert_tests")
                obj = get_class_or_method(commands, cmd_class)
                cmd = obj()
                inbound_data = unhexlify(f"02{inbound_message}")
                ack_response_item = DataItem(inbound_data, 0)
                pub.subscribe(self.validate_values, f"handler.{test_info}")
                send_data([ack_response_item], protocol.read_queue)
                await sleep(0.2)
                assert self._test_result
                _LOGGER.info("Completed Test: %s", test_info)
                pub.unsubscribe(self.validate_values, f"handler.{test_info}")
                _LOGGER.info("")


if __name__ == "__main__":
    unittest.main()
