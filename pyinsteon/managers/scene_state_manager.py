"""Track the on/off state of Insteon scenes."""

import logging
from typing import Awaitable, Callable, Iterator, Optional

from .. import devices
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT

_LOGGER = logging.getLogger(__name__)

SCENE_ADDED = "added"
SCENE_REMOVED = "removed"
_ON_EVENTS = (ON_EVENT, ON_FAST_EVENT)
_OFF_EVENTS = (OFF_EVENT, OFF_FAST_EVENT)

SceneTrigger = Callable[[int, bool], Awaitable[None]]


class InsteonScene:
    """The on/off state of an Insteon scene.

    A scene turns on or off when it is triggered through the modem. A scene with
    controllers also follows them: a press of any controller button sets the
    state, and controllers that report their state, such as keypad buttons, keep
    it in step. Battery-operated remotes only report presses.
    """

    def __init__(
        self, scene_num: int, name: str, controllers: list[dict], trigger: SceneTrigger
    ):
        """Init the InsteonScene class."""
        self._scene_num = scene_num
        self._name = name
        self._trigger = trigger
        self._controllers: list[dict] = []
        self._is_on: Optional[bool] = None
        self._has_device_state = False
        self._subscribers: list[Callable[[], None]] = []
        self._sources: list[tuple] = []
        self._set_controllers(controllers)

    @property
    def scene_num(self) -> int:
        """Return the scene number, which is the modem group."""
        return self._scene_num

    @property
    def name(self) -> str:
        """Return the scene name."""
        return self._name

    @property
    def controllers(self) -> list[dict]:
        """Return the scene's device controllers."""
        return [dict(controller) for controller in self._controllers]

    @property
    def is_on(self) -> Optional[bool]:
        """Return True if the scene is on, or None if the state is unknown."""
        return self._is_on

    @property
    def has_device_state(self) -> bool:
        """Return True if a controller reports its state."""
        return self._has_device_state

    def subscribe(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Call back on a change to the scene, and return a function to stop."""
        self._subscribers.append(callback)

        def unsubscribe():
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return unsubscribe

    def set_state(self, is_on: bool):
        """Set the scene state."""
        if self._is_on == is_on:
            return
        self._is_on = is_on
        self._call_subscribers()

    def restore_state(self, is_on: bool):
        """Restore a previously saved state when the state is unknown."""
        if self._is_on is None:
            self.set_state(is_on)

    async def async_on(self):
        """Turn the scene on."""
        await self._trigger(self._scene_num, True)

    async def async_off(self):
        """Turn the scene off."""
        await self._trigger(self._scene_num, False)

    def update(self, name: str, controllers: list[dict]):
        """Update the scene name and controllers."""
        changed = name != self._name
        self._name = name
        if [dict(controller) for controller in controllers] != self._controllers:
            changed = True
            self._set_controllers(controllers)
        if changed:
            self._call_subscribers()

    def close(self):
        """Stop following the scene's controllers."""
        for source, listener in self._sources:
            source.unsubscribe(listener)
        self._sources = []

    def _set_controllers(self, controllers: list[dict]):
        self.close()
        self._controllers = [dict(controller) for controller in controllers]
        self._has_device_state = False
        device_state = None
        for controller in self._controllers:
            device = devices[controller["address"]]
            group = controller["group"]
            if device is None:
                continue
            for name, event in device.events.get(group, {}).items():
                if name in _ON_EVENTS + _OFF_EVENTS:
                    self._listen(event, self._event_received)
            if device.is_battery or group not in device.groups:
                continue
            self._has_device_state = True
            self._listen(device.groups[group], self._value_changed)
            value = device.groups[group].value
            if device_state is None and value is not None:
                device_state = bool(value)
        if device_state is not None:
            self._is_on = device_state

    def _listen(self, source, listener):
        source.subscribe(listener)
        self._sources.append((source, listener))

    def _event_received(self, name, address, group, button=None):
        if name in _ON_EVENTS:
            self.set_state(True)
        elif name in _OFF_EVENTS:
            self.set_state(False)

    def _value_changed(self, name, address, value, group):
        if value is not None:
            self.set_state(bool(value))

    def _call_subscribers(self):
        for callback in list(self._subscribers):
            try:
                callback()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Error calling scene %d subscriber", self._scene_num)


class SceneStateManager:
    """The on/off states of all Insteon scenes."""

    def __init__(self, trigger: SceneTrigger):
        """Init the SceneStateManager class."""
        self._trigger = trigger
        self._scenes: dict[int, InsteonScene] = {}
        self._subscribers: list[Callable[[str, InsteonScene], None]] = []
        self._loaded = False

    def __iter__(self) -> Iterator[InsteonScene]:
        """Return an iterator of the scenes."""
        return iter(list(self._scenes.values()))

    def __len__(self) -> int:
        """Return the number of scenes."""
        return len(self._scenes)

    def get(self, scene_num: int) -> Optional[InsteonScene]:
        """Return a scene, or None."""
        return self._scenes.get(scene_num)

    @property
    def loaded(self) -> bool:
        """Return True once the scenes have been loaded."""
        return self._loaded

    def subscribe(
        self, callback: Callable[[str, InsteonScene], None]
    ) -> Callable[[], None]:
        """Call back when a scene is added or removed, and return a function to stop."""
        self._subscribers.append(callback)

        def unsubscribe():
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return unsubscribe

    def update(self, scenes: dict[int, dict], deleted: Optional[int] = None):
        """Add and update scenes from the scene list, and remove a deleted scene.

        Scenes missing from the list are only removed when they were deleted,
        so a scene whose devices have not been read yet keeps its state.
        """
        self._loaded = True
        for scene_num, scene in scenes.items():
            existing = self._scenes.get(scene_num)
            if existing:
                existing.update(scene["name"], scene.get("controllers", []))
                continue
            added = InsteonScene(
                scene_num, scene["name"], scene.get("controllers", []), self._trigger
            )
            self._scenes[scene_num] = added
            self._call_subscribers(SCENE_ADDED, added)
        if deleted is not None and deleted not in scenes and deleted in self._scenes:
            removed = self._scenes.pop(deleted)
            removed.close()
            self._call_subscribers(SCENE_REMOVED, removed)

    def _call_subscribers(self, event: str, scene: InsteonScene):
        for callback in list(self._subscribers):
            try:
                callback(event, scene)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Error calling scene list subscriber")
