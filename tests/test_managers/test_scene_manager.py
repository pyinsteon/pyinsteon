"""Test the device_link_manager class."""
import asyncio
import os
from random import randint
import unittest
from unittest.mock import AsyncMock, Mock, patch

import pytest

import pyinsteon
from pyinsteon import devices
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers.device_manager import DeviceManager
from pyinsteon.managers.scene_manager import (
    DeviceLinkSchema,
    async_add_or_update_scene,
    async_delete_scene,
    async_get_scene,
    async_get_scenes,
    async_load_scene_names,
    async_save_scene_names,
    set_scene_name,
)

from tests import load_devices, set_log_levels
from tests.utils import async_case

PWD = os.path.dirname(__file__)


def _reset_devices(addresses):
    """Reset the device ALDB pending records."""
    for addr in addresses:
        device = devices[addr]
        device.aldb.clear_pending()
        device.aldb.async_write = AsyncMock(return_value=(0, 0))
        device.aldb.async_write.call_count = 0
        device.aldb.clear = Mock()


@pytest.fixture(autouse=True)
def devices_fixture():
    """Load the devices fixture."""
    patched_devices = DeviceManager()
    with patch.object(pyinsteon, "devices", patched_devices):
        yield


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
    async def test_save_load_scenes(self):
        """Test saving and loading scenes."""

        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)
        for addr in devices:
            device = devices[addr]
            device.async_status = AsyncMock()

        set_scene_name(20, "My scene number 20")
        await async_save_scene_names(PWD)
        scene_file = os.path.join(PWD, "insteon_scenes.json")
        assert os.path.exists(scene_file)

        await load_devices(devices)
        await async_load_scene_names(PWD)
        scene_20 = await async_get_scene(20)
        assert scene_20["name"] == "My scene number 20"

    @async_case
    async def test_add_scene(self):
        """Test adding a scene."""

        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(1)

        scenes = await async_get_scenes()
        assert len(scenes) == 2

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
        await async_add_or_update_scene(scene_1, devices_1_info, scene_1_name)
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
        scenes = await async_get_scenes()
        assert len(scenes) == 3
        scene = await async_get_scene(scene_1)
        assert scene["name"] == scene_1_name
        assert len(scene["devices"]) == 2

        # Add Scene 2
        await async_add_or_update_scene(scene_2, devices_2_info, scene_2_name)
        assert len(devices.modem.aldb.pending_changes) == 1
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_3].aldb.pending_changes) == 1
        assert devices[responder_3].aldb.async_write.call_count == 1

        # Simulate the scene 2 records being written
        _reset_devices([devices.modem.address, responder_3])
        _add_rec_to_aldb(devices[responder_3], r_3_rec)
        _add_rec_to_aldb(devices.modem, c_2_rec)

        await asyncio.sleep(0.5)
        scenes = await async_get_scenes()
        assert len(scenes) == 4
        scene = await async_get_scene(scene_2)
        assert scene["name"] == scene_2_name
        assert len(scene["devices"]) == 1

        # Change Scene 1 - Add one device and remove another.
        _reset_devices([devices.modem.address, responder_1, responder_2, responder_3])

        await async_add_or_update_scene(scene_1, devices_1_mod_info)

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
        scenes = await async_get_scenes()
        assert len(scenes) == 4
        scene = await async_get_scene(scene_2)
        assert scene["name"] == scene_2_name
        assert len(scene["devices"]) == 1

    @async_case
    async def test_delete_scene(self):
        """Test deleting a scene."""

        modem = Hub("111111", 0x03, 51, 165, "Insteon modem")
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
        await async_add_or_update_scene(scene_num, devices_info, scene_name)
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
        scene = await async_get_scene(scene_num)
        assert scene["name"] == scene_name
        assert len(scene["devices"]) == 2

        # Delete the scene
        await async_delete_scene(scene_num, PWD)
        assert len(devices.modem.aldb.pending_changes) == 2
        assert devices.modem.aldb.async_write.call_count == 1

        assert len(devices[responder_1].aldb.pending_changes) == 1
        assert devices[responder_1].aldb.async_write.call_count == 1

        assert len(devices[responder_2].aldb.pending_changes) == 1
        assert devices[responder_2].aldb.async_write.call_count == 1
