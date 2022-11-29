"""Test the device_link_manager class."""
import asyncio
import os
import unittest
from random import randint
from unittest.mock import AsyncMock, Mock, patch

import pytest

import pyinsteon
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers.device_link_manager import DeviceLinkSchema
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


@pytest.fixture(autouse=True)
def devices_fixture():
    """Load the devices fixture."""
    with patch.object(pyinsteon, "devices", devices):
        yield


devices = DeviceManager()


def _add_rec_to_aldb(device, record):
    """Add a record to a device ALDB."""
    hwm = None
    for rec in device.aldb.find(target="000000"):
        hwm = rec
        break
    record.mem_addr = hwm.mem_addr
    hwm.mem_addr = hwm.mem_addr - 8
    records = {record.mem_addr: record, hwm.mem_addr: hwm}
    device.aldb.load_saved_records(device.aldb.status, records)


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

    @async_case
    async def test_save_load_scenes(self):
        """Test saving and loading scenes."""

        link_manager = devices.link_manager
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)
        for addr in devices:
            device = devices[addr]
            device.async_status = AsyncMock()
        link_manager = devices.link_manager

        dir_path = os.path.dirname(__file__)
        link_manager.set_scene_name(20, "My scene number 20")
        await link_manager.async_save_scene_names(dir_path)
        scene_file = os.path.join(dir_path, "insteon_scenes.json")
        assert os.path.exists(scene_file)

        await load_devices(devices)
        await link_manager.async_load_scene_names(dir_path)
        scene_20 = link_manager.get_scene(20)
        assert scene_20["name"] == "My scene number 20"

    @async_case
    async def test_add_scene(self):
        """Test adding a scene."""

        link_manager = devices.link_manager
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)

        assert len(link_manager.scenes) == 2

        scene_1 = randint(100, 255)
        scene_2 = randint(100, 255)
        scene_1_name = "Scene number 1 name"
        scene_2_name = "Scene number 1 name"
        devices_1_info = {}
        devices_2_info = {}
        devices_1_mod_info = {}

        responder_1 = devices["6f6f6f"].address
        responder_2 = devices["5e5e5e"].address
        responder_3 = devices["3c3c3c"].address
        _reset_devices([devices.modem.address, responder_1, responder_2, responder_3])

        device_1_data = {
            "address": responder_1.id,
            "data1": randint(0, 255),
            "data2": randint(0, 255),
            "data3": randint(0, 255),
        }
        device_2_data = {
            "address": responder_2.id,
            "data1": randint(0, 255),
            "data2": randint(0, 255),
            "data3": randint(0, 255),
        }
        device_3_data = {
            "address": responder_3.id,
            "data1": randint(0, 255),
            "data2": randint(0, 255),
            "data3": randint(0, 255),
        }
        devices_1_info = DeviceLinkSchema([device_1_data, device_2_data])
        devices_2_info = DeviceLinkSchema([device_3_data])
        devices_1_mod_info = DeviceLinkSchema([device_1_data, device_3_data])

        c_1_rec = ALDBRecord(
            memory=0,
            controller=True,
            group=scene_1,
            target=responder_1,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        c_2_rec = ALDBRecord(
            memory=0,
            controller=True,
            group=scene_1,
            target=responder_2,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_1_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=scene_1,
            target=devices.modem.address,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_2_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=scene_1,
            target=devices.modem.address,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_3_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=scene_2,
            target=devices.modem.address,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )

        # Add Scene 1
        await link_manager.async_add_or_update_scene(
            scene_1, devices_1_info, scene_1_name
        )
        assert len(devices.modem.aldb.pending_changes) == 2
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_1].aldb.pending_changes) == 1
        assert devices[responder_1].aldb.async_write.call_count == 1

        assert len(devices[responder_2].aldb.pending_changes) == 1
        assert devices[responder_2].aldb.async_write.call_count == 1

        # Simulate the scene 1 records being written
        _reset_devices([devices.modem.address, responder_1, responder_2])
        _add_rec_to_aldb(devices[responder_1], r_1_rec)
        _add_rec_to_aldb(devices[responder_2], r_2_rec)
        _add_rec_to_aldb(devices.modem, c_1_rec)
        await asyncio.sleep(0.5)
        assert len(link_manager.scenes) == 3
        scene = link_manager.get_scene(scene_1)
        assert scene["name"] == scene_1_name
        assert len(scene["devices"]) == 2

        # Add Scene 2
        await link_manager.async_add_or_update_scene(
            scene_2, devices_2_info, scene_2_name
        )
        assert len(devices.modem.aldb.pending_changes) == 1
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_3].aldb.pending_changes) == 1
        assert devices[responder_3].aldb.async_write.call_count == 1

        # Simulate the scene 2 records being written
        _reset_devices([devices.modem.address, responder_3])
        _add_rec_to_aldb(devices[responder_3], r_3_rec)
        _add_rec_to_aldb(devices.modem, c_2_rec)

        await asyncio.sleep(0.5)
        assert len(link_manager.scenes) == 4
        scene = link_manager.get_scene(scene_2)
        assert scene["name"] == scene_2_name
        assert len(scene["devices"]) == 1

        # Change Scene 1 - Add one device and remove another.
        _reset_devices([devices.modem.address, responder_1, responder_2, responder_3])

        await link_manager.async_add_or_update_scene(scene_1, devices_1_mod_info)

        # Removing 2 records and adding back 1
        assert len(devices.modem.aldb.pending_changes) == 3
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_1].aldb.pending_changes) == 2

        assert len(devices[responder_2].aldb.pending_changes) == 1
        assert devices[responder_2].aldb.async_write.call_count == 1

        assert len(devices[responder_3].aldb.pending_changes) == 1
        assert devices[responder_3].aldb.async_write.call_count == 1

        # Simulate the scene 1 modified records being written
        _reset_devices([devices.modem.address, responder_3])
        _add_rec_to_aldb(devices[responder_3], r_3_rec)
        _add_rec_to_aldb(devices.modem, c_2_rec)

        await asyncio.sleep(0.5)
        assert len(link_manager.scenes) == 4
        scene = link_manager.get_scene(scene_2)
        assert scene["name"] == scene_2_name
        assert len(scene["devices"]) == 1

    @async_case
    async def test_delete_scene(self):
        """Test deleting a scene."""

        link_manager = devices.link_manager
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)

        scene_num = randint(100, 255)
        scene_name = "Scene number 1 name"
        devices_info = {}

        responder_1 = devices["6f6f6f"].address
        responder_2 = devices["5e5e5e"].address
        responder_3 = devices["3c3c3c"].address
        _reset_devices([devices.modem.address, responder_1, responder_2, responder_3])

        device_1_data = {
            "address": responder_1.id,
            "data1": randint(0, 255),
            "data2": randint(0, 255),
            "data3": randint(0, 255),
        }
        device_2_data = {
            "address": responder_2.id,
            "data1": randint(0, 255),
            "data2": randint(0, 255),
            "data3": randint(0, 255),
        }
        devices_info = DeviceLinkSchema([device_1_data, device_2_data])

        c_1_rec = ALDBRecord(
            memory=0,
            controller=True,
            group=scene_num,
            target=responder_1,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_1_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=scene_num,
            target=devices.modem.address,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )

        c_2_rec = ALDBRecord(
            memory=0,
            controller=True,
            group=scene_num,
            target=responder_2,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )
        r_2_rec = ALDBRecord(
            memory=0,
            controller=False,
            group=scene_num,
            target=devices.modem.address,
            data1=0,
            data2=0,
            data3=0,
            in_use=True,
        )

        # Add Scene
        await link_manager.async_add_or_update_scene(
            scene_num, devices_info, scene_name
        )
        assert len(devices.modem.aldb.pending_changes) == 2
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_1].aldb.pending_changes) == 1
        assert devices[responder_1].aldb.async_write.call_count == 1

        assert len(devices[responder_2].aldb.pending_changes) == 1
        assert devices[responder_2].aldb.async_write.call_count == 1

        # Simulate the scene records being written
        _reset_devices([devices.modem.address, responder_1, responder_2])
        _add_rec_to_aldb(devices[responder_1], r_1_rec)
        _add_rec_to_aldb(devices[responder_2], r_2_rec)
        _add_rec_to_aldb(devices.modem, c_1_rec)
        _add_rec_to_aldb(devices.modem, c_2_rec)
        await asyncio.sleep(0.5)
        scene = link_manager.get_scene(scene_num)
        assert scene["name"] == scene_name
        assert len(scene["devices"]) == 2

        # Delete the scene
        await link_manager.async_delete_scene(scene_num)
        assert len(devices.modem.aldb.pending_changes) == 2
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_1].aldb.pending_changes) == 1
        assert devices[responder_1].aldb.async_write.call_count == 1

        assert len(devices[responder_2].aldb.pending_changes) == 1
        assert devices[responder_2].aldb.async_write.call_count == 1
