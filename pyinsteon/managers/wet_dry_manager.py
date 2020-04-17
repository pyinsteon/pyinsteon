"""Manage wet / dry state of the leak sensor."""
from typing import Callable

from ..address import Address
from ..handlers.from_device.on_level import OnLevelInbound
from ..subscriber_base import SubscriberBase


class WetDryManager(SubscriberBase):
    """Manage the wet / dry state of a leak sensor."""

    class WetDryEvent(SubscriberBase):
        """Wet or dry events."""

        def call_subscribers(self, dry):
            """Call subscribers of wet/dry events."""
            self._call_subscribers(dry=dry)

    def __init__(self, address, dry_group=1, wet_group=2):
        """Init the WetDryManager."""
        self._address = Address(address)
        self._wet_group = wet_group
        self._dry_group = dry_group
        subscriber_topic = "subscriber_{}_wet_dry".format(self._address.id)
        super().__init__(subscriber_topic)

        self._dry_handler = OnLevelInbound(self._address, self._dry_group)
        self._dry_events = self.WetDryEvent("{}_dry".format(subscriber_topic))
        self._dry_handler.subscribe(self._dry)

        self._wet_handler = OnLevelInbound(self._address, self._wet_group)
        self._wet_events = self.WetDryEvent("{}_wet".format(subscriber_topic))
        self._wet_handler.subscribe(self._wet)

    def subscribe(self, callback: Callable, force_strong_ref=False):
        """Subscribe to the event."""
        if force_strong_ref and callback not in self._subscribers:
            self._subscribers.append(callback)
        self.subscribe_wet(callback)
        self.subscribe_dry(callback)

    def subscribe_dry(self, callback):
        """Subscribe to dry events."""
        self._dry_events.subscribe(callback)

    def subscribe_wet(self, callback):
        """Subscribe to wet events."""
        self._wet_events.subscribe(callback)

    def _dry(self, on_level):
        """Dry event received."""
        self._dry_events.call_subscribers(dry=True)

    def _wet(self, on_level):
        """Dry event received."""
        self._wet_events.call_subscribers(dry=False)
