"""Test the device_link_manager class."""
import asyncio
from random import randint
import unittest
from unittest.mock import AsyncMock, Mock, patch

import pytest

import pyinsteon
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers.device_manager import DeviceManager
from pyinsteon.topics import ALDB_LINK_CHANGED

from tests import load_devices, set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


def _reset_devices(addresses):
    """Reset the device ALDB pending records."""
    for addr in addresses:
        device = devices[addr]
        device.aldb.clear_pending()
        device.aldb.async_write = AsyncMock()
        device.aldb.async_write.call_count = 0
        device.aldb.clear = Mock()


devices = DeviceManager()


@pytest.fixture(autouse=True)
def devices_fixture():
    """Load the devices fixture."""
    with patch.object(pyinsteon, "devices", devices):
        yield


class TestDeviceLinkManager(unittest.TestCase):
    """Test the DeviceLinkManager class."""

    def setUp(self) -> None:
        """Set up the tests."""
        set_log_levels(logger_topics=True)

    @async_case
    async def test_device_links(self):
        """Test device links."""

        link_manager = devices.link_manager
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)
        for addr in devices:
            device = devices[addr]
            device.async_status = AsyncMock()
        assert len(link_manager.links) == 2

        topic = "1a1a1a.1.on.all_link_broadcast"
        topic_item = TopicItem(topic, cmd_kwargs(0x11, 0xFF, None, "00.00.01"), 0)
        send_topics([topic_item])
        await asyncio.sleep(0.5)
        assert devices["3c3c3c"].async_status.call_count == 1

        controller = devices["1a1a1a"].address
        responder = devices["3c3c3c"].address
        link_data = devices.link_manager.links[controller][1][responder]
        assert link_data[0].data1 == 255
        assert link_data[0].data3 == 1

        # Test adding and removing links
        controller = devices["aaaaaa"].address
        responder_1 = devices["6f6f6f"].address
        responder_2 = devices["5e5e5e"].address
        controller_3 = devices["4d4d4d"].address
        responder_3 = devices["3c3c3c"].address

        group = randint(0, 255)
        c_topic = f"{controller.id}.{ALDB_LINK_CHANGED}"
        r_1_topic = f"{responder_1.id}.{ALDB_LINK_CHANGED}"
        r_2_topic = f"{responder_2.id}.{ALDB_LINK_CHANGED}"
        r_3_topic = f"{responder_3.id}.{ALDB_LINK_CHANGED}"
        c_rec = ALDBRecord(
            memory=0,
            controller=True,
            group=group,
            target=responder_1,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=group,
            target=controller,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_del_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=group,
            target=controller,
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
        )
        r_3_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=group,
            target=controller_3,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )

        # Create a controller record
        await asyncio.sleep(0.3)
        send_topics(
            [
                TopicItem(
                    c_topic,
                    {"record": c_rec, "sender": controller, "deleted": False},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1
        assert len(devices.link_manager.links[controller][group][responder_1]) == 1

        # Create corresponding responder record
        send_topics(
            [
                TopicItem(
                    r_1_topic,
                    {"record": r_rec, "sender": responder_1, "deleted": False},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1
        assert len(devices.link_manager.links[controller][group][responder_1]) == 1

        # Create second responder record
        send_topics(
            [
                TopicItem(
                    r_2_topic,
                    {"record": r_rec, "sender": responder_2, "deleted": False},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 3
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 2
        assert len(devices.link_manager.links[controller][group][responder_1]) == 1
        assert len(devices.link_manager.links[controller][group][responder_2]) == 1

        # Create new responder record with differnt controller
        send_topics(
            [
                TopicItem(
                    r_3_topic,
                    {"record": r_3_rec, "sender": responder_2, "deleted": False},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 4
        assert len(devices.link_manager.links[controller_3]) == 1
        assert len(devices.link_manager.links[controller_3][group]) == 1
        assert len(devices.link_manager.links[controller_3][group][responder_2]) == 1

        # Remove responder record
        send_topics(
            [
                TopicItem(
                    r_1_topic,
                    {"record": r_del_rec, "sender": responder_1, "deleted": True},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 4
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 2

        # Remove the corresponding controller record
        send_topics(
            [
                TopicItem(
                    c_topic,
                    {"record": c_rec, "sender": controller, "deleted": True},
                    0,
                )
            ]
        )
        await asyncio.sleep(0.1)
        assert len(devices.link_manager.links) == 4
        assert len(devices.link_manager.links[controller]) == 1
        assert len(devices.link_manager.links[controller][group]) == 1
