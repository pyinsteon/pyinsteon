"""Track per-device reachability and gate maintenance traffic.

Interactive commands always send. Maintenance traffic (ALDB loads, device
ID requests, status polls) backs off after repeated operation failures so
a dead or data-silent device cannot monopolize the powerline. Transport
ACKs only prove liveness; completed operations reset the failure count and
exhausted operations increment it.
"""

import random
import time

from ..address import Address

FAILURE_BURST = 3
BACKOFF_BASE = 60
BACKOFF_MAX = 3600


class DeviceHealth:
    """Reachability state for one device."""

    def __init__(self):
        """Init the DeviceHealth class."""
        self.last_heard = None
        self.consecutive_failures = 0
        self._next_maintenance = 0.0

    @property
    def next_maintenance(self) -> float:
        """Return the monotonic time maintenance may next be attempted."""
        return self._next_maintenance

    def heard(self):
        """Record an inbound frame from the device.

        Hearing a device proves it is alive but not that operations against
        it complete; devices can ACK every request and never deliver data.
        Backoff clears only on operation success or timer expiry.
        """
        self.last_heard = time.time()

    def record_success(self):
        """Record a successful command round trip."""
        self.consecutive_failures = 0
        self._next_maintenance = 0.0
        self.last_heard = time.time()

    def record_failure(self):
        """Record a failed command and extend the backoff window."""
        self.consecutive_failures += 1
        over = self.consecutive_failures - FAILURE_BURST
        if over >= 0:
            delay = min(BACKOFF_MAX, BACKOFF_BASE * 2**over)
            delay *= 0.75 + random.random() * 0.5
            self._next_maintenance = time.monotonic() + delay

    def can_attempt_maintenance(self) -> bool:
        """Return True if maintenance traffic may be sent now."""
        return time.monotonic() >= self._next_maintenance


_HEALTH = {}


def get_health(address) -> DeviceHealth:
    """Return the DeviceHealth record for an address."""
    addr = Address(address).id
    health = _HEALTH.get(addr)
    if health is None:
        health = DeviceHealth()
        _HEALTH[addr] = health
    return health
