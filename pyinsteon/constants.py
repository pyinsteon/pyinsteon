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


MESSAGE_START_CODE = 0x02
MESSAGE_ACK = 0x06
MESSAGE_NAK = 0x15

COMMAND_ASSIGN_TO_ALL_LINK_GROUP_0X01_NONE = {'cmd1': 0x01, 'cmd2': None}
COMMAND_DELETE_FROM_ALL_LINK_GROUP_0X02_NONE = {'cmd1': 0x02, 'cmd2': None}
COMMAND_PRODUCT_DATA_REQUEST_0X03_0X00 = {'cmd1': 0x03, 'cmd2': 0x00}
COMMAND_FX_USERNAME_0X03_0X01 = {'cmd1': 0x03, 'cmd2': 0x01}
COMMAND_DEVICE_TEXT_STRING_REQUEST_0X03_0X02 = {'cmd1': 0x03, 'cmd2': 0x02}
COMMAND_ENTER_LINKING_MODE_0X09_NONE = {'cmd1': 0x09, 'cmd2': None}
COMMAND_ENTER_UNLINKING_MODE_0X0A_NONE = {'cmd1': 0x0A, 'cmd2': None}
COMMAND_GET_INSTEON_ENGINE_VERSION_0X0D_0X00 = {'cmd1': 0x0D, 'cmd2': 0x00}
COMMAND_PING_0X0F_0X00 = {'cmd1': 0x0F, 'cmd2': 0x00}
COMMAND_ID_REQUEST_0X10_0X00 = {'cmd1': 0x10, 'cmd2': 0x00}
COMMAND_ID_REQUEST_RESPONSE_0X10_0X10 = {'cmd1': 0x10, 'cmd2': 0x10}
COMMAND_LIGHT_ON_0X11_NONE = {'cmd1': 0x11, 'cmd2': None}
COMMAND_LIGHT_ON_FAST_0X12_NONE = {'cmd1': 0x12, 'cmd2': None}
COMMAND_LIGHT_OFF_0X13_0X00 = {'cmd1': 0x13, 'cmd2': 0x00}
COMMAND_LIGHT_OFF_FAST_0X14_0X00 = {'cmd1': 0x14, 'cmd2': 0x00}
COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00 = {'cmd1': 0x15, 'cmd2': 0x00}
COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00 = {'cmd1': 0x16, 'cmd2': 0x00}
COMMAND_LIGHT_START_MANUAL_CHANGEDOWN_0X17_0X00 = {'cmd1': 0x17, 'cmd2': 0x00}
COMMAND_LIGHT_START_MANUAL_CHANGEUP_0X17_0X01 = {'cmd1': 0x17, 'cmd2': 0x01}
COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00 = {'cmd1': 0x18, 'cmd2': 0x00}
COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00 = {'cmd1': 0x19, 'cmd2': 0x00}
COMMAND_LIGHT_STATUS_REQUEST_0X19_0X01 = {'cmd1': 0x19, 'cmd2': 0x01}
COMMAND_LIGHT_STATUS_REQUEST_0X19_NONE = {'cmd1': 0x19, 'cmd2': None}
COMMAND_GET_OPERATING_FLAGS_0X1F_NONE = {'cmd1': 0x1F, 'cmd2': None}
COMMAND_SET_OPERATING_FLAGS_0X20_NONE = {'cmd1': 0x20, 'cmd2': None}
COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE = {'cmd1': 0x21, 'cmd2': None}
COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00 = {'cmd1': 0x22, 'cmd2': 0x00}
COMMAND_LIGHT_MANUALLY_TURNED_OFF_0X22_0X00 = {'cmd1': 0x22, 'cmd2': 0x00}
COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00 = {'cmd1': 0x23, 'cmd2': 0x00}
COMMAND_LIGHT_MANUALLY_TURNED_ON_0X23_0X00 = {'cmd1': 0x23, 'cmd2': 0x00}
COMMAND_REMOTE_SET_BUTTON_TAP1_TAP_0X25_0X01 = {'cmd1': 0x25, 'cmd2': 0x01}
COMMAND_REMOTE_SET_BUTTON_TAP2_TAP_0X25_0X02 = {'cmd1': 0x25, 'cmd2': 0x02}
COMMAND_LIGHT_SET_STATUS_0X27_NONE = {'cmd1': 0x27, 'cmd2': None}
COMMAND_SET_ADDRESS_MSB_0X28_NONE = {'cmd1': 0x28, 'cmd2': None}
COMMAND_POKE_ONE_BYTE_0X29_NONE = {'cmd1': 0x29, 'cmd2': None}
COMMAND_RESERVED_0X2A_NONE = {'cmd1': 0x2A, 'cmd2': None}
COMMAND_PEEK_ONE_BYTE_0X2B_NONE = {'cmd1': 0x2B, 'cmd2': None}
COMMAND_PEEK_ONE_BYTE_INTERNAL_0X2C_NONE = {'cmd1': 0x2C, 'cmd2': None}
COMMAND_POKE_ONE_BYTE_INTERNAL_0X2D_NONE = {'cmd1': 0x2D, 'cmd2': None}
COMMAND_LIGHT_ON_AT_RAMP_RATE_0X2E_NONE = {'cmd1': 0x2E, 'cmd2': None}
COMMAND_EXTENDED_GET_SET_0X2E_0X00 = {'cmd1': 0x2E, 'cmd2': 0x00}
COMMAND_LIGHT_OFF_AT_RAMP_RATE_0X2F_NONE = {'cmd1': 0x2F, 'cmd2': None}
COMMAND_EXTENDED_READ_WRITE_ALDB_0X2F_0X00 = {'cmd1': 0x2F, 'cmd2': 0x00}
COMMAND_EXTENDED_TRIGGER_ALL_LINK_0X30_0X00 = {'cmd1': 0x30, 'cmd2': 0x00}
COMMAND_SPRINKLER_VALVE_ON_0X40_NONE = {'cmd1': 0x40, 'cmd2': None}
COMMAND_SPRINKLER_VALVE_OFF_0X41_NONE = {'cmd1': 0x41, 'cmd2': None}
COMMAND_SPRINKLER_PROGRAM_ON_0X42_NONE = {'cmd1': 0x42, 'cmd2': None}
COMMAND_SPRINKLER_PROGRAM_OFF_0X43_NONE = {'cmd1': 0x43, 'cmd2': None}
COMMAND_SPRINKLER_CONTROLLOAD_INITIALIZATION_VALUES_0X44_0X00 = {'cmd1': 0x44,
                                                                 'cmd2': 0x00}
COMMAND_SPRINKLER_CONTROLLOAD_EEPROM_FROM_RAM_0X44_0X01 = {'cmd1': 0x44,
                                                           'cmd2': 0x01}
COMMAND_SPRINKLER_CONTROLGET_VALVE_STATUS_0X44_0X02 = {'cmd1': 0x44,
                                                       'cmd2': 0x02}
COMMAND_SPRINKLER_CONTROLINHIBIT_COMMAND_ACCEPTANCE_0X44_0X03 = {'cmd1': 0x44,
                                                                 'cmd2': 0x03}
COMMAND_SPRINKLER_CONTROLRESUME_COMMAND_ACCEPTANCE_0X44_0X04 = {'cmd1': 0x44,
                                                                'cmd2': 0x04}
COMMAND_SPRINKLER_CONTROLSKIP_FORWARD_0X44_0X05 = {'cmd1': 0x44, 'cmd2': 0x05}
COMMAND_SPRINKLER_CONTROLSKIP_BACK_0X44_0X06 = {'cmd1': 0x44, 'cmd2': 0x06}
COMMAND_SPRINKLER_CONTROLENABLE_PUMP_ON_V8_0X44_0X07 = {'cmd1': 0x44,
                                                        'cmd2': 0x07}
COMMAND_SPRINKLER_CONTROLDISABLE_PUMP_ON_V8_0X44_0X08 = {'cmd1': 0x44,
                                                         'cmd2': 0x08}
COMMAND_SPRINKLER_CONTROLBROADCAST_ON_0X44_0X09 = {'cmd1': 0x44, 'cmd2': 0x09}
COMMAND_SPRINKLER_CONTROLBROADCAST_OFF_0X44_0X0A = {'cmd1': 0x44, 'cmd2': 0x0A}
COMMAND_SPRINKLER_CONTROLLOAD_RAM_FROM_EEPROM_0X44_0X0B = {'cmd1': 0x44,
                                                           'cmd2': 0x0B}
COMMAND_SPRINKLER_CONTROLSENSOR_ON_0X44_0X0C = {'cmd1': 0x44, 'cmd2': 0x0C}
COMMAND_SPRINKLER_CONTROLSENSOR_OFF_0X44_0X0D = {'cmd1': 0x44, 'cmd2': 0x0D}
COMMAND_SPRINKLER_CONTROLDIAGNOSTICS_ON_0X44_0X0E = {'cmd1': 0x44,
                                                     'cmd2': 0x0E}
COMMAND_SPRINKLER_CONTROLDIAGNOSTICS_OFF_0X44_0X0F = {'cmd1': 0x44,
                                                      'cmd2': 0x0F}
COMMAND_SPRINKLER_GET_PROGRAM_REQUEST_0X45_NONE = {'cmd1': 0x45, 'cmd2': None}
COMMAND_IO_OUTPUT_ON_0X45_NONE = {'cmd1': 0x45, 'cmd2': None}
COMMAND_IO_OUTPUT_OFF_0X46_NONE = {'cmd1': 0x46, 'cmd2': None}
COMMAND_IO_ALARM_DATA_REQUEST_0X47_0X00 = {'cmd1': 0x47, 'cmd2': 0x00}
COMMAND_IO_WRITE_OUTPUT_PORT_0X48_NONE = {'cmd1': 0x48, 'cmd2': None}
COMMAND_IO_READ_INPUT_PORT_0X49_0X00 = {'cmd1': 0x49, 'cmd2': 0x00}
COMMAND_IO_GET_SENSOR_VALUE_0X4A_NONE = {'cmd1': 0x4A, 'cmd2': None}
COMMAND_IO_SET_SENSOR_1_NOMINAL_VALUE_0X4B_NONE = {'cmd1': 0x4B, 'cmd2': None}
COMMAND_IO_GET_SENSOR_ALARM_DELTA_0X4C_NONE = {'cmd1': 0x4C, 'cmd2': None}
COMMAND_FAN_STATUS_REPORT_0X4C_NONE = {'cmd1': 0x4C, 'cmd2': None}
COMMAND_IO_WRITE_CONFIGURATION_PORT_0X4D_NONE = {'cmd1': 0x4D, 'cmd2': None}
COMMAND_IO_READ_CONFIGURATION_PORT_0X4E_0X00 = {'cmd1': 0x4E, 'cmd2': 0x00}
COMMAND_IO_MODULE_CONTROLLOAD_INITIALIZATION_VALUES_0X4F_0X00 = {
    'cmd1': 0x4F, 'cmd2': 0x00}
COMMAND_IO_MODULE_CONTROLLOAD_EEPROM_FROM_RAM_0X4F_0X01 = {'cmd1': 0x4F,
                                                           'cmd2': 0x01}
COMMAND_IO_MODULE_CONTROLSTATUS_REQUEST_0X4F_0X02 = {'cmd1': 0x4F,
                                                     'cmd2': 0x02}
COMMAND_IO_MODULE_CONTROLREAD_ANALOG_ONCE_0X4F_0X03 = {'cmd1': 0x4F,
                                                       'cmd2': 0x03}
COMMAND_IO_MODULE_CONTROLREAD_ANALOG_ALWAYS_0X4F_0X04 = {'cmd1': 0x4F,
                                                         'cmd2': 0x04}
COMMAND_IO_MODULE_CONTROLENABLE_STATUS_CHANGE_MESSAGE_0X4F_0X09 = {
    'cmd1': 0x4F, 'cmd2': 0x09}
COMMAND_IO_MODULE_CONTROLDISABLE_STATUS_CHANGE_MESSAGE_0X4F_0X0A = {
    'cmd1': 0x4F, 'cmd2': 0x0A}
COMMAND_IO_MODULE_CONTROLLOAD_RAM_FROM_EEPROM_0X4F_0X0B = {
    'cmd1': 0x4F, 'cmd2': 0x0B}
COMMAND_IO_MODULE_CONTROLSENSOR_ON_0X4F_0X0C = {'cmd1': 0x4F, 'cmd2': 0x0C}
COMMAND_IO_MODULE_CONTROLSENSOR_OFF_0X4F_0X0D = {'cmd1': 0x4F, 'cmd2': 0x0D}
COMMAND_IO_MODULE_CONTROLDIAGNOSTICS_ON_0X4F_0X0E = {'cmd1': 0x4F,
                                                     'cmd2': 0x0E}
COMMAND_IO_MODULE_CONTROLDIAGNOSTICS_OFF_0X4F_0X0F = {'cmd1': 0x4F,
                                                      'cmd2': 0x0F}
COMMAND_POOL_DEVICE_ONPOOL_0X50_0X01 = {'cmd1': 0x50, 'cmd2': 0x01}
COMMAND_POOL_DEVICE_ONSPA_0X50_0X02 = {'cmd1': 0x50, 'cmd2': 0x02}
COMMAND_POOL_DEVICE_ONHEAT_0X50_0X03 = {'cmd1': 0x50, 'cmd2': 0x03}
COMMAND_POOL_DEVICE_ONPUMP_0X50_0X04 = {'cmd1': 0x50, 'cmd2': 0x04}
COMMAND_POOL_DEVICE_ONAUX_0X50_NONE = {'cmd1': 0x50, 'cmd2': None}
COMMAND_POOL_DEVICE_OFF_0X51_NONE = {'cmd1': 0x51, 'cmd2': None}
COMMAND_POOL_TEMPERATURE_UP_0X52_NONE = {'cmd1': 0x52, 'cmd2': None}
COMMAND_POOL_TEMPERATURE_DOWN_0X53_NONE = {'cmd1': 0x53, 'cmd2': None}
COMMAND_POOL_CONTROLLOAD_INITIALIZATION_VALUES_0X54_0X00 = {'cmd1': 0x54,
                                                            'cmd2': 0x00}
COMMAND_POOL_CONTROLLOAD_EEPROM_FROM_RAM_0X54_0X01 = {'cmd1': 0x54,
                                                      'cmd2': 0x01}
COMMAND_POOL_CONTROLGET_POOL_MODE_0X54_0X02 = {'cmd1': 0x54, 'cmd2': 0x02}
COMMAND_POOL_CONTROLGET_AMBIENT_TEMPERATURE_0X54_0X03 = {'cmd1': 0x54,
                                                         'cmd2': 0x03}
COMMAND_POOL_CONTROLGET_WATER_TEMPERATURE_0X54_0X04 = {'cmd1': 0x54,
                                                       'cmd2': 0x04}
COMMAND_POOL_CONTROLGET_PH_0X54_0X05 = {'cmd1': 0x54, 'cmd2': 0x05}
COMMAND_DOOR_MOVERAISE_DOOR_0X58_0X00 = {'cmd1': 0x58, 'cmd2': 0x00}
COMMAND_DOOR_MOVELOWER_DOOR_0X58_0X01 = {'cmd1': 0x58, 'cmd2': 0x01}
COMMAND_DOOR_MOVEOPEN_DOOR_0X58_0X02 = {'cmd1': 0x58, 'cmd2': 0x02}
COMMAND_DOOR_MOVECLOSE_DOOR_0X58_0X03 = {'cmd1': 0x58, 'cmd2': 0x03}
COMMAND_DOOR_MOVESTOP_DOOR_0X58_0X04 = {'cmd1': 0x58, 'cmd2': 0x04}
COMMAND_DOOR_MOVESINGLE_DOOR_OPEN_0X58_0X05 = {'cmd1': 0x58, 'cmd2': 0x05}
COMMAND_DOOR_MOVESINGLE_DOOR_CLOSE_0X58_0X06 = {'cmd1': 0x58, 'cmd2': 0x06}
COMMAND_DOOR_STATUS_REPORTRAISE_DOOR_0X59_0X00 = {'cmd1': 0x59, 'cmd2': 0x00}
COMMAND_DOOR_STATUS_REPORTLOWER_DOOR_0X59_0X01 = {'cmd1': 0x59, 'cmd2': 0x01}
COMMAND_DOOR_STATUS_REPORTOPEN_DOOR_0X59_0X02 = {'cmd1': 0x59, 'cmd2': 0x02}
COMMAND_DOOR_STATUS_REPORTCLOSE_DOOR_0X59_0X03 = {'cmd1': 0x59, 'cmd2': 0x03}
COMMAND_DOOR_STATUS_REPORTSTOP_DOOR_0X59_0X04 = {'cmd1': 0x59, 'cmd2': 0x04}
COMMAND_DOOR_STATUS_REPORTSINGLE_DOOR_OPEN_0X59_0X05 = {'cmd1': 0x59,
                                                        'cmd2': 0x05}
COMMAND_DOOR_STATUS_REPORTSINGLE_DOOR_CLOSE_0X59_0X06 = {'cmd1': 0x59,
                                                         'cmd2': 0x06}
COMMAND_WINDOW_COVERINGOPEN_0X60_0X01 = {'cmd1': 0x60, 'cmd2': 0x01}
COMMAND_WINDOW_COVERINGCLOSE_0X60_0X02 = {'cmd1': 0x60, 'cmd2': 0x02}
COMMAND_WINDOW_COVERINGSTOP_0X60_0X03 = {'cmd1': 0x60, 'cmd2': 0x03}
COMMAND_WINDOW_COVERINGPROGRAM_0X60_0X04 = {'cmd1': 0x60, 'cmd2': 0x04}
COMMAND_WINDOW_COVERING_POSITION_0X61_NONE = {'cmd1': 0x61, 'cmd2': None}
COMMAND_THERMOSTAT_TEMPERATURE_UP_0X68_NONE = {'cmd1': 0x68, 'cmd2': None}
COMMAND_THERMOSTAT_TEMPERATURE_DOWN_0X69_NONE = {'cmd1': 0x69, 'cmd2': None}
COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE = {'cmd1': 0x6A,
                                                     'cmd2': None}
COMMAND_THERMOSTAT_CONTROL_LOAD_INITIALIZATION_VALUES_0X6B_0X00 = {
    'cmd1': 0x6B, 'cmd2': 0x00}
COMMAND_THERMOSTAT_CONTROL_LOAD_EEPROM_FROM_RAM_0X6B_0X01 = {'cmd1': 0x6B,
                                                             'cmd2': 0x01}
COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02 = {'cmd1': 0x6B, 'cmd2': 0x02}
COMMAND_THERMOSTAT_CONTROL_GET_AMBIENT_TEMPERATURE_0X6B_0X03 = {'cmd1': 0x6B,
                                                                'cmd2': 0x03}
COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04 = {'cmd1': 0x6B, 'cmd2': 0x04}
COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05 = {'cmd1': 0x6B, 'cmd2': 0x05}
COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06 = {'cmd1': 0x6B, 'cmd2': 0x06}
COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07 = {'cmd1': 0x6B, 'cmd2': 0x07}
COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08 = {'cmd1': 0x6B, 'cmd2': 0x08}
COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09 = {'cmd1': 0x6B, 'cmd2': 0x09}
COMMAND_THERMOSTAT_CONTROL_PROGRAM_HEAT_0X6B_0X0A = {'cmd1': 0x6B,
                                                     'cmd2': 0x0A}
COMMAND_THERMOSTAT_CONTROL_PROGRAM_COOL_0X6B_0X0B = {'cmd1': 0x6B,
                                                     'cmd2': 0x0B}
COMMAND_THERMOSTAT_CONTROL_PROGRAM_AUTO_0X6B_0X0C = {'cmd1': 0x6B,
                                                     'cmd2': 0x0C}
COMMAND_THERMOSTAT_CONTROL_GET_EQUIPMENT_STATE_0X6B_0X0D = {'cmd1': 0x6B,
                                                            'cmd2': 0x0D}
COMMAND_THERMOSTAT_CONTROL_SET_EQUIPMENT_STATE_0X6B_0X0E = {'cmd1': 0x6B,
                                                            'cmd2': 0x0E}
COMMAND_THERMOSTAT_CONTROL_GET_TEMPERATURE_UNITS_0X6B_0X0F = {'cmd1': 0x6B,
                                                              'cmd2': 0x0F}
COMMAND_THERMOSTAT_CONTROL_SET_FAHRENHEIT_0X6B_0X10 = {'cmd1': 0x6B,
                                                       'cmd2': 0x10}
COMMAND_THERMOSTAT_CONTROL_SET_CELSIUS_0X6B_0X11 = {'cmd1': 0x6B, 'cmd2': 0x11}
COMMAND_THERMOSTAT_CONTROL_GET_FAN_ON_SPEED_0X6B_0X12 = {'cmd1': 0x6B,
                                                         'cmd2': 0x12}
COMMAND_THERMOSTAT_CONTROL_SET_FAN_ON_SPEED_LOW_0X6B_0X13 = {'cmd1': 0x6B,
                                                             'cmd2': 0x13}
COMMAND_THERMOSTAT_CONTROL_SET_FAN_ON_SPEED_MEDIUM_0X6B_0X14 = {'cmd1': 0x6B,
                                                                'cmd2': 0x14}
COMMAND_THERMOSTAT_CONTROL_SET_FAN_ON_SPEED_HIGH_0X6B_0X15 = {'cmd1': 0x6B,
                                                              'cmd2': 0x15}
COMMAND_THERMOSTAT_CONTROL_ENABLE_STATUS_CHANGE_MESSAGE_0X6B_0X16 = {
    'cmd1': 0x6B, 'cmd2': 0x16}
COMMAND_THERMOSTAT_CONTROL_DISABLE_STATUS_CHANGE_MESSAGE_0X6B_0X17 = {
    'cmd1': 0x6B, 'cmd2': 0x17}
COMMAND_THERMOSTAT_SET_COOL_SETPOINT_0X6C_NONE = {'cmd1': 0x6C, 'cmd2': None}
COMMAND_THERMOSTAT_SET_HEAT_SETPOINT_0X6D_NONE = {'cmd1': 0x6D, 'cmd2': None}
COMMAND_THERMOSTAT_TEMPERATURE_STATUS_0X6E_NONE = {'cmd1': 0x6E, 'cmd2': None}
COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE = {'cmd1': 0x6F, 'cmd2': None}
COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE = {'cmd1': 0x70, 'cmd2': None}
COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE = {'cmd1': 0x71,
                                                      'cmd2': None}
COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE = {'cmd1': 0x72,
                                                      'cmd2': None}

COMMAND_LEAK_DETECTOR_ANNOUNCE_0X70_NONE = {'cmd1': 0X70, 'cmd2': None}
COMMAND_ASSIGN_TO_COMPANION_GROUP_0X81_0X00 = {'cmd1': 0x81, 'cmd2': 0x00}


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
