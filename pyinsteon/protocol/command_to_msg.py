"""Create a topic and a direct message."""
import logging
from math import ceil

from .. import pub
from ..address import Address
from ..commands import commands
from ..constants import (
    DoorCommand,
    IOModuleControlCommand,
    PoolControlCommand,
    RampRate,
    SprinklerControlCommand,
    ThermostatCommand,
    ThermostatZoneInfo,
    WindowCoveringCommand,
)
from ..data_types.all_link_record_flags import AllLinkRecordFlags
from ..data_types.io_sensor_config_flags import IOPortConfigFlags
from ..data_types.message_flags import MessageFlags
from ..data_types.user_data import UserData
from ..topics import (
    ASSIGN_TO_ALL_LINK_GROUP,
    BEEP,
    BRIGHTEN_ONE_STEP,
    DELETE_FROM_ALL_LINK_GROUP,
    DEVICE_TEXT_STRING_REQUEST,
    DIM_ONE_STEP,
    DOOR_CONTROL,
    DOOR_STATUS_REPORT,
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
    IO_GET_SENSOR_ALARM_DELTA,
    IO_GET_SENSOR_VALUE,
    IO_MODULE_CONTROL,
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
    POOL_CONTROL,
    POOL_DEVICE_OFF,
    POOL_DEVICE_ON,
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
    SPRINKLER_CONTROL,
    SPRINKLER_GET_PROGRAM_REQUEST,
    SPRINKLER_PROGRAM_OFF,
    SPRINKLER_PROGRAM_ON,
    SPRINKLER_VALVE_OFF,
    SPRINKLER_VALVE_ON,
    STATUS_REQUEST,
    THERMOSTAT_CONTROL,
    THERMOSTAT_GET_ZONE_INFORMATION,
    THERMOSTAT_SET_COOL_SETPOINT,
    THERMOSTAT_SET_HEAT_SETPOINT,
    THERMOSTAT_TEMPERATURE_DOWN,
    THERMOSTAT_TEMPERATURE_UP,
    WINDOW_COVERING_CONTROL,
    WINDOW_COVERING_POSITION,
)
from ..utils import subscribe_topic
from .messages.outbound import send_extended, send_standard
from .topic_converters import topic_to_command_handler, topic_to_message_type

_LOGGER = logging.getLogger(__name__)

COMMAND_REGISTER = {}


def register_command_handlers():
    """Register outbound handlers."""
    for topic, func in COMMAND_REGISTER.items():
        subscribe_topic(func, topic)


# The following messages are all send_standard or send_extended messages
# The topis is based on the cmd1, cmd2 and extended message flags values


def _create_direct_message(
    topic, address, cmd2=None, user_data=None, crc=False, priority=5
):
    main_topic = topic.name.split(".")[1]
    command = commands.get_command(main_topic)
    extended = user_data is not None
    cmd2 = command.cmd2 if command.cmd2 is not None else cmd2 if cmd2 is not None else 0
    msg_type = topic_to_message_type(topic)
    flags = MessageFlags.create(msg_type, extended)
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


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=ASSIGN_TO_ALL_LINK_GROUP
)
def assign_to_all_link_group(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a ASSIGN_TO_ALL_LINK_GROUP command."""
    _create_direct_message(topic=topic, address=address, cmd2=group)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=DELETE_FROM_ALL_LINK_GROUP
)
def delete_from_all_link_group(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a DELETE_FROM_ALL_LINK_GROUP command."""
    _create_direct_message(topic=topic, address=address, cmd2=group)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=PRODUCT_DATA_REQUEST)
def product_data_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a PRODUCT_DATA_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=FX_USERNAME)
def fx_username(address: Address, topic=pub.AUTO_TOPIC):
    """Create a FX_USERNAME command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=DEVICE_TEXT_STRING_REQUEST
)
def device_text_string_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DEVICE_TEXT_STRING_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_DEVICE_TEXT_STRING)
def set_device_text_string(address: Address, value: str, topic=pub.AUTO_TOPIC):
    """Create a SET_DEVICE_TEXT_STRING command."""
    user_data = UserData()
    for item in range(0, min(len(value), 14)):
        user_data[f"d{item + 1}"] = ord(value[item])
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=SET_ALL_LINK_COMMAND_ALIAS
)
def set_all_link_command_alias(
    address: Address, cmd: int, alias: int, extended: bool, topic=pub.AUTO_TOPIC
):
    """Create a SET_ALL_LINK_COMMAND_ALIAS command."""
    alias_hi = alias >> 8
    alias_lo = alias & 0xFF
    data4 = 1 if extended else 0
    user_data = UserData({"d1": cmd, "d2": alias_hi, "d3": alias_lo, "d4": data4})
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_ALL_LINK)
def set_all_link(address: Address, topic=pub.AUTO_TOPIC):
    """Create a SET_ALL_LINK command."""
    user_data = UserData()
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ENTER_LINKING_MODE)
def enter_linking_mode(
    address: Address, group: int, extended: bool, topic=pub.AUTO_TOPIC
):
    """Create a ENTER_LINKING_MODE command."""
    if extended:
        user_data = UserData()
    else:
        user_data = None
    _create_direct_message(
        topic=topic, address=address, cmd2=group, user_data=user_data
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ENTER_UNLINKING_MODE)
def enter_unlinking_mode(
    address: Address, group: int, extended: bool, topic=pub.AUTO_TOPIC
):
    """Create a ENTER_UNLINKING_MODE command."""
    if extended:
        user_data = UserData()
    else:
        user_data = None
    _create_direct_message(
        topic=topic, address=address, cmd2=group, user_data=user_data
    )


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=GET_INSTEON_ENGINE_VERSION
)
def get_insteon_engine_version(address: Address, topic=pub.AUTO_TOPIC):
    """Create a GET_INSTEON_ENGINE_VERSION command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=PING)
def ping(address: Address, topic=pub.AUTO_TOPIC):
    """Create a PING command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ID_REQUEST)
def id_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a ID_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=0x00)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ON)
def on(address: Address, on_level: int, group=0, topic=pub.AUTO_TOPIC):
    """Create a ON command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=on_level, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ON_FAST)
def on_fast(address: Address, on_level: int, group: int, topic=pub.AUTO_TOPIC):
    """Create a ON_FAST command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=on_level, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=OFF)
def off(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a OFF command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=0, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=OFF_FAST)
def off_fast(address: Address, group: int, topic=pub.AUTO_TOPIC):
    """Create a OFF_FAST command."""
    user_data = None
    if group and group > 1:
        user_data = UserData({"d1": group})
    _create_direct_message(
        topic=topic, address=address, cmd2=0, user_data=user_data, priority=3
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=BRIGHTEN_ONE_STEP)
def brighten_one_step(address: Address, topic=pub.AUTO_TOPIC):
    """Create a BRIGHTEN_ONE_STEP command."""
    _create_direct_message(topic=topic, address=address, cmd2=0, priority=3)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=DIM_ONE_STEP)
def dim_one_step(address: Address, topic=pub.AUTO_TOPIC):
    """Create a DIM_ONE_STEP command."""
    _create_direct_message(topic=topic, address=address, cmd2=0, priority=3)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=STATUS_REQUEST)
def status_request(address: Address, status_type: int = 0, topic=pub.AUTO_TOPIC):
    """Create a STATUS_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=status_type, priority=7)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=GET_OPERATING_FLAGS)
def get_operating_flags(
    address: Address, flags_requested: int, extended: bool, topic=pub.AUTO_TOPIC
):
    """Create a GET_OPERATING_FLAGS command."""
    user_data = UserData() if extended else None
    _create_direct_message(
        topic=topic,
        address=address,
        cmd2=flags_requested,
        priority=7,
        user_data=user_data,
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_OPERATING_FLAGS)
def set_operating_flags(
    address: Address, cmd: int, extended=False, topic=pub.AUTO_TOPIC
):
    """Create a SET_OPERATING_FLAGS command."""
    user_data = UserData() if extended else None
    _create_direct_message(topic=topic, address=address, cmd2=cmd, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=INSTANT_CHANGE)
def instant_change(address: Address, on_level: int, topic=pub.AUTO_TOPIC):
    """Create a INSTANT_CHANGE command."""
    _create_direct_message(topic=topic, address=address, cmd2=on_level, priority=3)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_STATUS)
def set_status(address: Address, on_level: int, topic=pub.AUTO_TOPIC):
    """Create a SET_STATUS command."""
    _create_direct_message(topic=topic, address=address, cmd2=on_level)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_ADDRESS_MSB)
def set_address_msb(address: Address, high_byte: int, topic=pub.AUTO_TOPIC):
    """Create a SET_ADDRESS_MSB command."""
    _create_direct_message(topic=topic, address=address, cmd2=high_byte)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POKE_ONE_BYTE)
def poke_one_byte(address: Address, byte_to_write: int, topic=pub.AUTO_TOPIC):
    """Create a POKE_ONE_BYTE command."""
    _create_direct_message(topic=topic, address=address, cmd2=byte_to_write)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=PEEK_ONE_BYTE)
def peek_one_byte(address: Address, lsb: int, topic=pub.AUTO_TOPIC):
    """Create a PEEK_ONE_BYTE command."""
    _create_direct_message(topic=topic, address=address, cmd2=lsb)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=PEEK_ONE_BYTE_INTERNAL)
def peek_one_byte_internal(address: Address, lsb: int, topic=pub.AUTO_TOPIC):
    """Create a PEEK_ONE_BYTE_INTERNAL command."""
    _create_direct_message(topic=topic, address=address, cmd2=lsb)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POKE_ONE_BYTE_INTERNAL)
def poke_one_byte_internal(address: Address, byte_to_write: int, topic=pub.AUTO_TOPIC):
    """Create a POKE_ONE_BYTE_INTERNAL command."""
    _create_direct_message(topic=topic, address=address, cmd2=byte_to_write)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=ON_AT_RAMP_RATE)
def on_at_ramp_rate(
    address: Address, on_level: int, ramp_rate: RampRate, topic=pub.AUTO_TOPIC
):
    """Create a ON_AT_RAMP_RATE command."""
    on_level = max(0x10, on_level & 0xF0)
    ramp_rate = ceil(int(ramp_rate) / 2) + 1 & 0x0F
    cmd2 = on_level + ramp_rate
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, priority=3)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=EXTENDED_GET_SET)
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
        data[f"d{index}"] = items[f"data{index}"]
    user_data = UserData(data)
    _create_direct_message(topic=topic, address=address, user_data=user_data, crc=crc)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=EXTENDED_GET_SET_2)
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
        data[f"d{index}"] = items[f"data{index}"]
    user_data = UserData(data)
    _create_direct_message(topic=topic, address=address, user_data=user_data, crc=True)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=OFF_AT_RAMP_RATE)
def off_at_ramp_rate(address: Address, ramp_rate: RampRate, topic=pub.AUTO_TOPIC):
    """Create a OFF_AT_RAMP_RATE command."""
    ramp_rate = ceil(int(ramp_rate) / 2) + 1 & 0x0F
    cmd2 = ramp_rate
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
    flags = AllLinkRecordFlags.create(
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


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=EXTENDED_READ_WRITE_ALDB
)
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


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=EXTENDED_TRIGGER_ALL_LINK
)
def extended_trigger_all_link(
    address: Address, group: int, on_level: int, fast: bool, topic=pub.AUTO_TOPIC
):
    """Create a EXTENDED_TRIGGER_ALL_LINK command."""
    use_on_level = on_level not in [0x00, 0xFF]
    user_data = UserData(
        {
            "d1": group,
            "d2": 1 if use_on_level else 0,
            "d3": on_level if use_on_level else 0,
            "d4": 0x13 if on_level == 0 else 0x11,
            "d5": 0,
            "d6": 1 if fast else 0,
        }
    )
    _create_direct_message(topic=topic, address=address, cmd2=0, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=BEEP)
def beep(address: Address, topic=pub.AUTO_TOPIC):
    """Create a BEEP command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SET_SPRINKLER_PROGRAM)
def set_sprinkler_program(
    address: Address, program: int, timers: iter, topic=pub.AUTO_TOPIC
):
    """Create a SET_SPRINKLER_PROGRAM command."""
    user_data = UserData()
    curr_timer = 1
    for timer in timers:
        user_data[f"d{curr_timer}"] = timer
        curr_timer += 1
    _create_direct_message(
        topic=topic, address=address, cmd2=program, user_data=user_data
    )


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SPRINKLER_VALVE_ON)
def sprinkler_valve_on(address: Address, valve: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_VALVE_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=valve)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SPRINKLER_VALVE_OFF)
def sprinkler_valve_off(address: Address, valve: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_VALVE_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=valve)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SPRINKLER_PROGRAM_ON)
def sprinkler_program_on(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_PROGRAM_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SPRINKLER_PROGRAM_OFF)
def sprinkler_program_off(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_PROGRAM_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=SPRINKLER_CONTROL)
def sprinkler_control(
    address: Address, command: SprinklerControlCommand, topic=pub.AUTO_TOPIC
):
    """Create a SPRINKLER_CONTROL command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=SPRINKLER_GET_PROGRAM_REQUEST
)
def sprinkler_get_program_request(address: Address, program: int, topic=pub.AUTO_TOPIC):
    """Create a SPRINKLER_GET_PROGRAM_REQUEST command."""
    _create_direct_message(topic=topic, address=address, cmd2=program)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_OUTPUT_ON)
def io_output_on(address: Address, output: int, topic=pub.AUTO_TOPIC):
    """Create a IO_OUTPUT_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=output)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_OUTPUT_OFF)
def io_output_off(address: Address, output: int, topic=pub.AUTO_TOPIC):
    """Create a IO_OUTPUT_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=output)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_ALARM_DATA_REQUEST)
def io_alarm_data_request(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_ALARM_DATA_REQUEST command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_WRITE_OUTPUT_PORT)
def io_write_output_port(address: Address, value: int, topic=pub.AUTO_TOPIC):
    """Create a IO_WRITE_OUTPUT_PORT command."""
    _create_direct_message(topic=topic, address=address, cmd2=value)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_READ_INPUT_PORT)
def io_read_input_port(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_READ_INPUT_PORT command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_GET_SENSOR_VALUE)
def io_get_sensor_value(address: Address, sensor: int, topic=pub.AUTO_TOPIC):
    """Create a IO_GET_SENSOR_VALUE command."""
    _create_direct_message(topic=topic, address=address, cmd2=sensor)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=IO_SET_SENSOR_1_NOMINAL_VALUE
)
def io_set_sensor_1_nominal_value(address: Address, value: int, topic=pub.AUTO_TOPIC):
    """Create a IO_SET_SENSOR_1_NOMINAL_VALUE command."""
    _create_direct_message(topic=topic, address=address, cmd2=value)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=IO_SET_SENSOR_NOMINAL_VALUE
)
def io_set_sensor_nominal_value(
    address: Address, sensor: int, value: int, topic=pub.AUTO_TOPIC
):
    """Create a IO_SET_SENSOR_NOMINAL_VALUE command."""
    user_data = UserData({"d1": value})
    _create_direct_message(
        topic=topic, address=address, cmd2=sensor, user_data=user_data
    )


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=IO_GET_SENSOR_ALARM_DELTA
)
def io_get_sensor_alarm_delta(
    address: Address, sensor: int, delta: int, topic=pub.AUTO_TOPIC
):
    """Create a IO_GET_SENSOR_ALARM_DELTA command."""
    negative = delta < 0
    sensor = sensor & 0x0F
    delta = (abs(delta) << 4) & 0x70
    direction = 0x80 if negative else 0
    cmd2 = sensor + delta + direction
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=IO_WRITE_CONFIGURATION_PORT
)
def io_write_configuration_port(
    address: Address,
    port_flags: IOPortConfigFlags,
    topic=pub.AUTO_TOPIC,
):
    """Create a IO_WRITE_CONFIGURATION_PORT command."""
    cmd2 = int(port_flags)
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=IO_READ_CONFIGURATION_PORT
)
def io_read_configuration_port(address: Address, topic=pub.AUTO_TOPIC):
    """Create a IO_READ_CONFIGURATION_PORT command."""
    _create_direct_message(topic=topic, address=address)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=IO_MODULE_CONTROL)
def io_module_control(
    address: Address, command: IOModuleControlCommand, topic=pub.AUTO_TOPIC
):
    """Create a IO_MODULE_CONTROL command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POOL_DEVICE_ON)
def pool_device_on(address: Address, device_num: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_DEVICE_ON command."""
    _create_direct_message(topic=topic, address=address, cmd2=device_num)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=POOL_SET_DEVICE_TEMPERATURE
)
def pool_set_device_temperature(
    address: Address, device_num: int, degrees: int, topic=pub.AUTO_TOPIC
):
    """Create a POOL_SET_DEVICE_TEMPERATURE command."""
    user_data = UserData({"d1": device_num, "d2": degrees})
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POOL_DEVICE_OFF)
def pool_device_off(address: Address, device_num: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_DEVICE_OFF command."""
    _create_direct_message(topic=topic, address=address, cmd2=device_num)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=POOL_SET_DEVICE_HYSTERESIS
)
def pool_set_device_hysteresis(
    address: Address, device_num: int, hysteresis: int, topic=pub.AUTO_TOPIC
):
    """Create a POOL_SET_DEVICE_HYSTERESIS command."""
    user_data = UserData({"d1": device_num, "d2": hysteresis})
    _create_direct_message(topic=topic, address=address, user_data=user_data)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POOL_TEMPERATURE_UP)
def pool_temperature_up(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_TEMPERATURE_UP command."""
    cmd2 = degrees * 2
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POOL_TEMPERATURE_DOWN)
def pool_temperature_down(address: Address, degrees: int, topic=pub.AUTO_TOPIC):
    """Create a POOL_TEMPERATURE_DOWN command."""
    cmd2 = degrees * 2
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=POOL_CONTROL)
def pool_control(address: Address, command: PoolControlCommand, topic=pub.AUTO_TOPIC):
    """Create a POOL_CONTROL command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=DOOR_CONTROL)
def door_control(address: Address, command: DoorCommand, topic=pub.AUTO_TOPIC):
    """Create a DOOR_CONTROL command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=DOOR_STATUS_REPORT)
def door_status_report(address: Address, command: DoorCommand, topic=pub.AUTO_TOPIC):
    """Create a DOOR_STATUS_REPORT command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=WINDOW_COVERING_CONTROL)
def window_covering_command(
    address: Address, command: WindowCoveringCommand, topic=pub.AUTO_TOPIC
):
    """Create a WINDOW_COVERING_CONTROL command."""
    _create_direct_message(topic=topic, address=address, cmd2=int(command))


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=WINDOW_COVERING_POSITION
)
def window_covering_position(address: Address, position: int, topic=pub.AUTO_TOPIC):
    """Create a WINDOW_COVERING_POSITION command."""
    _create_direct_message(topic=topic, address=address, cmd2=position)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=THERMOSTAT_TEMPERATURE_UP
)
def thermostat_temperature_up(
    address: Address, degrees: int, zone: int, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_TEMPERATURE_UP command."""
    degrees_value = int(round(degrees * 2, 0))
    if not zone:
        cmd2 = degrees_value
        user_data = UserData()
    else:
        cmd2 = zone
        user_data = UserData({"d1": degrees_value})
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=THERMOSTAT_TEMPERATURE_DOWN
)
def thermostat_temperature_down(
    address: Address, degrees: int, zone: int, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_TEMPERATURE_DOWN command."""
    degrees_value = int(round(degrees * 2, 0))
    if not zone:
        cmd2 = degrees_value
        user_data = UserData()
    else:
        cmd2 = zone
        user_data = UserData({"d1": degrees_value})
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=THERMOSTAT_GET_ZONE_INFORMATION
)
def thermostat_get_zone_information(
    address: Address, zone: int, info: ThermostatZoneInfo, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_GET_ZONE_INFORMATION command.

    zone: (int) 0 to 31

    info: (int)
        0 = Temperature
        1 = Setpoint
        2 = Deadband
        3 = Humidity
    """
    zone = zone & 0x1F
    info_bits = (info << 5) & 0x60
    cmd2 = info_bits + zone
    _create_direct_message(topic=topic, address=address, cmd2=cmd2)


@topic_to_command_handler(register_list=COMMAND_REGISTER, topic=THERMOSTAT_CONTROL)
def thermostat_control(
    address: Address, thermostat_mode: ThermostatCommand, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_CONTROL command."""
    user_data = UserData()
    _create_direct_message(
        topic=topic, address=address, cmd2=int(thermostat_mode), user_data=user_data
    )


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=THERMOSTAT_SET_COOL_SETPOINT
)
def thermostat_set_cool_setpoint(
    address: Address, degrees: int, zone: int, deadband: int, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_SET_COOL_SETPOINT command."""
    if not zone:
        cmd2 = int(degrees * 2)
        user_data = UserData()
    else:
        cmd2 = zone
        user_data = UserData({"d1": degrees * 2, "d2": deadband * 2})
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)


@topic_to_command_handler(
    register_list=COMMAND_REGISTER, topic=THERMOSTAT_SET_HEAT_SETPOINT
)
def thermostat_set_heat_setpoint(
    address: Address, degrees: int, zone: int, deadband: int, topic=pub.AUTO_TOPIC
):
    """Create a THERMOSTAT_SET_HEAT_SETPOINT command."""
    if not zone:
        cmd2 = int(degrees * 2)
        user_data = UserData()
    else:
        cmd2 = zone
        user_data = UserData({"d1": degrees * 2, "d2": deadband * 2})
    _create_direct_message(topic=topic, address=address, cmd2=cmd2, user_data=user_data)
