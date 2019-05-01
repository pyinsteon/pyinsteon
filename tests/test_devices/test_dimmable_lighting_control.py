"""Test for Dimmable Lighting Control devices."""

import unittest
from pyinsteon.address import Address
from pyinsteon.handlers import ResponseStatus
from pyinsteon.devices.dimmable_lighting_control import (
    DimmableLightingControl, DIMMABLE_LIGHT_STATE)
from pyinsteon.topics import ON, OFF, ON_FAST, OFF_FAST
from tests.utils import TopicItem, async_case, send_topics, make_command_response_messages


class TestDimmableLIghtingControl(unittest.TestCase):
    """Test dimmable lighting control device."""

    def state_updated(self, **kwargs):
        """Run when the state is updated."""
        self.state_value = kwargs.get('value')

    def setUp(self):
        """Setup the test."""
        self.state_value = None
        self.address = Address('1a2b3c')
        self.device = DimmableLightingControl(self.address, 0x01, 0x02, 0x03, 'Test', 'Modem 1')
        self.device.states[DIMMABLE_LIGHT_STATE].subscribe(self.state_updated)

    @async_case
    async def test_on_command(self):
        """Test an ON message."""
        self.device.states[DIMMABLE_LIGHT_STATE].value = 0
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        responses = make_command_response_messages(self.address, ON, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_on_fast_command(self):
        """Test an ON message."""
        self.device.states[DIMMABLE_LIGHT_STATE].value = 0
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        responses = make_command_response_messages(self.address, ON_FAST, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_off_fast_command(self):
        """Test an ON message."""
        self.device.states[DIMMABLE_LIGHT_STATE].value = 255
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        responses = make_command_response_messages(self.address, OFF_FAST, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_off(fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00

    @async_case
    async def test_off_command(self):
        """Test an ON message."""
        self.device.states[DIMMABLE_LIGHT_STATE].value = 255
        cmd2 = 0x23
        target = Address('4d5e6f')
        user_data = None
        responses = make_command_response_messages(self.address, OFF, cmd2, target, user_data)
        send_topics(responses)

        response = await self.device.async_off(fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00
