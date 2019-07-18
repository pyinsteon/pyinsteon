"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from . import Device
from .commands import (STATUS_COMMAND, ON_INBOUND, OFF_INBOUND,
                       ON_FAST_INBOUND, OFF_FAST_INBOUND)
from ..handlers.from_device.on_level import OnLevelInbound
from ..handlers.from_device.off import OffInbound
from ..handlers.to_device.status_request import StatusRequestCommand

from ..states import OPEN_CLOSE_SENSOR_STATE
from ..states.open_close import NormallyOpen, NormallyClosed
from ..events import Event, OPEN_EVENT, CLOSE_EVENT


class OpenCloseControllerBase(Device):
    """Base device for Open/Close controllers."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=1):
        """Init the OpenCloseControllerBase class."""
        super().__init__(address, cat, subcat, firmware, description, model)

    def status(self, group=None):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self, group=None):
        """Request the status of the device."""
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[ON_INBOUND] = OnLevelInbound(self._address)
        self._handlers[OFF_INBOUND] = OffInbound(self._address)

        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)
        self._handlers[STATUS_COMMAND].subscribe(self._set_status)

    def _set_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[1].value = status

    def _subscribe_to_handlers(self, group, normally_open=True):
        state = self._states[group]
        state.add_handler(self._handlers[ON_INBOUND])
        state.add_handler(self._handlers[OFF_INBOUND])
        state.add_handler(self._handlers[ON_FAST_INBOUND])
        state.add_handler(self._handlers[OFF_FAST_INBOUND])

        if normally_open:
            open_inbound = ON_INBOUND
            close_inbound = OFF_INBOUND
        else:
            open_inbound = OFF_INBOUND
            close_inbound = ON_INBOUND

        self._events[OPEN_EVENT] = Event(name=OPEN_EVENT, address=self._address, group=group)
        self._events[OPEN_EVENT].add_handler(self._handlers[open_inbound])

        self._events[CLOSE_EVENT] = Event(name=CLOSE_EVENT, address=self._address, group=group)
        self._events[CLOSE_EVENT].add_handler(self._handlers[close_inbound])

class NormallyOpenControllerBase(OpenCloseControllerBase):
    """Normally open controller base."""

    def _register_states(self):
        """Register a Normally Open state."""
        self._states[1] = NormallyOpen(name=OPEN_CLOSE_SENSOR_STATE, address=self._address, group=1)
        self._subscribe_to_handlers(group=1, normally_open=True)

class NormallyClosedControllerBase(OpenCloseControllerBase):
    """Normally closed controller base."""

    def _register_states(self):
        """Register a Normally Open state."""
        self._states[1] = NormallyClosed(
            name=OPEN_CLOSE_SENSOR_STATE, address=self._address, group=1)
        self._subscribe_to_handlers(group=1, normally_open=False)
