"""Collection of topics mapped to commands (cmd1, cmd2)."""
import logging
from collections import namedtuple
from typing import Iterable

from ..topics import (
    ALL_LINK_CLEANUP_STATUS_REPORT,
    ASSIGN_TO_ALL_LINK_GROUP,
    ASSIGN_TO_COMPANION_GROUP,
    BEEP,
    BRIGHTEN_ONE_STEP,
    DELETE_FROM_ALL_LINK_GROUP,
    DEVICE_TEXT_STRING_REQUEST,
    DIM_ONE_STEP,
    DOOR_MOVE_CLOSE_DOOR,
    DOOR_MOVE_LOWER_DOOR,
    DOOR_MOVE_OPEN_DOOR,
    DOOR_MOVE_RAISE_DOOR,
    DOOR_MOVE_SINGLE_DOOR_CLOSE,
    DOOR_MOVE_SINGLE_DOOR_OPEN,
    DOOR_MOVE_STOP_DOOR,
    DOOR_STATUS_REPORT_CLOSE_DOOR,
    DOOR_STATUS_REPORT_LOWER_DOOR,
    DOOR_STATUS_REPORT_OPEN_DOOR,
    DOOR_STATUS_REPORT_RAISE_DOOR,
    DOOR_STATUS_REPORT_SINGLE_DOOR_CLOSE,
    DOOR_STATUS_REPORT_SINGLE_DOOR_OPEN,
    DOOR_STATUS_REPORT_STOP_DOOR,
    ENTER_LINKING_MODE,
    ENTER_UNLINKING_MODE,
    EXTENDED_GET_RESPONSE,
    EXTENDED_GET_SET,
    EXTENDED_GET_SET_2,
    EXTENDED_READ_WRITE_ALDB,
    EXTENDED_RECEIVED,
    EXTENDED_TRIGGER_ALL_LINK,
    FX_USERNAME,
    GET_INSTEON_ENGINE_VERSION,
    GET_OPERATING_FLAGS,
    ID_REQUEST,
    INSTANT_CHANGE,
    IO_ALARM_DATA_REQUEST,
    IO_ALARM_DATA_RESPONSE,
    IO_GET_SENSOR_ALARM_DELTA,
    IO_GET_SENSOR_VALUE,
    IO_MODULE_DIAGNOSTICS_OFF,
    IO_MODULE_DIAGNOSTICS_ON,
    IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE,
    IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE,
    IO_MODULE_LOAD_EEPROM_FROM_RAM,
    IO_MODULE_LOAD_INITIALIZATION_VALUES,
    IO_MODULE_LOAD_RAM_FROM_EEPROM,
    IO_MODULE_READ_ANALOG_ALWAYS,
    IO_MODULE_READ_ANALOG_ONCE,
    IO_MODULE_SENSOR_OFF,
    IO_MODULE_SENSOR_ON,
    IO_MODULE_STATUS_REQUEST,
    IO_OUTPUT_OFF,
    IO_OUTPUT_ON,
    IO_READ_CONFIGURATION_PORT,
    IO_READ_INPUT_PORT,
    IO_SET_SENSOR_1_NOMINAL_VALUE,
    IO_SET_SENSOR_NOMINAL_VALUE,
    IO_WRITE_CONFIGURATION_PORT,
    IO_WRITE_OUTPUT_PORT,
    LEAK_DETECTOR_ANNOUNCE,
    MANUALLY_TURNED_OFF,
    MANUALLY_TURNED_ON,
    OFF,
    OFF_AT_RAMP_RATE,
    OFF_FAST,
    ON,
    ON_AT_RAMP_RATE,
    ON_FAST,
    PEEK_ONE_BYTE,
    PEEK_ONE_BYTE_INTERNAL,
    PING,
    POKE_ONE_BYTE,
    POKE_ONE_BYTE_INTERNAL,
    POOL_DEVICE_OFF,
    POOL_DEVICE_ON,
    POOL_GET_AMBIENT_TEMPERATURE,
    POOL_GET_PH,
    POOL_GET_POOL_MODE,
    POOL_GET_WATER_TEMPERATURE,
    POOL_LOAD_EEPROM_FROM_RAM,
    POOL_LOAD_INITIALIZATION_VALUES,
    POOL_SET_DEVICE_HYSTERESIS,
    POOL_SET_DEVICE_TEMPERATURE,
    POOL_TEMPERATURE_DOWN,
    POOL_TEMPERATURE_UP,
    PRODUCT_DATA_REQUEST,
    REMOTE_SET_BUTTON_TAP1_TAP,
    REMOTE_SET_BUTTON_TAP2_TAP,
    SEND_EXTENDED,
    SEND_STANDARD,
    SET_ADDRESS_MSB,
    SET_ALL_LINK,
    SET_ALL_LINK_COMMAND_ALIAS,
    SET_DEVICE_TEXT_STRING,
    SET_OPERATING_FLAGS,
    SET_SPRINKLER_PROGRAM,
    SET_STATUS,
    SPRINKLER_BROADCAST_OFF,
    SPRINKLER_BROADCAST_ON,
    SPRINKLER_DIAGNOSTICS_OFF,
    SPRINKLER_DIAGNOSTICS_ON,
    SPRINKLER_DISABLE_PUMP_ON_V8,
    SPRINKLER_ENABLE_PUMP_ON_V8,
    SPRINKLER_GET_PROGRAM_REQUEST,
    SPRINKLER_GET_PROGRAM_RESPONSE,
    SPRINKLER_GET_VALVE_STATUS,
    SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE,
    SPRINKLER_LOAD_EEPROM_FROM_RAM,
    SPRINKLER_LOAD_INITIALIZATION_VALUES,
    SPRINKLER_LOAD_RAM_FROM_EEPROM,
    SPRINKLER_PROGRAM_OFF,
    SPRINKLER_PROGRAM_ON,
    SPRINKLER_RESUME_COMMAND_ACCEPTANCE,
    SPRINKLER_SENSOR_OFF,
    SPRINKLER_SENSOR_ON,
    SPRINKLER_SKIP_BACK,
    SPRINKLER_SKIP_FORWARD,
    SPRINKLER_VALVE_OFF,
    SPRINKLER_VALVE_ON,
    STANDARD_RECEIVED,
    START_MANUAL_CHANGE_DOWN,
    START_MANUAL_CHANGE_UP,
    STATUS_REQUEST,
    STOP_MANUAL_CHANGE,
    THERMOSTAT_CONTROL,
    THERMOSTAT_COOL_SET_POINT_STATUS,
    THERMOSTAT_GET_ZONE_INFORMATION,
    THERMOSTAT_HEAT_SET_POINT_STATUS,
    THERMOSTAT_HUMIDITY_STATUS,
    THERMOSTAT_MODE_STATUS,
    THERMOSTAT_SET_COOL_SETPOINT,
    THERMOSTAT_SET_HEAT_SETPOINT,
    THERMOSTAT_SET_POINT_RESPONSE,
    THERMOSTAT_SET_ZONE_COOL_SETPOINT,
    THERMOSTAT_SET_ZONE_HEAT_SETPOINT,
    THERMOSTAT_STATUS_RESPONSE,
    THERMOSTAT_TEMPERATURE_DOWN,
    THERMOSTAT_TEMPERATURE_STATUS,
    THERMOSTAT_TEMPERATURE_UP,
    THERMOSTAT_ZONE_TEMPERATURE_DOWN,
    THERMOSTAT_ZONE_TEMPERATURE_UP,
    WINDOW_COVERING_CLOSE,
    WINDOW_COVERING_OPEN,
    WINDOW_COVERING_POSITION,
    WINDOW_COVERING_PROGRAM,
    WINDOW_COVERING_STOP,
)

Command = namedtuple("Command", "cmd1 cmd2 user_data")
_LOGGER = logging.getLogger(__name__)


def _check_user_data_match(cmd_ud, user_data):
    """Check if the command user_data matches the input user_data."""
    if cmd_ud is None:
        return True
    if not user_data and not cmd_ud:
        return True
    if user_data and not cmd_ud:
        return False
    if cmd_ud and not user_data:
        return False
    for field in cmd_ud:
        if cmd_ud[field] != user_data.get(field):
            return False
    return True


def _check_match(command, cmd1, cmd2, user_data):
    """Check if the current command matches the input values."""
    if command.cmd1 != cmd1:
        return False
    cmd2_match = cmd2 is None or command.cmd2 is None or command.cmd2 == cmd2
    user_data_match = _check_user_data_match(command.user_data, user_data)
    return cmd2_match and user_data_match


class Commands:
    """List of topics and commands."""

    def __init__(self):
        """Init the Commands class."""
        self._topics = {}
        self._commands = {}
        self._use_group = {}

    def add(
        self,
        topic: str,
        cmd1: int,
        cmd2: int,
        user_data: Iterable,
        use_group: bool = False,
    ):
        """Add a command to the list."""
        self._topics[topic] = Command(cmd1, cmd2, user_data)
        self._use_group[topic] = use_group

    def get(self, topic: str):
        """Get the command elements of teh topic."""
        return self._topics.get(topic)

    def get_command(self, topic: str) -> (int, int, bool):
        """Get cmd1 and cmd2 from a topic.

        Returns (cmd1, cmd2, extended)
        """
        return self._topics.get(topic)

    def use_group(self, topic):
        """Return if a topic requires a group number."""
        return self._use_group.get(topic)

    def get_topics(self, cmd1, cmd2, user_data=None, send=False) -> str:
        """Generate a topic from a cmd1, cmd2 and extended flag."""
        found = False
        for topic in self._topics:
            command = self._topics[topic]
            if _check_match(command, cmd1, cmd2, user_data):
                found = True
                yield topic
        if not found:
            if user_data is None:
                yield SEND_STANDARD if send else STANDARD_RECEIVED
            else:
                yield SEND_EXTENDED if send else EXTENDED_RECEIVED


commands = Commands()


commands.add(STANDARD_RECEIVED, -1, None, False)
commands.add(EXTENDED_RECEIVED, -1, None, True)
commands.add(SEND_STANDARD, -2, None, False)
commands.add(SEND_EXTENDED, -2, None, {})
commands.add(ASSIGN_TO_ALL_LINK_GROUP, 0x01, None, False)
commands.add(DELETE_FROM_ALL_LINK_GROUP, 0x02, None, False)
commands.add(PRODUCT_DATA_REQUEST, 0x03, 0x00, None)
commands.add(FX_USERNAME, 0x03, 0x01, False)
commands.add(DEVICE_TEXT_STRING_REQUEST, 0x03, 0x02, False)
commands.add(SET_DEVICE_TEXT_STRING, 0x03, 0x03, {})
commands.add(SET_ALL_LINK_COMMAND_ALIAS, 0x03, 0x04, {})
commands.add(SET_ALL_LINK, 0x03, 0x04, {})
commands.add(ALL_LINK_CLEANUP_STATUS_REPORT, 0x06, None, None, True)
commands.add(ENTER_LINKING_MODE, 0x09, None, None)
commands.add(ENTER_UNLINKING_MODE, 0x0A, None, False)
commands.add(GET_INSTEON_ENGINE_VERSION, 0x0D, None, False)
commands.add(PING, 0x0F, None, False)
commands.add(ID_REQUEST, 0x10, None, False)
commands.add(ON, 0x11, None, None, True)
commands.add(ON_FAST, 0x12, None, None, True)
commands.add(OFF, 0x13, None, None, True)
commands.add(OFF_FAST, 0x14, None, None, True)
commands.add(BRIGHTEN_ONE_STEP, 0x15, None, False, True)
commands.add(DIM_ONE_STEP, 0x16, None, False, True)
commands.add(START_MANUAL_CHANGE_DOWN, 0x17, 0x00, False, True)
commands.add(START_MANUAL_CHANGE_UP, 0x17, 0x01, False, True)
commands.add(STOP_MANUAL_CHANGE, 0x18, None, False, True)
commands.add(STATUS_REQUEST, 0x19, None, None)
commands.add(GET_OPERATING_FLAGS, 0x1F, None, False)
commands.add(SET_OPERATING_FLAGS, 0x20, None, None)
commands.add(INSTANT_CHANGE, 0x21, None, False, True)
commands.add(MANUALLY_TURNED_OFF, 0x22, None, False, True)
commands.add(MANUALLY_TURNED_ON, 0x23, None, False, True)
commands.add(REMOTE_SET_BUTTON_TAP1_TAP, 0x25, 0x01, False)
commands.add(REMOTE_SET_BUTTON_TAP2_TAP, 0x25, 0x02, False)
commands.add(SET_STATUS, 0x27, None, False)
commands.add(SET_ADDRESS_MSB, 0x28, None, False)
commands.add(POKE_ONE_BYTE, 0x29, None, False)
commands.add(PEEK_ONE_BYTE, 0x2B, None, False)
commands.add(PEEK_ONE_BYTE_INTERNAL, 0x2C, None, False)
commands.add(POKE_ONE_BYTE_INTERNAL, 0x2D, None, False)

# cmd2 ne 0x00 => no confict w/ EXTENDED_GET_SET
# Conflict w/ THERMOSTAT_EXTENDED_STATUS but thermostat has no ramp rate so OK
commands.add(ON_AT_RAMP_RATE, 0x2E, None, False, True)
# direct is ed and direct_ack is sd
commands.add(EXTENDED_GET_SET, 0x2E, 0x00, None)
commands.add(EXTENDED_GET_RESPONSE, 0x2E, 0x00, {"d2": 0x01})
commands.add(
    THERMOSTAT_SET_POINT_RESPONSE, 0x2E, 0x00, {"d1": 0x00, "d2": 0x01, "d3": 0x01}
)
commands.add(EXTENDED_GET_SET_2, 0x2E, 0x02, None)
commands.add(THERMOSTAT_STATUS_RESPONSE, 0x2E, 0x02, {"d1": 0x01})

# cmd2 ne 0x00 => no confict w/ read aldb
commands.add(OFF_AT_RAMP_RATE, 0x2F, None, False, True)
# direct is ed and direct_ack is sd
commands.add(EXTENDED_READ_WRITE_ALDB, 0x2F, 0x00, None)
commands.add(EXTENDED_TRIGGER_ALL_LINK, 0x30, None, None)

commands.add(BEEP, 0x30, None, None)
commands.add(SET_SPRINKLER_PROGRAM, 0x40, None, True)
commands.add(SPRINKLER_VALVE_ON, 0x40, None, False)
commands.add(SPRINKLER_GET_PROGRAM_RESPONSE, 0x41, None, True)
commands.add(SPRINKLER_VALVE_OFF, 0x41, None, False)
commands.add(SPRINKLER_PROGRAM_ON, 0x42, None, None)
commands.add(SPRINKLER_PROGRAM_OFF, 0x43, None, None)
commands.add(SPRINKLER_LOAD_INITIALIZATION_VALUES, 0x44, 0x00, False)
commands.add(SPRINKLER_LOAD_EEPROM_FROM_RAM, 0x44, 0x01, False)
commands.add(SPRINKLER_GET_VALVE_STATUS, 0x44, 0x02, False)
commands.add(SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE, 0x44, 0x03, False)
commands.add(SPRINKLER_RESUME_COMMAND_ACCEPTANCE, 0x44, 0x04, False)
commands.add(SPRINKLER_SKIP_FORWARD, 0x44, 0x05, False)
commands.add(SPRINKLER_SKIP_BACK, 0x44, 0x06, False)
commands.add(SPRINKLER_ENABLE_PUMP_ON_V8, 0x44, 0x07, False)
commands.add(SPRINKLER_DISABLE_PUMP_ON_V8, 0x44, 0x08, False)
commands.add(SPRINKLER_BROADCAST_ON, 0x44, 0x09, False)
commands.add(SPRINKLER_BROADCAST_OFF, 0x44, 0x0A, False)
commands.add(SPRINKLER_LOAD_RAM_FROM_EEPROM, 0x44, 0x0B, False)
commands.add(SPRINKLER_SENSOR_ON, 0x44, 0x0C, False)
commands.add(SPRINKLER_SENSOR_OFF, 0x44, 0x0D, False)
commands.add(SPRINKLER_DIAGNOSTICS_ON, 0x44, 0x0E, False)
commands.add(SPRINKLER_DIAGNOSTICS_OFF, 0x44, 0x0F, False)
commands.add(SPRINKLER_GET_PROGRAM_REQUEST, 0x45, None, False)
commands.add(IO_OUTPUT_ON, 0x45, None, False)
commands.add(IO_OUTPUT_OFF, 0x46, None, False)
commands.add(IO_ALARM_DATA_REQUEST, 0x47, 0x00, False)
commands.add(IO_WRITE_OUTPUT_PORT, 0x48, None, False)
commands.add(IO_READ_INPUT_PORT, 0x49, 0x00, False)
commands.add(IO_GET_SENSOR_VALUE, 0x4A, None, False)
commands.add(IO_SET_SENSOR_1_NOMINAL_VALUE, 0x4B, None, False)
commands.add(IO_SET_SENSOR_NOMINAL_VALUE, 0x4B, None, True)
commands.add(IO_GET_SENSOR_ALARM_DELTA, 0x4C, None, False)
commands.add(IO_ALARM_DATA_RESPONSE, 0x4C, 0x00, {})
commands.add(IO_WRITE_CONFIGURATION_PORT, 0x4D, None, False)
commands.add(IO_READ_CONFIGURATION_PORT, 0x4E, 0x00, False)
commands.add(IO_MODULE_LOAD_INITIALIZATION_VALUES, 0x4F, 0x00, False)
commands.add(IO_MODULE_LOAD_EEPROM_FROM_RAM, 0x4F, 0x01, False)
commands.add(IO_MODULE_STATUS_REQUEST, 0x4F, 0x02, False)
commands.add(IO_MODULE_READ_ANALOG_ONCE, 0x4F, 0x03, False)
commands.add(IO_MODULE_READ_ANALOG_ALWAYS, 0x4F, 0x04, False)
commands.add(IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE, 0x4F, 0x09, False)
commands.add(IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE, 0x4F, 0x0A, False)
commands.add(IO_MODULE_LOAD_RAM_FROM_EEPROM, 0x4F, 0x0B, False)
commands.add(IO_MODULE_SENSOR_ON, 0x4F, 0x0C, False)
commands.add(IO_MODULE_SENSOR_OFF, 0x4F, 0x0D, False)
commands.add(IO_MODULE_DIAGNOSTICS_ON, 0x4F, 0x0E, False)
commands.add(IO_MODULE_DIAGNOSTICS_OFF, 0x4F, 0x0F, False)
commands.add(POOL_DEVICE_ON, 0x50, None, False)
commands.add(POOL_SET_DEVICE_TEMPERATURE, 0x50, None, {})
commands.add(POOL_DEVICE_OFF, 0x51, None, False)
commands.add(POOL_SET_DEVICE_HYSTERESIS, 0x51, None, {})
commands.add(POOL_TEMPERATURE_UP, 0x52, None, False)
commands.add(POOL_TEMPERATURE_DOWN, 0x53, None, False)
commands.add(POOL_LOAD_INITIALIZATION_VALUES, 0x54, 0x00, False)
commands.add(POOL_LOAD_EEPROM_FROM_RAM, 0x54, 0x01, False)
commands.add(POOL_GET_POOL_MODE, 0x54, 0x02, False)
commands.add(POOL_GET_AMBIENT_TEMPERATURE, 0x54, 0x03, False)
commands.add(POOL_GET_WATER_TEMPERATURE, 0x54, 0x04, False)
commands.add(POOL_GET_PH, 0x54, 0x05, False)
commands.add(DOOR_MOVE_RAISE_DOOR, 0x58, 0x00, False)
commands.add(DOOR_MOVE_LOWER_DOOR, 0x58, 0x01, False)
commands.add(DOOR_MOVE_OPEN_DOOR, 0x58, 0x02, False)
commands.add(DOOR_MOVE_CLOSE_DOOR, 0x58, 0x03, False)
commands.add(DOOR_MOVE_STOP_DOOR, 0x58, 0x04, False)
commands.add(DOOR_MOVE_SINGLE_DOOR_OPEN, 0x58, 0x05, False)
commands.add(DOOR_MOVE_SINGLE_DOOR_CLOSE, 0x58, 0x06, False)
commands.add(DOOR_STATUS_REPORT_RAISE_DOOR, 0x59, 0x00, False)
commands.add(DOOR_STATUS_REPORT_LOWER_DOOR, 0x59, 0x01, False)
commands.add(DOOR_STATUS_REPORT_OPEN_DOOR, 0x59, 0x02, False)
commands.add(DOOR_STATUS_REPORT_CLOSE_DOOR, 0x59, 0x03, False)
commands.add(DOOR_STATUS_REPORT_STOP_DOOR, 0x59, 0x04, False)
commands.add(DOOR_STATUS_REPORT_SINGLE_DOOR_OPEN, 0x59, 0x05, False)
commands.add(DOOR_STATUS_REPORT_SINGLE_DOOR_CLOSE, 0x59, 0x06, False)
commands.add(WINDOW_COVERING_OPEN, 0x60, 0x01, False)
commands.add(WINDOW_COVERING_CLOSE, 0x60, 0x02, False)
commands.add(WINDOW_COVERING_STOP, 0x60, 0x03, False)
commands.add(WINDOW_COVERING_PROGRAM, 0x60, 0x04, False)
commands.add(WINDOW_COVERING_POSITION, 0x61, None, False)
commands.add(THERMOSTAT_TEMPERATURE_UP, 0x68, None, False)
commands.add(THERMOSTAT_ZONE_TEMPERATURE_UP, 0x68, None, {})
commands.add(THERMOSTAT_TEMPERATURE_DOWN, 0x69, None, False)
commands.add(THERMOSTAT_ZONE_TEMPERATURE_DOWN, 0x69, None, {})
commands.add(THERMOSTAT_GET_ZONE_INFORMATION, 0x6A, None, False)
commands.add(THERMOSTAT_CONTROL, 0x6B, None, None, False)
commands.add(THERMOSTAT_SET_COOL_SETPOINT, 0x6C, None, None, False)
commands.add(THERMOSTAT_SET_ZONE_COOL_SETPOINT, 0x6C, None, {})
commands.add(THERMOSTAT_SET_HEAT_SETPOINT, 0x6D, None, None, False)
commands.add(THERMOSTAT_SET_ZONE_HEAT_SETPOINT, 0x6D, None, {})
commands.add(THERMOSTAT_TEMPERATURE_STATUS, 0x6E, None, False)
commands.add(THERMOSTAT_HUMIDITY_STATUS, 0x6F, None, False)
commands.add(THERMOSTAT_MODE_STATUS, 0x70, None, False)
commands.add(THERMOSTAT_COOL_SET_POINT_STATUS, 0x71, None, False)
commands.add(THERMOSTAT_HEAT_SET_POINT_STATUS, 0x72, None, False)
commands.add(LEAK_DETECTOR_ANNOUNCE, 0x70, None, False)
commands.add(ASSIGN_TO_COMPANION_GROUP, 0x81, 0x00, False)
