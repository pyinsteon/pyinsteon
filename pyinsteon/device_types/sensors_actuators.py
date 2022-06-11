"""Sensor/Actuator devices."""
import asyncio

from ..config import (
    DELAY,
    LED_BLINK_ON_TX_ON,
    MOMENTARY_DELAY,
    MOMENTARY_FOLLOW_SENSE,
    MOMENTARY_MODE_ON,
    MOMENTARY_ON_OFF_TRIGGER,
    PRESCALER,
    PROGRAM_LOCK_ON,
    RELAY_MODE,
    RELAY_ON_SENSE_ON,
    SENSE_SENDS_OFF,
    X10_HOUSE,
    X10_OFF,
    X10_UNIT,
)
from ..config.momentary_delay import MomentaryDelayProperty
from ..config.relay_mode import RelayModeProperty
from ..constants import PropertyType, RelayMode, ResponseStatus
from ..default_link import DefaultLink
from ..events import CLOSE_EVENT, OFF_EVENT, ON_EVENT, OPEN_EVENT, Event
from ..groups import OPEN_CLOSE_SENSOR, RELAY
from ..groups.on_off import OnOff
from ..groups.open_close import NormallyClosed
from ..handlers.to_device.off import OffCommand
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.to_device.status_request import STATUS_REQUEST, StatusRequestCommand
from ..managers.on_level_manager import OnLevelManager
from ..utils import multiple_status
from .device_base import Device
from .device_commands import OFF_COMMAND, ON_COMMAND
from .on_off_responder_base import OnOffResponderBase

ON_LEVEL_MANAGER = "on_level_manager"
RELAY_GROUP = 1
SENSOR_GROUP = 2


class SensorsActuators(OnOffResponderBase):
    """Sensor Actuator device."""


class SensorsActuators_IOLink(Device):
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

    @property
    def relay_mode(self) -> RelayMode:
        """Return the relay mode."""
        if not self._operating_flags[MOMENTARY_MODE_ON].value:
            return RelayMode.LATCHING
        if self._operating_flags[MOMENTARY_FOLLOW_SENSE].value:
            return RelayMode.MOMENTARY_C
        if self._operating_flags[MOMENTARY_ON_OFF_TRIGGER].value:
            return RelayMode.MOMENTARY_B
        return RelayMode.MOMENTARY_A

    async def async_set_relay_mode(self, relay_mode: RelayMode):
        """Set the relay mode and write to device."""

        def set_relay_mode(momentary_mode_on, momentary_follow_sense, momentary_on_off):
            """Set the values of the underlying properties."""
            self._operating_flags[MOMENTARY_MODE_ON].new_value = momentary_mode_on
            self._operating_flags[
                MOMENTARY_FOLLOW_SENSE
            ].new_value = momentary_follow_sense
            self._operating_flags[MOMENTARY_ON_OFF_TRIGGER].new_value = momentary_on_off

        if relay_mode is None:
            set_relay_mode(None, None, None)
            return

        relay_mode = RelayMode(int(relay_mode))

        if relay_mode == RelayMode.LATCHING:
            set_relay_mode(False, False, False)
        elif relay_mode == RelayMode.MOMENTARY_A:
            set_relay_mode(True, False, False)
        elif relay_mode == RelayMode.MOMENTARY_B:
            set_relay_mode(True, False, True)
        elif relay_mode == RelayMode.MOMENTARY_C:
            set_relay_mode(True, True, False)

        await self.async_write_op_flags()

    async def async_set_momentary_delay(self, seconds):
        """Set the delay in seconds.

        When the IOLinc is in momentary mode (A, B or C) the relay will
        turn off after the delay period.
        """
        delay = seconds * 10
        prescaler = 1
        if delay > 255:
            prescaler = int(round(delay / 255 + 0.5, 0))
            delay = int(round(delay / prescaler, 0))
        self._properties[PRESCALER].new_value = prescaler
        self._properties[DELAY].new_value = delay
        await self.async_write_ext_properties()

    def on(self, group: int = 0):
        """Turn on the relay."""
        self._handlers[RELAY_GROUP][ON_COMMAND].send()

    async def async_on(self, group: int = 0):
        """Turn on the relay."""
        return await self._handlers[RELAY_GROUP][ON_COMMAND].async_send()

    def off(self, group: int = 0):
        """Turn off the relay."""
        self._handlers[RELAY_GROUP][OFF_COMMAND].send()

    async def async_off(self, group: int = 0):
        """Turn off the relay."""
        return await self._handlers[RELAY_GROUP][OFF_COMMAND].async_send()

    def status(self, group=None):
        """Get the status of the relay and/or the sensor."""
        if group in [1, None]:
            self.relay_status()
        if group == [2, None]:
            self.sensor_status()

    async def async_status(self, group=None):
        """Get the status of the relay and/or the sensor."""
        response_1 = None
        response_2 = None
        if group in [1, None]:
            response_1 = await self.async_relay_status()
        if group in [2, None]:
            response_2 = await self.async_sensor_status()
        return multiple_status(response_1, response_2)

    def relay_status(self):
        """Get the status of the relay switch."""
        self._handlers[RELAY_GROUP][STATUS_REQUEST].send()

    async def async_relay_status(self):
        """Get the status of the relay switch."""
        response = None
        retries = 3
        while response != ResponseStatus.SUCCESS and retries:
            response = await self._handlers[RELAY_GROUP][STATUS_REQUEST].async_send()
            retries -= 1
        return response

    def sensor_status(self):
        """Get the status of the sensor."""
        self._handlers[SENSOR_GROUP][STATUS_REQUEST].send()

    async def async_sensor_status(self):
        """Get the status of the sensor."""
        response = None
        retries = 3
        while response != ResponseStatus.SUCCESS and retries:
            response = await self._handlers[SENSOR_GROUP][STATUS_REQUEST].async_send()
            retries -= 1
        return response

    def _register_op_flags_and_props(self):
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(
            RELAY_ON_SENSE_ON, 0, 2, 4, 5, prop_type=PropertyType.ADVANCED
        )  # Sensor triggers relay
        self._add_operating_flag(
            MOMENTARY_MODE_ON, 0, 3, 6, 7, prop_type=PropertyType.ADVANCED
        )
        self._add_operating_flag(
            MOMENTARY_ON_OFF_TRIGGER, 0, 4, 0x12, 0x13, prop_type=PropertyType.ADVANCED
        )
        self._add_operating_flag(X10_OFF, 0, 5, 0x0C, 0x0D)
        self._add_operating_flag(SENSE_SENDS_OFF, 0, 6, 0x0E, 0x0F)
        self._add_operating_flag(
            MOMENTARY_FOLLOW_SENSE, 0, 7, 0x14, 0x15, prop_type=PropertyType.ADVANCED
        )  # Check sensor before triggering?

        self._add_property(PRESCALER, 3, 7, prop_type=PropertyType.ADVANCED)
        self._add_property(DELAY, 4, 6, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[MOMENTARY_DELAY] = MomentaryDelayProperty(
            self._address,
            MOMENTARY_DELAY,
            self._properties[DELAY],
            self._properties[PRESCALER],
        )
        self._config[RELAY_MODE] = RelayModeProperty(
            self._address,
            RELAY_MODE,
            self._operating_flags[MOMENTARY_MODE_ON],
            self._operating_flags[MOMENTARY_FOLLOW_SENSE],
            self._operating_flags[MOMENTARY_ON_OFF_TRIGGER],
        )

    def _register_handlers_and_managers(self):
        """Register handlers and managers.

        The relay is controlled through group 1.
        The sensor and the relay both use group 1 to notify of changes. T
        When an on/off broadcast message is received, we need to check what the
        current status of the device is for both the relay and the sensor.
        """
        super()._register_handlers_and_managers()

        self._managers[ON_LEVEL_MANAGER] = OnLevelManager(self._address, 1)

        self._handlers[RELAY_GROUP] = {}
        self._handlers[RELAY_GROUP][ON_COMMAND] = OnLevelCommand(
            self._address, RELAY_GROUP
        )
        self._handlers[RELAY_GROUP][OFF_COMMAND] = OffCommand(
            self._address, RELAY_GROUP
        )
        self._handlers[RELAY_GROUP][STATUS_REQUEST] = StatusRequestCommand(
            self._address
        )

        self._handlers[SENSOR_GROUP] = {}
        self._handlers[SENSOR_GROUP][STATUS_REQUEST] = StatusRequestCommand(
            self.address, 1
        )

    def _register_groups(self):
        """Register the device groups.

        There really is only one group in the device, group 1. Both the relay and the sensor
        both send updates on group 1 for broadcast messages. We create two groups because
        we can keep the status of the relay and the sensor separate.
        """
        self._groups[RELAY_GROUP] = OnOff(RELAY, self._address, RELAY_GROUP)
        self._groups[SENSOR_GROUP] = NormallyClosed(
            OPEN_CLOSE_SENSOR, self._address, SENSOR_GROUP
        )

    def _register_events(self):
        self._events[RELAY_GROUP] = {}
        self._events[RELAY_GROUP][ON_EVENT] = Event(
            ON_EVENT, self._address, RELAY_GROUP
        )
        self._events[RELAY_GROUP][OFF_EVENT] = Event(
            OFF_EVENT, self._address, RELAY_GROUP
        )
        self._events[SENSOR_GROUP] = {}
        self._events[SENSOR_GROUP][OPEN_EVENT] = Event(
            OPEN_EVENT, self._address, SENSOR_GROUP
        )
        self._events[SENSOR_GROUP][CLOSE_EVENT] = Event(
            CLOSE_EVENT, self._address, SENSOR_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe to handelers and managers.

        The relay is controlled through group 1.
        The sensor and the relay both use group 1 to notify of changes. T
        When an on/off broadcast message is received, we need to check what the
        current status of the device is for both the relay and the sensor.
        """
        super()._subscribe_to_handelers_and_managers()
        switch_on_event = self._events[RELAY_GROUP][ON_EVENT]
        switch_off_event = self._events[RELAY_GROUP][OFF_EVENT]
        on_cmd = self._handlers[RELAY_GROUP][ON_COMMAND]
        off_cmd = self._handlers[RELAY_GROUP][OFF_COMMAND]
        switch_status_cmd = self._handlers[RELAY_GROUP][STATUS_REQUEST]

        on_cmd.subscribe(self._async_switch_changed)
        off_cmd.subscribe(self._async_switch_changed)
        on_cmd.subscribe(switch_on_event.trigger)
        off_cmd.subscribe(switch_off_event.trigger)
        switch_status_cmd.subscribe(self._handle_switch_status)

        self._managers[ON_LEVEL_MANAGER].subscribe(self._async_on_off_received)
        self._handlers[SENSOR_GROUP][STATUS_REQUEST].subscribe(
            self._handle_sensor_status
        )

    def _register_default_links(self):
        link = DefaultLink(
            is_controller=True,
            group=RELAY_GROUP,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        self._default_links.append(link)

    async def _async_switch_changed(self, on_level):
        """Catch on/off signal and fire appropriate response."""
        self._groups[RELAY_GROUP].value = on_level
        if on_level and self._operating_flags[MOMENTARY_MODE_ON].value:
            await self._delay_wait()

    def _calc_delay(self):
        """Calculate the momentary delay based on properties and flags."""
        delay = self._properties[DELAY].value
        delay = 255 if delay == 0 else delay
        if self._properties[PRESCALER].value is not None:
            prescaler = max(self._properties[PRESCALER].value, 1)
        else:
            prescaler = 1
        return delay * prescaler / 10

    async def _delay_wait(self):
        await asyncio.sleep(self._calc_delay())
        self._groups[RELAY_GROUP].value = 0
        self._events[RELAY_GROUP][OFF_EVENT].trigger(on_level=0)

    def _handle_switch_status(self, db_version, status):
        """Handle status response."""
        self._groups[RELAY_GROUP].set_value(status)

    def _handle_sensor_status(self, db_version, status):
        """Handle status response."""
        self._groups[SENSOR_GROUP].set_value(status)

    async def _async_on_off_received(self, on_level):
        """Process an on or off broadcast command."""
        orig_sensor = self._groups[SENSOR_GROUP].value
        orig_relay = self._groups[RELAY_GROUP].value

        # Need to get status since we don't know if the on/off message was for the relay
        # or the sensor. Get the sensor first since that is the most likely change.
        await self.async_sensor_status()
        if self._groups[SENSOR_GROUP].value != orig_sensor:
            if self._groups[SENSOR_GROUP].value:
                self._events[SENSOR_GROUP][OPEN_EVENT].trigger(on_level=255)
            else:
                self._events[SENSOR_GROUP][CLOSE_EVENT].trigger(on_level=0)

        await self.async_relay_status()
        if self._groups[RELAY_GROUP].value != orig_relay:
            if self._groups[RELAY_GROUP].value:
                self._events[RELAY_GROUP][ON_EVENT].trigger(on_level=255)
                if self._operating_flags[MOMENTARY_MODE_ON].value:
                    await self._delay_wait()
            else:
                self._events[RELAY_GROUP][OFF_EVENT].trigger(on_level=0)
