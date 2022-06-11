"""Manage the inbound messages that trigger a variable state's on level."""
from datetime import datetime, timedelta

from ..address import Address
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.off_all_link_cleanup import OffAllLinkCleanupInbound
from ..handlers.from_device.off_fast import OffFastInbound
from ..handlers.from_device.off_fast_all_link_cleanup import (
    OffFastAllLinkCleanupInbound,
)
from ..handlers.from_device.on_fast import OnFastInbound
from ..handlers.from_device.on_fast_all_link_cleanup import OnFastAllLinkCleanupInbound
from ..handlers.from_device.on_level import OnLevelInbound
from ..handlers.from_device.on_level_all_link_cleanup import OnAllLinkCleanupInbound
from ..subscriber_base import SubscriberBase

TIMEOUT_CLEANUP = timedelta(seconds=25)


class OnLevelManager:
    """Manage the inbound messages that trigger a variable state's on level.

    The manager is used in all variable state devices. These include:
        - Category 0 devices such as Mini-Remotes
        - All category 1 dimmable devices
        - All category 2 switch devices
        - etc

    This manager handles inbound broadcast messages that identify a state change of
    a device. It also handles inbound clean up messages that follow the broadcast
    message. Finally, it is responsible to deduplicate messages to ensure multiple
    broadcast and cleanup messages to the same group for the same state change
    only trigger once.
    """

    class Subscriber(SubscriberBase):
        """Internal class to trigger notification of events or state values."""

        def call_subscribers(self, on_level):
            """Call subscribers to this manager for the event type."""
            self._call_subscribers(on_level=on_level)

    def __init__(self, address, group, default_on_level=0xFF):
        """Init the OnLevelManager class."""
        self._address = Address(address)
        self._group = int(group)
        self._default_on_level = default_on_level
        self._last_event = datetime(1, 1, 1, 1, 1, 1)
        self._last_event_type = None

        # Setup event managers that will manange the subscribers to specific events
        self._on = self.Subscriber(
            f"subscriber_{self._address.id}_on_{self._group}_broadcast"
        )
        self._off = self.Subscriber(
            f"subscriber_{self._address.id}_off_{self._group}_broadcast"
        )
        self._on_fast = self.Subscriber(
            f"subscriber_{self._address.id}_on_fast_{self._group}_broadcast"
        )
        self._off_fast = self.Subscriber(
            f"subscriber_{self._address.id}_off_fast_{self._group}_broadcast"
        )

        # Register the handlers to listen to
        self._on_handler = OnLevelInbound(self._address, self._group)
        self._off_handler = OffInbound(self._address, self._group)
        self._on_fast_handler = OnFastInbound(self._address, self._group)
        self._off_fast_handler = OffFastInbound(self._address, self._group)
        self._on_cleanup_handler = OnAllLinkCleanupInbound(self._address, self._group)
        self._off_cleanup_handler = OffAllLinkCleanupInbound(self._address, self._group)
        self._on_fast_cleanup_handler = OnFastAllLinkCleanupInbound(
            self._address, self._group
        )
        self._off_fast_cleanup_handler = OffFastAllLinkCleanupInbound(
            self._address, self._group
        )

        # Subscribe to events
        self._on_handler.subscribe(self._on_event)
        self._off_handler.subscribe(self._off_event)
        self._on_fast_handler.subscribe(self._on_fast_event)
        self._off_fast_handler.subscribe(self._off_fast_event)
        self._on_cleanup_handler.subscribe(self._on_cleanup_event)
        self._off_cleanup_handler.subscribe(self._off_cleanup_event)
        self._on_fast_cleanup_handler.subscribe(self._on_fast_cleanup_event)
        self._off_fast_cleanup_handler.subscribe(self._off_fast_cleanup_event)

    def subscribe(self, callback):
        """Subscribe to all events (ON, OFF, ON FAST, OFF FAST)."""
        self._on.subscribe(callback)
        self._off.subscribe(callback)
        self._on_fast.subscribe(callback)
        self._off_fast.subscribe(callback)

    def subscribe_on(self, callback):
        """Subscribe to ON events."""
        self._on.subscribe(callback)

    def subscribe_off(self, callback):
        """Subscribe to OFF events."""
        self._off.subscribe(callback)

    def subscribe_on_fast(self, callback):
        """Subscribe to ON FAST events."""
        self._on_fast.subscribe(callback)

    def subscribe_off_fast(self, callback):
        """Subscribe to OFF FAST events."""
        self._off_fast.subscribe(callback)

    def _on_event(self, on_level):
        self._process_on_event(on_level=on_level)

    def _off_event(self, on_level):
        self._process_off_event()

    def _on_fast_event(self, on_level):
        self._process_on_fast_event(on_level=on_level)

    def _off_fast_event(self, on_level):
        self._process_off_fast_event()

    def _on_cleanup_event(self):
        self._process_on_event(on_level=self._default_on_level, is_cleanup=True)

    def _off_cleanup_event(self):
        self._process_off_event(is_cleanup=True)

    def _on_fast_cleanup_event(self):
        self._process_on_fast_event(on_level=self._default_on_level, is_cleanup=True)

    def _off_fast_cleanup_event(self):
        self._process_off_fast_event(is_cleanup=True)

    def _process_on_event(self, on_level, is_cleanup=False):
        if not is_cleanup or self._process_event("on"):
            self._on.call_subscribers(on_level=on_level)
            self._last_event = datetime.now()
            self._last_event_type = "on"

    def _process_off_event(self, is_cleanup=False):
        if not is_cleanup or self._process_event("off"):
            self._off.call_subscribers(on_level=0)
            self._last_event = datetime.now()
            self._last_event_type = "off"

    def _process_on_fast_event(self, on_level, is_cleanup=False):
        if not is_cleanup or self._process_event("on_fast"):
            self._on_fast.call_subscribers(on_level=on_level)
            self._last_event = datetime.now()
            self._last_event_type = "on_fast"

    def _process_off_fast_event(self, is_cleanup=False):
        if not is_cleanup or self._process_event("off_fast"):
            self._off_fast.call_subscribers(on_level=0)
            self._last_event = datetime.now()
            self._last_event_type = "off_fast"

    def _process_event(self, event_type):
        tdelta = datetime.now() - self._last_event
        if self._last_event_type == event_type and tdelta < TIMEOUT_CLEANUP:
            return False
        return True
