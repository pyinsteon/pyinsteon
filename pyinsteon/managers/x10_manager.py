"""Manage X10 functions."""
from .. import pub
from ..constants import X10Commands
from ..subscriber_base import SubscriberBase
from ..x10_address import X10Address


def all_units_off(housecode: str):
    """Send the X10 All Units OFF command."""


def all_lights_on(housecode: str):
    """Send the X10 All Lights ON command."""


def all_lights_off(housecode: str):
    """Send the X10 All Lights OFF command."""


class X10OnOffManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = "subscribers.{}.on_off".format(address.id)
        super().__init__(subscriber_topic=topic)
        on_topic = "{}.{}".format(address.id, str(X10Commands.ON))
        off_topic = "{}.{}".format(address.id, str(X10Commands.OFF))
        pub.subscribe(self._on_received, on_topic)
        pub.subscribe(self._off_received, off_topic)

    def subscribe_on(self, callback):
        """Subscribe to ON events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.ON))
        pub.subscribe(callback, topic)

    def subscribe_off(self, callback):
        """Subscribe to OFF events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.OFF))
        pub.subscribe(callback, topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)


class X10DimBrightenManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = "subscribers.{}.dim_bright".format(address.id)
        super().__init__(subscriber_topic=topic)
        dim_topic = "{}.{}".format(address.id, str(X10Commands.DIM))
        bright_topic = "{}.{}".format(address.id, str(X10Commands.BRIGHT))
        pub.subscribe(self._dim_received, dim_topic)
        pub.subscribe(self._bright_received, bright_topic)

    def subscribe_dim(self, callback):
        """Subscribe to DIM events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.DIM))
        pub.subscribe(callback, topic)

    def subscribe_bright(self, callback):
        """Subscribe to BRIGHT events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.BRIGHT))
        pub.subscribe(callback, topic)

    def _dim_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=-1)

    def _bright_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=1)


class X10AllLightsOnOffManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = "subscribers.{}.all_lights_on_off".format(address.id)
        super().__init__(subscriber_topic=topic)
        on_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_ON)
        )
        off_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_LIGHTS_OFF)
        )
        pub.subscribe(self._on_received, on_topic)
        pub.subscribe(self._off_received, off_topic)

    def subscribe_on(self, callback):
        """Subscribe to ON events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.ALL_LIGHTS_ON))
        pub.subscribe(callback, topic)

    def subscribe_off(self, callback):
        """Subscribe to OFF events."""
        topic = "{}.{}".format(self._subscriber_topic, str(X10Commands.ALL_LIGHTS_OFF))
        pub.subscribe(callback, topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)


class X10AllUnitsOffManager(SubscriberBase):
    """Manage Inbound X10 All Units Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10AllUnitsOffManager class."""
        topic = "subscribers.{}.{}".format(address.id, str(X10Commands.ALL_UNITS_OFF))
        super().__init__(subscriber_topic=topic)
        off_topic = "x10{}.{}".format(
            address.housecode.lower(), str(X10Commands.ALL_UNITS_OFF)
        )
        pub.subscribe(self._off_received, off_topic)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)
