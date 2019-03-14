"""Create a topic and a direct message."""
from .. import pub
from ..address import Address
from ..constants import MessageFlagType
from .message_flags import create as create_flags
from .outbound import send_standard, send_extended, Outbound
from .user_data import UserData
from .command_topics import command_list


def _create_direct_message(address, cmd1, cmd2, extended=False,
                           user_data=None) -> (str, Outbound):
    flags = create_flags(MessageFlagType.DIRECT, extended)
    if extended:
        msg = send_extended(address, cmd1, cmd2, flags, user_data)
    else:
        msg = send_standard(address, cmd1, cmd2, flags)
    main_topic = command_list.get_topic(cmd1, cmd2, extended)
    topic = 'send.{}.{}.direct'.format(address.id, main_topic)
    pub.sendMessage(topic, msg=msg)


def assign_to_all_link_group(address: Address, group: int) -> (str, Outbound):
    """Create a ASSIGN_TO_ALL_LINK_GROUP command."""
    cmd1 = 0x01
    cmd2 = group
    return _create_direct_message(address, cmd1, cmd2)


def delete_from_all_link_group(address: Address, group: int) -> (str, Outbound):
    """Create a DELETE_FROM_ALL_LINK_GROUP command."""
    cmd1 = 0x02
    cmd2 = group
    return _create_direct_message(address, cmd1, cmd2)


def product_data_request(address: Address) -> (str, Outbound):
    """Create a PRODUCT_DATA_REQUEST command."""
    cmd1 = 0x03
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def fx_username(address: Address) -> (str, Outbound):
    """Create a FX_USERNAME command."""
    cmd1 = 0x03
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def device_text_string_request(address: Address) -> (str, Outbound):
    """Create a DEVICE_TEXT_STRING_REQUEST command."""
    cmd1 = 0x03
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def set_device_text_string(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a SET_DEVICE_TEXT_STRING command."""
    cmd1 = 0x03
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def set_all_link_command_alias(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a SET_ALL_LINK_COMMAND_ALIAS command."""
    cmd1 = 0x03
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def set_all_link(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a SET_ALL_LINK command."""
    cmd1 = 0x03
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def enter_linking_mode(address: Address, group: int) -> (str, Outbound):
    """Create a ENTER_LINKING_MODE command."""
    cmd1 = 0x09
    cmd2 = group
    return _create_direct_message(address, cmd1, cmd2)


def enter_unlinking_mode(address: Address, group: int) -> (str, Outbound):
    """Create a ENTER_UNLINKING_MODE command."""
    cmd1 = 0x0a
    cmd2 = group
    return _create_direct_message(address, cmd1, cmd2)


def get_insteon_engine_version(address: Address) -> (str, Outbound):
    """Create a GET_INSTEON_ENGINE_VERSION command."""
    cmd1 = 0x0d
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def ping(address: Address) -> (str, Outbound):
    """Create a PING command."""
    cmd1 = 0x0f
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def id_request(address: Address) -> (str, Outbound):
    """Create a ID_REQUEST command."""
    cmd1 = 0x10
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def on(address: Address, on_level: int) -> (str, Outbound):
    """Create a ON command."""
    cmd1 = 0x11
    cmd2 = on_level
    return _create_direct_message(address, cmd1, cmd2)

def on_fast(address: Address, on_level: int) -> (str, Outbound):
    """Create a ON_FAST command."""
    cmd1 = 0x12
    cmd2 = on_level
    return _create_direct_message(address, cmd1, cmd2)


def off(address: Address) -> (str, Outbound):
    """Create a OFF command."""
    cmd1 = 0x13
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def off_fast(address: Address) -> (str, Outbound):
    """Create a OFF_FAST command."""
    cmd1 = 0x14
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def brighten_one_step(address: Address) -> (str, Outbound):
    """Create a BRIGHTEN_ONE_STEP command."""
    cmd1 = 0x15
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def dim_one_step(address: Address) -> (str, Outbound):
    """Create a DIM_ONE_STEP command."""
    cmd1 = 0x16
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def start_manual_change_down(address: Address) -> (str, Outbound):
    """Create a START_MANUAL_CHANGE_DOWN command."""
    cmd1 = 0x17
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def start_manual_change_up(address: Address) -> (str, Outbound):
    """Create a START_MANUAL_CHANGE_UP command."""
    cmd1 = 0x17
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def stop_manual_change(address: Address) -> (str, Outbound):
    """Create a STOP_MANUAL_CHANGE command."""
    cmd1 = 0x18
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def status_request(address: Address) -> (str, Outbound):
    """Create a STATUS_REQUEST command."""
    cmd1 = 0x19
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def status_request_alternate_1(address: Address) -> (str, Outbound):
    """Create a STATUS_REQUEST_ALTERNATE_1 command."""
    cmd1 = 0x19
    cmd2 = 0X01
    return _create_direct_message(address, cmd1, cmd2)


def status_request_alternate_2(address: Address) -> (str, Outbound):
    """Create a STATUS_REQUEST_ALTERNATE_2 command."""
    cmd1 = 0x19
    cmd2 = 0X02
    return _create_direct_message(address, cmd1, cmd2)


def status_request_alternate_3(address: Address) -> (str, Outbound):
    """Create a STATUS_REQUEST_ALTERNATE_3 command."""
    cmd1 = 0x19
    cmd2 = 0X03
    return _create_direct_message(address, cmd1, cmd2)


def get_operating_flags(address: Address, flags_requested: int) -> (str, Outbound):
    """Create a GET_OPERATING_FLAGS command."""
    cmd1 = 0x1f
    cmd2 = flags_requested
    return _create_direct_message(address, cmd1, cmd2)


def set_operating_flags(address: Address, flags_to_alter: int) -> (str, Outbound):
    """Create a SET_OPERATING_FLAGS command."""
    cmd1 = 0x20
    cmd2 = flags_to_alter
    return _create_direct_message(address, cmd1, cmd2)


def instant_change(address: Address, on_level: int) -> (str, Outbound):
    """Create a INSTANT_CHANGE command."""
    cmd1 = 0x21
    cmd2 = on_level
    return _create_direct_message(address, cmd1, cmd2)


def manually_turned_off(address: Address) -> (str, Outbound):
    """Create a MANUALLY_TURNED_OFF command."""
    cmd1 = 0x22
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def manually_turned_on(address: Address) -> (str, Outbound):
    """Create a MANUALLY_TURNED_ON command."""
    cmd1 = 0x23
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def remote_set_button_tap1_tap(address: Address) -> (str, Outbound):
    """Create a REMOTE_SET_BUTTON_TAP1_TAP command."""
    cmd1 = 0x25
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def remote_set_button_tap2_tap(address: Address) -> (str, Outbound):
    """Create a REMOTE_SET_BUTTON_TAP2_TAP command."""
    cmd1 = 0x25
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def set_status(address: Address, on_level: int) -> (str, Outbound):
    """Create a SET_STATUS command."""
    cmd1 = 0x27
    cmd2 = on_level
    return _create_direct_message(address, cmd1, cmd2)


def set_address_msb(address: Address, high_byte: int) -> (str, Outbound):
    """Create a SET_ADDRESS_MSB command."""
    cmd1 = 0x28
    cmd2 = high_byte
    return _create_direct_message(address, cmd1, cmd2)


def poke_one_byte(address: Address, byte_to_write: int) -> (str, Outbound):
    """Create a POKE_ONE_BYTE command."""
    cmd1 = 0x29
    cmd2 = byte_to_write
    return _create_direct_message(address, cmd1, cmd2)


def peek_one_byte(address: Address, lsb: int) -> (str, Outbound):
    """Create a PEEK_ONE_BYTE command."""
    cmd1 = 0x2b
    cmd2 = lsb
    return _create_direct_message(address, cmd1, cmd2)


def peek_one_byte_internal(address: Address, lsb: int) -> (str, Outbound):
    """Create a PEEK_ONE_BYTE_INTERNAL command."""
    cmd1 = 0x2c
    cmd2 = lsb
    return _create_direct_message(address, cmd1, cmd2)


def poke_one_byte_internal(address: Address, byte_to_write: int) -> (str, Outbound):
    """Create a POKE_ONE_BYTE_INTERNAL command."""
    cmd1 = 0x2d
    cmd2 = byte_to_write
    return _create_direct_message(address, cmd1, cmd2)


def on_at_ramp_rate(address: Address, on_level_and_ramp_rate: int) -> (str, Outbound):
    """Create a ON_AT_RAMP_RATE command."""
    cmd1 = 0x2e
    cmd2 = on_level_and_ramp_rate
    return _create_direct_message(address, cmd1, cmd2)


def extended_get_set(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a EXTENDED_GET_SET command."""
    cmd1 = 0x2e
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def off_at_ramp_rate(address: Address, ramp_rate: int) -> (str, Outbound):
    """Create a OFF_AT_RAMP_RATE command."""
    cmd1 = 0x2f
    cmd2 = ramp_rate
    return _create_direct_message(address, cmd1, cmd2)


def extended_read_write_aldb(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a EXTENDED_READ_WRITE_ALDB command."""
    cmd1 = 0x2f
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def extended_trigger_all_link(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a EXTENDED_TRIGGER_ALL_LINK command."""
    cmd1 = 0x30
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def set_sprinkler_program(address: Address, program: int, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a SET_SPRINKLER_PROGRAM command."""
    cmd1 = 0x40
    cmd2 = program
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def sprinkler_valve_on(address: Address, valve: int) -> (str, Outbound):
    """Create a SPRINKLER_VALVE_ON command."""
    cmd1 = 0x40
    cmd2 = valve
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_get_program_response(address: Address, program: int,
                                   OTHER_EXT_DATA) -> (str, Outbound):
    """Create a SPRINKLER_GET_PROGRAM_RESPONSE command."""
    cmd1 = 0x41
    cmd2 = program
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def sprinkler_valve_off(address: Address, valve: int) -> (str, Outbound):
    """Create a SPRINKLER_VALVE_OFF command."""
    cmd1 = 0x41
    cmd2 = valve
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_program_on(address: Address, program: int) -> (str, Outbound):
    """Create a SPRINKLER_PROGRAM_ON command."""
    cmd1 = 0x42
    cmd2 = program
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_program_off(address: Address, program: int) -> (str, Outbound):
    """Create a SPRINKLER_PROGRAM_OFF command."""
    cmd1 = 0x43
    cmd2 = program
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_load_initialization_values(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_LOAD_INITIALIZATION_VALUES command."""
    cmd1 = 0x44
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_load_eeprom_from_ram(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_LOAD_EEPROM_FROM_RAM command."""
    cmd1 = 0x44
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_get_valve_status(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_GET_VALVE_STATUS command."""
    cmd1 = 0x44
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_inhibit_command_acceptance(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE command."""
    cmd1 = 0x44
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_resume_command_acceptance(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_RESUME_COMMAND_ACCEPTANCE command."""
    cmd1 = 0x44
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_skip_forward(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_SKIP_FORWARD command."""
    cmd1 = 0x44
    cmd2 = 0x05
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_skip_back(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_SKIP_BACK command."""
    cmd1 = 0x44
    cmd2 = 0x06
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_enable_pump_on_v8(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_ENABLE_PUMP_ON_V8 command."""
    cmd1 = 0x44
    cmd2 = 0x07
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_disable_pump_on_v8(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_DISABLE_PUMP_ON_V8 command."""
    cmd1 = 0x44
    cmd2 = 0x08
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_broadcast_on(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_BROADCAST_ON command."""
    cmd1 = 0x44
    cmd2 = 0x09
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_broadcast_off(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_BROADCAST_OFF command."""
    cmd1 = 0x44
    cmd2 = 0x0a
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_load_ram_from_eeprom(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_LOAD_RAM_FROM_EEPROM command."""
    cmd1 = 0x44
    cmd2 = 0x0b
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_sensor_on(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_SENSOR_ON command."""
    cmd1 = 0x44
    cmd2 = 0x0c
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_sensor_off(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_SENSOR_OFF command."""
    cmd1 = 0x44
    cmd2 = 0x0d
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_diagnostics_on(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_DIAGNOSTICS_ON command."""
    cmd1 = 0x44
    cmd2 = 0x0e
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_diagnostics_off(address: Address) -> (str, Outbound):
    """Create a SPRINKLER_DIAGNOSTICS_OFF command."""
    cmd1 = 0x44
    cmd2 = 0x0f
    return _create_direct_message(address, cmd1, cmd2)


def sprinkler_get_program_request(address: Address, program: int) -> (str, Outbound):
    """Create a SPRINKLER_GET_PROGRAM_REQUEST command."""
    cmd1 = 0x45
    cmd2 = program
    return _create_direct_message(address, cmd1, cmd2)


def io_output_on(address: Address, output_num: int) -> (str, Outbound):
    """Create a IO_OUTPUT_ON command."""
    cmd1 = 0x45
    cmd2 = output_num
    return _create_direct_message(address, cmd1, cmd2)


def io_output_off(address: Address, output_num: int) -> (str, Outbound):
    """Create a IO_OUTPUT_OFF command."""
    cmd1 = 0x46
    cmd2 = output_num
    return _create_direct_message(address, cmd1, cmd2)


def io_alarm_data_request(address: Address) -> (str, Outbound):
    """Create a IO_ALARM_DATA_REQUEST command."""
    cmd1 = 0x47
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)

def io_write_output_port(address: Address, value: int) -> (str, Outbound):
    """Create a IO_WRITE_OUTPUT_PORT command."""
    cmd1 = 0x48
    cmd2 = value
    return _create_direct_message(address, cmd1, cmd2)


def io_read_input_port(address: Address) -> (str, Outbound):
    """Create a IO_READ_INPUT_PORT command."""
    cmd1 = 0x49
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def io_get_sensor_value(address: Address, sensor: int) -> (str, Outbound):
    """Create a IO_GET_SENSOR_VALUE command."""
    cmd1 = 0x4a
    cmd2 = sensor
    return _create_direct_message(address, cmd1, cmd2)


def io_set_sensor_1_nominal_value(address: Address, value: int) -> (str, Outbound):
    """Create a IO_SET_SENSOR_1_NOMINAL_VALUE command."""
    cmd1 = 0x4b
    cmd2 = value
    return _create_direct_message(address, cmd1, cmd2)


def io_set_sensor_nominal_value(address: Address, value: int,
                                OTHER_EXT_DATA) -> (str, Outbound):
    """Create a IO_SET_SENSOR_NOMINAL_VALUE command."""
    cmd1 = 0x4b
    cmd2 = value
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def io_get_sensor_alarm_delta(address: Address, sensor: int, delta: int,
                              direction: int) -> (str, Outbound):
    """Create a IO_GET_SENSOR_ALARM_DELTA command."""
    cmd1 = 0x4c
    sensor = sensor & 0x0f
    delta = delta & 0x07 << 4
    direction = 8 if bool(direction) else 0
    cmd2 = (sensor + delta + direction)
    return _create_direct_message(address, cmd1, cmd2)


def io_alarm_data_response(address: Address, OTHER_EXT_DATA) -> (str, Outbound):
    """Create a IO_ALARM_DATA_RESPONSE command."""
    cmd1 = 0x4c
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def io_write_configuration_port(address: Address, bits_0_1: bool,
                                bit_2: bool, bit_3: bool, bit_4: bool,
                                bit_5: bool, bit_6: bool, bit_7: bool
                                ) -> (str, Outbound):
    """Create a IO_WRITE_CONFIGURATION_PORT command."""
    cmd1 = 0x4d
    cmd2 = (bit_7 << 7 + bit_6 << 6 + bit_5 << 5 + bit_4 << 4 + bit_3 << 3 +
            bit_2 << 2 + bits_0_1 << 0)
    return _create_direct_message(address, cmd1, cmd2)


def io_read_configuration_port(address: Address) -> (str, Outbound):
    """Create a IO_READ_CONFIGURATION_PORT command."""
    cmd1 = 0x4e
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def io_module_load_initialization_values(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_LOAD_INITIALIZATION_VALUES command."""
    cmd1 = 0x4f
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def io_module_load_eeprom_from_ram(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_LOAD_EEPROM_FROM_RAM command."""
    cmd1 = 0x4f
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def io_module_status_request(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_STATUS_REQUEST command."""
    cmd1 = 0x4f
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def io_module_read_analog_once(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_READ_ANALOG_ONCE command."""
    cmd1 = 0x4f
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def io_module_read_analog_always(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_READ_ANALOG_ALWAYS command."""
    cmd1 = 0x4f
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def io_module_enable_status_change_message(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE command."""
    cmd1 = 0x4f
    cmd2 = 0x09
    return _create_direct_message(address, cmd1, cmd2)


def io_module_disable_status_change_message(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE command."""
    cmd1 = 0x4f
    cmd2 = 0x0a
    return _create_direct_message(address, cmd1, cmd2)


def io_module_load_ram_from_eeprom(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_LOAD_RAM_FROM_EEPROM command."""
    cmd1 = 0x4f
    cmd2 = 0x0b
    return _create_direct_message(address, cmd1, cmd2)


def io_module_sensor_on(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_SENSOR_ON command."""
    cmd1 = 0x4f
    cmd2 = 0x0c
    return _create_direct_message(address, cmd1, cmd2)


def io_module_sensor_off(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_SENSOR_OFF command."""
    cmd1 = 0x4f
    cmd2 = 0x0d
    return _create_direct_message(address, cmd1, cmd2)


def io_module_diagnostics_on(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_DIAGNOSTICS_ON command."""
    cmd1 = 0x4f
    cmd2 = 0x0e
    return _create_direct_message(address, cmd1, cmd2)


def io_module_diagnostics_off(address: Address) -> (str, Outbound):
    """Create a IO_MODULE_DIAGNOSTICS_OFF command."""
    cmd1 = 0x4f
    cmd2 = 0x0f
    return _create_direct_message(address, cmd1, cmd2)


def pool_device_on(address: Address, device_num: int) -> (str, Outbound):
    """Create a POOL_DEVICE_ON command."""
    cmd1 = 0x50
    cmd2 = device_num
    return _create_direct_message(address, cmd1, cmd2)


def pool_set_device_temperature(address: Address, device_num: int,
                                OTHER_EXT_DATA) -> (str, Outbound):
    """Create a POOL_SET_DEVICE_TEMPERATURE command."""
    cmd1 = 0x50
    cmd2 = device_num
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def pool_device_off(address: Address, device_num: int) -> (str, Outbound):
    """Create a POOL_DEVICE_OFF command."""
    cmd1 = 0x51
    cmd2 = device_num
    return _create_direct_message(address, cmd1, cmd2)


def pool_set_device_hysteresis(address: Address, device_num: int,
                               OTHER_EXT_DATA) -> (str, Outbound):
    """Create a POOL_SET_DEVICE_HYSTERESIS command."""
    cmd1 = 0x51
    cmd2 = device_num
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def pool_temperature_up(address: Address, degrees: int) -> (str, Outbound):
    """Create a POOL_TEMPERATURE_UP command."""
    cmd1 = 0x52
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def pool_temperature_down(address: Address, degrees: int) -> (str, Outbound):
    """Create a POOL_TEMPERATURE_DOWN command."""
    cmd1 = 0x53
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def pool_load_initialization_values(address: Address) -> (str, Outbound):
    """Create a POOL_LOAD_INITIALIZATION_VALUES command."""
    cmd1 = 0x54
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def pool_load_eeprom_from_ram(address: Address) -> (str, Outbound):
    """Create a POOL_LOAD_EEPROM_FROM_RAM command."""
    cmd1 = 0x54
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def pool_get_pool_mode(address: Address) -> (str, Outbound):
    """Create a POOL_GET_POOL_MODE command."""
    cmd1 = 0x54
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def pool_get_ambient_temperature(address: Address) -> (str, Outbound):
    """Create a POOL_GET_AMBIENT_TEMPERATURE command."""
    cmd1 = 0x54
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def pool_get_water_temperature(address: Address) -> (str, Outbound):
    """Create a POOL_GET_WATER_TEMPERATURE command."""
    cmd1 = 0x54
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def pool_get_ph(address: Address) -> (str, Outbound):
    """Create a POOL_GET_PH command."""
    cmd1 = 0x54
    cmd2 = 0x05
    return _create_direct_message(address, cmd1, cmd2)


def door_moveraise_door(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVERAISE_DOOR command."""
    cmd1 = 0x58
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def door_movelower_door(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVELOWER_DOOR command."""
    cmd1 = 0x58
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def door_moveopen_door(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVEOPEN_DOOR command."""
    cmd1 = 0x58
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def door_moveclose_door(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVECLOSE_DOOR command."""
    cmd1 = 0x58
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def door_movestop_door(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVESTOP_DOOR command."""
    cmd1 = 0x58
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def door_movesingle_door_open(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVESINGLE_DOOR_OPEN command."""
    cmd1 = 0x58
    cmd2 = 0x05
    return _create_direct_message(address, cmd1, cmd2)


def door_movesingle_door_close(address: Address) -> (str, Outbound):
    """Create a DOOR_MOVESINGLE_DOOR_CLOSE command."""
    cmd1 = 0x58
    cmd2 = 0x06
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportraise_door(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTRAISE_DOOR command."""
    cmd1 = 0x59
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportlower_door(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTLOWER_DOOR command."""
    cmd1 = 0x59
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportopen_door(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTOPEN_DOOR command."""
    cmd1 = 0x59
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportclose_door(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTCLOSE_DOOR command."""
    cmd1 = 0x59
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportstop_door(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTSTOP_DOOR command."""
    cmd1 = 0x59
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportsingle_door_open(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTSINGLE_DOOR_OPEN command."""
    cmd1 = 0x59
    cmd2 = 0x05
    return _create_direct_message(address, cmd1, cmd2)


def door_status_reportsingle_door_close(address: Address) -> (str, Outbound):
    """Create a DOOR_STATUS_REPORTSINGLE_DOOR_CLOSE command."""
    cmd1 = 0x59
    cmd2 = 0x06
    return _create_direct_message(address, cmd1, cmd2)


def window_coveringopen(address: Address) -> (str, Outbound):
    """Create a WINDOW_COVERINGOPEN command."""
    cmd1 = 0x60
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def window_coveringclose(address: Address) -> (str, Outbound):
    """Create a WINDOW_COVERINGCLOSE command."""
    cmd1 = 0x60
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def window_coveringstop(address: Address) -> (str, Outbound):
    """Create a WINDOW_COVERINGSTOP command."""
    cmd1 = 0x60
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def window_coveringprogram(address: Address) -> (str, Outbound):
    """Create a WINDOW_COVERINGPROGRAM command."""
    cmd1 = 0x60
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def window_covering_position(address: Address, position: int) -> (str, Outbound):
    """Create a WINDOW_COVERING_POSITION command."""
    cmd1 = 0x61
    cmd2 = position
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_temperature_up(address: Address, degrees: int) -> (str, Outbound):
    """Create a THERMOSTAT_TEMPERATURE_UP command."""
    cmd1 = 0x68
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_zone_temperature_up(address: Address, zone: int,
                                   OTHER_EXT_DATA) -> (str, Outbound):
    """Create a THERMOSTAT_ZONE_TEMPERATURE_UP command."""
    cmd1 = 0x68
    cmd2 = zone
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def thermostat_temperature_down(address: Address,
                                degrees: int) -> (str, Outbound):
    """Create a THERMOSTAT_TEMPERATURE_DOWN command."""
    cmd1 = 0x69
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_zone_temperature_down(address: Address, zone: int,
                                     OTHER_EXT_DATA) -> (str, Outbound):
    """Create a THERMOSTAT_ZONE_TEMPERATURE_DOWN command."""
    cmd1 = 0x69
    cmd2 = zone
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def thermostat_get_zone_information(address: Address, zone: int,
                                    info: int) -> (str, Outbound):
    """Create a THERMOSTAT_GET_ZONE_INFORMATION command.

    zone: (int) 0 to 31

    info: (int)
        0 = Temperature
        1 = Setpoint
        2 = Deadband
        3 = Humidity
    """
    zone = zone & 0x0f
    info = info & 0x03 << 5
    cmd1 = 0x6a
    cmd2 = info + zone
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_load_initialization_values(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_LOAD_INITIALIZATION_VALUES command."""
    cmd1 = 0x6b
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_load_eeprom_from_ram(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_LOAD_EEPROM_FROM_RAM command."""
    cmd1 = 0x6b
    cmd2 = 0x01
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_get_mode(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_GET_MODE command."""
    cmd1 = 0x6b
    cmd2 = 0x02
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_get_ambient_temperature(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_GET_AMBIENT_TEMPERATURE command."""
    cmd1 = 0x6b
    cmd2 = 0x03
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_on_heat(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_ON_HEAT command."""
    cmd1 = 0x6b
    cmd2 = 0x04
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_on_cool(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_ON_COOL command."""
    cmd1 = 0x6b
    cmd2 = 0x05
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_on_auto(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_ON_AUTO command."""
    cmd1 = 0x6b
    cmd2 = 0x06
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_on_fan(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_ON_FAN command."""
    cmd1 = 0x6b
    cmd2 = 0x07
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_off_fan(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_OFF_FAN command."""
    cmd1 = 0x6b
    cmd2 = 0x08
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_off_all(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_OFF_ALL command."""
    cmd1 = 0x6b
    cmd2 = 0x09
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_program_heat(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_PROGRAM_HEAT command."""
    cmd1 = 0x6b
    cmd2 = 0x0a
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_program_cool(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_PROGRAM_COOL command."""
    cmd1 = 0x6b
    cmd2 = 0x0b
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_program_auto(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_PROGRAM_AUTO command."""
    cmd1 = 0x6b
    cmd2 = 0x0c
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_get_equipment_state(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_GET_EQUIPMENT_STATE command."""
    cmd1 = 0x6b
    cmd2 = 0x0d
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_equipment_state(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_EQUIPMENT_STATE command."""
    cmd1 = 0x6b
    cmd2 = 0x0e
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_get_temperature_units(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_GET_TEMPERATURE_UNITS command."""
    cmd1 = 0x6b
    cmd2 = 0x0f
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_fahrenheit(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_FAHRENHEIT command."""
    cmd1 = 0x6b
    cmd2 = 0x10
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_celsius(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_CELSIUS command."""
    cmd1 = 0x6b
    cmd2 = 0x11
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_get_fan_on_speed(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_GET_FAN_ON_SPEED command."""
    cmd1 = 0x6b
    cmd2 = 0x12
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_fan_on_speed_low(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_FAN_ON_SPEED_LOW command."""
    cmd1 = 0x6b
    cmd2 = 0x13
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_fan_on_speed_medium(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_FAN_ON_SPEED_MEDIUM command."""
    cmd1 = 0x6b
    cmd2 = 0x14
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_fan_on_speed_high(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_SET_FAN_ON_SPEED_HIGH command."""
    cmd1 = 0x6b
    cmd2 = 0x15
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_enable_status_change_message(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_ENABLE_STATUS_CHANGE_MESSAGE command."""
    cmd1 = 0x6b
    cmd2 = 0x16
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_disable_status_change_message(address: Address) -> (str, Outbound):
    """Create a THERMOSTAT_DISABLE_STATUS_CHANGE_MESSAGE command."""
    cmd1 = 0x6b
    cmd2 = 0x17
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_cool_setpoint(address: Address, degrees: int) -> (str, Outbound):
    """Create a THERMOSTAT_SET_COOL_SETPOINT command."""
    cmd1 = 0x6c
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_zone_cool_setpoint(address: Address, zone: int,
                                      OTHER_EXT_DATA) -> (str, Outbound):
    """Create a THERMOSTAT_SET_ZONE_COOL_SETPOINT command."""
    cmd1 = 0x6c
    cmd2 = zone
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def thermostat_set_heat_setpoint(address: Address,
                                 degrees: int) -> (str, Outbound):
    """Create a THERMOSTAT_SET_HEAT_SETPOINT command."""
    cmd1 = 0x6d
    cmd2 = degrees * 2
    return _create_direct_message(address, cmd1, cmd2)


def thermostat_set_zone_heat_setpoint(address: Address, zone: int,
                                      OTHER_EXT_DATA) -> (str, Outbound):
    """Create a THERMOSTAT_SET_ZONE_HEAT_SETPOINT command."""
    cmd1 = 0x6d
    cmd2 = zone
    return _create_direct_message(address, cmd1, cmd2, True, OTHER_EXT_DATA)


def assign_to_companion_group(address: Address) -> (str, Outbound):
    """Create a ASSIGN_TO_COMPANION_GROUP command."""
    cmd1 = 0x81
    cmd2 = 0x00
    return _create_direct_message(address, cmd1, cmd2)
