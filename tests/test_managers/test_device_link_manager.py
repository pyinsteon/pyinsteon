"""Test the device_link_manager class."""
import asyncio
import unittest
from unittest.mock import AsyncMock

from pyinsteon import devices, link_manager
from pyinsteon.device_types.hub import Hub

# from pyinsteon.topics import (
#     DEVICE_LINK_CONTROLLER_CREATED,
#     DEVICE_LINK_CONTROLLER_REMOVED,
#     DEVICE_LINK_RESPONDER_CREATED,
#     DEVICE_LINK_RESPONDER_REMOVED,
# )
from tests import load_devices, set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


class TestDeviceLinkManager(unittest.TestCase):
    """Test the DeviceLinkManager class."""

    def setUp(self) -> None:
        """Set up the tests."""
        set_log_levels(logger_topics=True)

    @async_case
    async def test_device_links(self):
        """Test device links."""
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices()
        assert len(devices) == 8
        for addr in devices:
            device = devices[addr]
            device.async_status = AsyncMock()
        assert len(link_manager.scenes) == 2
        assert len(link_manager.links) == 2

        topic = "1a1a1a.1.on.all_link_broadcast"
        topic_item = TopicItem(topic, cmd_kwargs(0x11, 0xFF, None, "00.00.01"), 0.1)
        send_topics([topic_item])
        await asyncio.sleep(0.2)
        assert devices["3c3c3c"].async_status.call_count == 1
