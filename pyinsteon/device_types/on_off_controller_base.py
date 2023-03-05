"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from typing import Dict, Union

from ..address import Address
from ..constants import DeviceCategory
from ..default_link import DefaultLink
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT, Event
from ..groups import ON_OFF_SWITCH
from ..groups.on_off import OnOff
from ..handlers.to_device.status_request import StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from .device_base import Device
from .device_commands import STATUS_COMMAND

ON_LEVEL_MANAGER = "on_level_manager"
Byte = int


class OnOffControllerBase(Device):
    """Base device for ON/OFF controllers."""

    def __init__(
        self,
        address: Address,
        cat: DeviceCategory,
        subcat: Byte,
        firmware: Byte = 0x00,
        description: str = "",
        model: str = "",
        controllers: Union[Dict[int, str], None] = None,
        on_event_names: Union[Dict[int, str], None] = None,
        off_event_names: Union[Dict[int, str], None] = None,
        on_fast_event_names: Union[Dict[int, str], None] = None,
        off_fast_event_names: Union[Dict[int, str], None] = None,
    ):
        """Init the OnOffControllerBase class."""

        self._controllers = {1: ON_OFF_SWITCH} if controllers is None else controllers

        if on_event_names is None:
            self._on_event_names = {group: ON_EVENT for group in self._controllers}
        else:
            self._on_event_names = on_event_names

        if off_event_names is None:
            self._off_event_names = {group: OFF_EVENT for group in self._controllers}
        else:
            self._off_event_names = off_event_names

        if on_fast_event_names is None:
            self._on_fast_event_names = {
                group: ON_FAST_EVENT for group in self._controllers
            }
        else:
            self._on_fast_event_names = on_event_names

        if off_fast_event_names is None:
            self._off_fast_event_names = {
                group: OFF_FAST_EVENT for group in self._controllers
            }
        else:
            self._off_fast_event_names = off_event_names

        super().__init__(address, cat, subcat, firmware, description, model)

    async def async_status(self, group=None):
        """Request the status of the device."""
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        """Register default links for the device."""
        super()._register_default_links()
        for group in self._controllers:
            link = DefaultLink(
                is_controller=True,
                group=group,
                dev_data1=255,
                dev_data2=28,
                dev_data3=group,
                modem_data1=0,
                modem_data2=0,
                modem_data3=0,
            )
            self._default_links.append(link)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()

        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address, 0)
        for groups in (
            self._controllers,
            self._on_event_names,
            self._off_event_names,
            self._on_fast_event_names,
            self._off_fast_event_names,
        ):
            event_groups = [group for group in groups if group not in self._managers]
            for group in event_groups:
                self._managers[group] = {}
                self._managers[group][ON_LEVEL_MANAGER] = OnLevelManager(
                    self._address, group
                )

    def _register_groups(self):
        super()._register_groups()
        for group in self._controllers:
            if name := self._controllers.get(group):
                self._groups[group] = OnOff(name, self._address, group)

    def _register_events(self):
        super()._register_events()
        for group, name in self._on_event_names.items():
            self._events[group] = self._events.get(group, {})
            if group in self._controllers:
                button = self._controllers[group]
            else:
                button = None
            self._events[group][name] = Event(name, self._address, group, button)

        for group, name in self._off_event_names.items():
            self._events[group] = self._events.get(group, {})
            if group in self._controllers:
                button = self._controllers[group]
            else:
                button = None
            self._events[group][name] = Event(name, self._address, group, button)

        for group, name in self._on_fast_event_names.items():
            self._events[group] = self._events.get(group, {})
            if group in self._controllers:
                button = self._controllers[group]
            else:
                button = None
            self._events[group][name] = Event(name, self._address, group, button)

        for group, name in self._off_fast_event_names.items():
            self._events[group] = self._events.get(group, {})
            if group in self._controllers:
                button = self._controllers[group]
            else:
                button = None
            self._events[group][name] = Event(name, self._address, group, button)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)
        for group in self._controllers:
            if self._managers[group].get(ON_LEVEL_MANAGER):
                self._managers[group][ON_LEVEL_MANAGER].subscribe(
                    self._groups[group].set_value
                )

        for group, name in self._on_event_names.items():
            if self._managers[group].get(ON_LEVEL_MANAGER):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on(event.trigger)

        for group, name in self._off_event_names.items():
            event = self._events[group][name]
            if self._managers[group].get(ON_LEVEL_MANAGER):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_off(event.trigger)

        for group, name in self._on_fast_event_names.items():
            if self._managers[group].get(ON_LEVEL_MANAGER):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on_fast(event.trigger)

        for group, name in self._off_fast_event_names.items():
            if self._managers[group].get(ON_LEVEL_MANAGER):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_off_fast(
                    event.trigger
                )

    def _handle_status(self, db_version, status):
        """Handle status response."""
        # Add this to a separate handler for devices that the cmd1 field
        # returns the ALDB Versioh
        # self.aldb.version = db_version
        self._groups[1].set_value(status)
