"""Replay heartbeat broadcasts, including the firmware 71 OFF_FAST variant."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from pyinsteon import pub
from pyinsteon.managers import heartbeat_manager
from pyinsteon.protocol.messages.inbound import create
from pyinsteon.protocol.msg_to_topic import convert_to_topic

from tests.utils import async_case


def replay_heartbeat(command, address="112233", group=4):
    """Decode and dispatch a PLM standard-message frame without hardware."""
    # All-link broadcast, three hops left; cmd2=0x60 from issue #452.
    frame = bytearray.fromhex(f"0250{address}0000{group:02x}cf{command:02x}60")
    message, remaining = create(frame)
    assert not remaining
    for topic, kwargs in convert_to_topic(message):
        pub.sendMessage(topic, **kwargs)


@pytest.mark.parametrize(
    "command,on_level", [(0x11, 255), (0x13, 0), (0x12, 255), (0x14, 0)]
)
@async_case
async def test_heartbeat_broadcast_recovers_and_expires(command, on_level):
    """Normal and fast messages clear an expired warning and retain polarity."""
    start = datetime(2026, 1, 1)
    address = f"1122{command:02x}"
    states, on_events, off_events = [], [], []

    def state_changed(heartbeat):
        states.append(heartbeat)

    def on_received(on_level):
        on_events.append(on_level)

    def off_received(on_level):
        off_events.append(on_level)

    with patch.object(heartbeat_manager, "datetime", wraps=datetime) as clock:
        with patch.object(asyncio.get_running_loop(), "call_later") as schedule:
            clock.now.return_value = start
            manager = heartbeat_manager.HeartbeatManager(address, 4, max_duration=1)
            manager.subscribe(state_changed)
            manager.subscribe_on(on_received)
            manager.subscribe_off(off_received)
            try:
                clock.now.return_value = start + timedelta(minutes=2)
                manager._check_heartbeat()
                assert states == [True]
                replay_heartbeat(command, address)
                assert states == [True, False]
                assert manager._last_heartbeat == clock.now.return_value
                assert on_events == ([255] if on_level else [])
                assert off_events == ([] if on_level else [0])

                clock.now.return_value += timedelta(seconds=30)
                manager._check_heartbeat()
                assert states[-1] is False
                schedule.assert_called_with(
                    30 + heartbeat_manager.HB_CHECK_BUFFER,
                    manager._check_heartbeat,
                )
                clock.now.return_value += timedelta(seconds=31)
                manager._check_heartbeat()
                assert states[-1] is True
            finally:
                manager.unsubscribe(state_changed)
                manager._on_hb.unsubscribe(on_received)
                manager._off_hb.unsubscribe(off_received)


@pytest.mark.parametrize("address,group", [("445566", 4), ("112233", 3)])
@async_case
async def test_unrelated_fast_message_is_not_a_heartbeat(address, group):
    """A different device or group must not reset the monitored sensor."""
    with patch.object(asyncio.get_running_loop(), "call_later"):
        manager = heartbeat_manager.HeartbeatManager("112233", 4)
        original = manager._last_heartbeat
        replay_heartbeat(0x14, address, group)
        assert manager._last_heartbeat == original
