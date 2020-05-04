"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..default_link import DefaultLink
from ..events import OFF_EVENT, ON_EVENT, Event
from ..groups import ON_OFF_SWITCH
from ..groups.on_off import OnOff
from ..handlers.to_device.status_request import StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from .commands import STATUS_COMMAND, STATUS_COMMAND_HUB
from .device_base import Device

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
        on_event_name=ON_EVENT,
        off_event_name=OFF_EVENT,
        on_fast_event_name=None,
        off_fast_event_name=None,
    ):
        """Init the OnOffControllerBase class."""

        self._buttons = {1: ON_OFF_SWITCH} if buttons is None else buttons
        self._on_event_name = on_event_name
        self._off_event_name = off_event_name
        self._on_fast_event_name = on_fast_event_name
        self._off_fast_event_name = off_fast_event_name

        super().__init__(address, cat, subcat, firmware, description, model)

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
        self._handlers[STATUS_COMMAND_HUB] = StatusRequestCommand(self._address, 2)
        for group in self._buttons:
            if self._managers.get(group) is None:
                self._managers[group] = {}
            self._managers[group][ON_LEVEL_MANAGER] = OnLevelManager(
                self._address, group
            )

    def _register_groups(self):
        super()._register_groups()
        for group in self._buttons:
            if self._buttons[group] is not None:
                name = self._buttons[group]
                self._groups[group] = OnOff(name, self._address, group)

    def _register_events(self):
        super()._register_events()
        for group in self._buttons:
            self._events[group] = {}
            button = self._buttons[group]
            if self._on_event_name:
                self._events[group][self._on_event_name] = Event(
                    self._on_event_name, self._address, group, button
                )

            if self._off_event_name:
                self._events[group][self._off_event_name] = Event(
                    self._off_event_name, self._address, group, button
                )

            if self._on_fast_event_name:
                self._events[group][self._on_fast_event_name] = Event(
                    self._on_fast_event_name, self._address, group, button
                )

            if self._off_fast_event_name:
                self._events[group][self._off_fast_event_name] = Event(
                    self._off_fast_event_name, self._address, group, button
                )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)
        self._handlers[STATUS_COMMAND_HUB].subscribe(self._handle_status)
        for group in self._buttons:
            if self._groups.get(group) is not None:
                self._managers[group][ON_LEVEL_MANAGER].subscribe(
                    self._groups[group].set_value
                )
            if self._on_event_name:
                event = self._events[group][self._on_event_name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on(event.trigger)

            if self._off_event_name:
                event = self._events[group][self._off_event_name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_off(event.trigger)

            if self._on_fast_event_name:
                event = self._events[group][self._on_fast_event_name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_on_fast(event.trigger)

            if self._off_fast_event_name:
                event = self._events[group][self._off_fast_event_name]
                self._managers[group][ON_LEVEL_MANAGER].subscribe_off_fast(
                    event.trigger
                )

    def _handle_status(self, db_version, status):
        """Handle status response."""
        # Add this to a separate handler for devices that the cmd1 field
        # returns the ALDB Versioh
        # self.aldb.version = db_version
        self._groups[1].set_value(status)
