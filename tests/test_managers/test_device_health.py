"""Test device health tracking and maintenance backoff."""

import unittest
from unittest.mock import patch

from pyinsteon.managers.device_health import (
    BACKOFF_BASE,
    BACKOFF_MAX,
    FAILURE_BURST,
    DeviceHealth,
    get_health,
)


class TestDeviceHealth(unittest.TestCase):
    """Test the DeviceHealth backoff behavior."""

    def test_fresh_device_allows_maintenance(self):
        """A device with no history is always allowed."""
        health = DeviceHealth()
        assert health.can_attempt_maintenance()

    def test_burst_failures_do_not_back_off(self):
        """Failures inside the burst allowance do not delay maintenance."""
        health = DeviceHealth()
        for _ in range(FAILURE_BURST - 1):
            health.record_failure()
        assert health.can_attempt_maintenance()

    def test_backoff_engages_after_burst(self):
        """Failures beyond the burst set a future maintenance time."""
        health = DeviceHealth()
        for _ in range(FAILURE_BURST):
            health.record_failure()
        assert not health.can_attempt_maintenance()

    def test_backoff_grows_and_caps(self):
        """Backoff grows exponentially and respects the cap."""
        health = DeviceHealth()
        with patch("pyinsteon.managers.device_health.time") as mock_time:
            mock_time.monotonic.return_value = 1000.0
            mock_time.time.return_value = 1000.0
            for _ in range(FAILURE_BURST + 20):
                health.record_failure()
            delay = health.next_maintenance - 1000.0
            assert delay <= BACKOFF_MAX * 1.25
            assert delay >= BACKOFF_MAX * 0.75

    def test_first_backoff_near_base(self):
        """The first post-burst backoff is near the base delay."""
        health = DeviceHealth()
        with patch("pyinsteon.managers.device_health.time") as mock_time:
            mock_time.monotonic.return_value = 1000.0
            mock_time.time.return_value = 1000.0
            for _ in range(FAILURE_BURST):
                health.record_failure()
            delay = health.next_maintenance - 1000.0
            assert BACKOFF_BASE * 0.75 <= delay <= BACKOFF_BASE * 1.25

    def test_heard_does_not_clear_backoff(self):
        """An inbound frame proves liveness but does not clear backoff.

        Devices can ACK every request and never deliver data, so only a
        completed operation or timer expiry reopens maintenance.
        """
        health = DeviceHealth()
        for _ in range(FAILURE_BURST + 2):
            health.record_failure()
        assert not health.can_attempt_maintenance()
        health.heard()
        assert not health.can_attempt_maintenance()
        assert health.consecutive_failures == FAILURE_BURST + 2
        assert health.last_heard is not None

    def test_success_resets_everything(self):
        """A command success resets failures and backoff."""
        health = DeviceHealth()
        for _ in range(FAILURE_BURST + 2):
            health.record_failure()
        health.record_success()
        assert health.consecutive_failures == 0
        assert health.can_attempt_maintenance()

    def test_registry_returns_same_instance(self):
        """The registry returns one instance per address."""
        h1 = get_health("aa.bb.cc")
        h2 = get_health("AABBCC")
        assert h1 is h2

    def test_backoff_never_exceeds_the_cap(self):
        """Jitter is applied inside the cap, never on top of it."""
        health = DeviceHealth()
        with patch("pyinsteon.managers.device_health.time") as mock_time, patch(
            "pyinsteon.managers.device_health.random"
        ) as mock_random:
            mock_time.monotonic.return_value = 1000.0
            mock_time.time.return_value = 1000.0
            mock_random.random.return_value = 1.0
            for _ in range(FAILURE_BURST + 20):
                health.record_failure()
            assert health.next_maintenance - 1000.0 <= BACKOFF_MAX

    def test_expired_backoff_lets_one_more_operation_through(self):
        """A device far past the failure bar still gets a probe each window.

        Without this a device that hit the bar could never record a success
        because every operation aborts before it sends anything.
        """
        health = DeviceHealth()
        with patch("pyinsteon.managers.device_health.time") as mock_time:
            mock_time.monotonic.return_value = 1000.0
            mock_time.time.return_value = 1000.0
            for _ in range(FAILURE_BURST * 4 + 3):
                health.record_failure()
            assert not health.can_continue_operation()
            mock_time.monotonic.return_value = 1000.0 + BACKOFF_MAX * 2
            assert health.can_attempt_maintenance()
            assert health.can_continue_operation()
            health.record_failure()
            assert not health.can_continue_operation()


if __name__ == "__main__":
    unittest.main()
