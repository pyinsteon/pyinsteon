"""Sensor/Actuator devices."""
from ..events import CLOSE_EVENT, OPEN_EVENT, Event
from ..extended_property import DELAY, PRESCALER, X10_HOUSE, X10_UNIT
from ..groups import OPEN_CLOSE_SENSOR
from ..groups.open_close import NormallyOpen
from ..handlers.to_device.status_request import STATUS_REQUEST, StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from ..operating_flag import (
    LED_BLINK_ON_TX_ON,
    MOMENTARY_FOLLOW_SENSE,
    MOMENTARY_MODE_ON,
    MOMENTARY_ON_OFF_TRIGGER,
    PROGRAM_LOCK_ON,
    RELAY_ON_SENSE_ON,
    X10_OFF,
)
from ..utils import multiple_status
from .on_off_responder_base import OnOffResponderBase

ON_LEVEL_MANAGER = "on_level_manager"
SENSOR_GROUP = 2


class SensorsActuators(OnOffResponderBase):
    """Sensor Actuator device."""


class SensorsActuators_IOLink(SensorsActuators):
    """I/O Link device."""

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
        """Init the SensorsActuators_IOLink class."""
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )
        self._op_flags_manager.extended_write = True

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        if self._managers.get(SENSOR_GROUP) is None:
            self._managers[SENSOR_GROUP] = {}
        self._managers[SENSOR_GROUP][ON_LEVEL_MANAGER] = OnLevelManager(
            self._address, SENSOR_GROUP
        )
        if self._handlers.get(SENSOR_GROUP) is None:
            self._handlers[SENSOR_GROUP] = {}
        self._handlers[SENSOR_GROUP][STATUS_REQUEST] = StatusRequestCommand(
            self.address, 1
        )

    def status(self, group=None):
        """Get the status of the relay and/or the sensor."""
        if group in [1, None]:
            super().status()
        if group == [2, None]:
            self.sensor_status()

    async def async_status(self, group=None):
        """Get the status of the relay and/or the sensor."""
        response_1 = None
        response_2 = None
        if group in [1, None]:
            response_1 = await super().async_status()
        if group == [2, None]:
            response_2 = await self.async_sensor_status()
        return multiple_status(response_1, response_2)

    def relay_status(self):
        """Get the status of the relay switch."""
        super().status()

    async def async_relay_status(self):
        """Get the status of the relay switch."""
        return await super().async_status()

    def sensor_status(self):
        """Get the status of the sensor."""
        self._handlers[SENSOR_GROUP][STATUS_REQUEST].send()

    async def async_sensor_status(self):
        """Get the status of the sensor."""
        return await self._handlers[SENSOR_GROUP][STATUS_REQUEST].async_send()

    def _register_groups(self):
        super()._register_groups()
        # Off is a Open state and On is an Closed state
        self._groups[SENSOR_GROUP] = NormallyOpen(
            OPEN_CLOSE_SENSOR, self._address, SENSOR_GROUP
        )

    def _register_events(self):
        super()._register_events()
        if self._events.get(SENSOR_GROUP) is None:
            self._events[SENSOR_GROUP] = {}
        self._events[SENSOR_GROUP][OPEN_EVENT] = Event(
            OPEN_EVENT, self._address, SENSOR_GROUP
        )
        self._events[SENSOR_GROUP][CLOSE_EVENT] = Event(
            CLOSE_EVENT, self._address, SENSOR_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[SENSOR_GROUP][ON_LEVEL_MANAGER].subscribe(
            self._groups[SENSOR_GROUP].set_value
        )
        self._managers[SENSOR_GROUP][ON_LEVEL_MANAGER].subscribe_off(
            self._events[SENSOR_GROUP][OPEN_EVENT].trigger
        )
        self._managers[SENSOR_GROUP][ON_LEVEL_MANAGER].subscribe_on(
            self._events[SENSOR_GROUP][CLOSE_EVENT].trigger
        )

    def _register_operating_flags(self):
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RELAY_ON_SENSE_ON, 0, 2, 4, 5)
        self._add_operating_flag(MOMENTARY_MODE_ON, 0, 3, 6, 7)
        self._add_operating_flag(MOMENTARY_ON_OFF_TRIGGER, 0, 4, 0x12, 0x13)
        self._add_operating_flag(X10_OFF, 0, 5, 0x0C, 0x0D)
        self._add_operating_flag(MOMENTARY_FOLLOW_SENSE, 0, 6, 0x0E, 0x0F)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 7, 0x14, 0x15)

        self._add_property(PRESCALER, 3, 7)
        self._add_property(DELAY, 4, 6)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)

    def _open_event(self, on_level):
        """Catch open events and fire appropriate signals."""

    def _close_event(self, on_level):
        """Catch close events and fire appropriate signals."""

    def _open_close_group(self, on_level):
        """Catch open/close group signal and fire appropriate signals."""
