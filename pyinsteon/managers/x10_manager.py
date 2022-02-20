"""Manage X10 functions."""
from ..constants import X10Commands
from ..handlers.to_device.x10_send import X10CommandSend
from ..subscriber_base import SubscriberBase
from ..utils import publish_topic, subscribe_topic
from ..x10_address import X10Address, create


async def async_x10_all_units_off(housecode: str):
    """Send the X10 All Units OFF command."""
    cmd = X10CommandSend(create(housecode, 0), X10Commands.ALL_UNITS_OFF)
    return await cmd.async_send()


async def async_x10_all_lights_on(housecode: str):
    """Send the X10 All Lights ON command."""
    cmd = X10CommandSend(create(housecode, 0), X10Commands.ALL_LIGHTS_ON)
    return await cmd.async_send()


async def async_x10_all_lights_off(housecode: str):
    """Send the X10 All Lights OFF command."""
    cmd = X10CommandSend(create(housecode, 0), X10Commands.ALL_LIGHTS_OFF)
    return await cmd.async_send()


class X10OnOffManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = f"subscribers.{address.id}.on_off"
        super().__init__(subscriber_topic=topic)
        on_topic = f"{address.id}.{str(X10Commands.ON)}"
        off_topic = f"{address.id}.{str(X10Commands.OFF)}"
        subscribe_topic(self._on_received, on_topic)
        subscribe_topic(self._off_received, off_topic)
        self._on_subscriber_topic = f"{self._subscriber_topic}_on"
        self._off_subscriber_topic = f"{self._subscriber_topic}_off"

    def subscribe_on(self, callback: callable):
        """Subscribe to the ON event."""
        subscribe_topic(callback, self._on_subscriber_topic)

    def subscribe_off(self, callback: callable):
        """Subscribe to the OFF event."""
        subscribe_topic(callback, self._off_subscriber_topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)
        publish_topic(self._on_subscriber_topic, on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)
        publish_topic(self._off_subscriber_topic, on_level=0x00)


class X10DimBrightenManager(SubscriberBase):
    """Manage Inbound X10 On/Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10OnOffManager class."""
        topic = f"subscribers.{address.id}.dim_bright"
        super().__init__(subscriber_topic=topic)
        dim_topic = f"{address.id}.{str(X10Commands.DIM)}"
        bright_topic = f"{address.id}.{str(X10Commands.BRIGHT)}"
        subscribe_topic(self._dim_received, dim_topic)
        subscribe_topic(self._bright_received, bright_topic)

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
        topic = f"subscribers.{address.id}.all_lights_on_off"
        super().__init__(subscriber_topic=topic)
        on_topic = f"x10{address.housecode.lower()}.{str(X10Commands.ALL_LIGHTS_ON)}"
        off_topic = f"x10{address.housecode.lower()}.{str(X10Commands.ALL_LIGHTS_OFF)}"
        subscribe_topic(self._on_received, on_topic)
        subscribe_topic(self._off_received, off_topic)
        self._on_subscriber_topic = f"{self._subscriber_topic}_on"
        self._off_subscriber_topic = f"{self._subscriber_topic}_off"

    def subscribe_on(self, callback: callable):
        """Subscribe to the on command."""
        topic = f"{self._subscriber_topic}_on"
        subscribe_topic(callback, topic)

    def subscribe_off(self, callback: callable):
        """Subscribe to the off command."""
        topic = f"{self._subscriber_topic}_off"
        subscribe_topic(callback, topic)

    def _on_received(self):
        """Receive an ON message."""
        self._call_subscribers(on_level=0xFF)
        publish_topic(self._on_subscriber_topic, on_level=0xFF)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)
        publish_topic(self._off_subscriber_topic, on_level=0x00)


class X10AllUnitsOffManager(SubscriberBase):
    """Manage Inbound X10 All Units Off commands."""

    def __init__(self, address: X10Address):
        """Init the X10AllUnitsOffManager class."""
        topic = f"subscribers.{address.id}.{str(X10Commands.ALL_UNITS_OFF)}"
        super().__init__(subscriber_topic=topic)
        off_topic = f"x10{address.housecode.lower()}.{str(X10Commands.ALL_UNITS_OFF)}"
        subscribe_topic(self._off_received, off_topic)

    def _off_received(self):
        """Recieve an OFF message."""
        self._call_subscribers(on_level=0x00)
