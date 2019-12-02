"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from . import Device
from .commands import STATUS_COMMAND
from ..managers.on_level_manager import OnLevelManager
from ..handlers.to_device.status_request import StatusRequestCommand

from ..states import OPEN_CLOSE_SENSOR
from ..states.open_close import NormallyOpen, NormallyClosed
from ..events import Event, OPEN_EVENT, CLOSE_EVENT


class OpenCloseControllerBase(Device):
    """Base device for Open/Close controllers."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        normally_open=True,
        state_name=OPEN_CLOSE_SENSOR,
        open_event_name=OPEN_EVENT,
        close_event_name=CLOSE_EVENT,
    ):
        """Init the OpenCloseControllerBase class."""
        self._state_name = state_name
        self._open_event_name = open_event_name
        self._close_event_name = close_event_name
        self._normally_open = normally_open
        super().__init__(address, cat, subcat, firmware, description, model)

    def status(self, group=None):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self, group=None):
        """Request the status of the device."""
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address, 0)
        self._managers[1] = OnLevelManager(self._address, 1)

    def _register_states(self):
        """Register a Normally Open state."""
        if self._normally_open:
            self._states[1] = NormallyOpen(self._state_name, self._address, 1)
        else:
            self._states[1] = NormallyClosed(self._state_name, self._address, 1)

    def _register_events(self):
        self._events[1] = {}
        self._events[1][self._open_event_name] = Event(
            self._open_event_name, self._address, 1
        )
        self._events[1][self._close_event_name] = Event(
            self._close_event_name, self._address, 1
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)
        self._managers[1].subscribe(self._states[1].set_value)
        if self._normally_open:
            # Open is OFF and Close is ON
            self._managers[1].subscribe_off(self._events[self._open_event_name].trigger)
            self._managers[1].subscribe_on(self._events[self._close_event_name].trigger)
        else:
            # Close is OFF and Open is ON
            self._managers[1].subscribe_on(self._events[self._open_event_name].trigger)
            self._managers[1].subscribe_off(
                self._events[self._close_event_name].trigger
            )

    def _handle_status(self, db_version, status):
        """Set the status of the dimmable_switch state."""
        self._states[1].value = status


class NormallyOpenControllerBase(OpenCloseControllerBase):
    """Normally open controller base."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0,
        description="",
        model="",
        state_name=OPEN_CLOSE_SENSOR,
        open_event_name=OPEN_EVENT,
        close_event_name=CLOSE_EVENT,
    ):
        """Init the NormallyOpenControllerBase class."""
        super().__init__(
            address,
            cat,
            subcat,
            firmware=firmware,
            description=description,
            model=model,
            normally_open=True,
            state_name=state_name,
            open_event_name=open_event_name,
            close_event_name=close_event_name,
        )


class NormallyClosedControllerBase(OpenCloseControllerBase):
    """Normally closed controller base."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0,
        description="",
        model="",
        state_name=OPEN_CLOSE_SENSOR,
        open_event_name=OPEN_EVENT,
        close_event_name=CLOSE_EVENT,
    ):
        """Init the NormallyClosedControllerBase class."""
        super().__init__(
            address,
            cat,
            subcat,
            firmware=firmware,
            description=description,
            model=model,
            normally_open=False,
            state_name=state_name,
            open_event_name=open_event_name,
            close_event_name=close_event_name,
        )
