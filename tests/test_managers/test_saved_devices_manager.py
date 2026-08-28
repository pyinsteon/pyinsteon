"""Test saving and restoring devices from the device cache file."""

import json
import os
import tempfile
import unittest

from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus, EngineVersion
from pyinsteon.managers.device_id_manager import DeviceId
from pyinsteon.managers.saved_devices_manager import (
    DEVICE_INFO_FILE,
    SavedDeviceManager,
)
from pyinsteon.managers.utils import create_device

from tests.utils import async_case, random_address


class _Modem:
    """Stand-in modem carrying only an address."""

    def __init__(self):
        """Init the _Modem class."""
        self.address = random_address()


def _records(target):
    recs = [
        ALDBRecord(
            0x0FFF,
            controller=True,
            group=1,
            target=target,
            data1=0,
            data2=0,
            data3=0,
        ),
        ALDBRecord(
            0x0FF7,
            controller=False,
            group=0,
            target="000000",
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
            high_water_mark=True,
        ),
    ]
    return {rec.mem_addr: rec for rec in recs}


class TestSavedDevicesManager(unittest.TestCase):
    """Test the SavedDeviceManager file handling."""

    @async_case
    async def test_save_and_load_round_trip(self):
        """A saved device list is written atomically and loads back."""
        address = random_address()
        device = create_device(DeviceId(address, 0x02, 0x0A, 0x44))
        device.engine_version = EngineVersion.I2
        device.aldb.load_saved_records(ALDBStatus.LOADED, _records(random_address()))
        with tempfile.TemporaryDirectory() as workdir:
            mgr = SavedDeviceManager(workdir, _Modem())
            await mgr.async_save({address: device})

            device_file = os.path.join(workdir, DEVICE_INFO_FILE)
            assert os.path.exists(device_file)
            assert not os.path.exists(f"{device_file}.tmp")
            with open(device_file, encoding="utf-8") as afp:
                saved = json.load(afp)
            assert len(saved) == 1
            assert saved[0]["address"] == address.id
            assert saved[0]["aldb_status"] == ALDBStatus.LOADED.value

            loaded = await SavedDeviceManager(workdir, _Modem()).async_load()
            assert len(loaded) == 1
            assert loaded[address].aldb.status == ALDBStatus.LOADED
            assert len(loaded[address].aldb) == 2

    @async_case
    async def test_corrupt_device_file_is_kept_aside(self):
        """A corrupt device file is moved aside and logged as an error."""
        with tempfile.TemporaryDirectory() as workdir:
            device_file = os.path.join(workdir, DEVICE_INFO_FILE)
            with open(device_file, "w", encoding="utf-8") as afp:
                afp.write('{"unterminated": ')
            mgr = SavedDeviceManager(workdir, _Modem())
            with self.assertLogs(
                "pyinsteon.managers.saved_devices_manager", level="ERROR"
            ):
                loaded = await mgr.async_load()
            assert loaded == {}
            assert not os.path.exists(device_file)
            with open(f"{device_file}.corrupt", encoding="utf-8") as afp:
                assert afp.read() == '{"unterminated": '


if __name__ == "__main__":
    unittest.main()
