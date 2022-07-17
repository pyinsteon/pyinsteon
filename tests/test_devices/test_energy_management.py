"""Test energy management device functions."""

import asyncio
import unittest

from pyinsteon.constants import ResponseStatus
from pyinsteon.device_types.energy_management import EnergyManagement_LoadController
from pyinsteon.topics import OFF, ON, STATUS_REQUEST

from .. import set_log_levels
from ..utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics


class TestLoadController(unittest.TestCase):
    """Test the LoadController device."""

    def setUp(self):
        """Set up the tests."""
        self._switch_value = None
        self._sensor_value = None
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def switch_update(self, value, group, name, address):
        """Run when a state is updated."""
        self._switch_value = value

    def sensor_update(self, value, group, name, address):
        """Run when a state is updated."""
        self._sensor_value = value

    async def async_setup(self):
        """Set up the test."""
        self.address = random_address()
        self.device = EnergyManagement_LoadController(
            self.address, 0x01, 0x02, 0x03, "Test", "Modem 1"
        )
        self.device.groups[1].subscribe(self.switch_update)
        self.device.groups[2].subscribe(self.sensor_update)

    @async_case
    async def test_on_command(self):
        """Test an ON message."""
        await self.async_setup()
        self.device.groups[1].value = 0
        cmd1 = 0x11
        cmd2 = 0xFF
        target = random_address()
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, ON)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, ON)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_on()
        assert response == ResponseStatus.SUCCESS
        assert self._switch_value == cmd2

    @async_case
    async def test_off_command(self):
        """Test an OFF message."""
        await self.async_setup()
        self.device.groups[1].value = 0
        cmd1 = 0x13
        cmd2 = 0x00
        target = random_address()
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, OFF)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, OFF)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_off()
        assert response == ResponseStatus.SUCCESS
        assert self._switch_value == cmd2

    @async_case
    async def test_status(self):
        """Test a STATUS message."""
        await self.async_setup()
        self.device.groups[1].value = 0
        self.device.groups[2].value = 0xFF
        cmd1 = 0x19
        cmd2_1 = 0x00
        cmd2_2 = 0x01
        cmd1_response = 0xAA
        cmd2_1_response = 0xFF
        cmd2_2_response = 0x00
        target = random_address()
        user_data = None
        ack = "ack.{}.{}.direct".format(self.device.address.id, STATUS_REQUEST)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, "any_value")
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2_1, user_data), 0.25),
            TopicItem(
                direct_ack,
                cmd_kwargs(cmd1_response, cmd2_1_response, user_data, target),
                0.25,
            ),
            TopicItem(ack, cmd_kwargs(cmd1, cmd2_2, user_data), 0.25),
            TopicItem(
                direct_ack,
                cmd_kwargs(cmd1_response, cmd2_2_response, user_data, target),
                0.25,
            ),
        ]
        send_topics(responses)

        response = await self.device.async_status()
        assert response == ResponseStatus.SUCCESS
        assert self._switch_value == cmd2_1_response
        assert self._sensor_value == cmd2_2_response

        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2_2, user_data), 0.25),
            TopicItem(
                direct_ack,
                cmd_kwargs(cmd1_response, cmd2_2_response, user_data, target),
                0.25,
            ),
        ]
        send_topics(responses)
        response = await self.device.async_status(2)
        assert response == ResponseStatus.SUCCESS

    @async_case
    async def test_sensor_state_received(self):
        """Test a sensor broadcase message."""
        await self.async_setup()
        self.device.groups[1].value = 0
        self.device.groups[2].value = 0
        cmd1 = 0x11
        cmd2 = 0xFF
        user_data = None

        broadcast = "{}.2.{}.broadcast".format(self.device.address.id, ON)
        received = [
            TopicItem(
                broadcast,
                cmd_kwargs(cmd1, cmd2, user_data, hops_left=3, target="00.00.02"),
                0.01,
            ),
        ]
        send_topics(received)
        await asyncio.sleep(1)
        assert self._switch_value == 0
        assert self._sensor_value == cmd2
