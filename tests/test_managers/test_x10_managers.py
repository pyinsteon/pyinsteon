"""Test X10 all lights on/off manager."""
import asyncio
import unittest

from pyinsteon import pub
from pyinsteon.constants import X10Commands
from pyinsteon.managers.x10_manager import (
    X10AllLightsOnOffManager,
    X10AllUnitsOffManager,
    X10DimBrightenManager,
    X10OnOffManager,
    async_x10_all_lights_off,
    async_x10_all_lights_on,
    async_x10_all_units_off,
)
from pyinsteon.x10_address import create
from tests import set_log_levels
from tests.utils import async_case


class TestX10AllLightsOnOffManager(unittest.TestCase):
    """Test cases for X10 All Lights On/Off Manager."""

    def setUp(self):
        """Set up the test."""
        self._last_value = None
        self._on_event = False
        self._off_event = False
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def handle_on_off(self, on_level):
        """Handle On/Off commands."""
        self._last_value = on_level

    def handle_on(self, on_level):
        """Handle On event."""
        self._on_event = True

    def handle_off(self, on_level):
        """Handle Off event."""
        self._off_event = True

    @async_case
    async def test_on(self):
        """Test on command."""
        address = create("F", 1)
        topic = "x10_received"
        manager = X10OnOffManager(address)
        manager.subscribe(self.handle_on_off)
        manager.subscribe_on(self.handle_on)
        manager.subscribe_off(self.handle_off)
        address_bytes = bytes(address)
        pub.sendMessage(
            topic, raw_x10=int.from_bytes(address_bytes, byteorder="big"), x10_flag=0x00
        )
        command = (address.housecode_byte << 4) + int(X10Commands.ON)
        pub.sendMessage(topic, raw_x10=command, x10_flag=0x80)
        assert self._last_value == 0xFF
        assert self._on_event
        assert not self._off_event

    @async_case
    async def test_off(self):
        """Test off command."""
        address = create("F", 1)
        topic = "x10_received"
        manager = X10OnOffManager(address)
        manager.subscribe(self.handle_on_off)
        manager.subscribe_on(self.handle_on)
        manager.subscribe_off(self.handle_off)
        address_bytes = bytes(address)
        pub.sendMessage(
            topic, raw_x10=int.from_bytes(address_bytes, byteorder="big"), x10_flag=0x00
        )
        command = (address.housecode_byte << 4) + int(X10Commands.OFF)
        pub.sendMessage(topic, raw_x10=command, x10_flag=0x80)
        assert self._last_value == 0x00
        assert not self._on_event
        assert self._off_event

    @async_case
    async def test_all_lights_on(self):
        """Test the All Lights On command."""
        call_received = False

        def check_x10_call(raw_x10, x10_flag):
            """Check the X10 call params."""
            nonlocal call_received
            call_received = True
            assert raw_x10 == 0x61
            assert x10_flag == 0x80

        topic = "send.x10_send"
        pub.subscribe(check_x10_call, topic)
        await async_x10_all_lights_on(housecode="a")
        await asyncio.sleep(0.05)
        assert call_received
        pub.unsubscribe(check_x10_call, topic)

    @async_case
    async def test_all_lights_off(self):
        """Test the All Lights Off command."""
        call_received = False

        def check_x10_call(raw_x10, x10_flag):
            """Check the X10 call params."""
            nonlocal call_received
            call_received = True
            assert raw_x10 == 0x66
            assert x10_flag == 0x80

        topic = "send.x10_send"
        pub.subscribe(check_x10_call, topic)
        await async_x10_all_lights_off(housecode="a")
        await asyncio.sleep(0.05)
        assert call_received
        pub.unsubscribe(check_x10_call, topic)

    @async_case
    async def test_all_units_off(self):
        """Test the All Units Off command."""
        call_received = False

        def check_x10_call(raw_x10, x10_flag):
            """Check the X10 call params."""
            nonlocal call_received
            call_received = True
            assert raw_x10 == 0x60
            assert x10_flag == 0x80

        topic = "send.x10_send"
        pub.subscribe(check_x10_call, topic)
        await async_x10_all_units_off(housecode="a")
        await asyncio.sleep(0.05)
        assert call_received
        pub.unsubscribe(check_x10_call, topic)

    @async_case
    async def test_all_lights_on_manager(self):
        """Test all lights on manager."""
        address = create("C", 5)
        topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_ON)
        )
        manager = X10AllLightsOnOffManager(address)
        manager.subscribe(self.handle_on_off)
        manager.subscribe_on(self.handle_on)
        manager.subscribe_off(self.handle_off)
        pub.sendMessage(topic)
        assert self._last_value == 0xFF
        assert self._on_event
        assert not self._off_event

    @async_case
    async def test_all_lights_off_manager(self):
        """Test all lights off."""
        # Housecode B unitcode 3
        address = create("B", 3)
        topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_OFF)
        )
        manager = X10AllLightsOnOffManager(address)
        manager.subscribe(self.handle_on_off)
        manager.subscribe_on(self.handle_on)
        manager.subscribe_off(self.handle_off)
        pub.sendMessage(topic)
        assert self._last_value == 0x00
        assert not self._on_event
        assert self._off_event

    @async_case
    async def test_all_units_off_manager(self):
        """Test all units off."""
        # Housecode B unitcode 3
        address = create("A", 7)
        topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_UNITS_OFF)
        )
        manager = X10AllUnitsOffManager(address)
        manager.subscribe(self.handle_on_off)
        pub.sendMessage(topic)
        assert self._last_value == 0x00

    @async_case
    async def test_dim(self):
        """Test dimming."""
        address = create("D", 9)
        topic = f"{address.id}.{str(X10Commands.DIM)}"
        manager = X10DimBrightenManager(address)
        manager.subscribe(self.handle_on_off)
        pub.sendMessage(topic)
        assert self._last_value == -1

    @async_case
    async def test_brighten(self):
        """Test brighten."""
        address = create("D", 9)
        topic = f"{address.id}.{str(X10Commands.BRIGHT)}"
        manager = X10DimBrightenManager(address)
        manager.subscribe(self.handle_on_off)
        pub.sendMessage(topic)
        assert self._last_value == 1
