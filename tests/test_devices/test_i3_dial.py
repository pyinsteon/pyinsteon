"""Test the dial for the ON_AT_RAMP_RATE_INBOUND message."""

import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.device_types.dimmable_lighting_control import (
    DimmableLightingControl_Dial,
)

from tests import set_log_levels
from tests.utils import (
    DataItem,
    TopicItem,
    async_case,
    async_protocol_manager,
    cmd_kwargs,
    create_std_ext_msg,
    random_address,
    send_data,
    send_topics,
)


class TestI3Dial(unittest.TestCase):
    """Test creation of all devices."""

    def setUp(self) -> None:
        """Set up the test."""
        set_log_levels(logger_topics=True)
        return super().setUp()

    @async_case
    async def test_on_off_at_ramp_rate(self):
        """Test the i3 Dial for On/Off at ramp rate."""
        address = random_address()
        target = random_address()
        device = DimmableLightingControl_Dial(address, 0x01, 0x57, 0x00, "Dial", "PD01")

        on_levels = {
            0x0D: 15,
            0x1D: 31,
            0x2D: 47,
            0x3D: 63,
            0x4D: 79,
            0x5D: 95,
            0x6D: 111,
            0x7D: 127,
            0x8D: 143,
            0x9D: 159,
            0xAD: 175,
            0xBD: 191,
            0xCD: 207,
            0xDD: 223,
            0xED: 239,
            0xFD: 255,
        }
        for cmd2, on_level in on_levels.items():
            kwargs = cmd_kwargs(0x34, cmd2, None, target=target)
            send_topics(
                [
                    TopicItem(
                        topic=f"{address.id}.1.on_at_ramp_rate_inbound.all_link_broadcast",
                        kwargs=kwargs,
                        delay=0.01,
                    )
                ]
            )
            await asyncio.sleep(0.7)
            assert device.groups[1].value == on_level

    @async_case
    async def test_on_off_at_ramp_rate_fast(self):
        """Test the i3 Dial for On/Off at ramp rate."""
        address = random_address()
        target = Address("000001")
        device = DimmableLightingControl_Dial(address, 0x01, 0x57, 0x00, "Dial", "PD01")

        on_levels = {
            0x0D: 15,
            0x1D: 31,
            0x2D: 47,
            0x3D: 63,
            0x4D: 79,
            0x5D: 95,
            0x6D: 111,
            0x7D: 127,
            0x8D: 143,
            0x9D: 159,
            0xAD: 175,
            0xBD: 191,
            0xCD: 207,
            0xDD: 223,
            0xED: 239,
            0xFD: 255,
        }
        data = []
        async with async_protocol_manager() as protocol:
            for cmd2 in on_levels:
                msg = create_std_ext_msg(address, 0xC7, 0x34, cmd2, None, target, None)
                data.append(DataItem(msg, 0.1))
            send_data(data, protocol.read_queue)
            await asyncio.sleep(0.8 * len(on_levels) + 1)
            assert device.groups[1].value == 255
