"""Termostat device types."""
import logging
from datetime import datetime
from ..aldb import ALDB
from ..default_link import DefaultLink
from ..groups import (
    COOL_SET_POINT,
    FAN_MODE,
    HEAT_SET_POINT,
    HUMIDITY_HIGH,
    HUMIDITY_LOW,
    SYSTEM_MODE,
    TEMPERATURE,
    HUMIDITY,
)
from ..extended_property import (
    BACKLIGHT,
    CHANGE_DELAY,
    TEMP_OFFSET,
    HUMIDITY_OFFSET,
)
from ..groups.thermostat import FanMode, Humidity, SystemMode, Temperature, SetPoint
from ..handlers.from_device.thermostat_status_response import (
    ThermostatStatusResponseHandler,
)
from ..handlers.from_device.thermostat_set_point_response import (
    ThermostatSetPointResponseHandler,
)
from ..handlers.from_device.thermostat_cool_set_point import (
    ThermostatCoolSetPointHandler,
)
from ..handlers.from_device.thermostat_heat_set_point import (
    ThermostatHeatSetPointHandler,
)
from ..handlers.from_device.thermostat_mode import ThermostatModeHandler
from ..handlers.from_device.thermostat_humidity import ThermostatHumidityHandler
from ..handlers.from_device.thermostat_temperature import ThermostatTemperatureHandler
from ..handlers.to_device.thermostat_cool_set_point import ThermostatCoolSetPointCommand
from ..handlers.to_device.thermostat_heat_set_point import ThermostatHeatSetPointCommand
from ..handlers.to_device.thermostat_mode import ThermostatModeCommand
from ..handlers.to_device.extended_set import ExtendedSetCommand
from ..handlers.to_device.extended_set_2 import ExtendedSet2Command
from ..managers.thermostat_status_manager import GetThermostatStatus
from ..operating_flag import (
    BUTTON_LOCK_ON,
    CELSIUS,
    KEY_BEEP_ON,
    LED_ON,
    PROGRAM_LOCK_ON,
    TIME_24_HOUR_FORMAT,
)
from .commands import STATUS_COMMAND
from .device_base import Device
from ..utils import multiple_status
from ..constants import ResponseStatus

_LOGGER = logging.getLogger(__name__)


class ClimateControl_Thermostat(Device):
    """Thermostat device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the Thermostat class."""
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
        )
        self._aldb = ALDB(self._address, mem_addr=0x1FFF)

    # pylint: disable=arguments-differ
    async def async_status(self, group=None):
        """Get the status of the device."""
        return await self._managers[STATUS_COMMAND].async_status()

    async def async_set_cool_set_point(self, temperature):
        """Set the cool set point."""
        temperature = max(1, min(temperature, 127))
        return await self._handlers["cool_set_point_command"].async_send(temperature)

    async def async_set_heat_set_point(self, temperature):
        """Set the cool set point."""
        temperature = max(1, min(temperature, 127))
        return await self._handlers["heat_set_point_command"].async_send(temperature)

    async def async_set_humidity_high_set_point(self, humidity):
        """Set the humdity high set point."""
        humidity = min(humidity, 99)
        cmd_status = await self._handlers["humidity_high_command"].async_send(humidity)
        if cmd_status == ResponseStatus.SUCCESS:
            self._groups[3].value = humidity
        return cmd_status

    async def async_set_humidity_low_set_point(self, humidity):
        """Set the humidity low set point."""
        humidity = max(humidity, 1)
        cmd_status = await self._handlers["humidity_low_command"].async_send(humidity)
        if cmd_status == ResponseStatus.SUCCESS:
            self._groups[4].value = humidity
        return cmd_status

    async def async_set_mode(self, mode):
        """Set the thermastat mode."""
        return await self._handlers["mode_command"].async_send(mode)

    async def async_set_master(self, master):
        """Set the thermastat master mode."""
        return await self._handlers["set_master"].async_send(master)

    async def async_set_notify_changes(self):
        """Set the thermostat to notify of changes."""
        return await self._handlers["notify_changes_command"].async_send()

    async def async_set_day_time(self):
        """Set the thermostat day of the week and time."""
        curr_time = datetime.now()
        day = 0 if curr_time.weekday() == 6 else curr_time.weekday() + 1
        set_time_command = ExtendedSet2Command(self._address, 0x02, day)
        return await set_time_command.async_send(
            data3=curr_time.hour, data4=curr_time.minute, data5=curr_time.second
        )

    async def async_add_default_links(self):
        """Add the default links betweent he modem and the device."""
        result_links = await super().async_add_default_links()
        result_notify = await self.async_set_notify_changes()
        return multiple_status(result_links, result_notify)

    def _register_operating_flags(self):
        """Register thermostat operating flags."""
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(KEY_BEEP_ON, 0, 1, 2, 3)
        self._add_operating_flag(BUTTON_LOCK_ON, 0, 2, 4, 5)
        self._add_operating_flag(CELSIUS, 0, 3, 6, 7)
        self._add_operating_flag(TIME_24_HOUR_FORMAT, 0, 4, 8, 9)
        # self._add_operating_flag(SOFTWARE_LOCK_ON, 0, 5, 0x0A, 0x0B)  # ?
        self._add_operating_flag(LED_ON, 0, 6, 0x0C, 0x0D)

        self._add_property(TEMP_OFFSET, 5, 2, 0)
        self._add_property(HUMIDITY_OFFSET, 6, 3, 0)
        self._add_property(BACKLIGHT, 9, 5, 0)
        self._add_property(CHANGE_DELAY, 10, 6, 0)

    def _register_groups(self):
        """Register the thermostat groups."""
        self._groups[1] = SetPoint(COOL_SET_POINT, self._address, group=1, default=65,)
        self._groups[2] = SetPoint(HEAT_SET_POINT, self._address, group=2, default=95,)
        self._groups[3] = Humidity(HUMIDITY_HIGH, self._address, group=3, default=0)
        self._groups[4] = Humidity(HUMIDITY_LOW, self._address, group=4, default=0)
        self._groups[10] = Temperature(
            TEMPERATURE, self._address, self._operating_flags[CELSIUS], 10, 0
        )
        self._groups[11] = Humidity(HUMIDITY, self._address, group=11, default=0)
        self._groups[12] = SystemMode(SYSTEM_MODE, self._address, group=12, default=0)
        self._groups[13] = FanMode(FAN_MODE, self._address, group=13, default=4)

    def _register_handlers_and_managers(self):
        """Register thermostat handlers and managers."""
        super()._register_handlers_and_managers()
        self._managers[STATUS_COMMAND] = GetThermostatStatus(self._address)
        self._handlers["status_response"] = ThermostatStatusResponseHandler(
            self._address
        )
        self._handlers["set_point_response"] = ThermostatSetPointResponseHandler(
            self._address
        )
        self._handlers["cool_set_point_handler"] = ThermostatCoolSetPointHandler(
            self._address
        )
        self._handlers["heat_set_point_handler"] = ThermostatHeatSetPointHandler(
            self._address
        )
        self._handlers["humidity_handler"] = ThermostatHumidityHandler(self._address)
        self._handlers["temperature_handler"] = ThermostatTemperatureHandler(
            self._address
        )
        self._handlers["mode_handler"] = ThermostatModeHandler(self._address)

        self._handlers["cool_set_point_command"] = ThermostatCoolSetPointCommand(
            self._address
        )
        self._handlers["heat_set_point_command"] = ThermostatHeatSetPointCommand(
            self._address
        )
        self._handlers["mode_command"] = ThermostatModeCommand(self._address)
        self._handlers["notify_changes_command"] = ExtendedSetCommand(
            self._address, 0x00, 0x08
        )
        self._handlers["humidity_high_command"] = ExtendedSetCommand(
            self._address, 0x00, 0x0B
        )
        self._handlers["humidity_low_command"] = ExtendedSetCommand(
            self._address, 0x00, 0x0C
        )
        self._handlers["set_master"] = ExtendedSetCommand(self._address, 0x00, 0x09)

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        self._handlers["status_response"].subscribe(self._status_received)
        self._handlers["set_point_response"].subscribe(self._set_point_received)
        self._handlers["cool_set_point_handler"].subscribe(self._groups[1].set_value)
        self._handlers["heat_set_point_handler"].subscribe(self._groups[2].set_value)
        self._handlers["humidity_handler"].subscribe(self._groups[11].set_value)
        self._handlers["temperature_handler"].subscribe(self._temp_received)
        self._handlers["mode_handler"].subscribe(self._mode_received)
        self._operating_flags[CELSIUS].subscribe(self._temp_format_changed)

    def _register_default_links(self):
        """Register default links."""
        super()._register_default_links()
        link_1 = DefaultLink(
            is_controller=True,
            group=1,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0x01,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0x01,
        )
        link_2 = DefaultLink(
            is_controller=True,
            group=2,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0x02,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0x02,
        )
        link_3 = DefaultLink(
            is_controller=True,
            group=3,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0x03,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0x03,
        )
        link_4 = DefaultLink(
            is_controller=True,
            group=4,
            dev_data1=0,
            dev_data2=0,
            dev_data3=0x04,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0x04,
        )
        link_ef = DefaultLink(
            is_controller=True,
            group=0xEF,
            dev_data1=0x03,
            dev_data2=0,
            dev_data3=0xEF,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0xEF,
        )
        self._default_links.append(link_1)
        self._default_links.append(link_2)
        self._default_links.append(link_3)
        self._default_links.append(link_4)
        self._default_links.append(link_ef)

    def _status_received(
        self,
        day,
        hour,
        minute,
        second,
        system_mode,
        fan_mode,
        cool_set_point,
        humidity,
        temperature,
        status_flag,
        heat_set_point,
    ):
        """Receive the status update."""
        self._groups[12].set_value(system_mode)
        self._groups[13].set_value(fan_mode)
        self._groups[1].set_value(cool_set_point)
        self._groups[2].set_value(heat_set_point)
        self._groups[10].set_value(temperature)
        self._groups[11].set_value(humidity)

    def _set_point_received(
        self,
        stage_1_on_minutes,
        humidity_high,
        humidity_low,
        firmwire,
        cool_set_point,
        heat_set_point,
        rf_offset,
    ):
        """Receive set point info."""
        self._groups[1].set_value(cool_set_point)
        self._groups[2].set_value(heat_set_point)
        self._groups[3].set_value(humidity_high)
        self._groups[4].set_value(humidity_low)

    def _mode_received(self, system_mode, fan_mode):
        """Receive current temperature notification."""
        self._groups[12].set_value(system_mode)
        self._groups[13].set_value(fan_mode)

    def _temp_received(self, degrees):
        """Receive temperature status update and convert to celsius if needed."""
        # if not self._operating_flags[CELSIUS].value:
        #     degrees = to_celsius(degrees)
        self._groups[10].value = degrees

    def _temp_format_changed(self, name, value):
        """Recieve notification that the thermostat has changed to/from C/F."""
        self.status()
