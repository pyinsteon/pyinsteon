"""Collection of topics mapped to commands (cmd1, cmd2)."""
from collections import namedtuple

Command = namedtuple('Command', 'topic cmd1 cmd2 extended')

ASSIGN_TO_ALL_LINK_GROUP = 'assign_to_all_link_group'
DELETE_FROM_ALL_LINK_GROUP = 'delete_from_all_link_group'
PRODUCT_DATA_REQUEST = 'product_data_request'
FX_USERNAME = 'fx_username'
DEVICE_TEXT_STRING_REQUEST = 'device_text_string_request'
SET_DEVICE_TEXT_STRING = 'set_device_text_string'
SET_ALL_LINK_COMMAND_ALIAS = 'set_all_link_command_alias'
SET_ALL_LINK = 'set_all_link'
ENTER_LINKING_MODE = 'enter_linking_mode'
ENTER_UNLINKING_MODE = 'enter_unlinking_mode'
GET_INSTEON_ENGINE_VERSION = 'get_insteon_engine_version'
PING = 'ping'
ID_REQUEST = 'id_request'
ID_REQUEST_RESPONSE = 'id_request_response'
ON = 'on'
ON_FAST = 'on_fast'
OFF = 'off'
OFF_FAST = 'off_fast'
BRIGHTEN_ONE_STEP = 'brighten_one_step'
DIM_ONE_STEP = 'dim_one_step'
START_MANUAL_CHANGE_DOWN = 'start_manual_change_down'
START_MANUAL_CHANGE_UP = 'start_manual_change_up'
STOP_MANUAL_CHANGE = 'stop_manual_change'
STATUS_REQUEST = 'status_request'
STATUS_REQUEST_ALTERNATE_1 = 'status_request_alternate_1'
STATUS_REQUEST_ALTERNATE_2 = 'status_request_alternate_2'
STATUS_REQUEST_ALTERNATE_3 = 'status_request_alternate_3'
GET_OPERATING_FLAGS = 'get_operating_flags'
SET_OPERATING_FLAGS = 'set_operating_flags'
INSTANT_CHANGE = 'instant_change'
MANUALLY_TURNED_OFF = 'manually_turned_off'
MANUALLY_TURNED_ON = 'manually_turned_on'
REMOTE_SET_BUTTON_TAP1_TAP = 'remote_set_button_tap1_tap'
REMOTE_SET_BUTTON_TAP2_TAP = 'remote_set_button_tap2_tap'
SET_STATUS = 'set_status'
SET_ADDRESS_MSB = 'set_address_msb'
POKE_ONE_BYTE = 'poke_one_byte'
PEEK_ONE_BYTE = 'peek_one_byte'
PEEK_ONE_BYTE_INTERNAL = 'peek_one_byte_internal'
POKE_ONE_BYTE_INTERNAL = 'poke_one_byte_internal'
ON_AT_RAMP_RATE = 'on_at_ramp_rate'
EXTENDED_GET_SET = 'extended_get_set'
OFF_AT_RAMP_RATE = 'off_at_ramp_rate'
EXTENDED_READ_WRITE_ALDB = 'extended_read_write_aldb'
EXTENDED_TRIGGER_ALL_LINK = 'extended_trigger_all_link'
SPRINKLER_VALVE_ON = 'sprinkler_valve_on'
SPRINKLER_VALVE_OFF = 'sprinkler_valve_off'
SPRINKLER_PROGRAM_ON = 'sprinkler_program_on'
SPRINKLER_PROGRAM_OFF = 'sprinkler_program_off'
SPRINKLER_LOAD_INITIALIZATION_VALUES = 'sprinkler_load_initialization_values'
SPRINKLER_LOAD_EEPROM_FROM_RAM = 'sprinkler_load_eeprom_from_ram'
SPRINKLER_GET_VALVE_STATUS = 'sprinkler_get_valve_status'
SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE = 'sprinkler_inhibit_command_acceptance'
SPRINKLER_RESUME_COMMAND_ACCEPTANCE = 'sprinkler_resume_command_acceptance'
SPRINKLER_SKIP_FORWARD = 'sprinkler_skip_forward'
SPRINKLER_SKIP_BACK = 'sprinkler_skip_back'
SPRINKLER_ENABLE_PUMP_ON_V8 = 'sprinkler_enable_pump_on_v8'
SPRINKLER_DISABLE_PUMP_ON_V8 = 'sprinkler_disable_pump_on_v8'
SPRINKLER_BROADCAST_ON = 'sprinkler_broadcast_on'
SPRINKLER_BROADCAST_OFF = 'sprinkler_broadcast_off'
SPRINKLER_LOAD_RAM_FROM_EEPROM = 'sprinkler_load_ram_from_eeprom'
SPRINKLER_SENSOR_ON = 'sprinkler_sensor_on'
SPRINKLER_SENSOR_OFF = 'sprinkler_sensor_off'
SPRINKLER_DIAGNOSTICS_ON = 'sprinkler_diagnostics_on'
SPRINKLER_DIAGNOSTICS_OFF = 'sprinkler_diagnostics_off'
SPRINKLER_GET_PROGRAM_REQUEST = 'sprinkler_get_program_request'
IO_OUTPUT_ON = 'io_output_on'
IO_OUTPUT_OFF = 'io_output_off'
IO_ALARM_DATA_REQUEST = 'io_alarm_data_request'
IO_WRITE_OUTPUT_PORT = 'io_write_output_port'
IO_READ_INPUT_PORT = 'io_read_input_port'
IO_GET_SENSOR_VALUE = 'io_get_sensor_value'
IO_SET_SENSOR_1_NOMINAL_VALUE = 'io_set_sensor_1_nominal_value'
IO_GET_SENSOR_ALARM_DELTA = 'io_get_sensor_alarm_delta'
FAN_STATUS_REPORT = 'fan_status_report'
IO_WRITE_CONFIGURATION_PORT = 'io_write_configuration_port'
IO_READ_CONFIGURATION_PORT = 'io_read_configuration_port'
IO_MODULE_LOAD_INITIALIZATION_VALUES = 'io_module_load_initialization_values'
IO_MODULE_LOAD_EEPROM_FROM_RAM = 'io_module_load_eeprom_from_ram'
IO_MODULE_STATUS_REQUEST = 'io_module_status_request'
IO_MODULE_READ_ANALOG_ONCE = 'io_module_read_analog_once'
IO_MODULE_READ_ANALOG_ALWAYS = 'io_module_read_analog_always'
IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE = 'io_module_enable_status_change_message'
IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE = 'io_module_disable_status_change_message'
IO_MODULE_LOAD_RAM_FROM_EEPROM = 'io_module_load_ram_from_eeprom'
IO_MODULE_SENSOR_ON = 'io_module_sensor_on'
IO_MODULE_SENSOR_OFF = 'io_module_sensor_off'
IO_MODULE_DIAGNOSTICS_ON = 'io_module_diagnostics_on'
IO_MODULE_DIAGNOSTICS_OFF = 'io_module_diagnostics_off'
POOL_DEVICE_ON = 'pool_device_on'
POOL_DEVICE_OFF = 'pool_device_off'
POOL_TEMPERATURE_UP = 'pool_temperature_up'
POOL_TEMPERATURE_DOWN = 'pool_temperature_down'
POOL_LOAD_INITIALIZATION_VALUES = 'pool_load_initialization_values'
POOL_LOAD_EEPROM_FROM_RAM = 'pool_load_eeprom_from_ram'
POOL_GET_POOL_MODE = 'pool_get_pool_mode'
POOL_GET_AMBIENT_TEMPERATURE = 'pool_get_ambient_temperature'
POOL_GET_WATER_TEMPERATURE = 'pool_get_water_temperature'
POOL_GET_PH = 'pool_get_ph'
DOOR_MOVERAISE_DOOR = 'door_moveraise_door'
DOOR_MOVELOWER_DOOR = 'door_movelower_door'
DOOR_MOVEOPEN_DOOR = 'door_moveopen_door'
DOOR_MOVECLOSE_DOOR = 'door_moveclose_door'
DOOR_MOVESTOP_DOOR = 'door_movestop_door'
DOOR_MOVESINGLE_DOOR_OPEN = 'door_movesingle_door_open'
DOOR_MOVESINGLE_DOOR_CLOSE = 'door_movesingle_door_close'
DOOR_STATUS_REPORTRAISE_DOOR = 'door_status_reportraise_door'
DOOR_STATUS_REPORTLOWER_DOOR = 'door_status_reportlower_door'
DOOR_STATUS_REPORTOPEN_DOOR = 'door_status_reportopen_door'
DOOR_STATUS_REPORTCLOSE_DOOR = 'door_status_reportclose_door'
DOOR_STATUS_REPORTSTOP_DOOR = 'door_status_reportstop_door'
DOOR_STATUS_REPORTSINGLE_DOOR_OPEN = 'door_status_reportsingle_door_open'
DOOR_STATUS_REPORTSINGLE_DOOR_CLOSE = 'door_status_reportsingle_door_close'
WINDOW_COVERINGOPEN = 'window_coveringopen'
WINDOW_COVERINGCLOSE = 'window_coveringclose'
WINDOW_COVERINGSTOP = 'window_coveringstop'
WINDOW_COVERINGPROGRAM = 'window_coveringprogram'
WINDOW_COVERING_POSITION = 'window_covering_position'
THERMOSTAT_TEMPERATURE_UP = 'thermostat_temperature_up'
THERMOSTAT_TEMPERATURE_DOWN = 'thermostat_temperature_down'
THERMOSTAT_GET_ZONE_INFORMATION = 'thermostat_get_zone_information'
THERMOSTAT_LOAD_INITIALIZATION_VALUES = 'thermostat_load_initialization_values'
THERMOSTAT_LOAD_EEPROM_FROM_RAM = 'thermostat_load_eeprom_from_ram'
THERMOSTAT_GET_MODE = 'thermostat_get_mode'
THERMOSTAT_GET_AMBIENT_TEMPERATURE = 'thermostat_get_ambient_temperature'
THERMOSTAT_ON_HEAT = 'thermostat_on_heat'
THERMOSTAT_ON_COOL = 'thermostat_on_cool'
THERMOSTAT_ON_AUTO = 'thermostat_on_auto'
THERMOSTAT_ON_FAN = 'thermostat_on_fan'
THERMOSTAT_OFF_FAN = 'thermostat_off_fan'
THERMOSTAT_OFF_ALL = 'thermostat_off_all'
THERMOSTAT_PROGRAM_HEAT = 'thermostat_program_heat'
THERMOSTAT_PROGRAM_COOL = 'thermostat_program_cool'
THERMOSTAT_PROGRAM_AUTO = 'thermostat_program_auto'
THERMOSTAT_GET_EQUIPMENT_STATE = 'thermostat_get_equipment_state'
THERMOSTAT_SET_EQUIPMENT_STATE = 'thermostat_set_equipment_state'
THERMOSTAT_GET_TEMPERATURE_UNITS = 'thermostat_get_temperature_units'
THERMOSTAT_SET_FAHRENHEIT = 'thermostat_set_fahrenheit'
THERMOSTAT_SET_CELSIUS = 'thermostat_set_celsius'
THERMOSTAT_GET_FAN_ON_SPEED = 'thermostat_get_fan_on_speed'
THERMOSTAT_SET_FAN_ON_SPEED_LOW = 'thermostat_set_fan_on_speed_low'
THERMOSTAT_SET_FAN_ON_SPEED_MEDIUM = 'thermostat_set_fan_on_speed_medium'
THERMOSTAT_SET_FAN_ON_SPEED_HIGH = 'thermostat_set_fan_on_speed_high'
THERMOSTAT_ENABLE_STATUS_CHANGE_MESSAGE = 'thermostat_enable_status_change_message'
THERMOSTAT_DISABLE_STATUS_CHANGE_MESSAGE = 'thermostat_disable_status_change_message'
THERMOSTAT_SET_COOL_SETPOINT = 'thermostat_set_cool_setpoint'
THERMOSTAT_SET_HEAT_SETPOINT = 'thermostat_set_heat_setpoint'
THERMOSTAT_TEMPERATURE_STATUS = 'thermostat_temperature_status'
THERMOSTAT_HUMIDITY_STATUS = 'thermostat_humidity_status'
THERMOSTAT_MODE_STATUS = 'thermostat_mode_status'
THERMOSTAT_COOL_SET_POINT_STATUS = 'thermostat_cool_set_point_status'
THERMOSTAT_HEAT_SET_POINT_STATUS = 'thermostat_heat_set_point_status'
LEAK_DETECTOR_ANNOUNCE = 'leak_detector_announce'
ASSIGN_TO_COMPANION_GROUP = 'assign_to_companion_group'
SET_SPRINKLER_PROGRAM = 'set_sprinkler_program'
SPRINKLER_GET_PROGRAM_RESPONSE = 'sprinkler_get_program_response'
IO_SET_SENSOR_NOMINAL_VALUE = 'io_set_sensor_nominal_value'
IO_ALARM_DATA_RESPONSE = 'io_alarm_data_response'
POOL_SET_DEVICE_TEMPERATURE = 'pool_set_device_temperature'
POOL_SET_DEVICE_HYSTERESIS = 'pool_set_device_hysteresis'
THERMOSTAT_ZONE_TEMPERATURE_UP = 'thermostat_zone_temperature_up'
THERMOSTAT_ZONE_TEMPERATURE_DOWN = 'thermostat_zone_temperature_down'
THERMOSTAT_SET_ZONE_HEAT_SETPOINT = 'thermostat_set_zone_heat_setpoint'
THERMOSTAT_SET_ZONE_COOL_SETPOINT = 'thermostat_set_zone_cool_setpoint'

commands = [
    Command(ASSIGN_TO_ALL_LINK_GROUP, 0x01, None, False),
    Command(DELETE_FROM_ALL_LINK_GROUP, 0x02, None, False),
    Command(PRODUCT_DATA_REQUEST, 0x03, 0x00, False),
    Command(FX_USERNAME, 0x03, 0x01, False),
    Command(DEVICE_TEXT_STRING_REQUEST, 0x03, 0x02, False),
    Command(SET_DEVICE_TEXT_STRING, 0x03, 0x03, True),
    Command(SET_ALL_LINK_COMMAND_ALIAS, 0x03, 0x04, True),
    Command(SET_ALL_LINK, 0x03, 0x04, True),
    Command(ENTER_LINKING_MODE, 0x09, None, False),
    Command(ENTER_UNLINKING_MODE, 0x0a, None, False),
    Command(GET_INSTEON_ENGINE_VERSION, 0x0d, 0x00, False),
    Command(PING, 0x0f, 0x00, False),
    Command(ID_REQUEST, 0x10, 0x00, False),
    Command(ON, 0x11, None, False),
    Command(ON_FAST, 0x12, None, False),
    Command(OFF, 0x13, 0x00, False),
    Command(OFF_FAST, 0x14, 0x00, False),
    Command(BRIGHTEN_ONE_STEP, 0x15, 0x00, False),
    Command(DIM_ONE_STEP, 0x16, 0x00, False),
    Command(START_MANUAL_CHANGE_DOWN, 0x17, 0x00, False),
    Command(START_MANUAL_CHANGE_UP, 0x17, 0x01, False),
    Command(STOP_MANUAL_CHANGE, 0x18, 0x00, False),
    Command(STATUS_REQUEST, 0x19, 0x00, False),
    Command(STATUS_REQUEST_ALTERNATE_1, 0x19, 0X01, False),
    Command(STATUS_REQUEST_ALTERNATE_2, 0x19, 0X02, False),
    Command(STATUS_REQUEST_ALTERNATE_3, 0x19, 0X03, False),
    Command(GET_OPERATING_FLAGS, 0x1f, None, False),
    Command(SET_OPERATING_FLAGS, 0x20, None, False),
    Command(INSTANT_CHANGE, 0x21, None, False),
    Command(MANUALLY_TURNED_OFF, 0x22, 0x00, False),
    Command(MANUALLY_TURNED_ON, 0x23, 0x00, False),
    Command(REMOTE_SET_BUTTON_TAP1_TAP, 0x25, 0x01, False),
    Command(REMOTE_SET_BUTTON_TAP2_TAP, 0x25, 0x02, False),
    Command(SET_STATUS, 0x27, None, False),
    Command(SET_ADDRESS_MSB, 0x28, None, False),
    Command(POKE_ONE_BYTE, 0x29, None, False),
    Command(PEEK_ONE_BYTE, 0x2b, None, False),
    Command(PEEK_ONE_BYTE_INTERNAL, 0x2c, None, False),
    Command(POKE_ONE_BYTE_INTERNAL, 0x2d, None, False),

    Command(ON_AT_RAMP_RATE, 0x2e, None, False),  # Check
    Command(EXTENDED_GET_SET, 0x2e, 0x00, True),  # Check
    Command(OFF_AT_RAMP_RATE, 0x2f, None, False),  # Check
    Command(EXTENDED_READ_WRITE_ALDB, 0x2f, 0x00, True),  # Check
    Command(EXTENDED_TRIGGER_ALL_LINK, 0x30, 0x00, True),  # Check

    Command(SET_SPRINKLER_PROGRAM, 0x40, None, True),
    Command(SPRINKLER_VALVE_ON, 0x40, None, False),
    Command(SPRINKLER_GET_PROGRAM_RESPONSE, 0x41, None, True),
    Command(SPRINKLER_VALVE_OFF, 0x41, None, False),
    Command(SPRINKLER_PROGRAM_ON, 0x42, None, False),
    Command(SPRINKLER_PROGRAM_OFF, 0x43, None, False),
    Command(SPRINKLER_LOAD_INITIALIZATION_VALUES, 0x44, 0x00, False),
    Command(SPRINKLER_LOAD_EEPROM_FROM_RAM, 0x44, 0x01, False),
    Command(SPRINKLER_GET_VALVE_STATUS, 0x44, 0x02, False),
    Command(SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE, 0x44, 0x03, False),
    Command(SPRINKLER_RESUME_COMMAND_ACCEPTANCE, 0x44, 0x04, False),
    Command(SPRINKLER_SKIP_FORWARD, 0x44, 0x05, False),
    Command(SPRINKLER_SKIP_BACK, 0x44, 0x06, False),
    Command(SPRINKLER_ENABLE_PUMP_ON_V8, 0x44, 0x07, False),
    Command(SPRINKLER_DISABLE_PUMP_ON_V8, 0x44, 0x08, False),
    Command(SPRINKLER_BROADCAST_ON, 0x44, 0x09, False),
    Command(SPRINKLER_BROADCAST_OFF, 0x44, 0x0a, False),
    Command(SPRINKLER_LOAD_RAM_FROM_EEPROM, 0x44, 0x0b, False),
    Command(SPRINKLER_SENSOR_ON, 0x44, 0x0c, False),
    Command(SPRINKLER_SENSOR_OFF, 0x44, 0x0d, False),
    Command(SPRINKLER_DIAGNOSTICS_ON, 0x44, 0x0e, False),
    Command(SPRINKLER_DIAGNOSTICS_OFF, 0x44, 0x0f, False),
    Command(SPRINKLER_GET_PROGRAM_REQUEST, 0x45, None, False),
    Command(IO_OUTPUT_ON, 0x45, None, False),
    Command(IO_OUTPUT_OFF, 0x46, None, False),
    Command(IO_ALARM_DATA_REQUEST, 0x47, 0x00, False),
    Command(IO_WRITE_OUTPUT_PORT, 0x48, None, False),
    Command(IO_READ_INPUT_PORT, 0x49, 0x00, False),
    Command(IO_GET_SENSOR_VALUE, 0x4a, None, False),
    Command(IO_SET_SENSOR_1_NOMINAL_VALUE, 0x4b, None, False),
    Command(IO_SET_SENSOR_NOMINAL_VALUE, 0x4b, None, True),
    Command(IO_GET_SENSOR_ALARM_DELTA, 0x4c, None, False),
    Command(IO_ALARM_DATA_RESPONSE, 0x4c, 0x00, True),
    Command(IO_WRITE_CONFIGURATION_PORT, 0x4d, None, False),
    Command(IO_READ_CONFIGURATION_PORT, 0x4e, 0x00, False),
    Command(IO_MODULE_LOAD_INITIALIZATION_VALUES, 0x4f, 0x00, False),
    Command(IO_MODULE_LOAD_EEPROM_FROM_RAM, 0x4f, 0x01, False),
    Command(IO_MODULE_STATUS_REQUEST, 0x4f, 0x02, False),
    Command(IO_MODULE_READ_ANALOG_ONCE, 0x4f, 0x03, False),
    Command(IO_MODULE_READ_ANALOG_ALWAYS, 0x4f, 0x04, False),
    Command(IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE, 0x4f, 0x09, False),
    Command(IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE, 0x4f, 0x0a, False),
    Command(IO_MODULE_LOAD_RAM_FROM_EEPROM, 0x4f, 0x0b, False),
    Command(IO_MODULE_SENSOR_ON, 0x4f, 0x0c, False),
    Command(IO_MODULE_SENSOR_OFF, 0x4f, 0x0d, False),
    Command(IO_MODULE_DIAGNOSTICS_ON, 0x4f, 0x0e, False),
    Command(IO_MODULE_DIAGNOSTICS_OFF, 0x4f, 0x0f, False),
    Command(POOL_DEVICE_ON, 0x50, None, False),
    Command(POOL_SET_DEVICE_TEMPERATURE, 0x50, None, True),
    Command(POOL_DEVICE_OFF, 0x51, None, False),
    Command(POOL_SET_DEVICE_HYSTERESIS, 0x51, None, True),
    Command(POOL_TEMPERATURE_UP, 0x52, None, False),
    Command(POOL_TEMPERATURE_DOWN, 0x53, None, False),
    Command(POOL_LOAD_INITIALIZATION_VALUES, 0x54, 0x00, False),
    Command(POOL_LOAD_EEPROM_FROM_RAM, 0x54, 0x01, False),
    Command(POOL_GET_POOL_MODE, 0x54, 0x02, False),
    Command(POOL_GET_AMBIENT_TEMPERATURE, 0x54, 0x03, False),
    Command(POOL_GET_WATER_TEMPERATURE, 0x54, 0x04, False),
    Command(POOL_GET_PH, 0x54, 0x05, False),
    Command(DOOR_MOVERAISE_DOOR, 0x58, 0x00, False),
    Command(DOOR_MOVELOWER_DOOR, 0x58, 0x01, False),
    Command(DOOR_MOVEOPEN_DOOR, 0x58, 0x02, False),
    Command(DOOR_MOVECLOSE_DOOR, 0x58, 0x03, False),
    Command(DOOR_MOVESTOP_DOOR, 0x58, 0x04, False),
    Command(DOOR_MOVESINGLE_DOOR_OPEN, 0x58, 0x05, False),
    Command(DOOR_MOVESINGLE_DOOR_CLOSE, 0x58, 0x06, False),
    Command(DOOR_STATUS_REPORTRAISE_DOOR, 0x59, 0x00, False),
    Command(DOOR_STATUS_REPORTLOWER_DOOR, 0x59, 0x01, False),
    Command(DOOR_STATUS_REPORTOPEN_DOOR, 0x59, 0x02, False),
    Command(DOOR_STATUS_REPORTCLOSE_DOOR, 0x59, 0x03, False),
    Command(DOOR_STATUS_REPORTSTOP_DOOR, 0x59, 0x04, False),
    Command(DOOR_STATUS_REPORTSINGLE_DOOR_OPEN, 0x59, 0x05, False),
    Command(DOOR_STATUS_REPORTSINGLE_DOOR_CLOSE, 0x59, 0x06, False),
    Command(WINDOW_COVERINGOPEN, 0x60, 0x01, False),
    Command(WINDOW_COVERINGCLOSE, 0x60, 0x02, False),
    Command(WINDOW_COVERINGSTOP, 0x60, 0x03, False),
    Command(WINDOW_COVERINGPROGRAM, 0x60, 0x04, False),
    Command(WINDOW_COVERING_POSITION, 0x61, None, False),
    Command(THERMOSTAT_TEMPERATURE_UP, 0x68, None, False),
    Command(THERMOSTAT_ZONE_TEMPERATURE_UP, 0x68, None, True),
    Command(THERMOSTAT_TEMPERATURE_DOWN, 0x69, None, False),
    Command(THERMOSTAT_ZONE_TEMPERATURE_DOWN, 0x69, None, True),
    Command(THERMOSTAT_GET_ZONE_INFORMATION, 0x6a, None, False),
    Command(THERMOSTAT_LOAD_INITIALIZATION_VALUES, 0x6b, 0x00, False),
    Command(THERMOSTAT_LOAD_EEPROM_FROM_RAM, 0x6b, 0x01, False),
    Command(THERMOSTAT_GET_MODE, 0x6b, 0x02, False),
    Command(THERMOSTAT_GET_AMBIENT_TEMPERATURE, 0x6b, 0x03, False),
    Command(THERMOSTAT_ON_HEAT, 0x6b, 0x04, False),
    Command(THERMOSTAT_ON_COOL, 0x6b, 0x05, False),
    Command(THERMOSTAT_ON_AUTO, 0x6b, 0x06, False),
    Command(THERMOSTAT_ON_FAN, 0x6b, 0x07, False),
    Command(THERMOSTAT_OFF_FAN, 0x6b, 0x08, False),
    Command(THERMOSTAT_OFF_ALL, 0x6b, 0x09, False),
    Command(THERMOSTAT_PROGRAM_HEAT, 0x6b, 0x0a, False),
    Command(THERMOSTAT_PROGRAM_COOL, 0x6b, 0x0b, False),
    Command(THERMOSTAT_PROGRAM_AUTO, 0x6b, 0x0c, False),
    Command(THERMOSTAT_GET_EQUIPMENT_STATE, 0x6b, 0x0d, False),
    Command(THERMOSTAT_SET_EQUIPMENT_STATE, 0x6b, 0x0e, False),
    Command(THERMOSTAT_GET_TEMPERATURE_UNITS, 0x6b, 0x0f, False),
    Command(THERMOSTAT_SET_FAHRENHEIT, 0x6b, 0x10, False),
    Command(THERMOSTAT_SET_CELSIUS, 0x6b, 0x11, False),
    Command(THERMOSTAT_GET_FAN_ON_SPEED, 0x6b, 0x12, False),
    Command(THERMOSTAT_SET_FAN_ON_SPEED_LOW, 0x6b, 0x13, False),
    Command(THERMOSTAT_SET_FAN_ON_SPEED_MEDIUM, 0x6b, 0x14, False),
    Command(THERMOSTAT_SET_FAN_ON_SPEED_HIGH, 0x6b, 0x15, False),
    Command(THERMOSTAT_ENABLE_STATUS_CHANGE_MESSAGE, 0x6b, 0x16, False),
    Command(THERMOSTAT_DISABLE_STATUS_CHANGE_MESSAGE, 0x6b, 0x17, False),
    Command(THERMOSTAT_SET_COOL_SETPOINT, 0x6c, None, False),
    Command(THERMOSTAT_SET_ZONE_COOL_SETPOINT, 0x6c, None, True),
    Command(THERMOSTAT_SET_HEAT_SETPOINT, 0x6d, None, False),
    Command(THERMOSTAT_SET_ZONE_HEAT_SETPOINT, 0x6d, None, True),
    Command(THERMOSTAT_TEMPERATURE_STATUS, 0x6e, None, False),
    Command(THERMOSTAT_HUMIDITY_STATUS, 0x6f, None, False),
    Command(THERMOSTAT_MODE_STATUS, 0x70, None, False),
    Command(THERMOSTAT_COOL_SET_POINT_STATUS, 0x71, None, False),
    Command(THERMOSTAT_HEAT_SET_POINT_STATUS, 0x72, None, False),
    Command(LEAK_DETECTOR_ANNOUNCE, 0x70, None, False),
    Command(ASSIGN_TO_COMPANION_GROUP, 0x81, 0x00, False)]


class Commands():
    """List of commands mapped to topics."""
    def __init__(self):
        """Init the Commands class."""
        self._commands = commands

    def __iter__(self) -> Command:
        """Iterate the command list."""
        for item in self._commands:
            yield item

    def get_cmd1_cmd2(self, topic) -> (int, int, bool):
        """Get cmd1 and cmd2 from a topic.

        Returns (cmd1, cmd2, extended)
        """
        for item in self:
            if topic == item.topic:
                return item.cmd1, item.cmd2, item.extended
        return None, None, None

    def get_topic(self, cmd1, cmd2, extended=None) -> str:
        """Return a topic from a cmd1, cmd2 and extended flag."""
        for item in self:
            if item.cmd1 == cmd1:
                if not item.cmd2 or not cmd2 or item.cmd2 == cmd2:
                    if (not item.extended or
                            not extended or
                            item.extended == extended):
                        return item
        return None

command_list = Commands()

