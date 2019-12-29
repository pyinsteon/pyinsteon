"""Manage X10 functions."""
from .. import pub
from ..handlers.from_device.x10_received import X10Received
from ..constants import UC_LOOKUP, HC_LOOKUP, X10CommandType, X10Commands
from ..utils import parse_x10, byte_to_housecode, byte_to_command
from ..subscriber_base import SubscriberBase
from ..x10_address import create, X10Address


def all_units_off(housecode: str):
    """Send the X10 All Units OFF command."""


def all_lights_on(housecode: str):
    """Send the X10 All Lights ON command."""


def all_lights_off(housecode: str):
    """Send the X10 All Lights OFF command."""


class X10InboundManager:
    """Manage inbound X10 messages."""

    def __init__(self):
        """Init the X10InboundManager class."""
        self._last_housecode = None
        self._last_unitcode = None
        self._inbound_handler = X10Received()
        self._inbound_handler.subscribe(self._x10_received)

    def _x10_received(self, raw_x10, flags):
        """Manage X10 inbound messages."""
        housecode, uc_or_cmd, cmd_type = parse_x10(raw_x10, flags)
        topic = ""
        if self._last_unitcode is not None:
            address = create(HC_LOOKUP[housecode], self._last_unitcode)
            topic = "{}.{}".format(address.id, str(byte_to_command(uc_or_cmd)))
        elif cmd_type == X10CommandType.BROADCAST:
            topic = "x10{}.{}".format(
                byte_to_housecode(housecode), str(byte_to_command(uc_or_cmd))
            )
        else:
            self._last_unitcode = UC_LOOKUP[uc_or_cmd]
        if topic:
            pub.sendMessage(topic)
            self._last_unitcode = None


class X10OnOffManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = "subscribers.{}".format(address.id)
        super().__init__(subscriber_topic=topic)
        on_topic = "{}.{}".format(address.id, str(X10Commands.ON))
        off_topic = "{}.{}".format(address.id, str(X10Commands.OFF))
        all_off_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_UNITS_OFF)
        )
        pub.subscribe(self._on_received, on_topic)
        pub.subscribe(self._off_received, off_topic)
        pub.subscribe(self._off_received, all_off_topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)


class X10AllLightsOnOffManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = "subscribers.{}".format(address.id)
        super().__init__(subscriber_topic=topic)
        on_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_ON)
        )
        off_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_OFF)
        )
        pub.subscribe(self._on_received, on_topic)
        pub.subscribe(self._off_received, off_topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)
