"""Collection of topics mapped to commands (cmd1, cmd2)."""
import logging
from collections import namedtuple
from typing import Tuple

from .topics import (
    ALL_LINK_CLEANUP_STATUS_REPORT,
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
    EXTENDED_GET_RESPONSE,
    EXTENDED_GET_SET,
    EXTENDED_GET_SET_2,
    EXTENDED_READ_WRITE_ALDB,
    EXTENDED_READ_WRITE_ALDB_DIRECT_NAK,
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
    IO_MODULE_CONTROL,
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
    POOL_CONTROL,
    POOL_DEVICE_OFF,
    POOL_DEVICE_ON,
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
    SPRINKLER_CONTROL,
    SPRINKLER_GET_PROGRAM_REQUEST,
    SPRINKLER_GET_PROGRAM_RESPONSE,
    SPRINKLER_PROGRAM_OFF,
    SPRINKLER_PROGRAM_ON,
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
    THERMOSTAT_STATUS_RESPONSE,
    THERMOSTAT_TEMPERATURE_DOWN,
    THERMOSTAT_TEMPERATURE_STATUS,
    THERMOSTAT_TEMPERATURE_UP,
    WINDOW_COVERING_CONTROL,
    WINDOW_COVERING_POSITION,
)

Command = namedtuple("Command", "cmd1 cmd2 ud_allowed ud_required userdata")
_LOGGER = logging.getLogger(__name__)


def _check_userdata_match(command: Command, userdata: dict):
    """Check if the command userdata matches the input userdata."""
    if command.ud_allowed and not command.ud_required:
        return True

    if not userdata and not command.ud_required:
        return True

    if userdata and not command.ud_allowed:
        return False

    if command.ud_required and not userdata:
        return False

    for field, value in command.userdata.items():
        if value != userdata.get(field):
            return False
    return True


def _check_match(command, cmd1, cmd2, userdata):
    """Check if the current command matches the input values."""
    if command.cmd1 != cmd1:
        return False
    cmd2_match = cmd2 is None or command.cmd2 is None or command.cmd2 == cmd2
    userdata_match = _check_userdata_match(command, userdata)
    return cmd2_match and userdata_match


class Commands:
    """List of topics and commands."""

    def __init__(self):
        """Init the Commands class."""
        self._topics = {}
        self._commands = {}
        self._use_group = {}
        self._commands_topic_map = {}

    def add(
        self,
        topic: str,
        cmd1: int,
        cmd2: int = None,
        ud_allowed: bool = False,
        ud_required: bool = False,
        userdata: dict = None,
        use_group: bool = False,
    ):
        """Add a command to the list.

        Inputs:
          topic: string
          cmd1: hex byte value of the command
          cmd2: (Optional) hex byte of a specific cmd2 value
          ud_allowed: (Optional, default False)
            - If True, the message is allowed to have user data
            - If False, the messager cannot have user data
          ud_required: (Optional, default False)  Is user data required
            - NOTE: A DIRECT ACK command does not reply with userdata therefore most commands do not require userdata
          userdata: (Optional)  Dictionary of required values in userdata
            - Example: {"d1": 0x00}  Data 1 must be 0x00
        """
        if userdata is not None:
            ud_allowed = True
        if ud_required and userdata is None:
            userdata = {}
        self._topics[topic] = Command(cmd1, cmd2, ud_allowed, ud_required, userdata)
        self._use_group[topic] = use_group
        if self._commands_topic_map.get(cmd1) is None:
            self._commands_topic_map[cmd1] = []
        self._commands_topic_map[cmd1].append(topic)

    def get(self, topic: str) -> Command:
        """Get the command elements of the topic."""
        return self._topics.get(topic)

    def get_command(self, topic: str) -> Tuple[int, int, bool]:
        """Get cmd1 and cmd2 from a topic.

        Returns (cmd1, cmd2, extended)
        """
        return self._topics.get(topic)

    def _get_topics_from_cmd1(self, cmd1):
        """Get a list of topics from a cmd1 value."""
        return self._commands_topic_map.get(cmd1)

    def use_group(self, topic):
        """Return if a topic requires a group number."""
        return self._use_group.get(topic)

    def get_topics(self, cmd1, cmd2, userdata=None, send=False) -> str:
        """Generate a topic from a cmd1, cmd2 and extended flag."""
        found = False
        for topic in self._commands_topic_map.get(cmd1, {}):
            command = self._topics[topic]
            if _check_match(command, cmd1, cmd2, userdata):
                found = True
                yield topic
        if not found:
            if userdata is None:
                yield SEND_STANDARD if send else STANDARD_RECEIVED
            else:
                yield SEND_EXTENDED if send else EXTENDED_RECEIVED


commands = Commands()

commands.add(
    topic=STANDARD_RECEIVED,
    cmd1=-1,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=EXTENDED_RECEIVED,
    cmd1=-1,
    cmd2=None,
    ud_allowed=True,
    ud_required=True,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SEND_STANDARD,
    cmd1=-2,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SEND_EXTENDED,
    cmd1=-2,
    cmd2=None,
    ud_allowed=True,
    ud_required=True,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ASSIGN_TO_ALL_LINK_GROUP,
    cmd1=0x01,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=DELETE_FROM_ALL_LINK_GROUP,
    cmd1=0x02,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=PRODUCT_DATA_REQUEST,
    cmd1=0x03,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=FX_USERNAME,
    cmd1=0x03,
    cmd2=0x01,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=DEVICE_TEXT_STRING_REQUEST,
    cmd1=0x03,
    cmd2=0x02,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_DEVICE_TEXT_STRING,
    cmd1=0x03,
    cmd2=0x03,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_ALL_LINK_COMMAND_ALIAS,
    cmd1=0x03,
    cmd2=0x04,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_ALL_LINK,
    cmd1=0x03,
    cmd2=0x05,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ALL_LINK_CLEANUP_STATUS_REPORT,
    cmd1=0x06,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ENTER_LINKING_MODE,
    cmd1=0x09,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ENTER_UNLINKING_MODE,
    cmd1=0x0A,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=GET_INSTEON_ENGINE_VERSION,
    cmd1=0x0D,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=PING,
    cmd1=0x0F,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ID_REQUEST,
    cmd1=0x10,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ON,
    cmd1=0x11,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=ON_FAST,
    cmd1=0x12,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=OFF,
    cmd1=0x13,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=OFF_FAST,
    cmd1=0x14,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=BRIGHTEN_ONE_STEP,
    cmd1=0x15,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=DIM_ONE_STEP,
    cmd1=0x16,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=START_MANUAL_CHANGE_DOWN,
    cmd1=0x17,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=START_MANUAL_CHANGE_UP,
    cmd1=0x17,
    cmd2=0x01,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=STOP_MANUAL_CHANGE,
    cmd1=0x18,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=STATUS_REQUEST,
    cmd1=0x19,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=GET_OPERATING_FLAGS,
    cmd1=0x1F,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_OPERATING_FLAGS,
    cmd1=0x20,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=INSTANT_CHANGE,
    cmd1=0x21,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=MANUALLY_TURNED_OFF,
    cmd1=0x22,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=MANUALLY_TURNED_ON,
    cmd1=0x23,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=True,
)
commands.add(
    topic=REMOTE_SET_BUTTON_TAP1_TAP,
    cmd1=0x25,
    cmd2=0x01,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=REMOTE_SET_BUTTON_TAP2_TAP,
    cmd1=0x25,
    cmd2=0x02,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_STATUS,
    cmd1=0x27,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_ADDRESS_MSB,
    cmd1=0x28,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POKE_ONE_BYTE,
    cmd1=0x29,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=PEEK_ONE_BYTE,
    cmd1=0x2B,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=PEEK_ONE_BYTE_INTERNAL,
    cmd1=0x2C,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POKE_ONE_BYTE_INTERNAL,
    cmd1=0x2D,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=ON_AT_RAMP_RATE,
    cmd1=0x2E,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=EXTENDED_GET_SET,
    cmd1=0x2E,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=EXTENDED_GET_RESPONSE,
    cmd1=0x2E,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=True,
    userdata={"d2": 0x01},
    use_group=False,
)
# This is not consistant with the 2441TH dev guide
# It is consistand with 2441ZTH dev guide howerver
commands.add(
    topic=THERMOSTAT_SET_POINT_RESPONSE,
    cmd1=0x2E,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=True,
    userdata={"d2": 0x01, "d3": 0x01},
    use_group=False,
)
commands.add(
    topic=EXTENDED_GET_SET_2,
    cmd1=0x2E,
    cmd2=0x02,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_STATUS_RESPONSE,
    cmd1=0x2E,
    cmd2=0x02,
    ud_allowed=True,
    ud_required=True,
    userdata={"d1": 0x01},
    use_group=False,
)
# cmd2 ne 0x00 => no confict w/ read aldb
commands.add(
    topic=OFF_AT_RAMP_RATE,
    cmd1=0x2F,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
# direct is ed and direct_ack is sd
commands.add(
    topic=EXTENDED_READ_WRITE_ALDB,
    cmd1=0x2F,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
# Conflicts with OFF_AT_RAMP_RATE but only used when an ALDB read ack has already been received
commands.add(
    topic=EXTENDED_READ_WRITE_ALDB_DIRECT_NAK,
    cmd1=0x2F,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=EXTENDED_TRIGGER_ALL_LINK,
    cmd1=0x30,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=BEEP,
    cmd1=0x30,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SET_SPRINKLER_PROGRAM,
    cmd1=0x40,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_VALVE_ON,
    cmd1=0x40,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_GET_PROGRAM_RESPONSE,
    cmd1=0x41,
    cmd2=None,
    ud_allowed=True,
    ud_required=True,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_VALVE_OFF,
    cmd1=0x41,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_PROGRAM_ON,
    cmd1=0x42,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_PROGRAM_OFF,
    cmd1=0x43,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_CONTROL,
    cmd1=0x44,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=SPRINKLER_GET_PROGRAM_REQUEST,
    cmd1=0x45,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_OUTPUT_ON,
    cmd1=0x45,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_OUTPUT_OFF,
    cmd1=0x46,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_ALARM_DATA_REQUEST,
    cmd1=0x47,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_WRITE_OUTPUT_PORT,
    cmd1=0x48,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_READ_INPUT_PORT,
    cmd1=0x49,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_GET_SENSOR_VALUE,
    cmd1=0x4A,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_SET_SENSOR_1_NOMINAL_VALUE,
    cmd1=0x4B,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_SET_SENSOR_NOMINAL_VALUE,
    cmd1=0x4B,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_GET_SENSOR_ALARM_DELTA,
    cmd1=0x4C,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_ALARM_DATA_RESPONSE,
    cmd1=0x4C,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=True,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_WRITE_CONFIGURATION_PORT,
    cmd1=0x4D,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_READ_CONFIGURATION_PORT,
    cmd1=0x4E,
    cmd2=0x00,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=IO_MODULE_CONTROL,
    cmd1=0x4F,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_DEVICE_ON,
    cmd1=0x50,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_SET_DEVICE_TEMPERATURE,
    cmd1=0x50,
    cmd2=0x00,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_SET_DEVICE_HYSTERESIS,
    cmd1=0x50,
    cmd2=0x01,
    ud_allowed=True,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_DEVICE_OFF,
    cmd1=0x51,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_TEMPERATURE_UP,
    cmd1=0x52,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_TEMPERATURE_DOWN,
    cmd1=0x53,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=POOL_CONTROL,
    cmd1=0x54,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=DOOR_CONTROL,
    cmd1=0x58,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=DOOR_STATUS_REPORT,
    cmd1=0x59,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=WINDOW_COVERING_CONTROL,
    cmd1=0x60,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=WINDOW_COVERING_POSITION,
    cmd1=0x61,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_TEMPERATURE_UP,
    cmd1=0x68,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=True,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_TEMPERATURE_DOWN,
    cmd1=0x69,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=True,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_GET_ZONE_INFORMATION,
    cmd1=0x6A,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_CONTROL,
    cmd1=0x6B,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=True,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_SET_COOL_SETPOINT,
    cmd1=0x6C,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=True,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_SET_HEAT_SETPOINT,
    cmd1=0x6D,
    cmd2=None,
    ud_allowed=True,
    ud_required=False,
    userdata=True,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_TEMPERATURE_STATUS,
    cmd1=0x6E,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_HUMIDITY_STATUS,
    cmd1=0x6F,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=LEAK_DETECTOR_ANNOUNCE,
    cmd1=0x70,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_MODE_STATUS,
    cmd1=0x70,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_COOL_SET_POINT_STATUS,
    cmd1=0x71,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
commands.add(
    topic=THERMOSTAT_HEAT_SET_POINT_STATUS,
    cmd1=0x72,
    cmd2=None,
    ud_allowed=False,
    ud_required=False,
    userdata=None,
    use_group=False,
)
