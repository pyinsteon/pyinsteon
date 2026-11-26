"""Check contact events against the documented default sensor messages."""

import pytest

from pyinsteon import pub
from pyinsteon.device_types.open_close_controller_base import (
    NormallyClosedControllerBase,
)
from pyinsteon.device_types.security_health_safety import (
    SecurityHealthSafety_OpenCloseSensor,
)
from pyinsteon.events import CLOSE_EVENT, OPEN_EVENT
from pyinsteon.protocol.messages.inbound import create
from pyinsteon.protocol.msg_to_topic import convert_to_topic

from tests.utils import async_case


@pytest.mark.parametrize("normally_open", [True, False])
@pytest.mark.parametrize("command", [0x11, 0x13])
@async_case
async def test_contact_event_polarity(normally_open, command):
    """ON means open for the default sensor; normally-closed wiring is inverted."""
    address = f"ab{int(normally_open):02x}{command:02x}"
    device_type = (
        SecurityHealthSafety_OpenCloseSensor
        if normally_open
        else NormallyClosedControllerBase
    )
    device = device_type(address, 0x10, 0x02)
    received = []

    def event_received(name, address, group, button):
        received.append((name, address, group))

    for event in device.events[1].values():
        event.subscribe(event_received)
    try:
        frame = bytearray.fromhex(f"0250{address}000001cf{command:02x}ff")
        message, remaining = create(frame)
        assert not remaining
        for topic, kwargs in convert_to_topic(message):
            pub.sendMessage(topic, **kwargs)
        opened = (command == 0x11) == normally_open
        assert received == [(OPEN_EVENT if opened else CLOSE_EVENT, address, 1)]
        assert device.groups[1].value == (255 if opened else 0)
    finally:
        for event in device.events[1].values():
            event.unsubscribe(event_received)
