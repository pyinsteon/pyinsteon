"""Create a topic and a direct message."""
import logging
from math import ceil

from .. import pub
from ..address import Address
from ..constants import RampRate
from ..utils import subscribe_topic
from ..topics import (
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
    EXTENDED_GET_SET_2,
    EXTENDED_READ_WRITE_ALDB,
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
    STATUS_REQUEST,
    THERMOSTAT_GET_ZONE_INFORMATION,
    THERMOSTAT_CONTROL,
    THERMOSTAT_SET_COOL_SETPOINT,
    THERMOSTAT_SET_HEAT_SETPOINT,
    THERMOSTAT_SET_ZONE_COOL_SETPOINT,
    THERMOSTAT_SET_ZONE_HEAT_SETPOINT,
    THERMOSTAT_TEMPERATURE_DOWN,
    THERMOSTAT_TEMPERATURE_UP,
    THERMOSTAT_ZONE_TEMPERATURE_DOWN,
    THERMOSTAT_ZONE_TEMPERATURE_UP,
    WINDOW_COVERING_CLOSE,
    WINDOW_COVERING_OPEN,
    WINDOW_COVERING_POSITION,
    WINDOW_COVERING_PROGRAM,
    WINDOW_COVERING_STOP,
)
from .commands import commands
from .messages.all_link_record_flags import create
from .messages.message_flags import create as create_flags
from .messages.outbound import send_extended, send_standard
from .messages.user_data import UserData
from .topic_converters import topic_to_command_handler, topic_to_message_type

_LOGGER = logging.getLogger(__name__)
# pylint: disable=invalid-name
topic_register = {}


def register_command_handlers():
    """Register outbound handlers."""
    for topic in topic_register:
        func = topic_register[topic]
        subscribe_topic(func, topic)


# The following messages are all send_standard or send_extended messages
# The topis is based on the cmd1, cmd2 and extended message flags values


def _create_direct_message(
    topic, address, cmd2=None, user_data=None, crc=False, priority=5
):
    main_topic = topic.name.split(".")[1]
    command = commands.get_command(main_topic)
    extended = user_data is not None
    cmd2 = command.cmd2 if command.cmd2 is not None else cmd2
    flag_type = topic_to_message_type(topic)
    flags = create_flags(flag_type, extended)
    if extended:
        if crc:
            user_data.set_crc(command.cmd1, cmd2)
        else:
            user_data.set_checksum(command.cmd1, cmd2)
        send_extended(
            address=address,
            cmd1=command.cmd1,
            cmd2=cmd2,
            flags=flags,
            user_data=user_data,
            topic=topic,
            priority=priority,
        )
    else:
        send_standard(
            address=address,
            cmd1=command.cmd1,
            cmd2=cmd2,
            flags=flags,
            topic=topic,
            priority=priority,
        )


@topic_to_command_handler(register_list=topic_register, topic=ASSIGN_TO_ALL_LINK_GROUP)
def assign_to_all_link_group(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a ASSIGN_TO_ALL_LINK_GROUP command."""
    _create_direct_message(topic=topic, address=address, cmd2=group)


@topic_to_command_handler(
    register_list=topic_register, topic=DELETE_FROM_ALL_LINK_GROUP
)
def delete_from_all_link_group(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a DELETE_FROM_ALL_LINK_GROUP command."""
    _create_direct_message(topic=topic, address=address, cmd2=group)


@topic_to_command_handler(register_list=topic_register, topic=PRODUCT_DATA_REQUEST)
def product_data_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a PRODUCT_DATA_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=FX_USERNAME)
def fx_username(address: Address, topic=pub.AUTO_TOPIC):
    """Create a FX_USERNAME command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DEVICE_TEXT_STRING_REQUEST
)
def device_text_string_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DEVICE_TEXT_STRING_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SET_DEVICE_TEXT_STRING)
def set_device_text_string(address: Address, user_data, topic=pub.AUTO_TOPIC):
    """Create a SET_DEVICE_TEXT_STRING command."""
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=SET_ALL_LINK_COMMAND_ALIAS
)
def set_all_link_command_alias(address: Address, user_data, topic=pub.AUTO_TOPIC):
    """Create a SET_ALL_LINK_COMMAND_ALIAS command."""
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=SET_ALL_LINK)
def set_all_link(address: Address, user_data, topic=pub.AUTO_TOPIC):
    """Create a SET_ALL_LINK command."""
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=ENTER_LINKING_MODE)
def enter_linking_mode(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a ENTER_LINKING_MODE command."""
    user_data = UserData()
    _create_direct_message(
        topic=topic, address=address, cmd2=group, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=ENTER_UNLINKING_MODE)
def enter_unlinking_mode(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a ENTER_UNLINKING_MODE command."""
    _create_direct_message(topic=topic, address=address, cmd2=group)


@topic_to_command_handler(
    register_list=topic_register, topic=GET_INSTEON_ENGINE_VERSION
)
def get_insteon_engine_version(address: Address, topic=pub.AUTO_TOPIC):
    """Create a GET_INSTEON_ENGINE_VERSION command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=topic_register, topic=PING)
def ping(address: Address, topic=pub.AUTO_TOPIC):
    """Create a PING command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=topic_register, topic=ID_REQUEST)
def id_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a ID_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=topic_register, topic=ON)
def on(address: Address, on_level: int, group=0, topic=pub.AUTO_TOPIC):
    """Create a ON command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=on_level, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=topic_register, topic=ON_FAST)
def on_fast(address: Address, on_level: int, group: int, topic=pub.AUTO_TOPIC):
    """Create a ON_FAST command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=on_level, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=topic_register, topic=OFF)
def off(address: Address, group: int, cmd2: int = 0, topic=pub.AUTO_TOPIC):
    """Create a OFF command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=cmd2, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=topic_register, topic=OFF_FAST)
def off_fast(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a OFF_FAST command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=0, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=topic_register, topic=BRIGHTEN_ONE_STEP)
def brighten_one_step(address: Address, topic=pub.AUTO_TOPIC):
    """Create a BRIGHTEN_ONE_STEP command."""
    _create_direct_message(topic=topic, address=address, cmd2=0, priority=3)


@topic_to_command_handler(register_list=topic_register, topic=DIM_ONE_STEP)
def dim_one_step(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DIM_ONE_STEP command."""
    _create_direct_message(topic=topic, address=address, cmd2=0, priority=3)


@topic_to_command_handler(register_list=topic_register, topic=STATUS_REQUEST)
def status_request(address: Address, status_type: int = 0, topic=pub.AUTO_TOPIC):
    """Create a STATUS_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=status_type, priority=7)


@topic_to_command_handler(register_list=topic_register, topic=GET_OPERATING_FLAGS)
def get_operating_flags(address: Address, flags_requested: int, topic=pub.AUTO_TOPIC):
    """Create a GET_OPERATING_FLAGS command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=flags_requested, priority=7
    )


@topic_to_command_handler(register_list=topic_register, topic=SET_OPERATING_FLAGS)
def set_operating_flags(
    address: Address, cmd: int, extended=False, topic=pub.AUTO_TOPIC
):
    """Create a SET_OPERATING_FLAGS command."""
    user_data = UserData() if extended else None
    _create_direct_message(topic=topic, address=address, cmd2=cmd, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=INSTANT_CHANGE)
def instant_change(address: Address, on_level: int, topic=pub.AUTO_TOPIC):
    """Create a INSTANT_CHANGE command."""
    _create_direct_message(topic=topic, address=address, cmd2=on_level, priority=3)


@topic_to_command_handler(register_list=topic_register, topic=SET_STATUS)
def set_status(address: Address, on_level: int, topic=pub.AUTO_TOPIC):
    """Create a SET_STATUS command."""
    _create_direct_message(topic=topic, address=address, cmd2=on_level)


@topic_to_command_handler(register_list=topic_register, topic=SET_ADDRESS_MSB)
def set_address_msb(address: Address, high_byte: int, topic=pub.AUTO_TOPIC):
    """Create a SET_ADDRESS_MSB command."""
    _create_direct_message(topic=topic, address=address, cmd2=high_byte)


@topic_to_command_handler(register_list=topic_register, topic=POKE_ONE_BYTE)
def poke_one_byte(address: Address, byte_to_write: int, topic=pub.AUTO_TOPIC):
    """Create a POKE_ONE_BYTE command."""
    _create_direct_message(topic=topic, address=address, cmd2=byte_to_write)


@topic_to_command_handler(register_list=topic_register, topic=PEEK_ONE_BYTE)
def peek_one_byte(address: Address, lsb: int, topic=pub.AUTO_TOPIC):
    """Create a PEEK_ONE_BYTE command."""
    _create_direct_message(topic=topic, address=address, cmd2=lsb)


@topic_to_command_handler(register_list=topic_register, topic=PEEK_ONE_BYTE_INTERNAL)
def peek_one_byte_internal(address: Address, lsb: int, topic=pub.AUTO_TOPIC):
    """Create a PEEK_ONE_BYTE_INTERNAL command."""
    _create_direct_message(topic=topic, address=address, cmd2=lsb)


@topic_to_command_handler(register_list=topic_register, topic=POKE_ONE_BYTE_INTERNAL)
def poke_one_byte_internal(address: Address, byte_to_write: int, topic=pub.AUTO_TOPIC):
    """Create a POKE_ONE_BYTE_INTERNAL command."""
    _create_direct_message(topic=topic, address=address, cmd2=byte_to_write)


@topic_to_command_handler(register_list=topic_register, topic=ON_AT_RAMP_RATE)
def on_at_ramp_rate(
    address: Address, on_level: int, ramp_rate: RampRate, topic=pub.AUTO_TOPIC
):
    """Create a ON_AT_RAMP_RATE command."""
    on_level = min(0x10, on_level & 0xF0)
    ramp_rate = ceil(int(ramp_rate) / 2) + 1 & 0x0F
    cmd2 = on_level + ramp_rate
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, priority=3)


@topic_to_command_handler(register_list=topic_register, topic=EXTENDED_GET_SET)
def extended_get_set(
    address: Address,
    data1=0,
    data2=0,
    data3=0,
    data4=0,
    data5=0,
    data6=0,
    data7=0,
    data8=0,
    data9=0,
    data10=0,
    data11=0,
    data12=0,
    data13=0,
    data14=0,
    crc=False,
    topic=pub.AUTO_TOPIC,
):
    """Create a EXTENDED_GET_SET command."""
    data = {}
    items = locals()
    for index in range(1, 15):
        data["d{}".format(index)] = items["data{}".format(index)]
    user_data = UserData(data)
    _create_direct_message(
        topic=topic, address=address, cmd2=0, user_data=user_data, crc=crc
    )


@topic_to_command_handler(register_list=topic_register, topic=EXTENDED_GET_SET_2)
def extended_get_set_2(
    address: Address,
    data1=0,
    data2=0,
    data3=0,
    data4=0,
    data5=0,
    data6=0,
    data7=0,
    data8=0,
    data9=0,
    data10=0,
    data11=0,
    data12=0,
    data13=0,
    data14=0,
    topic=pub.AUTO_TOPIC,
):
    """Create a EXTENDED_GET_SET_2 command."""
    data = {}
    items = locals()
    for index in range(1, 15):
        data["d{}".format(index)] = items["data{}".format(index)]
    user_data = UserData(data)
    _create_direct_message(
        topic=topic, address=address, cmd2=0x02, user_data=user_data, crc=True
    )


@topic_to_command_handler(register_list=topic_register, topic=OFF_AT_RAMP_RATE)
def off_at_ramp_rate(
    address: Address, on_level: int, ramp_rate: RampRate, topic=pub.AUTO_TOPIC
):
    """Create a OFF_AT_RAMP_RATE command."""
    on_level = min(0x10, on_level & 0xF0)
    ramp_rate = ceil(int(ramp_rate) / 2) + 1 & 0x0F
    cmd2 = on_level + ramp_rate
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, priority=3)


def _read_aldb(address, mem_addr, num_recs, topic):
    # num_recs = 0 if mem_addr == 0x0000 else 1
    mem_hi = mem_addr >> 8
    mem_lo = mem_addr & 0xFF
    user_data = UserData(
        {"d1": 0x00, "d2": 0x00, "d3": mem_hi, "d4": mem_lo, "d5": num_recs}
    )
    _create_direct_message(topic=topic, address=address, cmd2=0, user_data=user_data)


def _write_aldb(
    address,
    mem_addr,
    controller,
    group,
    target,
    data1,
    data2,
    data3,
    in_use,
    high_water_mark,
    bit5,
    bit4,
    topic,
):
    address = Address(address)
    target = Address(target)
    mem_hi = mem_addr >> 8
    mem_lo = mem_addr & 0xFF
    flags = create(
        in_use=in_use, controller=controller, hwm=high_water_mark, bit5=bit5, bit4=bit4
    )
    user_data = UserData(
        {
            "d2": 0x02,
            "d3": mem_hi,
            "d4": mem_lo,
            "d5": 0x08,
            "d6": int(flags),
            "d7": group,
            "d8": target.high,
            "d9": target.middle,
            "d10": target.low,
            "d11": data1,
            "d12": data2,
            "d13": data3,
        }
    )
    _create_direct_message(topic=topic, address=address, cmd2=0, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=EXTENDED_READ_WRITE_ALDB)
def extended_read_write_aldb(
    address: Address,
    action: int,
    mem_addr: int,
    num_recs: int = 0,
    controller: bool = True,
    group: int = 0x01,
    target: Address = None,
    data1: int = 0x00,
    data2: int = 0x00,
    data3: int = 0x00,
    in_use: bool = True,
    high_water_mark: bool = False,
    bit5: int = 0,
    bit4: int = 0,
    topic=pub.AUTO_TOPIC,
):
    """Create a EXTENDED_READ_WRITE_ALDB command."""
    if action == 0x00:
        _read_aldb(address=address, mem_addr=mem_addr, num_recs=num_recs, topic=topic)
    elif action == 0x02:
        _write_aldb(
            address=address,
            mem_addr=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            high_water_mark=high_water_mark,
            bit5=bit5,
            bit4=bit4,
            topic=topic,
        )


@topic_to_command_handler(register_list=topic_register, topic=EXTENDED_TRIGGER_ALL_LINK)
def extended_trigger_all_link(address: Address, user_data, topic=pub.AUTO_TOPIC):
    """Create a EXTENDED_TRIGGER_ALL_LINK command."""
    _create_direct_message(topic=topic, address=address, cmd2=0, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=SET_SPRINKLER_PROGRAM)
def set_sprinkler_program(
    address: Address, program: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a SET_SPRINKLER_PROGRAM command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=program, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_VALVE_ON)
def sprinkler_valve_on(address: Address, valve: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_VALVE_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=valve)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_GET_PROGRAM_RESPONSE
)
def sprinkler_get_program_response(
    address: Address, program: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a SPRINKLER_GET_PROGRAM_RESPONSE command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=program, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_VALVE_OFF)
def sprinkler_valve_off(address: Address, valve: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_VALVE_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=valve)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_PROGRAM_ON)
def sprinkler_program_on(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_PROGRAM_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_PROGRAM_OFF)
def sprinkler_program_off(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_PROGRAM_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_LOAD_INITIALIZATION_VALUES
)
def sprinkler_load_initialization_values(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_LOAD_INITIALIZATION_VALUES command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_LOAD_EEPROM_FROM_RAM
)
def sprinkler_load_eeprom_from_ram(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_LOAD_EEPROM_FROM_RAM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_GET_VALVE_STATUS
)
def sprinkler_get_valve_status(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_GET_VALVE_STATUS command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE
)
def sprinkler_inhibit_command_acceptance(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_INHIBIT_COMMAND_ACCEPTANCE command."""
    user_data = UserData({"d1": 0x03})
    _create_direct_message(topic=topic, address=address, cmd2=0x44, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_RESUME_COMMAND_ACCEPTANCE
)
def sprinkler_resume_command_acceptance(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_RESUME_COMMAND_ACCEPTANCE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_SKIP_FORWARD)
def sprinkler_skip_forward(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_SKIP_FORWARD command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_SKIP_BACK)
def sprinkler_skip_back(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_SKIP_BACK command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_ENABLE_PUMP_ON_V8
)
def sprinkler_enable_pump_on_v8(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_ENABLE_PUMP_ON_V8 command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_DISABLE_PUMP_ON_V8
)
def sprinkler_disable_pump_on_v8(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_DISABLE_PUMP_ON_V8 command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_BROADCAST_ON)
def sprinkler_broadcast_on(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_BROADCAST_ON command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_BROADCAST_OFF)
def sprinkler_broadcast_off(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_BROADCAST_OFF command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_LOAD_RAM_FROM_EEPROM
)
def sprinkler_load_ram_from_eeprom(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_LOAD_RAM_FROM_EEPROM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_SENSOR_ON)
def sprinkler_sensor_on(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_SENSOR_ON command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_SENSOR_OFF)
def sprinkler_sensor_off(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_SENSOR_OFF command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_DIAGNOSTICS_ON)
def sprinkler_diagnostics_on(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_DIAGNOSTICS_ON command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=SPRINKLER_DIAGNOSTICS_OFF)
def sprinkler_diagnostics_off(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_DIAGNOSTICS_OFF command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=SPRINKLER_GET_PROGRAM_REQUEST
)
def sprinkler_get_program_request(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_GET_PROGRAM_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(register_list=topic_register, topic=IO_OUTPUT_ON)
def io_output_on(address: Address, output_num: int, topic=pub.AUTO_TOPIC):
    """Create a IO_OUTPUT_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=output_num)


@topic_to_command_handler(register_list=topic_register, topic=IO_OUTPUT_OFF)
def io_output_off(address: Address, output_num: int, topic=pub.AUTO_TOPIC):
    """Create a IO_OUTPUT_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=output_num)


@topic_to_command_handler(register_list=topic_register, topic=IO_ALARM_DATA_REQUEST)
def io_alarm_data_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_ALARM_DATA_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_WRITE_OUTPUT_PORT)
def io_write_output_port(address: Address, value: int, topic=pub.AUTO_TOPIC):
    """Create a IO_WRITE_OUTPUT_PORT command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_READ_INPUT_PORT)
def io_read_input_port(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_READ_INPUT_PORT command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_GET_SENSOR_VALUE)
def io_get_sensor_value(address: Address, sensor: int, topic=pub.AUTO_TOPIC):
    """Create a IO_GET_SENSOR_VALUE command."""
    _create_direct_message(topic=topic, address=address, cmd2=sensor)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_SET_SENSOR_1_NOMINAL_VALUE
)
def io_set_sensor_1_nominal_value(address: Address, value: int, topic=pub.AUTO_TOPIC):
    """Create a IO_SET_SENSOR_1_NOMINAL_VALUE command."""
    _create_direct_message(topic=topic, address=address, cmd2=value)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_SET_SENSOR_NOMINAL_VALUE
)
def io_set_sensor_nominal_value(
    address: Address, value: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a IO_SET_SENSOR_NOMINAL_VALUE command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=value, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=IO_GET_SENSOR_ALARM_DELTA)
def io_get_sensor_alarm_delta(
    address: Address, sensor: int, delta: int, direction: int, topic=pub.AUTO_TOPIC
):
    """Create a IO_GET_SENSOR_ALARM_DELTA command."""
    sensor = sensor & 0x0F
    delta = delta & 0x07 << 4
    direction = 8 if bool(direction) else 0
    cmd2 = sensor + delta + direction
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=topic_register, topic=IO_ALARM_DATA_RESPONSE)
def io_alarm_data_response(address: Address, user_data, topic=pub.AUTO_TOPIC):
    """Create a IO_ALARM_DATA_RESPONSE command."""
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_WRITE_CONFIGURATION_PORT
)
def io_write_configuration_port(
    address: Address,
    bits_0_1: bool,
    bit_2: bool,
    bit_3: bool,
    bit_4: bool,
    bit_5: bool,
    bit_6: bool,
    bit_7: bool,
    topic=pub.AUTO_TOPIC,
):
    """Create a IO_WRITE_CONFIGURATION_PORT command."""
    cmd2 = (
        bit_7
        << 7 + bit_6
        << 6 + bit_5
        << 5 + bit_4
        << 4 + bit_3
        << 3 + bit_2
        << 2 + bits_0_1
        << 0
    )
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_READ_CONFIGURATION_PORT
)
def io_read_configuration_port(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_READ_CONFIGURATION_PORT command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_LOAD_INITIALIZATION_VALUES
)
def io_module_load_initialization_values(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_LOAD_INITIALIZATION_VALUES command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_LOAD_EEPROM_FROM_RAM
)
def io_module_load_eeprom_from_ram(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_LOAD_EEPROM_FROM_RAM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_MODULE_STATUS_REQUEST)
def io_module_status_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_STATUS_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_READ_ANALOG_ONCE
)
def io_module_read_analog_once(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_READ_ANALOG_ONCE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_READ_ANALOG_ALWAYS
)
def io_module_read_analog_always(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_READ_ANALOG_ALWAYS command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE
)
def io_module_enable_status_change_message(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_ENABLE_STATUS_CHANGE_MESSAGE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE
)
def io_module_disable_status_change_message(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_DISABLE_STATUS_CHANGE_MESSAGE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=IO_MODULE_LOAD_RAM_FROM_EEPROM
)
def io_module_load_ram_from_eeprom(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_LOAD_RAM_FROM_EEPROM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_MODULE_SENSOR_ON)
def io_module_sensor_on(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_SENSOR_ON command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_MODULE_SENSOR_OFF)
def io_module_sensor_off(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_SENSOR_OFF command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_MODULE_DIAGNOSTICS_ON)
def io_module_diagnostics_on(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_DIAGNOSTICS_ON command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=IO_MODULE_DIAGNOSTICS_OFF)
def io_module_diagnostics_off(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_MODULE_DIAGNOSTICS_OFF command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=POOL_DEVICE_ON)
def pool_device_on(address: Address, device_num: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_DEVICE_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=device_num)


@topic_to_command_handler(
    register_list=topic_register, topic=POOL_SET_DEVICE_TEMPERATURE
)
def pool_set_device_temperature(
    address: Address, device_num: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a POOL_SET_DEVICE_TEMPERATURE command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=device_num, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=POOL_DEVICE_OFF)
def pool_device_off(address: Address, device_num: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_DEVICE_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=device_num)


@topic_to_command_handler(
    register_list=topic_register, topic=POOL_SET_DEVICE_HYSTERESIS
)
def pool_set_device_hysteresis(
    address: Address, device_num: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a POOL_SET_DEVICE_HYSTERESIS command."""
    _create_direct_message(
        topic=topic, address=address, cmd2=device_num, user_data=user_data
    )


@topic_to_command_handler(register_list=topic_register, topic=POOL_TEMPERATURE_UP)
def pool_temperature_up(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_TEMPERATURE_UP command."""
    cmd2 = degrees * 2
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=topic_register, topic=POOL_TEMPERATURE_DOWN)
def pool_temperature_down(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_TEMPERATURE_DOWN command."""
    cmd2 = degrees * 2
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=topic_register, topic=POOL_LOAD_INITIALIZATION_VALUES
)
def pool_load_initialization_values(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_LOAD_INITIALIZATION_VALUES command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=POOL_LOAD_EEPROM_FROM_RAM)
def pool_load_eeprom_from_ram(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_LOAD_EEPROM_FROM_RAM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=POOL_GET_POOL_MODE)
def pool_get_pool_mode(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_GET_POOL_MODE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=POOL_GET_AMBIENT_TEMPERATURE
)
def pool_get_ambient_temperature(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_GET_AMBIENT_TEMPERATURE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=POOL_GET_WATER_TEMPERATURE
)
def pool_get_water_temperature(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_GET_WATER_TEMPERATURE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=POOL_GET_PH)
def pool_get_ph(address: Address, topic=pub.AUTO_TOPIC):
    """Create a POOL_GET_PH command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=DOOR_MOVE_RAISE_DOOR)
def door_move_raise_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_RAISE_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=DOOR_MOVE_LOWER_DOOR)
def door_move_lower_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_LOWER_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=DOOR_MOVE_OPEN_DOOR)
def door_move_open_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_OPEN_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=DOOR_MOVE_CLOSE_DOOR)
def door_move_close_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_CLOSE_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=DOOR_MOVE_STOP_DOOR)
def door_move_stop_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_STOP_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_MOVE_SINGLE_DOOR_OPEN
)
def door_move_single_door_open(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_SINGLE_DOOR_OPEN command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_MOVE_SINGLE_DOOR_CLOSE
)
def door_move_single_door_close(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_MOVE_SINGLE_DOOR_CLOSE command."""
    user_data = UserData({"d1": 0x06})
    _create_direct_message(topic=topic, address=address, cmd2=0x58, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_RAISE_DOOR
)
def door_status_report_raise_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_RAISE_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_LOWER_DOOR
)
def door_status_reportlower_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_LOWER_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_OPEN_DOOR
)
def door_status_report_open_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_OPEN_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_CLOSE_DOOR
)
def door_status_report_close_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_CLOSE_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_STOP_DOOR
)
def door_status_report_stop_door(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_STOP_DOOR command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_SINGLE_DOOR_OPEN
)
def door_status_report_single_door_open(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_SINGLE_DOOR_OPEN command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=topic_register, topic=DOOR_STATUS_REPORT_SINGLE_DOOR_CLOSE
)
def door_status_report_single_door_close(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT_SINGLE_DOOR_CLOSE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=WINDOW_COVERING_OPEN)
def window_covering_open(address: Address, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_OPEN command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=WINDOW_COVERING_CLOSE)
def window_covering_close(address: Address, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_CLOSE command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=WINDOW_COVERING_STOP)
def window_covering_stop(address: Address, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_STOP command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=WINDOW_COVERING_PROGRAM)
def window_covering_program(address: Address, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_PROGRAM command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=topic_register, topic=WINDOW_COVERING_POSITION)
def window_covering_position(address: Address, position: int, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_POSITION command."""
    _create_direct_message(topic=topic, address=address, cmd2=position)


@topic_to_command_handler(register_list=topic_register, topic=THERMOSTAT_TEMPERATURE_UP)
def thermostat_temperature_up(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a THERMOSTAT_TEMPERATURE_UP command."""
    cmd2 = int(round(degrees * 2, 0))
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_ZONE_TEMPERATURE_UP
)
def thermostat_zone_temperature_up(
    address: Address, zone: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_ZONE_TEMPERATURE_UP command."""
    _create_direct_message(topic=topic, address=address, cmd2=zone, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_TEMPERATURE_DOWN
)
def thermostat_temperature_down(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a THERMOSTAT_TEMPERATURE_DOWN command."""
    cmd2 = int(round(degrees * 2, 0))
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_ZONE_TEMPERATURE_DOWN
)
def thermostat_zone_temperature_down(
    address: Address, zone: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_ZONE_TEMPERATURE_DOWN command."""
    _create_direct_message(topic=topic, address=address, cmd2=zone, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_GET_ZONE_INFORMATION
)
def thermostat_get_zone_information(
    address: Address, zone: int, info: int, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_GET_ZONE_INFORMATION command.

    zone: (int) 0 to 31

    info: (int)
        0 = Temperature
        1 = Setpoint
        2 = Deadband
        3 = Humidity
    """
    zone = zone & 0x0F
    info = info & 0x03 << 5
    cmd2 = info + zone
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=topic_register, topic=THERMOSTAT_CONTROL)
def thermostat_control(address: Address, mode: int, topic=pub.AUTO_TOPIC):
    """Create a THERMOSTAT_CONTROL command."""
    user_data = UserData()
    _create_direct_message(
        topic=topic, address=address, cmd2=int(mode), user_data=user_data
    )


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_SET_COOL_SETPOINT
)
def thermostat_set_cool_setpoint(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a THERMOSTAT_SET_COOL_SETPOINT command."""
    cmd2 = int(degrees * 2)
    user_data = UserData()
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_SET_ZONE_COOL_SETPOINT
)
def thermostat_set_zone_cool_setpoint(
    address: Address, zone: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_SET_ZONE_COOL_SETPOINT command."""
    _create_direct_message(topic=topic, address=address, cmd2=zone, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_SET_HEAT_SETPOINT
)
def thermostat_set_heat_setpoint(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a THERMOSTAT_SET_HEAT_SETPOINT command."""
    cmd2 = int(degrees * 2)
    user_data = UserData()
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)


@topic_to_command_handler(
    register_list=topic_register, topic=THERMOSTAT_SET_ZONE_HEAT_SETPOINT
)
def thermostat_set_zone_heat_setpoint(
    address: Address, zone: int, user_data, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_SET_ZONE_HEAT_SETPOINT command."""
    _create_direct_message(topic=topic, address=address, cmd2=zone, user_data=user_data)


@topic_to_command_handler(register_list=topic_register, topic=ASSIGN_TO_COMPANION_GROUP)
def assign_to_companion_group(address: Address, topic=pub.AUTO_TOPIC):
    """Create a ASSIGN_TO_COMPANION_GROUP command."""
    _create_direct_message(topic=topic, address=address)
