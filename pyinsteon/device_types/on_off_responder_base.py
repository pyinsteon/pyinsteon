"""Switched Lighting Control devices (CATEGORY 0x02)."""
from typing import Dict, Union

from ..address import Address
from ..constants import DeviceCategory
from ..groups import ON_OFF_SWITCH
from ..handlers.to_device.off import OffCommand
from ..handlers.to_device.off_fast import OffFastCommand
from ..handlers.to_device.on_fast import OnFastCommand
from ..handlers.to_device.on_level import OnLevelCommand
from .device_commands import OFF_COMMAND, OFF_FAST_COMMAND, ON_COMMAND, ON_FAST_COMMAND
from .on_off_controller_base import OnOffControllerBase

Byte = int


class OnOffResponderBase(OnOffControllerBase):
    """Switched Lighting Control device."""

    def __init__(
        self,
        address: Address,
        cat: DeviceCategory,
        subcat: Byte,
        firmware: Byte = 0x00,
        description: str = "",
        model: str = "",
        responders: Union[Dict[int, str], None] = None,
        controllers: Union[Dict[int, str], None] = None,
        on_event_names: Union[Dict[int, str], None] = None,
        off_event_names: Union[Dict[int, str], None] = None,
        on_fast_event_names: Union[Dict[int, str], None] = None,
        off_fast_event_names: Union[Dict[int, str], None] = None,
    ):
        """Init the OnOffResponderBase class."""

        self._responders = {1: ON_OFF_SWITCH} if not responders else responders
        all_controllers = self._responders.copy()
        if controllers:
            all_controllers.update(controllers)
        if responders:
            responders.update(responders)
        super().__init__(
            address,
            cat,
            subcat,
            firmware,
            description,
            model,
            all_controllers,
            on_event_names,
            off_event_names,
            on_fast_event_names,
            off_fast_event_names,
        )

    def on(self, group: int = 0):
        """Turn on the device."""
        group = 1 if not group else group
        self._handlers[group][ON_COMMAND].send(on_level=0xFF)

    async def async_on(self, group: int = 0):
        """Turn on the device."""
        group = 1 if not group else group
        return await self._handlers[group][ON_COMMAND].async_send(on_level=0xFF)

    def off(self, group: int = 0):
        """Turn off the device."""
        group = 1 if not group else group
        self._handlers[group][OFF_COMMAND].send()

    async def async_off(self, group: int = 0):
        """Turn off the device."""
        group = 1 if not group else group
        return await self._handlers[group][OFF_COMMAND].async_send()

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        for group in self._responders:
            self._handlers[group] = self._handlers.get(group, {})
            self._handlers[group][ON_COMMAND] = OnLevelCommand(self._address, group)
            self._handlers[group][OFF_COMMAND] = OffCommand(self._address, group)
            self._handlers[group][ON_FAST_COMMAND] = OnFastCommand(self._address, group)
            self._handlers[group][OFF_FAST_COMMAND] = OffFastCommand(
                self._address, group
            )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        for group in self._responders:
            if self._groups.get(group):
                self._handlers[group][ON_COMMAND].subscribe(
                    self._groups[group].set_value
                )
                self._handlers[group][OFF_COMMAND].subscribe(
                    self._groups[group].set_value
                )
                self._handlers[group][ON_FAST_COMMAND].subscribe(
                    self._groups[group].set_value
                )
                self._handlers[group][OFF_FAST_COMMAND].subscribe(
                    self._groups[group].set_value
                )

            if name := self._on_event_names.get(group):
                event = self._events[group][name]
                self._handlers[group][ON_COMMAND].subscribe(event.trigger)

            if name := self._off_event_names.get(group):
                event = self._events[group][name]
                self._handlers[group][OFF_COMMAND].subscribe(event.trigger)

            if name := self._on_fast_event_names.get(group):
                event = self._events[group][name]
                self._handlers[group][ON_FAST_COMMAND].subscribe(event.trigger)

            if name := self._off_fast_event_names.get(group):
                event = self._events[group][name]
                self._handlers[group][OFF_FAST_COMMAND].subscribe(event.trigger)
