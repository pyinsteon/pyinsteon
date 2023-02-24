"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..default_link import DefaultLink
from ..events import OFF_EVENT, ON_EVENT, Event
from ..groups import ON_OFF_SWITCH
from ..groups.on_off import OnOff
from ..handlers.to_device.status_request import StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from .device_base import Device
from .device_commands import STATUS_COMMAND

ON_LEVEL_MANAGER = "on_level_manager"


class OnOffControllerBase(Device):
    """Base device for ON/OFF controllers."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
        on_event_names=None,
        off_event_names=None,
        on_fast_event_names=None,
        off_fast_event_names=None,
    ):
        """Init the OnOffControllerBase class."""

        super().__init__(address, cat, subcat, firmware, description, model)

        self._buttons = {1: ON_OFF_SWITCH} if buttons is None else buttons

        if on_event_names is None:
            self._on_event_names = {1: ON_EVENT}
        else:
            self._on_event_names = on_event_names

        if off_event_names is None:
            self._off_event_names = {1: OFF_EVENT}
        else:
            self._off_event_names = off_event_names

        if on_fast_event_names is None:
            self._on_fast_event_names = {}
        else:
            self._on_fast_event_names = on_fast_event_names

        if off_fast_event_names is None:
            self._off_fast_event_names = {}
        else:
            self._off_fast_event_names = off_fast_event_names

    def status(self, group=None):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self, group=None):
        """Request the status of the device."""
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        """Register default links for the device."""
        super()._register_default_links()
        for group in self._buttons:
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
        for group in self._buttons:
            if self._managers.get(group) is None:
                self._managers[group] = {}
            self._managers[group][ON_LEVEL_MANAGER] = OnLevelManager(
                self._address, group
            )

    def _register_groups(self):
        super()._register_groups()
        for group in self._buttons:
            if name := self._buttons.get(group):
                self._groups[group] = OnOff(name, self._address, group)

    def _register_events(self):
        super()._register_events()
        for group in self._on_event_names:
            self._events[group] = self._events.get(group, {})
            button = self._buttons[group]
            if name := self._on_event_names.get(group):
                self._events[group][name] = Event(name, self._address, group, button)

            if name := self._off_event_names.get(group):
                self._events[group][name] = Event(name, self._address, group, button)

            if name := self._on_fast_event_names.get(group):
                self._events[group][name] = Event(name, self._address, group, button)

            if name := self._off_fast_event_names.get(group):
                self._events[group][name] = Event(name, self._address, group, button)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)
        for group in self._buttons:
            if self._groups.get(group) is not None:
                self._managers[group][ON_LEVEL_MANAGER].subscribe(
                    self._groups[group].set_value
                )
            if name := self._on_event_names.get(group):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on(event.trigger)

            if name := self._off_event_names.get(group):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_off(event.trigger)

            if name := self._on_fast_event_names.get(group):
                event = self._events[group][name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on_fast(event.trigger)

            if name := self._off_fast_event_names.get(group):
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
