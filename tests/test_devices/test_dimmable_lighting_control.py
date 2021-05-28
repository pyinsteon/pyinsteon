"""Test for Dimmable Lighting Control devices."""

import unittest

from pyinsteon.address import Address
from pyinsteon.constants import ResponseStatus
from pyinsteon.device_types.dimmable_lighting_control import DimmableLightingControl
from pyinsteon.topics import OFF, OFF_FAST, ON, ON_FAST
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


class TestDimmableLIghtingControl(unittest.TestCase):
    """Test dimmable lighting control device."""

    def state_updated(self, value, group, name, address):
        """Run when the state is updated."""
        self.state_value = value

    def setUp(self):
        """Set up the test."""
        self.state_value = None
        self.address = Address("1a2b3c")
        self.device = DimmableLightingControl(
            self.address, 0x01, 0x02, 0x03, "Test", "Modem 1"
        )
        self.device.groups[1].subscribe(self.state_updated)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_on_command(self):
        """Test an ON message."""
        self.device.groups[1].value = 0
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address("4d5e6f")
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, ON)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, ON)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_on_fast_command(self):
        """Test an ON message."""
        self.device.groups[1].value = 0
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address("4d5e6f")
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, ON_FAST)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, ON_FAST)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_on(on_level=cmd2, fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == cmd2

    @async_case
    async def test_off_fast_command(self):
        """Test an ON message."""
        self.device.groups[1].value = 255
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address("4d5e6f")
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, OFF_FAST)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, OFF_FAST)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_off(fast=True)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00

    @async_case
    async def test_off_command(self):
        """Test an ON message."""
        self.device.groups[1].value = 255
        cmd1 = 0x22
        cmd2 = 0x23
        target = Address("4d5e6f")
        user_data = None
        ack = "ack.{}.1.{}.direct".format(self.device.address.id, OFF)
        direct_ack = "{}.{}.direct_ack".format(self.device.address.id, OFF)
        responses = [
            TopicItem(ack, cmd_kwargs(cmd1, cmd2, user_data), 0.25),
            TopicItem(direct_ack, cmd_kwargs(cmd1, cmd2, user_data, target), 0.25),
        ]
        send_topics(responses)

        response = await self.device.async_off(fast=False)
        assert response == ResponseStatus.SUCCESS
        assert self.state_value == 0x00
