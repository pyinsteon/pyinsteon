"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from . import Device
from .commands import (STATUS_COMMAND, ON_INBOUND, OFF_INBOUND,
                       ON_FAST_INBOUND, OFF_FAST_INBOUND)
from ..handlers.from_device.on_level import OnLevelInbound
from ..handlers.from_device.off import OffInbound
from ..handlers.from_device.on_fast import OnFastInbound
from ..handlers.from_device.off_fast import OffFastInbound
from ..handlers.to_device.status_request import StatusRequestCommand
from ..states import DIMMABLE_LIGHT_STATE
from ..states.on_level import OnLevel
from ..events import Event, ON_EVENT, ON_FAST_EVENT, OFF_EVENT, OFF_FAST_EVENT


class VariableControllerBase(Device):
    """Variable state value controller device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=range(1, 2)):
        """Init the VariableControllerBase class."""
        super().__init__(address, cat, subcat, firmware, description, model)
        if not hasattr(self, '_button_names'):
            self._button_names = {}
        for button in buttons:
            self._setup_button(button)

    def status(self):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self):
        """Request the status of the device.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[ON_INBOUND] = OnLevelInbound(self._address)
        self._handlers[OFF_INBOUND] = OffInbound(self._address)

        self._handlers[ON_FAST_INBOUND] = OnFastInbound(self._address)
        self._handlers[OFF_FAST_INBOUND] = OffFastInbound(self._address)

        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)
        self._handlers[STATUS_COMMAND].subscribe(self._set_status)

    def _set_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[1].value = status

    def _setup_button(self, group):
        self._states[group] = OnLevel(name=DIMMABLE_LIGHT_STATE,
                                      address=self._address,
                                      group=group)
        state = self._states[group]
        state.add_handler(self._handlers[ON_INBOUND])
        state.add_handler(self._handlers[OFF_INBOUND])
        state.add_handler(self._handlers[ON_FAST_INBOUND])
        state.add_handler(self._handlers[OFF_FAST_INBOUND])

        self._events[ON_EVENT] = Event(name=ON_EVENT, address=self._address, group=group)
        self._events[ON_EVENT].add_handler(self._handlers[ON_INBOUND])

        self._events[OFF_EVENT] = Event(name=OFF_EVENT, address=self._address, group=group)
        self._events[OFF_EVENT].add_handler(self._handlers[OFF_INBOUND])

        self._events[ON_FAST_EVENT] = Event(name=ON_FAST_EVENT, address=self._address,
                                            group=group)
        self._events[ON_FAST_EVENT].add_handler(self._handlers[ON_FAST_INBOUND])

        self._events[OFF_FAST_EVENT] = Event(name=OFF_FAST_EVENT, address=self._address,
                                             group=group)
        self._events[OFF_FAST_EVENT].add_handler(self._handlers[OFF_FAST_INBOUND])
