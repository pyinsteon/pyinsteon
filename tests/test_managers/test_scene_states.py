"""Test the on/off state of Insteon scenes."""

import gc
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyinsteon.constants import ResponseStatus
from pyinsteon.events import OFF_EVENT, ON_EVENT
from pyinsteon.managers import scene_manager as scenes, scene_state_manager
from pyinsteon.managers.scene_state_manager import (
    SCENE_ADDED,
    SCENE_REMOVED,
    SceneStateManager,
)

from tests.test_managers import test_scene_controllers
from tests.test_managers.test_scene_controllers import KEYPAD, LINKS, REMOTE
from tests.utils import async_case

# Share the scene controller tests' isolated devices fixture.
scene_devices = test_scene_controllers.scene_devices


@pytest.fixture
def state_devices(request, monkeypatch):
    """Build devices with fresh scene states and a fake modem trigger."""
    build_devices = request.getfixturevalue("scene_devices")
    monkeypatch.setattr(
        scenes, "scene_states", SceneStateManager(scenes._async_trigger_scene)
    )
    sent = []

    def handler(command):
        def build():
            async def async_send(group):
                sent.append((command, group))
                return ResponseStatus.SUCCESS

            return SimpleNamespace(async_send=async_send)

        return build

    monkeypatch.setattr(scenes, "SendAllLinkOnCommandHandler", handler("on"))
    monkeypatch.setattr(scenes, "SendAllLinkOffCommandHandler", handler("off"))
    monkeypatch.setattr(scenes, "_get_scene_device_status", AsyncMock())
    monkeypatch.setattr(scenes.asyncio, "sleep", AsyncMock())

    def build():
        devices = build_devices()
        monkeypatch.setattr(scene_state_manager, "devices", devices)
        return devices, sent

    yield build
    # Free the scenes' listeners while this test's publisher is still in use.
    # Otherwise a later collection can free them while another test publishes.
    gc.collect()


async def _save(tmp_path, controllers=None, scene_num=-1, name="Evening"):
    return await scenes.async_add_or_update_scene(
        scene_num, LINKS, name, str(tmp_path), controllers or []
    )


@async_case
async def test_app_only_scene_follows_triggers(state_devices, tmp_path):
    """A scene without controllers only changes when it is triggered."""
    _, sent = state_devices()
    scene_num, _ = await _save(tmp_path)
    states = await scenes.async_load_scene_states(str(tmp_path))
    scene = states.get(scene_num)
    assert (scene.name, scene.is_on, scene.has_device_state) == ("Evening", None, False)
    changes = MagicMock()
    unsubscribe = scene.subscribe(changes)

    await scene.async_on()
    assert scene.is_on is True
    await scenes.async_trigger_scene_off(scene_num)
    assert scene.is_on is False
    assert sent == [("on", scene_num), ("off", scene_num)]
    assert changes.call_count == 2

    unsubscribe()
    await scene.async_on()
    assert changes.call_count == 2


@async_case
async def test_restores_only_unknown_states(state_devices, tmp_path):
    """A saved state is only restored while the scene state is unknown."""
    state_devices()
    scene_num, _ = await _save(tmp_path)
    scene = (await scenes.async_load_scene_states(str(tmp_path))).get(scene_num)
    scene.restore_state(True)
    assert scene.is_on is True
    scene.restore_state(False)
    assert scene.is_on is True


@async_case
async def test_scene_follows_keypad_button_state(state_devices, tmp_path):
    """A keypad controller supplies the scene state and its changes."""
    devices, _ = state_devices()
    button = devices[KEYPAD].groups[3]
    button.value = True
    scene_num, _ = await _save(tmp_path, [{"address": KEYPAD, "group": 3}])
    scene = (await scenes.async_load_scene_states(str(tmp_path))).get(scene_num)
    assert (scene.is_on, scene.has_device_state) == (True, True)

    button.value = False
    assert scene.is_on is False
    devices[KEYPAD].events[3][ON_EVENT].trigger(on_level=255)
    assert scene.is_on is True


@async_case
async def test_remote_scene_follows_button_presses(state_devices, tmp_path):
    """Remote presses set the scene state, even when the press repeats."""
    devices, _ = state_devices()
    scene_num, _ = await _save(tmp_path, [{"address": REMOTE, "group": 1}])
    scene = (await scenes.async_load_scene_states(str(tmp_path))).get(scene_num)
    assert (scene.is_on, scene.has_device_state) == (None, False)
    events = devices[REMOTE].events[1]

    events[ON_EVENT].trigger(on_level=255)
    assert scene.is_on is True
    await scene.async_off()
    assert scene.is_on is False
    events[ON_EVENT].trigger(on_level=255)
    assert scene.is_on is True
    events[OFF_EVENT].trigger(on_level=0)
    assert scene.is_on is False


@async_case
async def test_scene_list_changes(state_devices, tmp_path):
    """Saving adds and renames scenes, and only a deletion removes one."""
    devices, _ = state_devices()
    states = await scenes.async_load_scene_states(str(tmp_path))
    assert len(states) == 0
    events = []
    states.subscribe(lambda event, scene: events.append((event, scene.scene_num)))

    scene_num, _ = await _save(tmp_path)
    assert events == [(SCENE_ADDED, scene_num)]
    scene = states.get(scene_num)
    changes = MagicMock()
    scene.subscribe(changes)

    await _save(tmp_path, [{"address": KEYPAD, "group": 3}], scene_num, "Late")
    assert (scene.name, scene.controllers) == (
        "Late",
        [{"address": KEYPAD, "group": 3}],
    )
    assert scene.has_device_state
    assert changes.call_count == 1

    # A scene that is missing from a refresh, but was not deleted, is kept.
    states.update({})
    assert states.get(scene_num) is scene

    devices[KEYPAD].groups[3].value = True
    await scenes.async_delete_scene(scene_num, str(tmp_path))
    assert events == [(SCENE_ADDED, scene_num), (SCENE_REMOVED, scene_num)]
    assert states.get(scene_num) is None
    # The removed scene stops following its controller.
    devices[KEYPAD].groups[3].value = False
    assert scene.is_on is True


@async_case
async def test_failed_delete_keeps_scene(state_devices, tmp_path):
    """A scene whose deletion is incomplete keeps its state."""
    devices, _ = state_devices()
    scene_num, _ = await _save(tmp_path, [{"address": KEYPAD, "group": 3}])
    states = await scenes.async_load_scene_states(str(tmp_path))
    devices[KEYPAD].aldb._write_manager.async_write = AsyncMock(
        return_value=ResponseStatus.FAILURE
    )
    result = await scenes.async_delete_scene(scene_num, str(tmp_path))
    assert result != ResponseStatus.SUCCESS
    assert states.get(scene_num) is not None


@async_case
async def test_imported_scene_is_added(state_devices, tmp_path, monkeypatch):
    """Importing a device scene adds it to the scene states."""
    state_devices()
    states = await scenes.async_load_scene_states(str(tmp_path))
    events = []
    states.subscribe(lambda event, scene: events.append(event))
    candidate = {"controllers": [], "importable": True, "issues": [], "links": LINKS}
    monkeypatch.setattr(
        scenes.controller_manager, "find_device_scenes", lambda: [candidate]
    )
    await scenes.async_import_device_scene([], "Imported", str(tmp_path))
    assert [scene.name for scene in states] == ["Imported"]
    assert events == [SCENE_ADDED]
