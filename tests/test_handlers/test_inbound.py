"""Test the sending and receiving of direct commands using the MockPLM."""
import json
import unittest
from asyncio import sleep
from binascii import unhexlify

import aiofiles

import pyinsteon.handlers.from_device as commands
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
from pyinsteon.utils import subscribe_topic

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

FILE = "from_device.json"


async def import_commands():
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
    for k in ["flags", "cmd1", "cmd2"]:
        if str(msg_dict.get(k)).startswith("0x"):
            msg_dict[k] = int.from_bytes(unhexlify(msg_dict[k][2:]), "big")
    for k in msg_dict["user_data"]:
        if str(msg_dict["user_data"][k]).startswith("0x"):
            msg_dict["user_data"][k] = int.from_bytes(
                unhexlify(msg_dict["user_data"][k][2:]), "big"
            )
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


class TestInbound(unittest.TestCase):
    """Test a set of handlers that handle direct commands."""

    def setUp(self):
        """Set up the tests."""
        self._assert_tests = []
        self._current_test = None
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        self._assert_result = True
        self._call_count = 0

    async def async_validate_values(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Validate what should be returned from the handler."""
        if not topic.name.startswith("handler"):
            return
        self._call_count += 1
        for test in self._assert_tests:
            if kwargs.get(test) is None:
                continue
            try:
                if test == "address" or test == "target":
                    self._assert_tests[test] = Address(self._assert_tests[test])
                elif str(self._assert_tests[test]).startswith("0x"):
                    self._assert_tests[test] = int.from_bytes(
                        unhexlify(self._assert_tests[test]), "big"
                    )
                if type(self._assert_tests[test]) == "float":
                    self._assert_tests[test] = round(self._assert_tests[test], 1)
                if test == "data":
                    for k, v in self._assert_tests[test].items():
                        assert kwargs[test][k] == v
                else:
                    assert kwargs.get(test) == self._assert_tests[test]
            except (AssertionError, KeyError):
                self._assert_result = False
                raise AssertionError(
                    "Failed test '{}' with argument '{}' value {} vs expected value {}".format(
                        self._current_test,
                        test,
                        kwargs.get(test),
                        self._assert_tests[test],
                    )
                )

    @async_case
    async def test_inbound(self):
        """Test direct command."""

        async with async_protocol_manager(auto_ack=False) as protocol:

            tests = await import_commands()
            subscribe_topic(self.async_validate_values, pub.ALL_TOPICS)

            for test_info in tests:
                self._current_test = test_info
                test_command = tests[test_info]
                cmd_class = test_command.get("command")
                params = test_command.get("params")
                inbound_message = test_command.get("message")
                if params.get("address") == "":
                    params["address"] = random_address()
                inbound_message["address"] = params["address"]
                self._assert_tests = test_command.get("assert_tests")
                obj = get_class_or_method(commands, cmd_class)
                cmd = obj(**params)
                inbound_data_item = create_message(inbound_message, 0)
                self._call_count = 0
                send_data([inbound_data_item], protocol.read_queue)
                await sleep(0.1)
                assert self._call_count == 1
                assert self._assert_result


if __name__ == "__main__":
    unittest.main()
