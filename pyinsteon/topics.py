"""Constants used to ensure topic consistantancy."""
DEVICE_LIST_CHANGED = "device_list_changed"

STANDARD_RECEIVED = "standard_message_received"
EXTENDED_RECEIVED = "extended_message_received"
X10_RECEIVED = "x10_received"
ALL_LINKING_COMPLETED = "all_linking_completed"
BUTTON_EVENT_REPORT = "button_event_report"
USER_RESET_DETECTED = "user_reset_detected"
ALL_LINK_CLEANUP_FAILURE_REPORT = "all_link_cleanup_failure_report"
ALL_LINK_RECORD_RESPONSE = "all_link_record_response"
ALL_LINK_CLEANUP_STATUS_REPORT = "all_link_cleanup_status_report"
GET_IM_INFO = "get_im_info"
SEND_ALL_LINK_COMMAND = "send_all_link_command"
SEND_STANDARD = "send_standard"
SEND_EXTENDED = "send_extended"
X10_SEND = "x10_send"
START_ALL_LINKING = "start_all_linking"
CANCEL_ALL_LINKING = "cancel_all_linking"
SET_HOST_DEVICE_CATEGORY = "set_host_device_category"
RESET_IM = "reset_im"
SET_ACK_MESSAGE_BYTE = "set_ack_message_byte"
GET_FIRST_ALL_LINK_RECORD = "get_first_all_link_record"
GET_NEXT_ALL_LINK_RECORD = "get_next_all_link_record"
SET_IM_CONFIGURATION = "set_im_configuration"
GET_ALL_LINK_RECORD_FOR_SENDER = "get_all_link_record_for_sender"
LED_ON = "led_on"
LED_OFF = "led_off"
MANAGE_ALL_LINK_RECORD = "manage_all_link_record"
SET_NAK_MESSAGE_BYTE = "set_nak_message_byte"
SET_ACK_MESSAGE_TWO_BYTES = "set_ack_message_two_bytes"
RF_SLEEP = "rf_sleep"
GET_IM_CONFIGURATION = "get_im_configuration"
READ_EEPROM = "read_eeprom"
READ_EEPROM_RESPONSE = "read_eeprom_response"
WRITE_EEPROM = "write_eeprom"

# Command Topics
ASSIGN_TO_ALL_LINK_GROUP = "assign_to_all_link_group"
DELETE_FROM_ALL_LINK_GROUP = "delete_from_all_link_group"
PRODUCT_DATA_REQUEST = "product_data_request"
FX_USERNAME = "fx_username"
DEVICE_TEXT_STRING_REQUEST = "device_text_string_request"
SET_DEVICE_TEXT_STRING = "set_device_text_string"
SET_ALL_LINK_COMMAND_ALIAS = "set_all_link_command_alias"
SET_ALL_LINK = "set_all_link"
ENTER_LINKING_MODE = "enter_linking_mode"
ENTER_UNLINKING_MODE = "enter_unlinking_mode"
GET_INSTEON_ENGINE_VERSION = "get_insteon_engine_version"
PING = "ping"
ID_REQUEST = "id_request"
ID_REQUEST_RESPONSE = "id_request_response"
ON = "on"
ON_FAST = "on_fast"
OFF = "off"
OFF_FAST = "off_fast"
BRIGHTEN_ONE_STEP = "brighten_one_step"
DIM_ONE_STEP = "dim_one_step"
START_MANUAL_CHANGE_DOWN = "start_manual_change_down"
START_MANUAL_CHANGE_UP = "start_manual_change_up"
STOP_MANUAL_CHANGE = "stop_manual_change"
STATUS_REQUEST = "status_request"
GET_OPERATING_FLAGS = "get_operating_flags"
SET_OPERATING_FLAGS = "set_operating_flags"
INSTANT_CHANGE = "instant_change"
MANUALLY_TURNED_OFF = "manually_turned_off"
MANUALLY_TURNED_ON = "manually_turned_on"
REMOTE_SET_BUTTON_TAP1_TAP = "remote_set_button_tap1_tap"
REMOTE_SET_BUTTON_TAP2_TAP = "remote_set_button_tap2_tap"
SET_STATUS = "set_status"
SET_ADDRESS_MSB = "set_address_msb"
POKE_ONE_BYTE = "poke_one_byte"
PEEK_ONE_BYTE = "peek_one_byte"
PEEK_ONE_BYTE_INTERNAL = "peek_one_byte_internal"
POKE_ONE_BYTE_INTERNAL = "poke_one_byte_internal"
ON_AT_RAMP_RATE = "on_at_ramp_rate"
EXTENDED_GET_SET = "extended_get_set"
EXTENDED_GET_RESPONSE = "extended_get_response"
THERMOSTAT_SET_POINT_RESPONSE = "thermostat_set_point_response"
THERMOSTAT_STATUS_RESPONSE = "thermostat_status_response"
EXTENDED_GET_SET_2 = "extended_get_set_2"
OFF_AT_RAMP_RATE = "off_at_ramp_rate"
EXTENDED_READ_WRITE_ALDB = "extended_read_write_aldb"
EXTENDED_READ_WRITE_ALDB_DIRECT_NAK = "extended_read_write_aldb_direct_nak"
EXTENDED_TRIGGER_ALL_LINK = "extended_trigger_all_link"
ALDB_RECORD_RECEIVED = "aldb_record_received"
BEEP = "beep"
SPRINKLER_VALVE_ON = "sprinkler_valve_on"
SPRINKLER_VALVE_OFF = "sprinkler_valve_off"
SPRINKLER_PROGRAM_ON = "sprinkler_program_on"
SPRINKLER_PROGRAM_OFF = "sprinkler_program_off"
SPRINKLER_CONTROL = "sprinkler_control"
SPRINKLER_GET_PROGRAM_REQUEST = "sprinkler_get_program_request"
IO_OUTPUT_ON = "io_output_on"
IO_OUTPUT_OFF = "io_output_off"
IO_ALARM_DATA_REQUEST = "io_alarm_data_request"
IO_WRITE_OUTPUT_PORT = "io_write_output_port"
IO_READ_INPUT_PORT = "io_read_input_port"
IO_GET_SENSOR_VALUE = "io_get_sensor_value"
IO_SET_SENSOR_1_NOMINAL_VALUE = "io_set_sensor_1_nominal_value"
IO_GET_SENSOR_ALARM_DELTA = "io_get_sensor_alarm_delta"
FAN_STATUS_REPORT = "fan_status_report"
IO_WRITE_CONFIGURATION_PORT = "io_write_configuration_port"
IO_READ_CONFIGURATION_PORT = "io_read_configuration_port"
IO_MODULE_CONTROL = "io_module_control"
POOL_DEVICE_ON = "pool_device_on"
POOL_DEVICE_OFF = "pool_device_off"
POOL_TEMPERATURE_UP = "pool_temperature_up"
POOL_TEMPERATURE_DOWN = "pool_temperature_down"
POOL_CONTROL = "pool_control"
POOL_SET_DEVICE_TEMPERATURE = "pool_set_device_temperature"
POOL_SET_DEVICE_HYSTERESIS = "pool_set_device_hysteresis"
DOOR_CONTROL = "door_control"
DOOR_STATUS_REPORT = "door_status_report"
WINDOW_COVERING_CONTROL = "window_covering_control"
WINDOW_COVERING_POSITION = "window_covering_position"
THERMOSTAT_TEMPERATURE_UP = "thermostat_temperature_up"
THERMOSTAT_TEMPERATURE_DOWN = "thermostat_temperature_down"
THERMOSTAT_GET_ZONE_INFORMATION = "thermostat_get_zone_information"
THERMOSTAT_CONTROL = "thermostat_control"
THERMOSTAT_SET_COOL_SETPOINT = "thermostat_set_cool_setpoint"
THERMOSTAT_SET_HEAT_SETPOINT = "thermostat_set_heat_setpoint"
THERMOSTAT_EXTENDED_STATUS = "thermostat_extended_status"
THERMOSTAT_TEMPERATURE_STATUS = "thermostat_temperature_status"
THERMOSTAT_HUMIDITY_STATUS = "thermostat_humidity_status"
THERMOSTAT_MODE_STATUS = "thermostat_mode_status"
THERMOSTAT_COOL_SET_POINT_STATUS = "thermostat_cool_set_point_status"
THERMOSTAT_HEAT_SET_POINT_STATUS = "thermostat_heat_set_point_status"
LEAK_DETECTOR_ANNOUNCE = "leak_detector_announce"
SET_SPRINKLER_PROGRAM = "set_sprinkler_program"
SPRINKLER_GET_PROGRAM_RESPONSE = "sprinkler_get_program_response"
IO_SET_SENSOR_NOMINAL_VALUE = "io_set_sensor_nominal_value"
IO_ALARM_DATA_RESPONSE = "io_alarm_data_response"

ALDB_LINK_CHANGED = "aldb.link_changed"

ALDB_VERSION = "aldb_version"
ALDB_STATUS_CHANGED = "aldb_status_changed"
EXTENDED_PROPERTIES_CHANGED = "extended_properties_changed"


GET_QUEUE_SIZE = "get_queue_size"
SEND_QUEUE_SIZE = "send_queue_size"
ADD_DEFAULT_LINKS = "add_default_links"
