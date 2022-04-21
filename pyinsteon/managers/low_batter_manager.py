"""Low battery manager."""

import asyncio

from ..address import Address
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.on_level import OnLevelInbound
from ..subscriber_base import SubscriberBase
from ..utils import subscribe_topic

WAIT_TIME = 5


class LowBatteryManager(SubscriberBase):
    """Low battery manager."""

    class LowBatterySubscriber(SubscriberBase):
        """Low battery event subscriptions."""

        def call_subscribers(self, low_battery):
            """Call subscribers of this event."""
            self._call_subscribers(low_battery=low_battery)

    def __init__(self, address, group):
        """Init the LowBatteryManager class."""
        self._address = Address(address)
        self._group = group
        subscriber_topic = f"subscriber_{self._address.id}_low_battery"
        super().__init__(subscriber_topic)

        self._on_low_battery = OnLevelInbound(self._address, self._group)
        self._off_low_battery = OffInbound(self._address, self._group)
        self._on_low_battery.subscribe(self._low_battery)
        self._off_low_battery.subscribe(self._low_battery)
        self._low_battery_recd = False
        self._low_battery_state = False
        self._low_battery_event = self.LowBatterySubscriber(f"{subscriber_topic}.true")
        self._low_battery_clear_event = self.LowBatterySubscriber(
            f"{subscriber_topic}.false"
        )
        subscribe_topic(self._all_device_messages, self._address.id)

    def subscribe_low_battery_event(self, callback):
        """Subscribe to low battery event."""
        self._low_battery_event.subscribe(callback)

    def subscribe_low_battery_clear_event(self, callback):
        """Subscribe to low battery event."""
        self._low_battery_clear_event.subscribe(callback)

    def _all_device_messages(self, **kwargs):
        """Capture all messages for this device."""
        loop = asyncio.get_event_loop()
        target = kwargs.get("target")
        # stop if this is a low battery message
        if target and Address(target).low == self._group:
            return
        self._low_battery_recd = False
        loop.call_later(WAIT_TIME, self._check_low_battery)

    def _low_battery(self, on_level):
        """Low battery message received."""
        self._low_battery_recd = True
        self._low_battery_state = True
        self._low_battery_event.call_subscribers(low_battery=True)

    def _check_low_battery(self):
        """Check if a low battery message was received since the last message."""
        if not self._low_battery_recd and self._low_battery_state:
            self._low_battery_clear_event.call_subscribers(low_battery=False)
