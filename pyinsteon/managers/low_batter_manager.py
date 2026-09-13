"""Low battery manager."""

from ..address import Address
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.on_level import OnLevelInbound
from ..subscriber_base import SubscriberBase


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
        self._off_low_battery.subscribe(self._low_battery_clear)
        self._low_battery_state = False
        self._low_battery_event = self.LowBatterySubscriber(f"{subscriber_topic}.true")
        self._low_battery_clear_event = self.LowBatterySubscriber(
            f"{subscriber_topic}.false"
        )

    def subscribe_low_battery_event(self, callback):
        """Subscribe to low battery event."""
        self._low_battery_event.subscribe(callback)

    def subscribe_low_battery_clear_event(self, callback):
        """Subscribe to low battery clear event."""
        self._low_battery_clear_event.subscribe(callback)

    def _low_battery(self, on_level):
        """Low battery message received."""
        self._low_battery_state = True
        self._low_battery_event.call_subscribers(low_battery=True)

    def _low_battery_clear(self, on_level):
        """Good battery message received."""
        self._low_battery_state = False
        self._low_battery_clear_event.call_subscribers(low_battery=False)
