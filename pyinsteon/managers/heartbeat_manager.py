"""Heartbeat manager."""

from datetime import datetime, timedelta
import asyncio

from ..subscriber_base import SubscriberBase
from ..address import Address
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.on_level import OnLevelInbound


class HeartbeatManager(SubscriberBase):
    """Heartbeat manager."""

    class OnOffHeartbeat(SubscriberBase):
        """On / Off events for subscribers."""

        def call_subscribers(self, on_level):
            """Call subscribers to the event."""
            self._call_subscribers(on_level=on_level)

    def __init__(self, address, group, max_duration=1275):
        """Init the HeartbeatManager class."""
        self._address = Address(address)
        self._group = group
        self._max_duration = max_duration
        subscriber_topic = "subscriber_{}_heartbeat".format(self._address.id)
        super().__init__(subscriber_topic)

        self._on_inbound = OnLevelInbound(self._address, self._group)
        self._off_inbound = OffInbound(self._address, self._group)
        self._on_inbound.subscribe(self._on_heartbeat_received)
        self._off_inbound.subscribe(self._off_heartbeat_received)

        self._on_hb = self.OnOffHeartbeat("{}.{}".format(subscriber_topic, "on"))
        self._off_hb = self.OnOffHeartbeat("{}.{}".format(subscriber_topic, "off"))

        self._last_heartbeat = datetime.now() - timedelta(hours=12)
        self._schedule_next_check()

    def subscribe_on(self, callback):
        """Subscribe to ON heartbeat events."""
        self._on_hb.subscribe(callback)

    def subscribe_off(self, callback):
        """Subscribe to OFF heartbeat events."""
        self._off_hb.subscribe(callback)

    def _on_heartbeat_received(self, on_level):
        """Listen for ON messages from device."""
        self._last_heartbeat = datetime.now()
        self._call_subscribers(heartbeat=True)
        self._on_hb.call_subscribers(on_level=0xFF)

    def _off_heartbeat_received(self, on_level):
        """Listen for OFF messages from device."""
        self._last_heartbeat = datetime.now()
        self._call_subscribers(heartbeat=True)
        self._off_hb.call_subscribers(on_level=0)

    def _check_heartbeat(self):
        """Check if a heartbeat as arrived since max_duration."""
        td_last_heartbeat = datetime.now() - self._last_heartbeat
        if td_last_heartbeat > timedelta(minutes=self._max_duration):
            self._call_subscribers(heartbeat=False)
        else:
            self._call_subscribers(heartbeat=True)
        self._schedule_next_check()

    def _schedule_next_check(self):
        """Schedule the next time we check for the heartbeat."""
        loop = asyncio.get_event_loop()
        next_test_time = self._last_heartbeat + timedelta(
            minutes=self._max_duration + 5
        )
        loop.call_at(next_test_time.timestamp(), self._check_heartbeat)
