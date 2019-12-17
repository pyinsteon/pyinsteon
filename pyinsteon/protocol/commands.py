"""Collection of topics mapped to commands (cmd1, cmd2)."""
from ..topics import (
    ALL_LINK_CLEANUP_STATUS_REPORT,
    ASSIGN_TO_ALL_LINK_GROUP,
    ASSIGN_TO_COMPANION_GROUP,
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
    EXTENDED_GET_SET,
    EXTENDED_READ_WRITE_ALDB,
    EXTENDED_TRIGGER_ALL_LINK,
    BEEP,
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
    SEND_STANDARD,
    EXTENDED_RECEIVED,
    SEND_EXTENDED,
    START_MANUAL_CHANGE_DOWN,
    START_MANUAL_CHANGE_UP,
    STATUS_REQUEST,
    STOP_MANUAL_CHANGE,
    THERMOSTAT_COOL_SET_POINT_STATUS,
    THERMOSTAT_DISABLE_STATUS_CHANGE_MESSAGE,
    THERMOSTAT_ENABLE_STATUS_CHANGE_MESSAGE,
    THERMOSTAT_GET_AMBIENT_TEMPERATURE,
    THERMOSTAT_GET_EQUIPMENT_STATE,
    THERMOSTAT_GET_FAN_ON_SPEED,
    THERMOSTAT_GET_MODE,
    THERMOSTAT_GET_TEMPERATURE_UNITS,
    THERMOSTAT_GET_ZONE_INFORMATION,
    THERMOSTAT_HEAT_SET_POINT_STATUS,
    THERMOSTAT_HUMIDITY_STATUS,
    THERMOSTAT_LOAD_EEPROM_FROM_RAM,
    THERMOSTAT_LOAD_INITIALIZATION_VALUES,
    THERMOSTAT_MODE_STATUS,
    THERMOSTAT_OFF_ALL,
    THERMOSTAT_OFF_FAN,
    THERMOSTAT_ON_AUTO,
    THERMOSTAT_ON_COOL,
    THERMOSTAT_ON_FAN,
    THERMOSTAT_ON_HEAT,
    THERMOSTAT_PROGRAM_AUTO,
    THERMOSTAT_PROGRAM_COOL,
    THERMOSTAT_PROGRAM_HEAT,
    THERMOSTAT_SET_CELSIUS,
    THERMOSTAT_SET_COOL_SETPOINT,
    THERMOSTAT_SET_EQUIPMENT_STATE,
    THERMOSTAT_SET_FAHRENHEIT,
    THERMOSTAT_SET_FAN_ON_SPEED_HIGH,
    THERMOSTAT_SET_FAN_ON_SPEED_LOW,
    THERMOSTAT_SET_FAN_ON_SPEED_MEDIUM,
    THERMOSTAT_SET_HEAT_SETPOINT,
    THERMOSTAT_SET_ZONE_COOL_SETPOINT,
    THERMOSTAT_SET_ZONE_HEAT_SETPOINT,
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


class Commands:
    """List of topics and commands."""

    def __init__(self):
        """Init the Commands class."""
        self._topics = {}
        self._commands = {}
        self._use_group = {}

    def add(
        self, topic: str, cmd1: int, cmd2: int, extended: bool, use_group: bool = False
    ):
        """Add a command to the list."""
        self._topics[topic] = (cmd1, cmd2, extended)
        self._use_group[topic] = use_group
        self._commands[(cmd1, cmd2, extended)] = topic

    def get(self, topic: str):
        """Get the command elements of teh topic."""
        return self._topics.get(topic)

    def get_cmd1_cmd2(self, topic: str) -> (int, int, bool):
        """Get cmd1 and cmd2 from a topic.

        Returns (cmd1, cmd2, extended)
        """
        return self._topics.get(topic)

    def use_group(self, topic):
        """Return if a topic requires a group number."""
        return self._use_group.get(topic)

    def get_topics(self, cmd1, cmd2, extended=None, send=False) -> str:
        """Generate a topic from a cmd1, cmd2 and extended flag."""
        found = False
        topic = self._commands.get((cmd1, cmd2, extended))
        if topic:
            found = True
            yield topic
        topic = self._commands.get((cmd1, cmd2, None))
        if topic:
            found = True
            yield topic
        topic = self._commands.get((cmd1, None, extended))
        if topic:
            found = True
            yield topic
        topic = self._commands.get((cmd1, None, None))
        if topic:
            found = True
            yield topic
        if not found:
            if send:
                yield self._commands.get((-2, None, extended))
                return
            yield self._commands.get((-1, None, extended))


commands = Commands()


commands.add(STANDARD_RECEIVED, -1, None, False)
commands.add(EXTENDED_RECEIVED, -1, None, True)
commands.add(SEND_STANDARD, -2, None, False)
commands.add(SEND_EXTENDED, -2, None, True)
commands.add(ASSIGN_TO_ALL_LINK_GROUP, 0x01, None, False)
commands.add(DELETE_FROM_ALL_LINK_GROUP, 0x02, None, False)
commands.add(PRODUCT_DATA_REQUEST, 0x03, 0x00, None)
commands.add(FX_USERNAME, 0x03, 0x01, False)
commands.add(DEVICE_TEXT_STRING_REQUEST, 0x03, 0x02, False)
commands.add(SET_DEVICE_TEXT_STRING, 0x03, 0x03, True)
commands.add(SET_ALL_LINK_COMMAND_ALIAS, 0x03, 0x04, True)
commands.add(SET_ALL_LINK, 0x03, 0x04, True)
commands.add(ALL_LINK_CLEANUP_STATUS_REPORT, 0x06, None, None)
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
commands.add(SET_OPERATING_FLAGS, 0x20, None, False)
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

# cmd2 ne 0x00 => no confict w/ ext get set
commands.add(ON_AT_RAMP_RATE, 0x2E, None, False, True)
# Check if direct_ack is sd or ed message
commands.add(EXTENDED_GET_SET, 0x2E, None, None)
# cmd2 ne 0x00 => no confict w/ read aldb
commands.add(OFF_AT_RAMP_RATE, 0x2F, None, False, True)
# direct_ack is sd msg
commands.add(EXTENDED_READ_WRITE_ALDB, 0x2F, None, None)
# Check direct_ack sd or ed msg
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
commands.add(IO_ALARM_DATA_RESPONSE, 0x4C, 0x00, True)
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
commands.add(POOL_SET_DEVICE_TEMPERATURE, 0x50, None, True)
commands.add(POOL_DEVICE_OFF, 0x51, None, False)
commands.add(POOL_SET_DEVICE_HYSTERESIS, 0x51, None, True)
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
commands.add(THERMOSTAT_ZONE_TEMPERATURE_UP, 0x68, None, True)
commands.add(THERMOSTAT_TEMPERATURE_DOWN, 0x69, None, False)
commands.add(THERMOSTAT_ZONE_TEMPERATURE_DOWN, 0x69, None, True)
commands.add(THERMOSTAT_GET_ZONE_INFORMATION, 0x6A, None, False)
commands.add(THERMOSTAT_LOAD_INITIALIZATION_VALUES, 0x6B, 0x00, False)
commands.add(THERMOSTAT_LOAD_EEPROM_FROM_RAM, 0x6B, 0x01, False)
commands.add(THERMOSTAT_GET_MODE, 0x6B, 0x02, False)
commands.add(THERMOSTAT_GET_AMBIENT_TEMPERATURE, 0x6B, 0x03, False)
commands.add(THERMOSTAT_ON_HEAT, 0x6B, 0x04, False)
commands.add(THERMOSTAT_ON_COOL, 0x6B, 0x05, False)
commands.add(THERMOSTAT_ON_AUTO, 0x6B, 0x06, False)
commands.add(THERMOSTAT_ON_FAN, 0x6B, 0x07, False)
commands.add(THERMOSTAT_OFF_FAN, 0x6B, 0x08, False)
commands.add(THERMOSTAT_OFF_ALL, 0x6B, 0x09, False)
commands.add(THERMOSTAT_PROGRAM_HEAT, 0x6B, 0x0A, False)
commands.add(THERMOSTAT_PROGRAM_COOL, 0x6B, 0x0B, False)
commands.add(THERMOSTAT_PROGRAM_AUTO, 0x6B, 0x0C, False)
commands.add(THERMOSTAT_GET_EQUIPMENT_STATE, 0x6B, 0x0D, False)
commands.add(THERMOSTAT_SET_EQUIPMENT_STATE, 0x6B, 0x0E, False)
commands.add(THERMOSTAT_GET_TEMPERATURE_UNITS, 0x6B, 0x0F, False)
commands.add(THERMOSTAT_SET_FAHRENHEIT, 0x6B, 0x10, False)
commands.add(THERMOSTAT_SET_CELSIUS, 0x6B, 0x11, False)
commands.add(THERMOSTAT_GET_FAN_ON_SPEED, 0x6B, 0x12, False)
commands.add(THERMOSTAT_SET_FAN_ON_SPEED_LOW, 0x6B, 0x13, False)
commands.add(THERMOSTAT_SET_FAN_ON_SPEED_MEDIUM, 0x6B, 0x14, False)
commands.add(THERMOSTAT_SET_FAN_ON_SPEED_HIGH, 0x6B, 0x15, False)
commands.add(THERMOSTAT_ENABLE_STATUS_CHANGE_MESSAGE, 0x6B, 0x16, False)
commands.add(THERMOSTAT_DISABLE_STATUS_CHANGE_MESSAGE, 0x6B, 0x17, False)
commands.add(THERMOSTAT_SET_COOL_SETPOINT, 0x6C, None, False)
commands.add(THERMOSTAT_SET_ZONE_COOL_SETPOINT, 0x6C, None, True)
commands.add(THERMOSTAT_SET_HEAT_SETPOINT, 0x6D, None, False)
commands.add(THERMOSTAT_SET_ZONE_HEAT_SETPOINT, 0x6D, None, True)
commands.add(THERMOSTAT_TEMPERATURE_STATUS, 0x6E, None, False)
commands.add(THERMOSTAT_HUMIDITY_STATUS, 0x6F, None, False)
commands.add(THERMOSTAT_MODE_STATUS, 0x70, None, False)
commands.add(THERMOSTAT_COOL_SET_POINT_STATUS, 0x71, None, False)
commands.add(THERMOSTAT_HEAT_SET_POINT_STATUS, 0x72, None, False)
commands.add(LEAK_DETECTOR_ANNOUNCE, 0x70, None, False)
commands.add(ASSIGN_TO_COMPANION_GROUP, 0x81, 0x00, False)
