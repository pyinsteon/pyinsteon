"""Test the sending and receiving of direct commands using the MockPLM."""

from asyncio import sleep
import json
from os import path
import unittest

import aiofiles
from pubsub import pub

from pyinsteon.constants import ResponseStatus
import pyinsteon.handlers as commands

# pylint: disable=unused-import
# flake8: noqa: F401
from pyinsteon.handlers.all_link_cleanup_status_report import AllLinkCleanupStatusReport
from pyinsteon.handlers.cancel_all_linking import CancelAllLinkingCommandHandler
from pyinsteon.handlers.get_first_all_link_record import GetFirstAllLinkRecordHandler
from pyinsteon.handlers.get_im_configuration import GetImConfigurationHandler
from pyinsteon.handlers.get_im_info import GetImInfoHandler
from pyinsteon.handlers.get_next_all_link_record import GetNextAllLinkRecordHandler
from pyinsteon.handlers.read_eeprom import ReadEepromHandler
from pyinsteon.handlers.send_all_link import SendAllLinkCommandHandler
from pyinsteon.handlers.set_im_configuration import SetImConfigurationHandler
from pyinsteon.handlers.start_all_linking import StartAllLinkingCommandHandler

# pylint: disable=unused-import
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from pyinsteon.handlers.to_device.x10_send import X10CommandSend
from pyinsteon.handlers.write_eeprom import WriteEepromHandler

# pylint: enable=unused-import
from pyinsteon.utils import subscribe_topic
from pyinsteon.x10_address import create as create_x10_address

from tests import _LOGGER, set_log_levels
from tests.utils import (
    async_case,
    async_protocol_manager,
    get_class_or_method,
    random_address,
)

FILE = "nak_responses.json"


async def import_commands():
    """Import and parse the commands to test."""

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, FILE)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


class TestNakResponses(unittest.TestCase):
    """Test a set of handlers for NAK responses."""

    def setUp(self):
        """Set up the tests."""
        self._assert_tests = []
        self._assert_result = True
        self._current_test = None
        self._call_count = 0
        self._nak_count = 0
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="debug",
            logger_topics=True,
        )

    async def validate_values(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Validate what should be returned from the handler."""
        if not topic.name.startswith("handler"):
            return
        self._call_count += 1
        self._assert_result = not self._assert_tests
        for assert_test in self._assert_tests:
            try:
                assert_test_received = kwargs.get(assert_test)
                assert_test_expected = self._assert_tests[assert_test]
                if isinstance(assert_test_received, bytearray):
                    assert_test_expected = bytearray(assert_test_expected)
                assert assert_test_received == assert_test_expected
                self._assert_result = True
            except AssertionError as ex:
                self._assert_result = False
                raise AssertionError(
                    "Failed test '{}' with argument '{}' value {} vs expected value {}".format(
                        self._current_test,
                        assert_test,
                        kwargs.get(assert_test),
                        self._assert_tests[assert_test],
                    )
                ) from ex

    @async_case
    async def test_nak_response(self):
        """Test NAK command response."""

        async with async_protocol_manager(always_nak=True):
            self._nak_count = 0

            def listen_for_nak(topic=pub.AUTO_TOPIC):
                if self._current_test in str(topic):
                    print(topic)
                    self._nak_count += 1

            tests = await import_commands()
            subscribe_topic(self.validate_values, pub.ALL_TOPICS)
            subscribe_topic(listen_for_nak, "nak")

            for test_info in tests:
                self._nak_count = 0

                self._current_test = test_info
                _LOGGER.info("Starting test: %s", test_info)
                test_command = tests[test_info]
                command = test_command["command"]
                cmd_class = command["class"]
                params = command["params"]
                if params.get("address"):
                    params["address"] = random_address()
                if params.get("housecode"):
                    params["address"] = create_x10_address(
                        params["housecode"], params["unitcode"]
                    )
                    params.pop("housecode")
                    params.pop("unitcode")
                send_params = command.get("send_params")
                if send_params.get("target"):
                    send_params["target"] = random_address()
                nak_count = test_command["nak_count"]
                obj = get_class_or_method(commands, cmd_class)
                cmd = obj(**params)

                self._assert_tests = test_command.get("response")
                self._call_count = 0
                try:
                    response = await cmd.async_send(**send_params)
                except Exception as ex:
                    raise Exception(
                        "Failed test {} with error: {}".format(
                            self._current_test, str(ex)
                        )
                    ) from ex
                await sleep(0.1)
                try:
                    assert response == ResponseStatus.FAILURE
                    assert self._nak_count == nak_count
                    if self._assert_tests:
                        call_count = test_command.get("call_count", 1)
                        assert self._call_count == call_count
                except AssertionError as ex:
                    raise AssertionError(
                        "Failed test: {} command response: {}  call count {}  nak count {}".format(
                            self._current_test,
                            response,
                            self._call_count,
                            self._nak_count,
                        )
                    ) from ex
                await sleep(0.5)
                assert self._assert_result
                _LOGGER.info("Completed test: %s", test_info)
                _LOGGER.info("")
