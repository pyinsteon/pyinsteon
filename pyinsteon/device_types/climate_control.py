"""Termostat device types."""
import logging
from datetime import datetime
from ..aldb import ALDB
from ..aldb.aldb_battery import ALDBBattery
from ..default_link import DefaultLink
from ..groups import (
    COOL_SET_POINT,
    COOLING,
    DEHUMIDIFYING,
    FAN_MODE,
    HEAT_SET_POINT,
    HEATING,
    HUMIDIFYING,
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
from ..groups.on_off import OnOff
from ..managers.on_level_manager import OnLevelManager
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
from .battery_base import BatteryDeviceBase
from ..utils import multiple_status, to_fahrenheit, set_bit
from ..constants import ResponseStatus

_LOGGER = logging.getLogger(__name__)

GRP_COOL_ON = 1
GRP_HEAT_ON = 2
GRP_HUMID_HI_ON = 3
GRP_HUMID_LO_ON = 4
GRP_NOTIFY = 0xEF

GRP_TEMP = 10
GRP_HUMID = 11
GRP_SYS_MODE = 12
GRP_FAN_MODE = 13
GRP_COOL_SP = 14
GRP_HEAT_SP = 15
GRP_HUMID_HI_SP = 16
GRP_HUMID_LO_SP = 17

OP_FLAG_POS = 13


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
            self._groups[GRP_HUMID_HI_SP].value = humidity
        return cmd_status

    async def async_set_humidity_low_set_point(self, humidity):
        """Set the humidity low set point."""
        humidity = max(humidity, 1)
        cmd_status = await self._handlers["humidity_low_command"].async_send(humidity)
        if cmd_status == ResponseStatus.SUCCESS:
            self._groups[GRP_HUMID_LO_SP].value = humidity
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

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        flags = 0x00
        for flag_name in self._ext_property_manager.flag_info:
            flag_info = self._ext_property_manager.flag_info[flag_name]
            if flag_info.data_field == OP_FLAG_POS:
                flag = self.properties[flag_name]
                value = flag.new_value if flag.is_dirty else flag.value
                flags = set_bit(flags, flag_info.bit, bool(value))
        result = await self._handlers["op_flag_write"].async_send(data4=flags)
        if result == ResponseStatus.SUCCESS:
            for flag_name in self._ext_property_manager.flag_info:
                flag_info = self._ext_property_manager.flag_info[flag_name]
                if flag_info.data_field == OP_FLAG_POS:
                    flag = self.properties[flag_name]
                    if flag.is_dirty:
                        flag.load(flag.new_value)
        return result

    def _register_operating_flags(self):
        """Register thermostat operating flags."""
        self._add_property(PROGRAM_LOCK_ON, OP_FLAG_POS, None, 0, 0)
        self._add_property(KEY_BEEP_ON, OP_FLAG_POS, None, 0, 1)
        self._add_property(BUTTON_LOCK_ON, OP_FLAG_POS, None, 0, 2)
        self._add_property(CELSIUS, OP_FLAG_POS, None, 0, 3)
        self._add_property(TIME_24_HOUR_FORMAT, OP_FLAG_POS, None, 0, 4)
        self._add_property(LED_ON, OP_FLAG_POS, None, 0, 6)

        self._add_property(TEMP_OFFSET, 5, 2, 0)
        self._add_property(HUMIDITY_OFFSET, 6, 3, 0)
        self._add_property(BACKLIGHT, 9, 5, 0)
        self._add_property(CHANGE_DELAY, 10, 6, 0)

    def _register_groups(self):
        """Register the thermostat groups."""
        self._groups[GRP_COOL_ON] = OnOff(COOLING, self._address, GRP_COOL_ON)
        self._groups[GRP_HEAT_ON] = OnOff(HEATING, self._address, GRP_HEAT_ON)
        self._groups[GRP_HUMID_HI_ON] = OnOff(
            DEHUMIDIFYING, self._address, GRP_HUMID_HI_ON
        )
        self._groups[GRP_HUMID_LO_ON] = OnOff(
            HUMIDIFYING, self._address, GRP_HUMID_LO_ON
        )

        self._groups[GRP_TEMP] = Temperature(TEMPERATURE, self._address, GRP_TEMP, 0)
        self._groups[GRP_HUMID] = Humidity(
            HUMIDITY, self._address, group=GRP_HUMID, default=0
        )
        self._groups[GRP_SYS_MODE] = SystemMode(
            SYSTEM_MODE, self._address, group=GRP_SYS_MODE, default=0
        )
        self._groups[GRP_FAN_MODE] = FanMode(
            FAN_MODE, self._address, group=GRP_FAN_MODE, default=4
        )
        self._groups[GRP_COOL_SP] = SetPoint(
            COOL_SET_POINT, self._address, group=GRP_COOL_SP, default=65,
        )
        self._groups[GRP_HEAT_SP] = SetPoint(
            HEAT_SET_POINT, self._address, group=GRP_HEAT_SP, default=95,
        )
        self._groups[GRP_HUMID_HI_SP] = Humidity(
            HUMIDITY_HIGH, self._address, group=GRP_HUMID_HI_SP, default=0
        )
        self._groups[GRP_HUMID_LO_SP] = Humidity(
            HUMIDITY_LOW, self._address, group=GRP_HUMID_LO_SP, default=0
        )

    def _register_handlers_and_managers(self):
        """Register thermostat handlers and managers."""
        super()._register_handlers_and_managers()
        self._managers[GRP_COOL_ON] = OnLevelManager(self._address, GRP_COOL_ON, 0x00)
        self._managers[GRP_HEAT_ON] = OnLevelManager(self._address, GRP_HEAT_ON, 0x00)
        self._managers[GRP_HUMID_HI_ON] = OnLevelManager(
            self._address, GRP_HUMID_HI_ON, 0x00
        )
        self._managers[GRP_HUMID_LO_ON] = OnLevelManager(
            self._address, GRP_HUMID_LO_ON, 0x00
        )

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

        self._handlers["op_flag_write"] = ExtendedSetCommand(self._address, 0x00, 0x04)

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        self._managers[GRP_COOL_ON].subscribe(self._groups[GRP_COOL_ON].set_value)
        self._managers[GRP_HEAT_ON].subscribe(self._groups[GRP_HEAT_ON].set_value)
        self._managers[GRP_HUMID_HI_ON].subscribe(
            self._groups[GRP_HUMID_HI_ON].set_value
        )
        self._managers[GRP_HUMID_LO_ON].subscribe(
            self._groups[GRP_HUMID_LO_ON].set_value
        )

        self._handlers["status_response"].subscribe(self._status_received)
        self._handlers["set_point_response"].subscribe(self._set_point_received)
        self._handlers["cool_set_point_handler"].subscribe(
            self._groups[GRP_COOL_SP].set_value
        )
        self._handlers["heat_set_point_handler"].subscribe(
            self._groups[GRP_HEAT_SP].set_value
        )
        self._handlers["humidity_handler"].subscribe(self._groups[GRP_HUMID].set_value)
        self._handlers["temperature_handler"].subscribe(self._temp_received)
        self._handlers["mode_handler"].subscribe(self._mode_received)
        self._properties[CELSIUS].subscribe(self._temp_format_first_set)

    def _register_default_links(self):
        """Register default links."""
        super()._register_default_links()
        link_1 = DefaultLink(
            is_controller=True,
            group=GRP_COOL_ON,
            dev_data1=0,
            dev_data2=0,
            dev_data3=GRP_COOL_ON,
            modem_data1=0,
            modem_data2=0,
            modem_data3=GRP_COOL_ON,
        )
        link_2 = DefaultLink(
            is_controller=True,
            group=GRP_HEAT_ON,
            dev_data1=0,
            dev_data2=0,
            dev_data3=GRP_HEAT_ON,
            modem_data1=0,
            modem_data2=0,
            modem_data3=GRP_HEAT_ON,
        )
        link_3 = DefaultLink(
            is_controller=True,
            group=GRP_HUMID_HI_ON,
            dev_data1=0,
            dev_data2=0,
            dev_data3=GRP_HUMID_HI_ON,
            modem_data1=0,
            modem_data2=0,
            modem_data3=GRP_HUMID_HI_ON,
        )
        link_4 = DefaultLink(
            is_controller=True,
            group=GRP_HUMID_LO_ON,
            dev_data1=0,
            dev_data2=0,
            dev_data3=GRP_HUMID_LO_ON,
            modem_data1=0,
            modem_data2=0,
            modem_data3=GRP_HUMID_LO_ON,
        )
        link_ef = DefaultLink(
            is_controller=True,
            group=GRP_NOTIFY,
            dev_data1=0x03,
            dev_data2=0,
            dev_data3=GRP_NOTIFY,
            modem_data1=0,
            modem_data2=0,
            modem_data3=GRP_NOTIFY,
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
        cooling,
        heating,
        celsius,
        heat_set_point,
    ):
        """Receive the status update."""
        self._groups[GRP_COOL_ON].set_value(cooling)
        self._groups[GRP_HEAT_ON].set_value(heating)
        self._groups[GRP_SYS_MODE].set_value(system_mode)
        self._groups[GRP_FAN_MODE].set_value(fan_mode)
        self._groups[GRP_COOL_SP].set_value(cool_set_point)
        self._groups[GRP_HEAT_SP].set_value(heat_set_point)
        if not self._properties[CELSIUS].value:
            temperature = to_fahrenheit(temperature)
        self._groups[GRP_TEMP].set_value(temperature)
        self._groups[GRP_HUMID].set_value(humidity)

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
        self._groups[GRP_COOL_SP].set_value(cool_set_point)
        self._groups[GRP_HEAT_SP].set_value(heat_set_point)
        self._groups[GRP_HUMID_HI_SP].set_value(humidity_high)
        self._groups[GRP_HUMID_LO_SP].set_value(humidity_low)

    def _mode_received(self, system_mode, fan_mode):
        """Receive current temperature notification."""
        self._groups[GRP_SYS_MODE].set_value(system_mode)
        self._groups[GRP_FAN_MODE].set_value(fan_mode)

    def _temp_received(self, degrees):
        """Receive temperature status update and convert to celsius if needed."""
        self._groups[GRP_TEMP].value = degrees

    def _temp_format_changed(self, name, value):
        """Recieve notification that the thermostat has changed to/from C/F."""
        self.status()

    def _temp_format_first_set(self, name, value):
        """Set up the trigger for a temperature format change.

        The first time the format is set, we don't need to do anything. If
        the format changes later, we need to get the status update to change the
        measurements from F to C or vise versa.
        """
        self._properties[CELSIUS].unsubscribe(self._temp_format_first_set)
        self._properties[CELSIUS].unsubscribe(self._temp_format_changed)


class ClimateControl_WirelessThermostat(BatteryDeviceBase, ClimateControl_Thermostat):
    """Wireless Thermostat device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the Wireless Thermostat class."""
        super(ClimateControl_WirelessThermostat, self).__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
        )
        self._aldb = ALDBBattery(
            address=address, mem_addr=0x1FFF, run_command=self._run_on_wake
        )

    async def async_set_humidity_high_set_point(self, humidity):
        """Set the humdity high set point."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_humidity_high_set_point,
            humidity=humidity,
        )

    async def async_set_humidity_low_set_point(self, humidity):
        """Set the humidity low set point."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_humidity_low_set_point,
            humidity=humidity,
        )

    async def async_set_master(self, master):
        """Set the thermastat master mode."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_master, master=master
        )

    async def async_set_mode(self, mode):
        """Set the thermastat mode."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_mode, mode=mode
        )

    async def async_set_notify_changes(self):
        """Set the thermostat to notify of changes."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_notify_changes
        )

    async def async_set_cool_set_point(self, temperature):
        """Set the cool set point."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_cool_set_point,
            temperature=temperature,
        )

    async def async_set_day_time(self):
        """Set the thermostat day of the week and time."""
        return self._run_on_wake(super(BatteryDeviceBase, self).async_set_day_time)

    async def async_set_heat_set_point(self, temperature):
        """Set the cool set point."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_set_heat_set_point,
            temperature=temperature,
        )
