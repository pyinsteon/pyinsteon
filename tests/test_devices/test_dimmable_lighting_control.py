"""Test for Dimmable Lighting Control devices."""

import unittest
from pyinsteon.address import Address
from pyinsteon.handlers import ResponseStatus
from pyinsteon.device_types.dimmable_lighting_control import DimmableLightingControl
from pyinsteon.topics import ON, OFF, ON_FAST, OFF_FAST
from tests.utils import async_case, send_topics, make_command_response_messages


class TestDimmableLIghtingControl(unittest.TestCase):
    """Test dimmable lighting control device."""

    def state_updated(self, value, group, name, address):
        """Run when the state is updated."""
        self.state_value = value

    def setUp(self):
        """Setup the test."""
        self.state_value = None
        self.address = Address('1a2b3c')
        self.device = DimmableLightingControl(self.address, 0x01, 0x02, 0x03, 'Test', 'Modem 1')
        self.device.states[1].subscribe(self.state_updated)

    @async_case
    async def test_on_command(self):
        """Test an ON message."""
        self.device.states[1].value = 0
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        topic = '{}.{}'.format(ON, 1)
        responses = make_command_response_messages(self.address, topic, cmd1, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_on_fast_command(self):
        """Test an ON message."""
        self.device.states[1].value = 0
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        topic = '{}.{}'.format(ON_FAST, 1)
        responses = make_command_response_messages(self.address, topic, cmd1,
                                                   cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_off_fast_command(self):
        """Test an ON message."""
        self.device.states[1].value = 255
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        topic = '{}.{}'.format(OFF_FAST, 1)
        responses = make_command_response_messages(self.address, topic, cmd1, cmd2,
                                                   target, user_data)
        send_topics(responses)

        response = await self.device.async_off(fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00

    @async_case
    async def test_off_command(self):
        """Test an ON message."""
        self.device.states[1].value = 255
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        topic = '{}.{}'.format(OFF, 1)
        responses = make_command_response_messages(self.address, topic, cmd1, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_off(fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00
