"""Test logical scenes backed by distinct controller/group pairs."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from pubsub.core import Publisher
import pytest

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.config import ON_LEVEL, RAMP_RATE
from pyinsteon.constants import ALDBStatus, ResponseStatus
from pyinsteon.device_types.dimmable_lighting_control import (
    DimmableLightingControl_KeypadLinc_6,
    DimmableLightingControl_SwitchLinc01,
)
from pyinsteon.device_types.general_controller import GeneralController_MiniRemote_8
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers import (
    scene_controller_manager as controllers,
    scene_manager as scenes,
)
from pyinsteon.managers.device_link_manager import DeviceLinkManager
from pyinsteon.managers.device_manager import DeviceManager

from tests.utils import async_case

MODEM = "111111"
KEYPAD = "222222"
REMOTE = "333333"
LIGHT = "444444"
OTHER = "555555"
REMOTE_2 = "666666"
OLD_MODEM = "777777"
LINKS = [{"address": LIGHT, "data1": 128, "data2": 28, "data3": 1}]
CONTROLLERS = [{"address": KEYPAD, "group": 3}, {"address": REMOTE, "group": 1}]


@pytest.fixture
def scene_devices(monkeypatch):
    """Build isolated devices with real ALDBs and successful transport writes."""
    publisher = Publisher()
    monkeypatch.setattr(pub, "_publisher", publisher)
    monkeypatch.setattr(pub, "_topicMgr", publisher.getTopicMgr())
    for method in ("subscribe", "unsubscribe", "unsubAll", "sendMessage"):
        monkeypatch.setattr(pub, method, getattr(publisher, method))
    controllers._scenes.clear()
    scenes._scene_names.clear()
    monkeypatch.setattr(scenes, "_scene_lock", asyncio.Lock())
    monkeypatch.setattr(controllers, "_state_lock", asyncio.Lock())

    def build():
        devices = DeviceManager()
        devices.modem = Hub(MODEM, 3, 51, 165)
        for device in (
            DimmableLightingControl_KeypadLinc_6(KEYPAD, 1, 9),
            GeneralController_MiniRemote_8(REMOTE, 0, 0x1B),
            DimmableLightingControl_SwitchLinc01(LIGHT, 1, 1),
            DimmableLightingControl_KeypadLinc_6(OTHER, 1, 9),
            GeneralController_MiniRemote_8(REMOTE_2, 0, 0x1B),
        ):
            devices._devices[device.address] = device
        for address in devices:
            devices[address].async_keep_awake = AsyncMock(
                return_value=ResponseStatus.SUCCESS
            )
            aldb = devices[address].aldb
            hwm = ALDBRecord(
                aldb.first_mem_addr,
                controller=False,
                group=0,
                target="000000",
                data1=0,
                data2=0,
                data3=0,
                in_use=False,
                high_water_mark=True,
            )
            aldb.load_saved_records(ALDBStatus.LOADED, {hwm.mem_addr: hwm})
            aldb._write_manager.async_write = AsyncMock(
                return_value=ResponseStatus.SUCCESS
            )
            # Keypad buttons have been read and do not set other buttons.
            for name, prop in devices[address].properties.items():
                if name.startswith(("on_mask", "off_mask")):
                    prop.set_value(0)
        monkeypatch.setattr(controllers, "devices", devices)
        monkeypatch.setattr(scenes, "devices", devices)
        return devices

    yield build
    controllers._scenes.clear()
    scenes._scene_names.clear()


def active(device, **criteria):
    """Return active records matching the requested criteria."""
    return list(device.aldb.find(in_use=True, **criteria))


@async_case
async def test_distinct_groups_and_idempotency(scene_devices, tmp_path):
    """A single logical scene uses each hardware button's own group."""
    devices = scene_devices()
    scene_num, result = await scenes.async_add_or_update_scene(
        -1, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    assert (scene_num, result) == (20, ResponseStatus.SUCCESS)
    for address, group in ((MODEM, 20), (KEYPAD, 3), (REMOTE, 1)):
        records = active(
            devices[LIGHT], target=address, group=group, is_controller=False
        )
        assert len(records) == 1
        assert (records[0].data1, records[0].data2, records[0].data3) == (128, 28, 1)
        assert (
            len(active(devices[address], target=LIGHT, group=group, is_controller=True))
            == 1
        )
    assert set(await scenes.async_get_scenes(str(tmp_path))) == {20}
    scene = await scenes.async_get_scene(20, str(tmp_path))
    assert scene["controllers"] == CONTROLLERS
    assert len(scene["devices"][Address(LIGHT)]) == 1
    assert not scene["pending"]
    counts = {addr: len(devices[addr].aldb) for addr in devices}
    writes = {
        addr: devices[addr].aldb._write_manager.async_write.call_count
        for addr in devices
    }
    await scenes.async_add_or_update_scene(20, LINKS, work_dir=str(tmp_path))
    assert {addr: len(devices[addr].aldb) for addr in devices} == counts
    assert {
        addr: devices[addr].aldb._write_manager.async_write.call_count
        for addr in devices
    } == writes


@async_case
async def test_synchronized_edits_and_targeted_delete(scene_devices, tmp_path):
    """Update all associated groups without touching another controller's group 3."""
    devices = scene_devices()
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    devices[OTHER].aldb.add(group=3, target=LIGHT, controller=True)
    devices[LIGHT].aldb.add(group=3, target=OTHER, data1=99, data2=27, data3=1)
    await devices[OTHER].aldb.async_write()
    await devices[LIGHT].aldb.async_write()
    changed = [{"address": LIGHT, "data1": 42, "data2": 15, "data3": 1}]
    await scenes.async_add_or_update_scene(20, changed, work_dir=str(tmp_path))
    assert [rec.data1 for rec in active(devices[LIGHT], target=KEYPAD)] == [42]
    assert [rec.data2 for rec in active(devices[LIGHT], target=REMOTE)] == [15]
    assert [rec.data1 for rec in active(devices[LIGHT], target=OTHER)] == [99]
    assert await scenes.async_delete_scene(20, str(tmp_path)) == ResponseStatus.SUCCESS
    assert not active(devices[KEYPAD], target=LIGHT)
    assert not active(devices[REMOTE], target=LIGHT)
    assert [rec.data1 for rec in active(devices[LIGHT], target=OTHER)] == [99]
    assert len(active(devices[OTHER], target=LIGHT)) == 1
    assert await scenes.async_get_scenes(str(tmp_path)) == {}


@async_case
async def test_restart_and_controller_removal(scene_devices, tmp_path):
    """Controller associations survive restart and explicitly empty means app-only."""
    devices = scene_devices()
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    controllers._scenes.clear()
    scene = await scenes.async_get_scene(20, str(tmp_path))
    assert scene["controllers"] == CONTROLLERS
    await scenes.async_add_or_update_scene(
        20, LINKS, work_dir=str(tmp_path), controllers=[]
    )
    assert not active(devices[LIGHT], target=KEYPAD)
    assert not active(devices[LIGHT], target=REMOTE)
    assert len(active(devices[LIGHT], target=MODEM, group=20)) == 1
    assert (await scenes.async_get_scene(20, str(tmp_path)))["controllers"] == []


@async_case
async def test_default_reporting_links_and_no_self_links(scene_devices, tmp_path):
    """Preserve controller reporting and don't write hardware self-links."""
    devices = scene_devices()
    devices[KEYPAD].aldb.add(group=3, target=MODEM, controller=True)
    devices.modem.aldb.add(group=3, target=KEYPAD, controller=False)
    await devices[KEYPAD].aldb.async_write()
    await devices.modem.aldb.async_write()
    links = [*LINKS, {"address": KEYPAD, "data1": 255, "data2": 28, "data3": 3}]
    await scenes.async_add_or_update_scene(
        20, links, "Evening", str(tmp_path), CONTROLLERS
    )
    assert not active(devices[KEYPAD], target=KEYPAD)
    assert len(active(devices[KEYPAD], target=MODEM, group=3, is_controller=True)) == 1
    assert (
        len(active(devices[KEYPAD], target=MODEM, group=20, is_controller=False)) == 1
    )
    await scenes.async_delete_scene(20, str(tmp_path))
    assert len(active(devices[KEYPAD], target=MODEM, group=3, is_controller=True)) == 1
    assert len(active(devices.modem, target=KEYPAD, group=3, is_controller=False)) == 1


@async_case
async def test_conflicting_managed_controller(scene_devices, tmp_path):
    """A button cannot own two distinct logical scenes."""
    scene_devices()
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    with pytest.raises(controllers.SceneControllerError, match="belongs to scene"):
        await scenes.async_add_or_update_scene(
            21, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    assert controllers.scene_numbers() == {20}


@pytest.mark.parametrize("side", ["controller", "responder"])
@async_case
async def test_unmanaged_conflict(scene_devices, tmp_path, side):
    """Reject unmanaged hardware groups even when only one side of the link exists."""
    devices = scene_devices()
    if side == "controller":
        devices[KEYPAD].aldb.add(group=3, target=LIGHT, controller=True)
        await devices[KEYPAD].aldb.async_write()
    else:
        devices[LIGHT].aldb.add(group=3, target=KEYPAD, data3=1)
        await devices[LIGHT].aldb.async_write()
    with pytest.raises(
        controllers.SceneControllerError, match="already controls|existing responder"
    ):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    assert not controllers.scene_numbers()


@pytest.mark.parametrize(
    "selection",
    [
        [{"address": KEYPAD, "group": 2}],
        [{"address": MODEM, "group": 20}],
        [{"address": "999999", "group": 1}],
        [CONTROLLERS[0], CONTROLLERS[0]],
    ],
)
@async_case
async def test_invalid_controllers_before_mutation(scene_devices, tmp_path, selection):
    """Reject unknown devices, unavailable buttons, modem selectors and duplicates."""
    devices = scene_devices()
    with pytest.raises(controllers.SceneControllerError):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=selection
        )
    assert all(not devices[addr].aldb.pending_changes for addr in devices)


@async_case
async def test_incomplete_and_unrelated_pending_databases(scene_devices, tmp_path):
    """Never silently write partial databases or pending edits owned by another editor."""
    devices = scene_devices()
    devices[LIGHT].aldb._status = ALDBStatus.PARTIAL
    with pytest.raises(
        controllers.SceneControllerError, match="complete All-Link Database"
    ):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    devices[LIGHT].aldb._status = ALDBStatus.LOADED
    devices[LIGHT].aldb.add(group=99, target=OTHER, data3=1)
    with pytest.raises(controllers.SceneControllerError, match="unrelated pending"):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    assert len(devices[LIGHT].aldb.pending_changes) == 1


@async_case
async def test_failed_creation_retry_after_restart(scene_devices, tmp_path):
    """Reserve the scene ID and preserve desired settings when a remote is asleep."""
    devices = scene_devices()
    writer = devices[REMOTE].aldb._write_manager.async_write
    writer.return_value = ResponseStatus.FAILURE
    assert await scenes.async_add_or_update_scene(
        -1, LINKS, "Evening", str(tmp_path), CONTROLLERS
    ) == (20, ResponseStatus.FAILURE)
    scene = await scenes.async_get_scene(20, str(tmp_path))
    assert scene["pending"]
    assert scene["name"] == "Evening"
    assert scene["devices"][Address(LIGHT)][0].data1 == 128
    assert 20 in await scenes.async_get_scenes(str(tmp_path))
    devices[REMOTE].aldb.clear_pending()
    controllers._scenes.clear()
    writer.return_value = ResponseStatus.SUCCESS
    assert await scenes.async_add_or_update_scene(
        20, LINKS, work_dir=str(tmp_path)
    ) == (20, ResponseStatus.SUCCESS)
    scene = await scenes.async_get_scene(20, str(tmp_path))
    assert not scene["pending"]
    assert scene["name"] == "Evening"
    assert len(active(devices[LIGHT], target=REMOTE)) == 1


@async_case
async def test_failed_removal_retains_ownership(scene_devices, tmp_path):
    """A failed deletion can be retried even after responders have been removed."""
    devices = scene_devices()
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    writer = devices[KEYPAD].aldb._write_manager.async_write
    writer.return_value = ResponseStatus.FAILURE
    assert await scenes.async_delete_scene(20, str(tmp_path)) == ResponseStatus.FAILURE
    assert (await scenes.async_get_scene(20, str(tmp_path)))["pending"]
    devices[KEYPAD].aldb.clear_pending()
    controllers._scenes.clear()
    writer.return_value = ResponseStatus.SUCCESS
    assert await scenes.async_delete_scene(20, str(tmp_path)) == ResponseStatus.SUCCESS
    assert not active(devices[KEYPAD], target=LIGHT)
    assert await scenes.async_get_scenes(str(tmp_path)) == {}


@async_case
async def test_helpers_update_both_underlying_groups(scene_devices, tmp_path):
    """Single-device scene helpers synchronize hardware and modem responders."""
    devices = scene_devices()
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    await scenes.async_add_device_to_scene(OTHER, 20, data1=70, work_dir=str(tmp_path))
    assert [rec.data1 for rec in active(devices[OTHER], target=KEYPAD, group=3)] == [70]
    await scenes.async_remove_device_from_scene(OTHER, 20, work_dir=str(tmp_path))
    assert not active(devices[OTHER], target=KEYPAD, group=3)
    assert not active(devices[OTHER], target=MODEM, group=20)


@async_case
async def test_corrupt_metadata_is_not_overwritten(scene_devices, tmp_path):
    """Refuse to mutate hardware when ownership metadata is unreadable."""
    devices = scene_devices()
    filename = tmp_path / controllers.SCENE_CONTROLLERS_FILE
    filename.write_text('{"version": 999, "scenes": {}}')
    with pytest.raises(controllers.SceneControllerError, match="Cannot load"):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    assert json.loads(filename.read_text())["version"] == 999
    assert all(not devices[addr].aldb.pending_changes for addr in devices)


@async_case
async def test_simultaneous_creation_allocates_distinct_groups(scene_devices, tmp_path):
    """Concurrent creates serialize allocation and ownership checks."""
    scene_devices()
    results = await asyncio.gather(
        scenes.async_add_or_update_scene(
            -1, LINKS, "First", str(tmp_path), [CONTROLLERS[0]]
        ),
        scenes.async_add_or_update_scene(
            -1, LINKS, "Second", str(tmp_path), [CONTROLLERS[1]]
        ),
    )
    assert results == [(20, ResponseStatus.SUCCESS), (21, ResponseStatus.SUCCESS)]


@async_case
async def test_asleep_remote_is_not_reported_as_success(scene_devices, tmp_path):
    """A queued battery write is not a completed scene save."""
    devices = scene_devices()
    devices[REMOTE].async_keep_awake.return_value = ResponseStatus.FAILURE
    assert await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    ) == (20, ResponseStatus.FAILURE)
    devices[REMOTE].aldb._write_manager.async_write.assert_not_called()
    assert (await scenes.async_get_scene(20, str(tmp_path)))["pending"]
    devices[REMOTE].async_keep_awake.return_value = ResponseStatus.SUCCESS
    assert await scenes.async_add_or_update_scene(
        20, LINKS, work_dir=str(tmp_path)
    ) == (20, ResponseStatus.SUCCESS)


@async_case
async def test_read_during_write_does_not_replace_journal(scene_devices, tmp_path):
    """Polling the editor while saving cannot restore stale pending metadata."""
    devices = scene_devices()
    reads = []

    async def write(record, force=False):
        reads.append(asyncio.create_task(scenes.async_get_scene(20, str(tmp_path))))
        return ResponseStatus.SUCCESS

    devices[LIGHT].aldb._write_manager.async_write.side_effect = write
    await scenes.async_add_or_update_scene(
        20, LINKS, "Evening", str(tmp_path), CONTROLLERS
    )
    assert all(not scene["pending"] for scene in await asyncio.gather(*reads))
    assert not (await scenes.async_get_scene(20, str(tmp_path)))["pending"]


@pytest.mark.parametrize("output", [0, 1])
@async_case
async def test_native_activation_updates_only_its_group(
    scene_devices, tmp_path, output
):
    """Hardware button broadcasts update Home Assistant using the right responder settings."""
    devices = scene_devices()
    await scenes.async_add_or_update_scene(
        20, [{**LINKS[0], "data3": output}], "First", str(tmp_path), [CONTROLLERS[0]]
    )
    other_links = [{"address": LIGHT, "data1": 200, "data2": 15, "data3": 1}]
    await scenes.async_add_or_update_scene(
        21, other_links, "Second", str(tmp_path), [{"address": KEYPAD, "group": 4}]
    )
    manager = DeviceLinkManager(devices)
    responders = manager.get_responders(Address(KEYPAD), 3)
    assert [link.data1 for link in responders[Address(LIGHT)]] == [128]
    devices[LIGHT].async_status = AsyncMock(return_value=ResponseStatus.SUCCESS)
    await manager._async_check_responders(
        topic=SimpleNamespace(name=f"{KEYPAD}.3.on.all_link_broadcast")
    )
    assert devices[LIGHT].groups[1].value == 128
    devices[LIGHT].async_status.assert_awaited_once()


@async_case
async def test_capacity_failure_before_mutation(scene_devices, tmp_path):
    """Refuse a scene which cannot leave space for a high-water-mark record."""
    devices = scene_devices()
    hwm = ALDBRecord(
        7,
        controller=False,
        group=0,
        target="000000",
        data1=0,
        data2=0,
        data3=0,
        in_use=False,
        high_water_mark=True,
    )
    devices[LIGHT].aldb.load_saved_records(
        ALDBStatus.LOADED, {7: hwm}, first_mem_addr=7
    )
    with pytest.raises(controllers.SceneControllerError, match="is full"):
        await scenes.async_add_or_update_scene(
            20, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
        )
    assert all(not devices[addr].aldb.pending_changes for addr in devices)


@async_case
async def test_multiple_responder_outputs(scene_devices, tmp_path):
    """Different outputs share a controller record but have distinct responder records."""
    devices = scene_devices()
    links = [
        {"address": OTHER, "data1": 255, "data2": 28, "data3": 3},
        {"address": OTHER, "data1": 0, "data2": 0, "data3": 4},
    ]
    await scenes.async_add_or_update_scene(
        20, links, "Keypad indicators", str(tmp_path), CONTROLLERS
    )
    assert [
        (rec.data3, rec.data1) for rec in active(devices[OTHER], target=KEYPAD, group=3)
    ] == [(3, 255), (4, 0)]
    assert len(active(devices[KEYPAD], target=OTHER, group=3, is_controller=True)) == 1
    await scenes.async_add_or_update_scene(20, links[:1], work_dir=str(tmp_path))
    assert [rec.data3 for rec in active(devices[OTHER], target=KEYPAD, group=3)] == [3]
    assert len(active(devices[KEYPAD], target=OTHER, group=3, is_controller=True)) == 1


@async_case
async def test_default_name_uses_allocated_modem_group(scene_devices, tmp_path):
    """A nameless device scene uses the allocated scene number, not the sentinel."""
    scene_devices()
    assert await scenes.async_add_or_update_scene(
        -1, LINKS, work_dir=str(tmp_path), controllers=CONTROLLERS
    ) == (20, ResponseStatus.SUCCESS)
    assert (await scenes.async_get_scene(20, str(tmp_path)))[
        "name"
    ] == "Insteon Scene 20"


@async_case
async def test_controllers_respond_to_the_scene(scene_devices, tmp_path):
    """Home Assistant and other controllers drive each controller button."""
    devices = scene_devices()
    devices[LIGHT].properties[ON_LEVEL].set_value(64)
    devices[LIGHT].properties[RAMP_RATE].set_value(20)
    selected = [
        {"address": LIGHT, "group": 1},
        {"address": KEYPAD, "group": 3},
        {"address": REMOTE, "group": 1},
    ]
    await scenes.async_add_or_update_scene(20, [], "Evening", str(tmp_path), selected)

    for source, group in ((MODEM, 20), (KEYPAD, 3), (REMOTE, 1)):
        records = active(
            devices[LIGHT], target=source, group=group, is_controller=False
        )
        assert [(rec.data1, rec.data2, rec.data3) for rec in records] == [(64, 20, 1)]
    for source, group in ((MODEM, 20), (LIGHT, 1), (REMOTE, 1)):
        records = active(
            devices[KEYPAD], target=source, group=group, is_controller=False
        )
        assert [(rec.data1, rec.data2, rec.data3) for rec in records] == [(255, 28, 3)]
    assert not active(devices[LIGHT], target=LIGHT)
    assert not active(devices[KEYPAD], target=KEYPAD, is_controller=False)
    assert not active(devices[REMOTE], is_controller=False, group=20)
    scene = await scenes.async_get_scene(20, str(tmp_path))
    assert set(scene["devices"]) == {Address(LIGHT), Address(KEYPAD)}

    assert await scenes.async_delete_scene(20, str(tmp_path)) == ResponseStatus.SUCCESS
    for device in (devices[LIGHT], devices[KEYPAD]):
        assert not active(device, is_controller=False, group=20)


@async_case
async def test_explicit_settings_override_controller_defaults(scene_devices, tmp_path):
    """A configured level for a controller button replaces its local settings."""
    devices = scene_devices()
    devices[LIGHT].properties[ON_LEVEL].set_value(64)
    links = [{"address": LIGHT, "data1": 100, "data2": 10, "data3": 1}]
    await scenes.async_add_or_update_scene(
        20, links, "Evening", str(tmp_path), [{"address": LIGHT, "group": 1}]
    )
    records = active(devices[LIGHT], target=MODEM, group=20, is_controller=False)
    assert [(rec.data1, rec.data2, rec.data3) for rec in records] == [(100, 10, 1)]


async def hand_link(devices, controller, group, responder, data1, data2, data3):
    """Write a hand-made controller/responder link pair."""
    devices[controller].aldb.add(group=group, target=responder, controller=True)
    devices[responder].aldb.add(
        group=group,
        target=controller,
        controller=False,
        data1=data1,
        data2=data2,
        data3=data3,
    )
    for address in (controller, responder):
        # Battery writes otherwise stay queued until the device wakes.
        if devices[address].is_battery:
            await devices[address].aldb.async_write_on_wake()
        else:
            await devices[address].aldb.async_write()


def duplicate_record(device, record, data1):
    """Insert a second copy of a record with a different level."""
    records = dict(device.aldb.items())
    mem_addr = min(records)
    records[mem_addr] = ALDBRecord(
        mem_addr,
        controller=record.is_controller,
        group=record.group,
        target=record.target,
        data1=data1,
        data2=record.data2,
        data3=record.data3,
        in_use=True,
        high_water_mark=False,
    )
    records[mem_addr - 8] = ALDBRecord(
        mem_addr - 8,
        controller=False,
        group=0,
        target="000000",
        data1=0,
        data2=0,
        data3=0,
        in_use=False,
        high_water_mark=True,
    )
    device.aldb.load_saved_records(ALDBStatus.LOADED, records)


@async_case
async def test_import_hand_made_scene(scene_devices, tmp_path):
    """Buttons that control each other import as one scene, adopting their links."""
    devices = scene_devices()
    for controller, group in ((KEYPAD, 3), (LIGHT, 1)):
        await hand_link(devices, controller, group, OTHER, 128, 20, 1)
    await hand_link(devices, KEYPAD, 3, LIGHT, 200, 10, 1)
    await hand_link(devices, LIGHT, 1, KEYPAD, 255, 28, 3)
    await scenes.async_add_or_update_scene(-1, LINKS, "Duplicate", str(tmp_path))
    other_records = len(devices[OTHER].aldb)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert found == [
        {
            "controllers": [
                {"address": KEYPAD, "group": 3},
                {"address": LIGHT, "group": 1},
            ],
            "links": [
                {"address": KEYPAD, "data1": 255, "data2": 28, "data3": 3},
                {"address": LIGHT, "data1": 200, "data2": 10, "data3": 1},
                {"address": OTHER, "data1": 128, "data2": 20, "data3": 1},
            ],
            "issues": [],
            "importable": True,
        }
    ]
    scene_num, result = await scenes.async_import_device_scene(
        found[0]["controllers"], "Evening", str(tmp_path)
    )
    assert (scene_num, result) == (21, ResponseStatus.SUCCESS)

    assert len(active(devices[OTHER], target=LIGHT, group=1)) == 1
    assert len(active(devices[LIGHT], target=KEYPAD, group=3)) == 1
    assert len(active(devices[KEYPAD], target=LIGHT, group=1)) == 1
    for address in (KEYPAD, LIGHT, OTHER):
        assert len(active(devices[address], target=MODEM, group=21)) == 1
    assert len(devices[OTHER].aldb) == other_records + 1
    scene = await scenes.async_get_scene(21, str(tmp_path))
    assert scene["name"] == "Evening"
    assert scene["controllers"] == found[0]["controllers"]
    assert await scenes.async_find_device_scenes(str(tmp_path)) == []

    assert await scenes.async_delete_scene(20, str(tmp_path)) == ResponseStatus.SUCCESS
    assert len(active(devices[LIGHT], target=MODEM, group=21)) == 1
    assert len(active(devices[OTHER], target=KEYPAD, group=3)) == 1


@async_case
async def test_import_reads_set_button_links_on_single_output_devices(
    scene_devices, tmp_path
):
    """A responder link storing output 0 imports as the device's only output."""
    devices = scene_devices()
    await hand_link(devices, KEYPAD, 4, LIGHT, 191, 20, 0)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert found[0]["links"] == [
        {"address": LIGHT, "data1": 191, "data2": 20, "data3": 1}
    ]
    scene_num, _ = await scenes.async_import_device_scene(
        found[0]["controllers"], "Set button", str(tmp_path)
    )
    scene = await scenes.async_get_scene(scene_num, str(tmp_path))
    light = scene["devices"][devices[LIGHT].address]
    assert [(link.data1, link.data2, link.data3) for link in light] == [(191, 20, 1)]
    # The set-button link is adopted as-is rather than duplicated or rewritten.
    hand_made = active(devices[LIGHT], target=KEYPAD, group=4)
    assert [(rec.data1, rec.data2, rec.data3) for rec in hand_made] == [(191, 20, 0)]


@async_case
async def test_output_zero_matches_the_only_output(scene_devices, tmp_path):
    """Scenes journaled with output 0 keep their records when saved with output 1."""
    devices = scene_devices()
    controller = [{"address": KEYPAD, "group": 3}]
    link = {"address": LIGHT, "data1": 128, "data2": 28, "data3": 0}
    scene_num, result = await scenes.async_add_or_update_scene(
        -1, [link], "Legacy", str(tmp_path), controller
    )
    assert result == ResponseStatus.SUCCESS

    def light_records():
        return sorted(
            (rec.group, str(rec.target), rec.data3)
            for _, rec in devices[LIGHT].aldb.items()
            if rec.is_in_use
        )

    before = light_records()
    writes = devices[LIGHT].aldb._write_manager.async_write.await_count
    _, result = await scenes.async_add_or_update_scene(
        scene_num, [{**link, "data3": 1}], "Legacy", str(tmp_path), controller
    )
    assert result == ResponseStatus.SUCCESS
    assert light_records() == before
    assert devices[LIGHT].aldb._write_manager.async_write.await_count == writes


@async_case
async def test_import_splits_buttons_with_different_settings(scene_devices, tmp_path):
    """Buttons whose shared responders use different levels import separately."""
    devices = scene_devices()
    await hand_link(devices, KEYPAD, 4, OTHER, 100, 28, 1)
    await hand_link(devices, REMOTE, 2, OTHER, 50, 28, 1)
    await hand_link(devices, REMOTE, 2, KEYPAD, 255, 28, 4)
    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert [item["controllers"] for item in found] == [
        [{"address": KEYPAD, "group": 4}],
        [{"address": REMOTE, "group": 2}],
    ]
    assert all(item["importable"] for item in found)


@async_case
async def test_blocked_device_scene_is_reported_not_imported(scene_devices, tmp_path):
    """Buttons with conflicting or unreadable links cannot be imported."""
    devices = scene_devices()
    await hand_link(devices, KEYPAD, 5, LIGHT, 100, 28, 1)
    duplicate_record(devices[LIGHT], active(devices[LIGHT], target=KEYPAD)[0], 50)
    devices[KEYPAD].aldb.add(group=6, target=OTHER, controller=True)
    await devices[KEYPAD].aldb.async_write()
    devices[OTHER].aldb._status = ALDBStatus.PARTIAL

    found = await scenes.async_find_device_scenes(str(tmp_path))
    issues = {item["controllers"][0]["group"]: item["issues"] for item in found}
    assert issues[5] == ["44.44.44 has conflicting links to this button"]
    assert issues[6] == [
        "Read the complete All-Link Database for 55.55.55",
        "The button has no responders",
    ]
    assert not any(item["importable"] for item in found)
    with pytest.raises(controllers.SceneControllerError, match="conflicting"):
        await scenes.async_import_device_scene(
            [{"address": KEYPAD, "group": 5}], "Blocked", str(tmp_path)
        )
    assert not active(devices[LIGHT], target=MODEM)


async def keypad_and_remotes(devices):
    """Link keypad buttons and remotes as hand-made scenes for the same lights.

    Each remote button also lights its keypad button and turns off the keypad's
    load and other scene buttons, as they are commonly linked.
    """
    scenes_by_button = {3: (1, 200), 5: (2, 0), 6: (3, 255)}
    for group, (remote_group, level) in scenes_by_button.items():
        for controller, controller_group in (
            (KEYPAD, group),
            (REMOTE, remote_group),
            (REMOTE_2, remote_group),
        ):
            await hand_link(devices, controller, controller_group, LIGHT, level, 27, 1)
            await hand_link(devices, controller, controller_group, OTHER, level, 27, 1)
        for remote in (REMOTE, REMOTE_2):
            await hand_link(devices, remote, remote_group, KEYPAD, 0, 27, 1)
            for button in scenes_by_button:
                on_level = 255 if button == group else 0
                await hand_link(
                    devices, remote, remote_group, KEYPAD, on_level, 28, button
                )


@async_case
async def test_remotes_lighting_a_keypad_button_join_its_scene(scene_devices, tmp_path):
    """Keypad buttons and the remote buttons lighting them are one scene each."""
    devices = scene_devices()
    await keypad_and_remotes(devices)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert [item["controllers"] for item in found] == [
        [
            {"address": KEYPAD, "group": group},
            {"address": REMOTE, "group": remote_group},
            {"address": REMOTE_2, "group": remote_group},
        ]
        for group, remote_group in ((3, 1), (5, 2), (6, 3))
    ]
    assert all(item["importable"] for item in found)
    # Each scene keeps its own levels for the shared lights.
    assert found[0]["links"] == [
        {"address": KEYPAD, "data1": 0, "data2": 27, "data3": 1},
        {"address": KEYPAD, "data1": 255, "data2": 28, "data3": 3},
        {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 5},
        {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 6},
        {"address": LIGHT, "data1": 200, "data2": 27, "data3": 1},
        {"address": OTHER, "data1": 200, "data2": 27, "data3": 1},
    ]
    assert [link["data1"] for link in found[2]["links"][-2:]] == [255, 255]


@async_case
async def test_linked_buttons_with_different_levels_stay_separate(
    scene_devices, tmp_path
):
    """A remote lighting a keypad button but setting other levels is not merged."""
    devices = scene_devices()
    await hand_link(devices, KEYPAD, 3, LIGHT, 200, 27, 1)
    await hand_link(devices, REMOTE, 1, LIGHT, 100, 27, 1)
    await hand_link(devices, REMOTE, 1, KEYPAD, 255, 28, 3)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert [item["controllers"] for item in found] == [
        [{"address": KEYPAD, "group": 3}],
        [{"address": REMOTE, "group": 1}],
    ]


@async_case
async def test_linked_scene_import_resolves_duplicates_without_waking_remotes(
    scene_devices, tmp_path
):
    """A duplicate the other buttons agree on, and stale links, do not block import."""
    devices = scene_devices()
    await keypad_and_remotes(devices)
    for remote in (REMOTE, REMOTE_2):
        devices[remote].aldb.add(group=1, target=OLD_MODEM, controller=True)
        await devices[remote].aldb.async_write_on_wake()
    light_link = active(devices[LIGHT], target=KEYPAD, group=3)[0]
    duplicate_record(devices[LIGHT], light_link, 51)
    for remote in (REMOTE, REMOTE_2):
        devices[remote].async_keep_awake.reset_mock()
        devices[remote].aldb._write_manager.async_write.reset_mock()

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert found[0]["issues"] == []
    assert {"address": LIGHT, "data1": 200, "data2": 27, "data3": 1} in found[0][
        "links"
    ]
    scene_num, result = await scenes.async_import_device_scene(
        found[0]["controllers"], "Evening", str(tmp_path)
    )
    assert result == ResponseStatus.SUCCESS

    records = active(devices[LIGHT], target=KEYPAD, group=3)
    assert [(rec.data1, rec.data2) for rec in records] == [(200, 27)]
    for remote in (REMOTE, REMOTE_2):
        assert not devices[remote].async_keep_awake.called
        assert not devices[remote].aldb._write_manager.async_write.called
        assert active(devices[remote], target=OLD_MODEM, group=1)
        light = active(devices[LIGHT], target=remote, group=1)
        assert [(rec.data1, rec.data2) for rec in light] == [(200, 27)]
    assert len(active(devices[LIGHT], target=MODEM, group=scene_num)) == 1


def keypad_button_settings(device, group, on_buttons, off_buttons, on_level, ramp_rate):
    """Set the buttons a keypad button turns on and off, and its load level."""
    suffix = "" if group == 1 else f"_{group}"
    device.properties[f"on_mask{suffix}"].set_value(
        sum(1 << (button - 1) for button in on_buttons)
    )
    device.properties[f"off_mask{suffix}"].set_value(
        sum(1 << (button - 1) for button in off_buttons)
    )
    device.properties[f"on_level{suffix}"].set_value(on_level)
    device.properties[f"ramp_rate{suffix}"].set_value(ramp_rate)


@async_case
async def test_keypad_scene_imports_the_keypads_own_buttons(scene_devices, tmp_path):
    """A keypad button's load level and button settings import with its scene."""
    devices = scene_devices()
    keypad = devices[KEYPAD]
    # Button A turns the load off over 2 seconds and buttons C and D off.
    keypad_button_settings(keypad, 3, (1, 3), (1, 5, 6), 0, 27)
    await hand_link(devices, KEYPAD, 3, LIGHT, 200, 28, 1)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert found == [
        {
            "controllers": [{"address": KEYPAD, "group": 3}],
            "links": [
                {"address": KEYPAD, "data1": 0, "data2": 27, "data3": 1},
                {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 5},
                {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 6},
                {"address": LIGHT, "data1": 200, "data2": 28, "data3": 1},
            ],
            "issues": [],
            "importable": True,
        }
    ]
    scene_num, result = await scenes.async_import_device_scene(
        found[0]["controllers"], "Evening", str(tmp_path)
    )
    assert result == ResponseStatus.SUCCESS

    # The modem scene sets the keypad as a press of button A does.
    records = {
        rec.data3: (rec.data1, rec.data2)
        for rec in active(keypad, target=MODEM, group=scene_num, is_controller=False)
    }
    assert records == {1: (0, 27), 3: (255, 28), 5: (0, 28), 6: (0, 28)}
    # The keypad applies its own settings when button A is pressed.
    assert active(keypad, target=KEYPAD) == []
    scene = await scenes.async_get_scene(scene_num, str(tmp_path))
    assert sorted(
        (link.data3, link.data1, link.data2)
        for link in scene["devices"][Address(KEYPAD)]
    ) == [(1, 0, 27), (3, 255, 28), (5, 0, 28), (6, 0, 28)]


@async_case
async def test_keypad_load_follows_a_button_at_its_level(scene_devices, tmp_path):
    """A button that turns the load on imports the button's level and ramp rate."""
    devices = scene_devices()
    keypad_button_settings(devices[KEYPAD], 6, (1, 6), (3, 5), 255, 27)
    await hand_link(devices, KEYPAD, 6, LIGHT, 255, 28, 1)
    # The main button controls the same light, but is not part of button D's scene.
    await hand_link(devices, KEYPAD, 1, LIGHT, 255, 28, 1)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert [item["controllers"] for item in found] == [
        [{"address": KEYPAD, "group": 1}],
        [{"address": KEYPAD, "group": 6}],
    ]
    assert found[1]["links"][:3] == [
        {"address": KEYPAD, "data1": 255, "data2": 27, "data3": 1},
        {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 3},
        {"address": KEYPAD, "data1": 0, "data2": 28, "data3": 5},
    ]


@async_case
async def test_unread_keypad_buttons_block_import(scene_devices, tmp_path):
    """A keypad whose button settings have not been read is not imported."""
    devices = scene_devices()
    devices[KEYPAD].properties["on_mask_3"]._is_loaded = False
    await hand_link(devices, KEYPAD, 3, LIGHT, 200, 28, 1)

    found = await scenes.async_find_device_scenes(str(tmp_path))
    assert found[0]["issues"] == [f"Read the properties of {Address(KEYPAD)}"]
    assert not found[0]["importable"]
