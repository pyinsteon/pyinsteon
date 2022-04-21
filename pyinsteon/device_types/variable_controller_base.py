"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""

from ..default_link import DefaultLink
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT, Event
from ..groups import DIMMABLE_LIGHT
from ..groups.on_level import OnLevel
from ..handlers.to_device.status_request import StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from .device_base import Device
from .device_commands import STATUS_COMMAND

ON_LEVEL_MANAGER = "on_level_manager"


class VariableControllerBase(Device):
    """Variable state value controller device."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
    ):
        """Init the VariableControllerBase class."""
        self._buttons = {1: DIMMABLE_LIGHT} if buttons is None else buttons
        super().__init__(address, cat, subcat, firmware, description, model)

    # pylint: disable=arguments-differ
    async def async_status(self):
        """Request the status of the device.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action

        """
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        """Register default links.

        Default links:
            is_controller group dev_data1 dev_data2 dev_data3 modem_data1 modem_data2 modem_data3

        """
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
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)
        for group in self._buttons:
            if self._managers.get(group) is None:
                self._managers[group] = {}
            self._managers[group][ON_LEVEL_MANAGER] = OnLevelManager(
                self._address, group
            )

    def _register_groups(self):
        super()._register_groups()
        for group in self._buttons:
            name = self._buttons[group]
            self._groups[group] = OnLevel(name=name, address=self._address, group=group)

    def _register_events(self):
        super()._register_events()
        for group in self._buttons:
            if self._events.get(group) is None:
                self._events[group] = {}
            button = self._buttons[group]
            self._events[group][ON_EVENT] = Event(
                ON_EVENT, self._address, group, button
            )
            self._events[group][OFF_EVENT] = Event(
                OFF_EVENT, self._address, group, button
            )
            self._events[group][ON_FAST_EVENT] = Event(
                ON_FAST_EVENT, self._address, group, button
            )
            self._events[group][OFF_FAST_EVENT] = Event(
                OFF_FAST_EVENT, self._address, group, button
            )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)
        for group in self._buttons:
            state = self._groups[group]
            self._managers[group][ON_LEVEL_MANAGER].subscribe(state.set_value)

            event = self._events[group][ON_EVENT]
            self._managers[group][ON_LEVEL_MANAGER].subscribe_on(event.trigger)

            event = self._events[group][OFF_EVENT]
            self._managers[group][ON_LEVEL_MANAGER].subscribe_off(event.trigger)

            event = self._events[group][ON_FAST_EVENT]
            self._managers[group][ON_LEVEL_MANAGER].subscribe_on_fast(event.trigger)

            event = self._events[group][OFF_FAST_EVENT]
            self._managers[group][ON_LEVEL_MANAGER].subscribe_off_fast(event.trigger)

    def _handle_status(self, db_version, status):
        """Set the status of the dimmable_switch state."""
        self._groups[1].value = status
