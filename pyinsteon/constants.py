"""INSTEON PLM constants for reuse across the module."""

from enum import Enum, IntEnum


class HexIntEnum(IntEnum):
    """IntEnum represented as a hex string or lowercase name."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return f"0x{self.value:02x}"

    def __str__(self):
        """Emit the string of the Enum."""
        # pylint: disable=no-member
        return self.name.lower()


class DeviceCategory(HexIntEnum):
    """Device categories."""

    GENERALIZED_CONTROLLERS = 0x00
    DIMMABLE_LIGHTING_CONTROL = 0x01
    SWITCHED_LIGHTING_CONTROL = 0x02
    NETWORK_BRIDGES = 0x03
    IRRIGATION_CONTROL = 0x04
    CLIMATE_CONTROL = 0x05
    POOL_AND_SPA_CONTROL = 0x06
    SENSORS_AND_ACTUATORS = 0x07
    HOME_ENTERTAINMENT = 0x08
    ENERGY_MANAGEMENT = 0x09
    BUILT_IN_APPLIANCE_CONTROL = 0x0A
    PLUMBING = 0x0B
    COMMUNICATION = 0x0C
    COMPUTER_CONTROL = 0x0D
    WINDOW_COVERINGS = 0x0E
    ACCESS_CONTROL = 0x0F
    SECURITY_HEALTH_SAFETY = 0x10
    SURVEILLANCE = 0x11
    AUTOMOTIVE = 0x12
    PET_CARE = 0x13
    TIMEKEEPING = 0x15
    HOLIDAY = 0x16
    UNKNOWN = 0xFF


class MessageId(HexIntEnum):
    """Message type definitions."""

    STANDARD_RECEIVED = 0x50
    EXTENDED_RECEIVED = 0x51
    X10_RECEIVED = 0x52
    ALL_LINKING_COMPLETED = 0x53
    BUTTON_EVENT_REPORT = 0x54
    USER_RESET_DETECTED = 0x55
    ALL_LINK_CLEANUP_FAILURE_REPORT = 0x56
    ALL_LINK_RECORD_RESPONSE = 0x57
    ALL_LINK_CLEANUP_STATUS_REPORT = 0x58
    READ_EEPROM_RESPONSE = 0x59
    GET_IM_INFO = 0x60
    SEND_ALL_LINK_COMMAND = 0x61
    SEND_STANDARD = 0x62
    SEND_EXTENDED = 0x62
    X10_SEND = 0x63
    START_ALL_LINKING = 0x64
    CANCEL_ALL_LINKING = 0x65
    SET_HOST_DEVICE_CATEGORY = 0x66
    RESET_IM = 0x67
    SET_ACK_MESSAGE_BYTE = 0x68
    GET_FIRST_ALL_LINK_RECORD = 0x69
    GET_NEXT_ALL_LINK_RECORD = 0x6A
    SET_IM_CONFIGURATION = 0x6B
    GET_ALL_LINK_RECORD_FOR_SENDER = 0x6C
    LED_ON = 0x6D
    LED_OFF = 0x6E
    MANAGE_ALL_LINK_RECORD = 0x6F
    SET_NAK_MESSAGE_BYTE = 0x70
    SET_ACK_MESSAGE_TWO_BYTES = 0x71
    RF_SLEEP = 0x72
    GET_IM_CONFIGURATION = 0x73
    CANCEL_CLEANUP = 0x74
    READ_EEPROM = 0x75
    WRITE_EEPROM = 0x76
    BEEP = 0x77
    UNKNOWN = 0x99  # Only used to test for bad message types


class MessageFlagType(HexIntEnum):
    """Message flag mesage type."""

    DIRECT = 0
    DIRECT_ACK = 1
    ALL_LINK_CLEANUP = 2
    ALL_LINK_CLEANUP_ACK = 3
    BROADCAST = 4
    DIRECT_NAK = 5
    ALL_LINK_BROADCAST = 6
    ALL_LINK_CLEANUP_NAK = 7


class AckNak(HexIntEnum):
    """ACK/NAK values."""

    ACK = 0x06
    NAK = 0x15


class ALDBStatus(HexIntEnum):
    """All-Link Database load status."""

    EMPTY = 0
    LOADED = 1
    LOADING = 2
    FAILED = 3
    PARTIAL = 4
    DIRTY = 5


class ReadWriteMode(HexIntEnum):
    """Modem read mode."""

    UNKNOWN = 0x00
    STANDARD = 0x01
    EEPROM = 0x02
    PEEK_POKE = 0x03


class EngineVersion(HexIntEnum):
    """Insteon Engine Version.

    - Unknown is used when the Insteon Engine Version has not be successfully queried
    - Other is used when the Insteon Engine Version query comes back with a number different than expected
    """

    I1 = 0x00
    I2 = 0x01
    I2CS = 0x02
    OTHER = 0xFE
    UNKNOWN = 0xFF


class X10CommandType(HexIntEnum):
    """X10 command types."""

    UNITCODE = 0x00
    COMMAND = 0x80


class PropertyType(HexIntEnum):
    """Describes the device property class type."""

    STANDARD = 0x00
    ADVANCED = 0x01
    DERIVED = 0x02


class ThermostatMode(HexIntEnum):
    """Thermostat system modes."""

    OFF = 0x00
    HEAT = 0x01
    COOL = 0x02
    AUTO = 0x03
    FAN_AUTO = 0x04
    FAN_ALWAYS_ON = 0x8


class FanSpeed(HexIntEnum):
    """Fan speeds."""

    OFF = 0x00
    LOW = 0x40
    MEDIUM = 0xC0
    HIGH = 0xFF


class FanSpeedRange(Enum):
    """Fan speed ranges."""

    OFF = [0x00]
    LOW = range(0x01, 0x7F)
    MEDIUM = range(0x80, 0xFE)
    HIGH = [0xFF]


class RelayMode(HexIntEnum):
    """Relay mode used by Sensor Actuator device class 0x07."""

    LATCHING = 0
    MOMENTARY_A = 1
    MOMENTARY_B = 2
    MOMENTARY_C = 3


class ToggleMode(HexIntEnum):
    """Toggle mode used by KeypadLinc device class 0x01 and 0x02."""

    TOGGLE = 0
    ON_ONLY = 1
    OFF_ONLY = 2


class X10Commands(HexIntEnum):
    """X10 Commands."""

    ALL_UNITS_OFF = 0x00
    ALL_LIGHTS_ON = 0x01
    ALL_LIGHTS_OFF = 0x06
    ON = 0x02
    OFF = 0x03
    DIM = 0x04
    BRIGHT = 0x05
    EXTENDED_CODE = 0x07
    HAIL_REQUEST = 0x08
    HAIL_ACKNOWLEDGE = 0x09
    PRE_SET_DIM = 0x0A
    STATUS_IS_ON = 0x0B
    STATUS_IS_OFF = 0x0C
    STATUS_REQUEST = 0x0D


class ImButtonEvents(HexIntEnum):
    """IM Button Events values."""

    SET_TAPPED = 0x02
    SET_HELD = 0x03
    SET_RELEASED_AFTER_HOLD = 0x04
    SET_2_TAPPED = 0x12
    SET_2_HELD = 0x13
    SET_2_RELEASED_AFTER_HOLD = 0x14
    SET_3_TAPPED = 0x22
    SET_3_HELD = 0x23
    SET_3_RELEASED_AFTER_HOLD = 0x24


class AllLinkMode(HexIntEnum):
    """All Link Mode values."""

    RESPONDER = 0x00
    CONTROLLER = 0x01
    EITHER = 0x03
    DELETE = 0xFF


class ManageAllLinkRecordAction(HexIntEnum):
    """Manage All Link Record Action values."""

    FIND_FIRST = 0x00
    FIND_NEXT = 0x01
    MOD_FIRST_OR_ADD = 0x20
    MOD_FIRST_CTRL_OR_ADD = 0x40
    MOD_FIRST_RESP_OR_ADD = 0x41
    DELETE_FIRST = 0x80


class RampRate(IntEnum):
    """Ramp rate values."""

    MIN_9 = 0x00
    MIN_8 = 0x01
    MIN_7 = 0x02
    MIN_6 = 0x03
    MIN_5 = 0x04
    MIN_4_5 = 0x05
    MIN_4 = 0x06
    MIN_3_5 = 0x07
    MIN_3 = 0x08
    MIN_2_5 = 0x09
    MIN_2 = 0x0A
    MIN_1_5 = 0x0B
    MIN_1 = 0x0C
    SEC_47 = 0x0D
    SEC_43 = 0x0E
    SEC_38_5 = 0x0F
    SEC_34 = 0x10
    SEC_32 = 0x11
    SEC_30 = 0x12
    SEC_28 = 0x13
    SEC_26 = 0x14
    SEC_23_5 = 0x15
    SEC_21_5 = 0x16
    SEC_19 = 0x17
    SEC_8_5 = 0x18
    SEC_6_5 = 0x19
    SEC_4_5 = 0x1A
    SEC_2 = 0x1B
    SEC_0_5 = 0x1C
    SEC_0_3 = 0x1D
    SEC_0_2 = 0x1E
    SEC_0_1 = 0x1F


class ResponseStatus(HexIntEnum):
    """Response status of an outbound message."""

    FAILURE = 0
    SUCCESS = 1
    DEVICE_UNRESPONSIVE = 3
    UNSENT = 4
    RUN_ON_WAKE = 5
    DIRECT_NAK_ALDB = 0xFF
    DIRECT_NAK_NO_LOAD = 0xFE
    DIRECT_NAK_CHECK_SUM = 0xFD
    DIRECT_NAK_PRE_NAK = 0xFC
    DIRECT_NAK_INVALID_COMMAND = 0xFB


class LinkStatus(Enum):
    """Status of a link between two devices."""

    MISSING_CONTROLLER = 0
    MISSING_RESPONDER = 1
    MISSING_TARGET = 2
    FOUND = 3
    TARGET_DB_NOT_LOADED = 4


MESSAGE_START_CODE = 0x02
MESSAGE_ACK = 0x06
MESSAGE_NAK = 0x15

CONTROL_FLAG_RECORD_IN_USE_0X80 = 0x80
CONTROL_FLAG_CONTROLER_0X40 = 0x40
CONTROL_FLAG_RECORD_HAS_BEEN_USED_0X02 = 0x02

# X10 House code lookup
HC_LOOKUP = {
    "a": 0x06,
    "b": 0x0E,
    "c": 0x02,
    "d": 0x0A,
    "e": 0x01,
    "f": 0x09,
    "g": 0x05,
    "h": 0x0D,
    "i": 0x07,
    "j": 0x0F,
    "k": 0x03,
    "l": 0x0B,
    "m": 0x00,
    "n": 0x08,
    "o": 0x04,
    "p": 0x0C,
}

# X10 Unit code lookup
UC_LOOKUP = {
    1: 0x06,
    2: 0x0E,
    3: 0x02,
    4: 0x0A,
    5: 0x01,
    6: 0x09,
    7: 0x05,
    8: 0x0D,
    9: 0x07,
    10: 0x0F,
    11: 0x03,
    12: 0x0B,
    13: 0x00,
    14: 0x08,
    15: 0x04,
    16: 0x0C,
}

RAMP_RATES = {
    0x00: 2,
    0x01: 480,
    0x02: 420,
    0x03: 360,
    0x04: 300,
    0x05: 270,
    0x06: 240,
    0x07: 210,
    0x08: 180,
    0x09: 150,
    0x0A: 120,
    0x0B: 90,
    0x0C: 60,
    0x0D: 47,
    0x0E: 43,
    0x0F: 38.5,
    0x10: 34,
    0x11: 32,
    0x12: 30,
    0x13: 28,
    0x14: 26,
    0x15: 23.5,
    0x16: 21.5,
    0x17: 19,
    0x18: 8.5,
    0x19: 6.5,
    0x1A: 4.5,
    0x1B: 2,
    0x1C: 0.5,
    0x1D: 0.3,
    0x1E: 0.2,
    0x1F: 0.1,
}


RAMP_RATES_SEC = {
    480: 0x01,
    420: 0x02,
    360: 0x03,
    300: 0x04,
    270: 0x05,
    240: 0x06,
    210: 0x07,
    180: 0x08,
    150: 0x09,
    120: 0x0A,
    90: 0x0B,
    60: 0x0C,
    47: 0x0D,
    43: 0x0E,
    38.5: 0x0F,
    34: 0x10,
    32: 0x11,
    30: 0x12,
    28: 0x13,
    26: 0x14,
    23.5: 0x15,
    21.5: 0x16,
    19: 0x17,
    8.5: 0x18,
    6.5: 0x19,
    4.5: 0x1A,
    2: 0x1B,
    0.5: 0x1C,
    0.3: 0x1D,
    0.2: 0x1E,
    0.1: 0x1F,
}


class DeviceAction(IntEnum):
    """Device list actions."""

    ADDED = 0
    REMOVED = 1
    COMPLETED = 2


class SprinklerControlCommand(HexIntEnum):
    """Sprinkler control options."""

    LOAD_INITIALIZATION_VALUES = 0x00
    LOAD_EEPROM_FROM_RAM = 0x01
    GET_VALVE_STATUS = 0x02
    INHIBIT_COMMAND_ACCEPTANCE = 0x03
    RESUME_COMMAND_ACCEPTANCE = 0x04
    SKIP_FORWARD = 0x05
    SKIP_BACK = 0x06
    ENABLE_PUMP_ON_V8 = 0x07
    DISABLE_PUMP_ON_V8 = 0x08
    BROADCAST_ON = 0x09
    BROADCAST_OFF = 0x0A
    LOAD_RAM_FROM_EEPROM = 0x0B
    SENSOR_ON = 0x0C
    SENSOR_OFF = 0x0D
    DIAGNOSTICS_ON = 0x0E
    DIAGNOSTICS_OFF = 0x0F


class IOModuleControlCommand(HexIntEnum):
    """IO Module control options."""

    LOAD_INITIALIZATION_VALUES = 0x00
    LOAD_EEPROM_FROM_RAM = 0x01
    STATUS_REQUEST = 0x02
    READ_ANALOG_ONCE = 0x03
    READ_ANALOG_ALWAYS = 0x04
    ENABLE_STATUS_CHANGE_MESSAGE = 0x09
    DISABLE_STATUS_CHANGE_MESSAGE = 0x0A
    LOAD_RAM_FROM_EEPROM = 0x0B
    SENSOR_ON = 0x0C
    SENSOR_OFF = 0x0D
    DIAGNOSTICS_ON = 0x0E
    DIAGNOSTICS_OFF = 0x0F


class PoolControlCommand(HexIntEnum):
    """Pool Module control options."""

    LOAD_INITIALIZATION_VALUES = 0x00
    LOAD_EEPROM_FROM_RAM = 0x01
    GET_MODE = 0x02
    GET_AMBIENT_TEMPERATURE = 0x03
    GET_WATER_TEMPERATURE = 0x04
    GET_PH = 0x05


class DoorCommand(HexIntEnum):
    """Door Module command options."""

    RAISE_DOOR = 0x00
    LOWER_DOOR = 0x01
    OPEN_DOOR = 0x02
    CLOSE_DOOR = 0x03
    STOP_DOOR = 0x04
    SINGLE_DOOR_OPEN = 0x05
    SINGLE_DOOR_CLOSE = 0x06


class WindowCoveringCommand(HexIntEnum):
    """Window Covering command options."""

    OPEN = 0x01
    CLOSE = 0x02
    STOP = 0x03
    PROGRAM = 0x04


class ThermostatCommand(HexIntEnum):
    """Thermostat command options."""

    LOAD_INITIALIZATION_VALUES = 0x00
    LOAD_EEPROM_FROM_RAM = 0x01
    GET_THERMOSTAT_MODE = 0x02
    GET_AMBIENT_TEMPERATURE = 0x03
    ON_HEAT = 0x04
    ON_COOL = 0x05
    ON_AUTO = 0x06
    ON_FAN = 0x07
    OFF_FAN = 0x08
    OFF_ALL = 0x09
    PROGRAM_HEAT = 0x0A
    PROGRAM_COOL = 0x0B
    PROGRAM_AUTO = 0x0C
    GET_EQUIPMENT_STATE = 0x0D
    SET_EQUIPMENT_STATE = 0x0E
    GET_TEMPERATURE_UNITS = 0x0F
    SET_FAHRENHEIT = 0x10
    SET_CELSIUS = 0x11
    GET_FAN_ON_SPEED = 0x12
    SET_FAN_ON_SPEED_LOW = 0x13
    SET_FAN_ON_SPEED_MEDIUM = 0x14
    SET_FAN_ON_SPEED_HIGH = 0x15
    ENABLE_STATUS_CHANGE_MESSAGE = 0x16
    DISABLE_STATUS_CHANGE_MESSAGE = 0x17


class ThermostatZoneInfo(HexIntEnum):
    """Thermostat zone information options."""

    TEMPERATURE = 0x00
    SETPOINT = 0x01
    DEADBAND = 0x10
    HUMIDITY = 0x11
