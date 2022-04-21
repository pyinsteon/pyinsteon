"""Test the tools base class."""
import asyncio
import os
import sys
from unittest.mock import patch

import pyinsteon
from pyinsteon.address import Address
from pyinsteon.constants import RelayMode, ThermostatMode, ToggleMode
from pyinsteon.tools.tools_base import ToolsBase
from tests.utils import async_case, random_address

from .tools_utils import (
    MockDevices,
    ToolsTestBase,
    clean_buffer,
    get_bad_address,
    get_curr_dir,
    get_good_address,
)


async def async_run_tests(async_method, input_values_set):
    """Run the tests."""
    for args, kwargs, expected_value in input_values_set:
        try:
            value_out = await async_method(*args, **kwargs)
            assert value_out == expected_value
        except ValueError:
            assert expected_value == "ValueError"


class ToolsBaseTester(ToolsBase):
    """Testing class for the ToolsBase class."""

    def __init__(self, loop, args=None, menu=None, stdin=None, stdout=None):
        """Init the ToolsBaseTester class."""
        super().__init__(loop, args=args, menu=menu, stdin=stdin, stdout=stdout)
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        self.call_count = 0
        self.call_count_background = 0
        self.called_with = ()

    async def do_async_test_args(self, arg1, arg2, *args, kwarg1=1, kwarg2=2, **kwargs):
        """Test all argument options."""
        self.called_with = (
            arg1,
            arg2,
            *args,
            {"kwarg1": kwarg1, "kwarg2": kwarg2, **kwargs},
        )
        self.call_count += 1

    async def do_async_test(self, arg1, arg2, log_stdout=None, background=False):
        """Test for async methods in foreground and background mode with arguments."""
        self.arg1 = arg1
        self.arg2 = arg2
        if background:
            self.call_count_background += 1
        else:
            self.call_count += 1
        log_stdout("async_test command ran.")

    async def do_async_test_no_background(self, arg1, arg2, arg3=75):
        """Test for async methods in foreground and background mode with arguments."""
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.call_count += 1
        self._log_stdout("do_async_test_no_background command ran.")

    def menu_my_menu_1(self):
        """Mock menu 1."""
        self.call_count += 1

    def menu_my_menu_2(self):
        """Mock menu 1."""
        self.call_count += 1

    async def ensure_hex_byte_test(self):
        """Test the ensure_hex_byte method."""

        name = "hex value"
        log_stdout = self._log_background
        ask_value = False

        input_values_set = [
            (["0a", name, ask_value, log_stdout], {}, 10),
            (["0x05", name, ask_value, log_stdout], {}, 5),
            (["0x0102", name, ask_value, log_stdout], {}, 258),
            (["0101", name, ask_value, log_stdout], {}, 257),
            (["01", name, ask_value, log_stdout], {}, 1),
            (["03", name, False, log_stdout], {"values": [3, 4]}, 3),
            (["0103", name, False, log_stdout], {"values": [258, 259, 260]}, 259),
            (["010101", name, False, log_stdout], {"values": [65792, 65793]}, 65793),
            (["1", name, ask_value, log_stdout], {}, "ValueError"),
            (["001", name, ask_value, log_stdout], {}, "ValueError"),
            (["0n43", name, ask_value, log_stdout], {}, "ValueError"),
            (["02", name, False, log_stdout], {"values": [22, 23]}, "ValueError"),
            ([None, name, ask_value, log_stdout], {}, "ValueError"),
        ]

        await async_run_tests(
            async_method=self._ensure_hex_byte, input_values_set=input_values_set
        )

        log_stdout = self._log_background
        ask_value = False

        input_values_set = [
            ([None, name, True, log_stdout], {}, 10),  # input 0a
            ([None, name, True, log_stdout], {}, None),  # Input ""
            ([None, name, True, log_stdout], {}, 11),  # Input 0n and 0x0b
            (
                [None, name, True, log_stdout],
                {"values": [15, 16]},
                15,
            ),  # Input 01 and 0x0f
            (
                [None, name, True, log_stdout],
                {"values": [3841, 3840]},
                3840,
            ),  # Input 0x0f00
            (
                [None, name, True, log_stdout],
                {"values": [983040, 983041]},
                983040,
            ),  # 0x0f0000
        ]
        await async_run_tests(
            async_method=self._ensure_hex_byte, input_values_set=input_values_set
        )

    async def ensure_arg_value_test(self):
        """Test the _ensure_arg_value method."""

        # Test each argument name to make sure it works correctly
        input_values_set = [
            (["auto_led", "y", False, self._log_stdout], {}, True),
            (["awake_time", "10", False, self._log_stdout], {}, 10),
            (["button", "3", False, self._log_stdout], {}, 3),
            (["buttons", ["1", "2", "3"], False, self._log_stdout], {}, [1, 2, 3]),
            (["deadman", "n", False, self._log_stdout], {}, False),
            (["disable_auto_linking", "y", False, self._log_stdout], {}, True),
            (["fast", "y", False, self._log_stdout], {}, True),
            (["force", "n", False, self._log_stdout], {}, False),
            (["group", "100", False, self._log_stdout], {}, 100),
            (["humidity", "22", False, self._log_stdout], {}, 22),
            (["link_mode", "y", False, self._log_stdout], {}, True),
            (["logging_mode", "y", False, self._log_stdout], {}, True),
            (
                ["master", "11.22.33", False, self._log_stdout],
                {},
                [Address("11.22.33")],
            ),
            (["monitor_mode", "N", False, self._log_stdout], {}, False),
            (["on_level", "88", False, self._log_stdout], {}, 88),
            (["open_level", "33", False, self._log_stdout], {}, 33),
            (["relay_mode", "0", False, self._log_stdout], {}, RelayMode(0)),
            (["seconds", "99", False, self._log_stdout], {}, 99),
            (["temperature", "55", False, self._log_stdout], {}, 55),
            (["thermostat_mode", "1", False, self._log_stdout], {}, ThermostatMode(1)),
            (["toggle_mode", "2", False, self._log_stdout], {}, ToggleMode(2)),
            (["unkown_arg", "2", False, self._log_stdout], {}, "2"),
            (["toggle_mode", "x", False, self._log_stdout], {}, "ValueError"),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the bool type to ensure it handles errors correctly
        input_values_set = [
            (["auto_led", "y", False, self._log_stdout], {}, True),
            (["auto_led", "n", False, self._log_stdout], {}, False),
            (["auto_led", None, False, self._log_stdout], {}, None),
            (["auto_led", None, False, self._log_stdout], {"default": True}, True),
            (["auto_led", "p", False, self._log_stdout], {}, "ValueError"),
            (
                ["auto_led", "c", False, self._log_stdout],
                {"values": ["c", "r"], "true_val": "c"},
                True,
            ),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the byte type to ensure it handles errors correctly
        input_values_set = [
            (["awake_time", "0", False, self._log_stdout], {}, 0),
            (["awake_time", "100", False, self._log_stdout], {}, 100),
            (["awake_time", "255", False, self._log_stdout], {}, 255),
            (["awake_time", "256", False, self._log_stdout], {}, "ValueError"),
            (["awake_time", "x", False, self._log_stdout], {}, "ValueError"),
            (["awake_time", None, False, self._log_stdout], {}, None),
            (["awake_time", None, False, self._log_stdout], {"default": 12}, 12),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the range type to ensure it handles errors correctly
        input_values_set = [
            (["button", "1", False, self._log_stdout], {}, 1),
            (["button", "4", False, self._log_stdout], {}, 4),
            (["button", "8", False, self._log_stdout], {}, 8),
            (["button", "9", False, self._log_stdout], {}, "ValueError"),
            (["button", "3", False, self._log_stdout], {"values": [1, 2, 3, 4]}, 3),
            (
                ["button", "8", False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                "ValueError",
            ),
            (["button", "x", False, self._log_stdout], {}, "ValueError"),
            (["button", None, False, self._log_stdout], {}, None),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the buttons type to ensure it handles errors correctly
        input_values_set = [
            (["buttons", ["1", "2"], False, self._log_stdout], {}, [1, 2]),
            (["buttons", ["4", "3", "2"], False, self._log_stdout], {}, [4, 3, 2]),
            (
                ["buttons", ["8", "5", "6", "7"], False, self._log_stdout],
                {},
                [8, 5, 6, 7],
            ),
            (["buttons", ["9"], False, self._log_stdout], {}, "ValueError"),
            (
                ["buttons", ["3", "4"], False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                [3, 4],
            ),
            (
                ["buttons", ["3", "4"], False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                [3, 4],
            ),
            (
                ["buttons", ["3", "4", None], False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                [3, 4],
            ),
            (
                ["buttons", ["3"], False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                "ValueError",
            ),
            (
                ["buttons", ["3"], False, self._log_stdout],
                {"values": [1, 2, 3, 4], "require_two": False},
                [3],
            ),
            (
                ["buttons", ["3", None], False, self._log_stdout],
                {"values": [1, 2, 3, 4], "require_two": False},
                [3],
            ),
            (
                ["buttons", ["8"], False, self._log_stdout],
                {"values": [1, 2, 3, 4]},
                "ValueError",
            ),
            (["buttons", ["x"], False, self._log_stdout], {}, "ValueError"),
            (["buttons", None, False, self._log_stdout], {}, None),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the address type to ensure it handles errors correctly
        test_address = random_address()
        input_values_set = [
            (
                ["master", str(test_address), False, self._log_stdout],
                {},
                [test_address],
            ),
            (["master", "not.an.address", False, self._log_stdout], {}, "ValueError"),
            (["master", None, False, self._log_stdout], {}, []),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

        # Test the enum type to ensure it handles errors correctly
        test_address = random_address()
        input_values_set = [
            (["relay_mode", "0", False, self._log_stdout], {}, RelayMode(0)),
            (["relay_mode", "3", False, self._log_stdout], {}, RelayMode(3)),
            (["relay_mode", "4", False, self._log_stdout], {}, "ValueError"),
            (["thermostat_mode", "0", False, self._log_stdout], {}, ThermostatMode(0)),
            (["thermostat_mode", "8", False, self._log_stdout], {}, ThermostatMode(8)),
            (["thermostat_mode", "6", False, self._log_stdout], {}, "ValueError"),
            (["toggle_mode", "0", False, self._log_stdout], {}, ToggleMode(0)),
            (["toggle_mode", "2", False, self._log_stdout], {}, ToggleMode(2)),
            (["toggle_mode", "4", False, self._log_stdout], {}, "ValueError"),
        ]
        await async_run_tests(
            async_method=self._ensure_arg_value, input_values_set=input_values_set
        )

    def parse_args_test(self):
        """Test the parse_args method."""
        args, kwargs, is_valid = self._parse_args(
            self.do_async_test,
            [
                "value_arg_1",
                "value_arg_2",
            ],
        )
        assert is_valid
        assert args == ["value_arg_1", "value_arg_2"]
        assert "background" in kwargs
        assert "log_stdout" in kwargs

        args, kwargs, is_valid = self._parse_args(
            self.do_async_test_args,
            [
                "value_arg_1",
                "value_arg_2",
                "varg_1",
                "varg_2",
                "kwarg1=3",
                "kwarg2=4",
                "other_kwarg=5",
            ],
        )
        assert is_valid
        assert args == ["value_arg_1", "value_arg_2", "varg_1", "varg_2"]
        assert kwargs.get("kwarg1") == "3"
        assert kwargs.get("kwarg2") == "4"
        assert kwargs.get("other_kwarg") == "5"

        args, kwargs, is_valid = self._parse_args(
            self.do_async_test,
            [
                "arg2=value_arg_2",
                "arg1=value_arg_1",
            ],
        )
        assert is_valid
        assert args == []
        assert kwargs.get("arg2") == "value_arg_2"
        assert kwargs.get("arg1") == "value_arg_1"
        assert "background" in kwargs
        assert "log_stdout" in kwargs

    def get_menus_test(self):
        """Test the get_menus method."""
        menus = self._get_menus()
        assert menus == ["my_menu_1", "my_menu_2"]

    async def ensure_address_test(self, good_address, bad_address, devices):
        """Test the ensure_address method."""

        name = "address"
        ask_value = False
        log_stdout = self._log_background
        all_addresses = list(devices)

        input_values_set = [
            ([good_address, name, ask_value, log_stdout], {}, [good_address]),
            ([str(good_address), name, ask_value, log_stdout], {}, [good_address]),
            ([repr(good_address), name, ask_value, log_stdout], {}, [good_address]),
            ([None, name, ask_value, log_stdout], {}, []),
            (["xx.yy.zz", name, ask_value, log_stdout], {}, "ValueError"),
            ([repr(bad_address), name, ask_value, log_stdout], {}, "ValueError"),
            (
                [repr(bad_address), name, ask_value, log_stdout],
                {"match_device": False},
                [bad_address],
            ),
            (["all", name, ask_value, log_stdout], {}, all_addresses),
            (["all", name, ask_value, log_stdout], {"allow_all": False}, "ValueError"),
        ]
        await async_run_tests(
            async_method=self._ensure_address, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout

        input_values_set = [
            (
                [None, name, ask_value, log_stdout],
                {},
                [good_address],
            ),  # input good_address
            ([None, name, ask_value, log_stdout], {}, []),  # input bad_address, ""
            (
                [None, name, ask_value, log_stdout],
                {"match_device": False},
                [bad_address],
            ),  # input bad_address
            ([None, name, ask_value, log_stdout], {}, []),  # input "xx.yy.zz", ""
            ([None, name, ask_value, log_stdout], {}, []),  # input ""
            ([None, name, ask_value, log_stdout], {}, all_addresses),  # input "all"
            (
                [None, name, ask_value, log_stdout],
                {"allow_all": False},
                [],
            ),  # input "all", ""
        ]
        await async_run_tests(
            async_method=self._ensure_address, input_values_set=input_values_set
        )

    async def ensure_string_test(self, string_1, string_2, string_3):
        """Test the ensure_string method."""

        name = "String"
        ask_value = False
        log_stdout = self._log_background

        input_values_set = [
            (["my_string", None, name, ask_value, log_stdout], {}, "my_string"),
            (
                [string_1, [string_1, string_2], name, ask_value, log_stdout],
                {},
                string_1,
            ),
            (
                [string_2, [string_1, string_2], name, ask_value, log_stdout],
                {},
                string_2,
            ),
            ([None, [string_1, string_2], name, ask_value, log_stdout], {}, None),
            (
                [string_3, [string_1, string_2], name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {"default": string_1},
                string_1,
            ),
        ]
        await async_run_tests(
            async_method=self._ensure_string, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout
        input_values_set = [
            ([None, None, name, ask_value, log_stdout], {}, string_1),  # input string_1
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {},
                string_1,
            ),  # input string_1
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {},
                string_2,
            ),  # input string_2
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {},
                None,
            ),  # input string_3, ""
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {},
                None,
            ),  # input ""
            (
                [None, [string_1, string_2], name, ask_value, log_stdout],
                {"default": string_1},
                string_1,
            ),  # input ""
        ]
        await async_run_tests(
            async_method=self._ensure_string, input_values_set=input_values_set
        )

    async def ensure_float_test(self, float_1, minimum, maximum):
        """Test the ensure_float method."""

        name = "Float"
        ask_value = False
        log_stdout = self._log_background

        input_values_set = [
            ([33.3, minimum, maximum, name, ask_value, log_stdout], {}, 33.3),
            ([minimum, minimum, maximum, name, ask_value, log_stdout], {}, minimum),
            ([maximum, minimum, maximum, name, ask_value, log_stdout], {}, maximum),
            (
                [minimum - 1, minimum, maximum, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            (
                [maximum + 1, minimum, maximum, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            ([None, minimum, maximum, name, ask_value, log_stdout], {}, None),
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {"default": float_1},
                float_1,
            ),
            (["a", minimum, maximum, name, ask_value, log_stdout], {}, "ValueError"),
            (
                ["b", minimum, maximum, name, ask_value, log_stdout],
                {"default": float_1},
                "ValueError",
            ),
        ]
        await async_run_tests(
            async_method=self._ensure_float, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout
        input_values_set = [
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                float_1,
            ),  # Input float_1
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                minimum,
            ),  # input minimum
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                maximum,
            ),  # Input maximum
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input ""
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input minimum - 1, ""
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input maximum + 1, ""
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {"default": float_1},
                float_1,
            ),  # Input ""
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input "a", ""
            (
                [None, minimum, maximum, name, ask_value, log_stdout],
                {"default": float_1},
                float_1,
            ),  # Input "b", ""
        ]
        await async_run_tests(
            async_method=self._ensure_float, input_values_set=input_values_set
        )

    async def ensure_int_test(self, int_1, minimum, maximum):
        """Test the ensure_int method."""

        values = range(minimum, maximum + 1)
        name = "Int"
        ask_value = False
        log_stdout = self._log_background

        input_values_set = [
            ([33, values, name, ask_value, log_stdout], {}, 33),
            ([minimum, values, name, ask_value, log_stdout], {}, minimum),
            ([maximum, values, name, ask_value, log_stdout], {}, maximum),
            (
                [minimum - 1, values, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            (
                [maximum + 1, values, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            ([None, values, name, ask_value, log_stdout], {}, None),
            (
                [None, values, name, ask_value, log_stdout],
                {"default": int_1},
                int_1,
            ),
            (["a", values, name, ask_value, log_stdout], {}, "ValueError"),
            (
                ["b", values, name, ask_value, log_stdout],
                {"default": int_1},
                "ValueError",
            ),
        ]
        await async_run_tests(
            async_method=self._ensure_int, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout
        input_values_set = [
            (
                [None, values, name, ask_value, log_stdout],
                {},
                int_1,
            ),  # Input int_1
            (
                [None, values, name, ask_value, log_stdout],
                {},
                minimum,
            ),  # input minimum
            (
                [None, values, name, ask_value, log_stdout],
                {},
                maximum,
            ),  # Input maximum
            (
                [None, values, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input ""
            (
                [None, values, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input minimum - 1, ""
            (
                [None, values, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input maximum + 1, ""
            (
                [None, values, name, ask_value, log_stdout],
                {"default": int_1},
                int_1,
            ),  # Input ""
            (
                [None, values, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input "a", ""
            (
                [None, values, name, ask_value, log_stdout],
                {"default": int_1},
                int_1,
            ),  # Input "b", ""
        ]
        await async_run_tests(
            async_method=self._ensure_int, input_values_set=input_values_set
        )

    async def ensure_bool_test(self, char_1, char_2, values):
        """Test the ensure_bool method.

        value, name, ask_value, log_stdout, true_val=None, values=None, default=None
        """
        name = "Bool"
        ask_value = False
        log_stdout = self._log_background

        input_values_set = [
            (["y", name, ask_value, log_stdout], {}, True),
            (["n", name, ask_value, log_stdout], {}, False),
            (["a", name, ask_value, log_stdout], {}, "ValueError"),
            (
                ["a", name, ask_value, log_stdout],
                {"true_val": "a", "values": ["a", "b"]},
                True,
            ),
            (
                ["b", name, ask_value, log_stdout],
                {"true_val": "a", "values": ["a", "b"]},
                False,
            ),
            ([None, name, ask_value, log_stdout], {}, None),
            ([None, name, ask_value, log_stdout], {"default": True}, True),
        ]
        await async_run_tests(
            async_method=self._ensure_bool, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout

        input_values_set = [
            ([None, name, ask_value, log_stdout], {}, True),  # Input "y"
            ([None, name, ask_value, log_stdout], {}, False),  # Input "n"
            ([None, name, ask_value, log_stdout], {}, None),  # Input ""
            ([None, name, ask_value, log_stdout], {"default": True}, True),  # Input ""
            ([None, name, ask_value, log_stdout], {}, None),  # Input "a", ""
            (
                [None, name, ask_value, log_stdout],
                {"true_val": char_1, "values": values},
                True,
            ),  # Input char_1
            (
                [None, name, ask_value, log_stdout],
                {"true_val": char_1, "values": values},
                False,
            ),  # Input char_2
            (
                ["q", name, ask_value, log_stdout],
                {"true_val": char_1, "values": values, "default": False},
                False,
            ),  # Input ""
        ]
        await async_run_tests(
            async_method=self._ensure_bool, input_values_set=input_values_set
        )

    async def ensure_byte_test(
        self,
        byte_1,
    ):
        """Test the ensure_byte method."""

        minimum = 0
        maximum = 255
        name = "Byte"
        ask_value = False
        log_stdout = self._log_background

        input_values_set = [
            ([33, name, ask_value, log_stdout], {}, 33),
            ([minimum, name, ask_value, log_stdout], {}, minimum),
            ([maximum, name, ask_value, log_stdout], {}, maximum),
            (
                [minimum - 1, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            (
                [maximum + 1, name, ask_value, log_stdout],
                {},
                "ValueError",
            ),
            ([None, name, ask_value, log_stdout], {}, None),
            (
                [None, name, ask_value, log_stdout],
                {"default": byte_1},
                byte_1,
            ),
            (["a", name, ask_value, log_stdout], {}, "ValueError"),
            (
                ["b", name, ask_value, log_stdout],
                {"default": byte_1},
                "ValueError",
            ),
        ]
        await async_run_tests(
            async_method=self._ensure_byte, input_values_set=input_values_set
        )

        ask_value = True
        log_stdout = self._log_stdout
        input_values_set = [
            (
                [None, name, ask_value, log_stdout],
                {},
                byte_1,
            ),  # Input byte_1
            (
                [None, name, ask_value, log_stdout],
                {},
                minimum,
            ),  # input minimum
            (
                [None, name, ask_value, log_stdout],
                {},
                maximum,
            ),  # Input maximum
            (
                [None, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input ""
            (
                [None, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input minimum - 1, ""
            (
                [None, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input maximum + 1, ""
            (
                [None, name, ask_value, log_stdout],
                {"default": byte_1},
                byte_1,
            ),  # Input ""
            (
                [None, name, ask_value, log_stdout],
                {},
                None,
            ),  # Input "a", ""
            (
                [None, name, ask_value, log_stdout],
                {"default": byte_1},
                byte_1,
            ),  # Input "b", ""
        ]
        await async_run_tests(
            async_method=self._ensure_byte, input_values_set=input_values_set
        )

    async def get_workdir_test(self, curr_dir, cwd):
        """Test the get_workdir method."""
        out_value = await self._get_workdir()  # Input curr_dir
        assert out_value == curr_dir

        out_value = await self._get_workdir()  # Input "."
        assert out_value == cwd

        out_value = await self._get_workdir()  # Input ""
        assert out_value is None

        out_value = await self._get_workdir()  # Input "/not_a_dir", ""
        assert out_value is None


class TestToolsBase(ToolsTestBase):
    """Test the tools base class."""

    @async_case
    async def test_ensure_hex_byte(self):
        """Test the hex input method."""
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester, ["0a", "", "0n", "0x0b", "01", "0f", "0f00", "0f0000"]
            )
            await cmd_mgr.ensure_hex_byte_test()

    @async_case
    async def test_ensure_arg_value(self):
        """Test the ensure_arg_value method."""
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(ToolsBaseTester, [])
            await cmd_mgr.ensure_arg_value_test()

    @async_case
    async def test_parse_args(self):
        """Test the parse_args method."""
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(ToolsBaseTester, [])
            cmd_mgr.parse_args_test()

    @async_case
    async def test_get_menus(self):
        """Test the get_menus method."""
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(ToolsBaseTester, [])
            cmd_mgr.get_menus_test()

    @async_case
    async def test_ensure_address(self):
        """Test the ensure_address method."""
        devices = MockDevices()
        good_address = get_good_address(devices)
        bad_address = get_bad_address(devices)
        async with self.test_lock:
            with patch.object(pyinsteon.tools.tools_base, "devices", devices):
                cmd_mgr, _, _ = self.setup_cmd_tool(
                    ToolsBaseTester,
                    [
                        good_address,
                        bad_address,
                        "",
                        bad_address,
                        "xx.yy.zz",
                        "",
                        "",
                        "all",
                        "all",
                        "",
                    ],
                    allow_logging=False,
                )
                await cmd_mgr.ensure_address_test(
                    good_address=good_address, bad_address=bad_address, devices=devices
                )

    @async_case
    async def test_ensure_string(self):
        """Test the ensure_string method."""
        string_1 = "string_1"
        string_2 = "string_2"
        string_3 = "string_3"
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [string_1, string_1, string_2, string_3, "", "", ""],
                allow_logging=False,
            )
            await cmd_mgr.ensure_string_test(
                string_1=string_1, string_2=string_2, string_3=string_3
            )

    @async_case
    async def test_ensure_float(self):
        """Test the ensure_float method."""
        float_1 = 3.4
        minimum = 0
        maximum = 240
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [
                    str(float_1),
                    str(minimum),
                    str(maximum),
                    "",
                    str(minimum - 1),
                    "",
                    str(maximum + 2),
                    "",
                    "",
                    "a",
                    "",
                    "b",
                    "",
                ],
                allow_logging=False,
            )
            await cmd_mgr.ensure_float_test(
                float_1=float_1,
                minimum=minimum,
                maximum=maximum,
            )

    @async_case
    async def test_ensure_int(self):
        """Test the ensure_int method."""
        int_1 = 5
        minimum = 4
        maximum = 240
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [
                    str(int_1),
                    str(minimum),
                    str(maximum),
                    "",
                    str(minimum - 1),
                    "",
                    str(maximum + 2),
                    "",
                    "",
                    "a",
                    "",
                    "b",
                    "",
                ],
                allow_logging=False,
            )
            await cmd_mgr.ensure_int_test(int_1=int_1, minimum=minimum, maximum=maximum)

    @async_case
    async def test_ensure_bool(self):
        """Test the ensure_bool method."""
        char_1 = "a"
        char_2 = "b"
        values = [char_1, char_2]
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [
                    "y",
                    "n",
                    "",
                    "",
                    "a",
                    "",
                    char_1,
                    char_2,
                    "",
                ],
                allow_logging=False,
            )
            await cmd_mgr.ensure_bool_test(char_1=char_1, char_2=char_2, values=values)

    @async_case
    async def test_ensure_byte(self):
        """Test the ensure_byte method."""
        byte_1 = 5
        minimum = 0
        maximum = 255
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [
                    str(byte_1),
                    str(minimum),
                    str(maximum),
                    "",
                    str(minimum - 1),
                    "",
                    str(maximum + 2),
                    "",
                    "",
                    "a",
                    "",
                    "b",
                    "",
                ],
                allow_logging=False,
            )
            await cmd_mgr.ensure_byte_test(byte_1=byte_1)

    @async_case
    async def test_get_workdir(self):
        """Test the get_workdir method."""
        curr_dir = get_curr_dir(__file__)
        cwd = os.getcwd()
        async with self.test_lock:
            cmd_mgr, _, _ = self.setup_cmd_tool(
                ToolsBaseTester,
                [
                    str(curr_dir),
                    ".",
                    "",
                    "/not_a_dir",
                    "",
                ],
                allow_logging=False,
            )
            await cmd_mgr.get_workdir_test(curr_dir=curr_dir, cwd=cwd)

    @async_case
    async def test_onecmd(self):
        """Test onecmd method."""

        def reset_cmd_mgr(cmd_mgr):
            """Reset the cmd_mgr to default values."""
            cmd_mgr.arg1 = None
            cmd_mgr.arg2 = None
            cmd_mgr.arg3 = None
            cmd_mgr.call_count = 0
            cmd_mgr.call_count_background = 0

        async with self.test_lock:
            cmd_mgr, _, stdout = self.setup_cmd_tool(
                ToolsBaseTester,
                [],
                allow_logging=False,
            )
            line = "async_test"
            await cmd_mgr.async_onecmd(line)
            assert cmd_mgr.arg1 is None
            assert cmd_mgr.arg2 is None
            assert cmd_mgr.call_count == 1

            reset_cmd_mgr(cmd_mgr)
            line = "async_test arg1"
            await cmd_mgr.async_onecmd(line)
            assert cmd_mgr.arg1 == "arg1"
            assert cmd_mgr.arg2 is None
            assert cmd_mgr.call_count == 1

            reset_cmd_mgr(cmd_mgr)
            line = "async_test arg1 arg2"
            await cmd_mgr.async_onecmd(line)
            assert cmd_mgr.arg1 == "arg1"
            assert cmd_mgr.arg2 == "arg2"
            assert cmd_mgr.call_count == 1

            reset_cmd_mgr(cmd_mgr)
            stdout.buffer = []
            line = "async_test arg1 arg2 arg3"
            await cmd_mgr.async_onecmd(line)
            buffer = clean_buffer(stdout.buffer)
            assert buffer[0] == "Too many arguements\n"
            assert cmd_mgr.call_count == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test -b arg1 arg2"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 1
            assert cmd_mgr.arg1 == "arg1"
            assert cmd_mgr.arg2 == "arg2"

            reset_cmd_mgr(cmd_mgr)
            line = "async_test_no_background arg1 arg2 arg3=5"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 1

            reset_cmd_mgr(cmd_mgr)
            line = "async_test --background arg1 arg2"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 1
            assert cmd_mgr.arg1 == "arg1"
            assert cmd_mgr.arg2 == "arg2"

            reset_cmd_mgr(cmd_mgr)
            line = "async_test -b arg1"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test -b arg1 arg2 arg3"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test -b arg1 arg2 arg4=1"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test arg1 arg2=1 arg3"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test arg1=2 arg2"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "async_test_no_background -b arg1 arg2"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 1
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "my_menu_1"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 1
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = "not_a_command"
            await cmd_mgr.async_onecmd(line)
            await asyncio.sleep(0.1)
            assert cmd_mgr.call_count == 0
            assert cmd_mgr.call_count_background == 0

            reset_cmd_mgr(cmd_mgr)
            line = ""
            return_val = await cmd_mgr.async_onecmd(line)
            assert return_val == cmd_mgr.emptyline()

    @async_case
    async def test_start(self):
        """Test the start command."""
        device = None
        username = None
        host = None
        hub_version = None
        port = None

        def set_connection_values(
            device_in, username_in, host_in, hub_version_in, port_in
        ):
            """Set the connection values."""
            nonlocal device, username, host, hub_version, port
            device = device_in
            host = host_in
            username = username_in
            hub_version = hub_version_in
            port = port_in

        class MockLoop:
            """Mock the event loop."""

            def __init__(self, *args, **kwargs):
                """Init the MockLoop class."""

            def run_until_complete(self, task, *args, **kwargs):
                """Mock the run_until_complete method."""
                async_task = asyncio.create_task(task)
                asyncio.ensure_future(async_task)

            def add_signal_handler(self, *args, **kwargs):
                """Mock the add_signal_handler method."""

        def mock_get_event_loop(*args, **kwargs):
            """Mock the get_event_loop method."""
            return MockLoop()

        async def mock_async_cmdloop(self, *args, **kwargs):
            """Mock the async_cmdloop method."""
            nonlocal device, username, host, hub_version, port

            assert self.device == device
            if host is not None:
                def_port = {1: 9761, 2: 25105}
                assert self.host == host
                assert self.username == username
                if hub_version is not None:
                    assert self.hub_version == hub_version
                else:
                    assert self.hub_version == 2
                if port is not None:
                    assert self.port == port
                else:
                    assert self.port == def_port.get(self.hub_verion)

        get_event_loop_saved = asyncio.get_event_loop
        asyncio.get_event_loop = mock_get_event_loop

        async with self.test_lock:
            try:
                cmd_mgr, _, _ = self.setup_cmd_tool(ToolsBaseTester, [])
                ToolsBaseTester.async_cmdloop = mock_async_cmdloop

                device = "/dev/ttyS3"
                sys.argv = ["some_command", "--device", device]
                cmd_mgr.start()
                await asyncio.sleep(0.1)

                set_connection_values(None, "my_host", "my_user", None, None)
                sys.argv = ["some_command", "--host", host, "--username", username]
                cmd_mgr.start()
                await asyncio.sleep(0.1)

                set_connection_values(None, "my_host", "my_user", "1", None)
                sys.argv = [
                    "some_command",
                    "--host",
                    host,
                    "--username",
                    username,
                    "--hub_version",
                    hub_version,
                ]
                cmd_mgr.start()
                await asyncio.sleep(0.1)

                set_connection_values(None, "my_host", "my_user", "1", "1000")
                sys.argv = [
                    "some_command",
                    "--host",
                    host,
                    "--username",
                    username,
                    "--hub_version",
                    hub_version,
                    "--port",
                    port,
                ]
                cmd_mgr.start()
                await asyncio.sleep(0.1)

                set_connection_values(None, "my_host", "my_user", "2", "1000")
                sys.argv = [
                    "some_command",
                    "--host",
                    host,
                    "--username",
                    username,
                    "--port",
                    port,
                ]
                cmd_mgr.start()
                await asyncio.sleep(0.1)

                device = None

            finally:
                asyncio.get_event_loop = get_event_loop_saved
