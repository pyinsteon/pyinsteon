"""Heartbeat manager."""

from datetime import datetime, timedelta
import asyncio

from ..subscriber_base import SubscriberBase
from ..address import Address
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.on_level import OnLevelInbound

class HeartbeatManager(SubscriberBase):
    """Heartbeat manager."""

    def __init__(self, address, group, max_duration=1275):
        """Init the HeartbeatManager class."""
        self._address = Address(address)
        self._group = group
        self._max_duration = max_duration
        subscriber_topic = 'subscriber_{}_heartbeat'.format(self._address)
        super().__init__(subscriber_topic)

        self._on_hb = OnLevelInbound(self._address, self._group)
        self._off_hb = OffInbound(self._address, self._group)
        self._on_hb.subscribe(self._heartbeat_received)
        self._off_hb.subscribe(self._heartbeat_received)
        self._last_heartbeat = datetime.now() - timedelta(hours=12)
        self._schedule_next_check()

    def _heartbeat_received(self, on_level):
        """Listen for all messages from device."""
        self._last_heartbeat = datetime.now()

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
        next_test_time = self._last_heartbeat + timedelta(minutes=self._max_duration + 5)
        loop.call_at(next_test_time.timestamp(), self._check_heartbeat)
