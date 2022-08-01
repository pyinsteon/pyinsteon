"""Test the device_link_manager class."""
import asyncio
import unittest
from random import randint
from unittest.mock import AsyncMock

from pyinsteon import pub
from pyinsteon.managers.device_manager import DeviceManager
from pyinsteon.topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from tests import load_devices, set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics


class TestDeviceLinkManager(unittest.TestCase):
    """Test the DeviceLinkManager class."""

    def setUp(self) -> None:
        """Set up the tests."""
        set_log_levels(logger_topics=True)

    @async_case
    async def test_device_links(self):
        """Test device links."""

        devices = DeviceManager()
        link_manager = devices.link_manager
        await load_devices(devices)
        assert len(devices) == 8
        for addr in devices:
            device = devices[addr]
            device.async_status = AsyncMock()
        assert len(link_manager.scenes) == 2
        print(link_manager.links)
        assert len(link_manager.links) == 2

        topic = "1a1a1a.1.on.all_link_broadcast"
        topic_item = TopicItem(topic, cmd_kwargs(0x11, 0xFF, None, "00.00.01"), 0)
        send_topics([topic_item])
        await asyncio.sleep(0.5)
        assert devices["3c3c3c"].async_status.call_count == 1

        controller = devices["1a1a1a"].address
        responder = devices["3c3c3c"].address
        link_data = devices.link_manager.links[controller][1][responder]
        assert link_data.data1 == 255
        assert link_data.data3 == 1

        # Test adding and removing links
        controller = random_address()
        responder_1 = random_address()
        responder_2 = random_address()
        controller_3 = random_address()
        responder_3 = random_address()
        group = randint(0, 255)
        add_c_topic = f"{DEVICE_LINK_CONTROLLER_CREATED}.{controller.id}"
        add_r_1_topic = f"{DEVICE_LINK_RESPONDER_CREATED}.{responder_1.id}"
        rem_r_1_topic = f"{DEVICE_LINK_RESPONDER_REMOVED}.{responder_1.id}"
        add_r_2_topic = f"{DEVICE_LINK_RESPONDER_CREATED}.{responder_2.id}"
        add_r_3_topic = f"{DEVICE_LINK_RESPONDER_CREATED}.{responder_3.id}"

        # Create a controller record
        send_topics(
            [
                TopicItem(
                    add_c_topic,
                    {
                        "controller": controller,
                        "responder": responder_1,
                        "group": group,
                    },
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1

        # Create corresponding responder record
        send_topics(
            [
                TopicItem(
                    add_r_1_topic,
                    {
                        "controller": controller,
                        "responder": responder_1,
                        "group": group,
                    },
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1

        # Create second responder record
        send_topics(
            [
                TopicItem(
                    add_r_2_topic,
                    {
                        "controller": controller,
                        "responder": responder_2,
                        "group": group,
                    },
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 2

        # Create new responder record with differnt controller
        send_topics(
            [
                TopicItem(
                    add_r_3_topic,
                    {
                        "controller": controller_3,
                        "responder": responder_3,
                        "group": group,
                    },
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 4
        assert len(devices.link_manager.links[controller_3]) == 1
        assert len(devices.link_manager.links[controller_3][group]) == 1

        # Remove responder record
        pub.sendMessage(
            rem_r_1_topic,
            **{"controller": controller, "responder": responder_1, "group": group},
        )
        assert len(devices.link_manager.links) == 4
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1
