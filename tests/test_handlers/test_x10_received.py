"""Test an X10 message received."""
import unittest

from pyinsteon import pub
from pyinsteon.handlers.from_device.x10_received import X10Received
from tests.utils import async_case


class TestX10Received(unittest.TestCase):
    """Test case for X10 message received."""

    def setUp(self):
        """Set up the test."""
        self._x10_receieved = None

    def x10_subscriber(self, topic=pub.AUTO_TOPIC):
        """Handle X10 command."""
        self._x10_receieved = topic.name

    @async_case
    async def test_x10_on_received(self):
        """Test X10 message received."""
        handler = X10Received()
        pub.subscribe(self.x10_subscriber, "x10g09")
        handler.subscribe(self.x10_subscriber)
        # Receive housecode G unitcode 9
        handler.handle_x10_received(0x57, 0x00)
        # Receive housecode G command On
        handler.handle_x10_received(0x52, 0x80)
        assert self._x10_receieved == "x10g09.on"

    @async_case
    async def test_x10_off_received(self):
        """Test X10 message received."""
        handler = X10Received()
        pub.subscribe(self.x10_subscriber, "x10a03")
        handler.subscribe(self.x10_subscriber)
        # Receive housecode A unitcode 3
        handler.handle_x10_received(0x62, 0x00)
        # Receive housecode A command Off
        handler.handle_x10_received(0x63, 0x80)
        assert self._x10_receieved == "x10a03.off"

    @async_case
    async def test_x10_all_lights_on(self):
        """Test X10 message received."""
        handler = X10Received()
        pub.subscribe(self.x10_subscriber, "x10c")
        handler.subscribe(self.x10_subscriber)
        # Receive housecode C All Lights On
        handler.handle_x10_received(0x21, 0x80)
        assert self._x10_receieved == "x10c.all_lights_on"
