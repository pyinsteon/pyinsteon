"""INSTEON PLM constants for reuse across the module."""

from enum import IntEnum


class DeviceCategory(IntEnum):
    """Device categories."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    GENERALIZED_CONTROLLERS = 0x00
    DIMMABLE_LIGHTING_CONTROL = 0x01
    SWITCHED_LIGHTING_CONTROL = 0x02
    NETWORK_BRIDGES = 0x03
    IRRIGATION_CONTROL = 0x04
    CLIMATE_CONTROL = 0x05
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


class MessageId(IntEnum):
    """Message type definitions."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    STANDARD_RECEIVED = 0x50
    EXTENDED_RECEIVED = 0x51
    X10_RECEIVED = 0x52
    ALL_LINKING_COMPLETED = 0x53
    BUTTON_EVENT_REPORT = 0x54
    USER_RESET_DETECTED = 0x55
    ALL_LINK_CLEANUP_FAILURE_REPORT = 0x56
    ALL_LINK_RECORD_RESPONSE = 0x57
    ALL_LINK_CLEANUP_STATUS_REPORT = 0x58
    GET_IM_INFO = 0x60
    SEND_ALL_LINK_COMMAND = 0x61
    SEND_STANDARD = 0x62
    SEND_EXTENDED = 0x62
    X10_SEND = 0x63
    START_ALL_LINKING = 0x64
    CANCEL_ALL_LINKING = 0x65
    SET_HOST_DEV_CAT = 0x66
    RESET_IM = 0x67
    SET_ACK_MESSAGE_BYTE = 0x68
    GET_FIRST_ALL_LINK_RECORD = 0x69
    GET_NEXT_ALL_LINK_RECORD = 0x6a
    SET_IM_CONFIGURATION = 0x6b
    GET_ALL_LINK_RECORD_FOR_SENDER = 0x6c
    LED_ON = 0x6d
    LED_OFF = 0x6e
    MANAGE_ALL_LINK_RECORD = 0x6f
    SET_NAK_MESSAGE_BYTE = 0x70
    SET_ACK_MESSAGE_TWO_BYTES = 0x71
    RF_SLEEP = 0x72
    GET_IM_CONFIGURATION = 0x73


class MessageFlagType(IntEnum):
    """Message flag mesage type."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    DIRECT = 0
    DIRECT_ACK = 1
    ALL_LINK_CLEANUP = 2
    ALL_LINK_CLEANUP_ACK = 3
    BROADCAST = 4
    DIRECT_NAK = 5
    ALL_LINK_BROADCAST = 6
    ALL_LINK_CLEANUP_NAK = 7


class AckNak(IntEnum):
    """ACK/NAK values."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    ACK = 0x06
    NAK = 0x15


class X10CommandType(IntEnum):
    """X10 command types."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    DIRECT = 0
    BROADCAST = 1


class ThermostatMode(IntEnum):
    """Thermostat system modes."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    OFF = 0x00
    HEAT = 0x01
    COOL = 0x02
    AUTO = 0x03
    FAN_AUTO = 0x04
    FAN_ALWAYS_ON = 0x8


class FanSpeed(IntEnum):
    """Fan speeds."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    OFF = 0x00
    LOW = 0x3f
    MEDIUM = 0xbe
    HIGH = 0xff


class RelayMode(IntEnum):
    """Relay mode used by Sensor Actuator device class 0x07."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    UNKNOWN = 0
    LATCHING = 1
    MOMENTARY_A = 2
    MOMENTARY_B = 3
    MOMENTARY_C = 4


class X10Commands(IntEnum):
    """X10 Commands."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

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


class ImButtonEvents(IntEnum):
    """IM Button Events values."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    SET_TAPPED = 0x02
    SET_HELD = 0x03
    SET_RELEASED_AFTER_HOLD = 0x04
    SET_2_TAPPED = 0x12
    SET_2_HELD = 0x13
    SET_2_RELEASED_AFTER_HOLD = 0x14
    SET_3_TAPPED = 0x22
    SET_3_HELD = 0x23
    SET_3_RELEASED_AFTER_HOLD = 0x24


class AllLinkMode(IntEnum):
    """All Link Mode values."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

    RESPONDER = 0x00
    CONTROLLER = 0x01
    EITHER = 0x03
    DELETE = 0xFF


class ManageAllLinkRecordAction(IntEnum):
    """Manage All Link Record Action values."""

    def __repr__(self):
        """Emit the representation of the Enum."""
        return '0x{0:02x}'.format(self.value)

    def __str__(self):
        """Emit the string of the Enum."""
        #pylint: disable=no-member
        return self.name.lower()

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


class ResponseStatus(IntEnum):
    """Response status of an outbound message."""

    FAILURE = 0
    SUCCESS = 1
    UNCLEAR = 2
    INPROGRESS = 4
    UNSENT = 8


MESSAGE_START_CODE = 0x02
MESSAGE_ACK = 0x06
MESSAGE_NAK = 0x15

CONTROL_FLAG_RECORD_IN_USE_0X80 = 0x80
CONTROL_FLAG_CONTROLER_0X40 = 0x40
CONTROL_FLAG_RECORD_HAS_BEEN_USED_0X02 = 0x02

# X10 House code lookup
HC_LOOKUP = {'a': 0x06,
             'b': 0x0e,
             'c': 0x02,
             'd': 0x0a,
             'e': 0x01,
             'f': 0x09,
             'g': 0x05,
             'h': 0x0d,
             'i': 0x07,
             'j': 0x0f,
             'k': 0x03,
             'l': 0x0b,
             'm': 0x00,
             'n': 0x08,
             'o': 0x04,
             'p': 0x0c}

# X10 Unit code lookup
UC_LOOKUP = {1: 0x06,
             2: 0x0e,
             3: 0x02,
             4: 0x0a,
             5: 0x01,
             6: 0x09,
             7: 0x05,
             8: 0x0d,
             9: 0x07,
             10: 0x0f,
             11: 0x03,
             12: 0x0b,
             13: 0x00,
             14: 0x08,
             15: 0x04,
             16: 0x0c,
             20: 0x20,  # All Units Off fake device
             21: 0x21,  # All Lights On fake device
             22: 0x22}  # All Lights Off fake device
