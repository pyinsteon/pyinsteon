"""Test features specific to the KeyPadLinc."""
import logging
import random
import unittest

from pyinsteon import pub
from pyinsteon.commands import OFF, ON, STATUS_REQUEST
from pyinsteon.config import NON_TOGGLE_MASK, NON_TOGGLE_ON_OFF_MASK, OFF_MASK, ON_MASK
from pyinsteon.constants import ResponseStatus
from pyinsteon.device_types.dimmable_lighting_control import (
    DimmableLightingControl_KeypadLinc_8,
)
from pyinsteon.utils import bit_is_set
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics

_LOGGER = logging.getLogger(__name__)


class TestKeyPadLinkFeatures(unittest.TestCase):
    """Test setting the KeyPadLink features."""

    def setUp(self):
        """Set up the test."""
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    @async_case
    async def test_set_radio_buttons(self):
        """Test the `set_radio_buttons` feature."""

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )
        device.set_radio_buttons([3, 4, 5, 6])

        masks = {
            1: None,
            2: None,
            3: int("00111000", 2),
            4: int("00110100", 2),
            5: int("00101100", 2),
            6: int("00011100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    @async_case
    async def test_clear_radio_buttons(self):
        """Test the `set_radio_buttons` feature."""

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            on_mask.load(0)
            off_mask.load(0)

        device.set_radio_buttons([3, 4, 5, 6])
        device.clear_radio_buttons([4, 5])

        masks = {
            1: None,
            2: None,
            3: int("00100000", 2),
            4: None,
            5: None,
            6: int("00000100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    @async_case
    async def test_clear_radio_buttons_when_preset(self):
        """Test clearing an existing radio button group."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        preset_masks = {
            1: 0,
            2: 0,
            3: int("00111000", 2),
            4: int("00110100", 2),
            5: int("00101100", 2),
            6: int("00011100", 2),
            7: 0,
            8: 0,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            on_mask.load(preset_masks[button])
            off_mask.load(preset_masks[button])

        device.clear_radio_buttons([4, 5])

        masks = {
            1: None,
            2: None,
            3: int("00100000", 2),
            4: 0,
            5: 0,
            6: int("00000100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    @async_case
    async def test_set_toggle_mode(self):
        """Test setting toggle modes."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        device.properties[NON_TOGGLE_MASK].load(0)
        device.properties[NON_TOGGLE_ON_OFF_MASK].load(0)

        masks = {
            1: [0, 0],
            2: [0, 0],
            3: [1, 1],
            4: [1, 0],
            5: [0, 0],
            6: [0, 0],
            7: [0, 0],
            8: [0, 0],
        }

        device.set_toggle_mode(3, 1)
        device.set_toggle_mode(4, 2)

        for button in range(1, 9):
            non_toggle_mask = device.properties[NON_TOGGLE_MASK]
            non_toggle_on_off_mask = device.properties[NON_TOGGLE_ON_OFF_MASK]

            assert bit_is_set(non_toggle_mask.new_value, button - 1) == bool(
                masks[button][0]
            )
            assert bit_is_set(non_toggle_on_off_mask.new_value, button - 1) == bool(
                masks[button][1]
            )

    @async_case
    async def test_on_command(self):
        """Test an ON message."""
        state_values = {}

        def state_updated(value, group, name, address):
            """Run when the state is updated."""
            nonlocal state_values
            state_values[group] = value

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )
        for button in device.groups:
            device.groups[button].set_value(0)
            device.groups[button].subscribe(state_updated)
        cmd1 = 0x11
        cmd2 = 0x23
        target = device.address
        user_data = None
        ack = "ack.{}.1.{}.direct".format(device.address.id, ON)
        direct_ack = "{}.{}.direct_ack".format(device.address.id, ON)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await device.async_on(on_level=cmd2, fast=False)
        assert response == ResponseStatus.SUCCESS
        assert state_values.get(1) == cmd2
        for button in device.groups:
            if button == 1:
                continue
            assert state_values.get(2) is None

    @async_case
    async def test_off_command(self):
        """Test an OFF message."""
        state_values = {}

        def state_updated(value, group, name, address):
            """Run when the state is updated."""
            nonlocal state_values
            state_values[group] = value

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )
        for button in device.groups:
            device.groups[button].set_value(255)
            device.groups[button].subscribe(state_updated)
        cmd1 = 0x13
        cmd2 = 0x00
        target = device.address
        user_data = None
        ack = "ack.{}.1.{}.direct".format(device.address.id, OFF)
        direct_ack = "{}.{}.direct_ack".format(device.address.id, OFF)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await device.async_off(fast=False)
        assert response == ResponseStatus.SUCCESS
        assert state_values.get(1) == cmd2
        for button in device.groups:
            if button == 1:
                continue
            assert state_values.get(2) is None

    @async_case
    async def test_status_request_command(self):
        """Test an Status Request message."""
        status_received = False
        status_1_received = False
        state_values = {}

        def state_updated(value, group, name, address):
            """Run when the state is updated."""
            nonlocal state_values
            _LOGGER.info("Group %s updated: %s", str(group), str(value))
            state_values[group] = value

        def receive_status(db_version, status):
            """Run when the state is updated."""
            nonlocal status_received
            _LOGGER.info("Status received")
            status_received = True

        def receive_status_1(db_version, status):
            """Run when the state is updated."""
            nonlocal status_1_received
            _LOGGER.info("Status 1 received")
            status_1_received = True

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )
        for button in device.groups:
            device.groups[button].set_value(0)
            device.groups[button].subscribe(state_updated)
        cmd1_status = random.randint(0, 255)
        cmd2_status = random.randint(0, 255)
        cmd1_status_1 = random.randint(0, 255)
        cmd2_status_1 = random.randint(0, 255)
        cmd1_on = 0x11
        cmd2_on = random.randint(0, 255)
        target = device.address
        user_data = None
        ack_status_0 = "ack.{}.{}.direct".format(device.address.id, STATUS_REQUEST)
        ack_status_1 = "ack.{}.{}.direct".format(device.address.id, STATUS_REQUEST)
        direct_ack_status = "{}.{}.direct_ack".format(device.address.id, STATUS_REQUEST)
        ack_on = "ack.{}.1.{}.direct".format(device.address.id, ON)
        direct_ack_on = "{}.{}.direct_ack".format(device.address.id, ON)
        status_1_handler_topic = f"handler.{device.address.id}.1.status_request.direct"
        status_handler_topic = f"handler.{device.address.id}.2.status_request.direct"
        pub.subscribe(receive_status, status_handler_topic)
        pub.subscribe(receive_status_1, status_1_handler_topic)
        responses = [
            TopicItem(ack_status_0, cmd_kwargs(0x19, 0x02, user_data), 0.5),
            TopicItem(
                direct_ack_status,
                cmd_kwargs(cmd1_status, cmd2_status, user_data, target),
                0.25,
            ),
            TopicItem(ack_status_1, cmd_kwargs(0x19, 0x01, user_data), 0.25),
            TopicItem(
                direct_ack_status,
                cmd_kwargs(cmd1_status_1, cmd2_status_1, user_data, target),
                0.25,
            ),
            TopicItem(ack_on, cmd_kwargs(cmd1_on, cmd2_on, user_data), 0.25),
            TopicItem(
                direct_ack_on, cmd_kwargs(cmd1_on, cmd2_on, user_data, target), 0.25
            ),
        ]
        send_topics(responses)

        response = await device.async_status()
        assert response == ResponseStatus.SUCCESS
        assert status_received
        assert status_1_received
        assert state_values.get(1) == cmd2_status
        for bit in range(1, 8):
            bit_set = bit_is_set(cmd2_status_1, bit)
            button = bit + 1
            if bit_set:
                assert state_values.get(button)
            else:
                assert state_values.get(button) is None

        # Confirm that an ON command does not trigger the status handler again
        status_received = False
        status_1_received = False
        response = await device.async_on(on_level=cmd2_on, fast=False)
        assert response == ResponseStatus.SUCCESS
        assert not status_received
        assert not status_1_received
        assert state_values.get(1) == cmd2_on
        for bit in range(1, 8):
            bit_set = bit_is_set(cmd2_status_1, bit)
            button = bit + 1
            if bit_set:
                assert state_values.get(button)
            else:
                assert state_values.get(button) is None
