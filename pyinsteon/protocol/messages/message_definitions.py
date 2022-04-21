"""Message definitions."""

from collections import namedtuple

from ...address import Address
from ...constants import (
    AckNak,
    AllLinkMode,
    DeviceCategory,
    ImButtonEvents,
    ManageAllLinkRecordAction,
    MessageId,
    X10CommandType,
)
from ...data_types.all_link_record_flags import AllLinkRecordFlags
from ...data_types.im_config_flags import IMConfigurationFlags
from ...data_types.message_flags import MessageFlags
from ...data_types.user_data import UserData
from .message_definition import MessageDefinition

MessageField = namedtuple("MessageField", "name length type")


# MessageDefinition = namedtuple("MessageDefinition", "type fields")

# INSTEON Standard Message Received 0x50
FLD_STD_REC = [
    MessageField("address", 3, Address),
    MessageField("target", 3, Address),
    MessageField("flags", 1, MessageFlags),
    MessageField("cmd1", 1, int),
    MessageField("cmd2", 1, int),
]

# INSTEON Extended Message Received 0x51
FLD_EXT_REC = FLD_STD_REC.copy()
FLD_EXT_REC.append(MessageField("user_data", 14, UserData))

# X10 Send / Received 0x63 / 0x52
FLD_X10_SEND_REC = [
    MessageField("raw_x10", 1, int),
    MessageField("x10_flag", 1, X10CommandType),
]
FLD_X10_SEND_REC_ACK = FLD_X10_SEND_REC.copy()
FLD_X10_SEND_REC_ACK.append(MessageField("ack", 1, AckNak))

# ALL-Linking Completed 0x53
FLD_ALL_LINK_COMPLETE = [
    MessageField("link_mode", 1, AllLinkMode),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
    MessageField("cat", 1, DeviceCategory),
    MessageField("subcat", 1, int),
    MessageField("firmware", 1, int),
]

# IM Button Event Report 0x54
FLD_IM_BTN_EVENT_REPORT_REC = [MessageField("event", 1, ImButtonEvents)]

# IM User Reset Detected 0x55
FLD_USER_RESET_REC = []

# ALL-Link Cleanup Failure Report 0x56
FLD_ALL_LINK_CLEANUP_FAILURE = [
    MessageField("error", 1, int),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
]

# ALL-Link Record Response 0x57
FLD_ALL_LINK_RECORD_RESP = [
    MessageField("flags", 1, AllLinkRecordFlags),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
    MessageField("data1", 1, int),
    MessageField("data2", 1, int),
    MessageField("data3", 1, int),
]

# All-Link Cleanup Status Report 0x58
FLD_ALL_LINK_CLEANUP_REPORT_ACK = [MessageField("ack", 1, AckNak)]

# Read from EEPROM Response 0x59
FLD_READ_EEPROM_RESPONSE = [
    MessageField("mem_hi", 1, int),
    MessageField("mem_low", 1, int),
    MessageField("flags", 1, AllLinkRecordFlags),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
    MessageField("data1", 1, int),
    MessageField("data2", 1, int),
    MessageField("data3", 1, int),
]

# Get IM Info 0x60
FLD_GET_IM_INFO_SEND = []
FLD_GET_IM_INFO_REC = [
    MessageField("address", 3, Address),
    MessageField("cat", 1, DeviceCategory),
    MessageField("subcat", 1, int),
    MessageField("firmware", 1, int),
    MessageField("ack", 1, AckNak),
]

# Send All-Link Command 0x61
FLD_SEND_ALL_LINK_CMD = [
    MessageField("group", 1, int),
    MessageField("cmd1", 1, int),
    MessageField("cmd2", 1, int),
]
FLD_SEND_ALL_LINK_CMD_ACK = FLD_SEND_ALL_LINK_CMD.copy()
FLD_SEND_ALL_LINK_CMD_ACK.append(MessageField("ack", 1, AckNak))

# Send INSTEON Standard or Extended Message 0x62
FLD_STD_SEND = [
    MessageField("address", 3, Address),
    MessageField("flags", 1, MessageFlags),
    MessageField("cmd1", 1, int),
    MessageField("cmd2", 1, int),
]
FLD_EXT_SEND = FLD_STD_SEND.copy()
FLD_EXT_SEND.append(MessageField("user_data", 14, UserData))

# Send INSTEON Standard or Extended Message ACK/NAK 0x62
FLD_STD_SEND_ACK = FLD_STD_SEND.copy()
FLD_STD_SEND_ACK.append(MessageField("ack", 1, AckNak))
FLD_EXT_SEND_ACK = FLD_EXT_SEND.copy()
FLD_EXT_SEND_ACK.append(MessageField("ack", 1, AckNak))

# Send X10 0x63 (SEE X10 Received 0x52)

# Start All-Linking 0x64
FLD_START_ALL_LINKING = [
    MessageField("link_mode", 1, AllLinkMode),
    MessageField("group", 1, int),
]
FLD_START_ALL_LINKING_ACK = FLD_START_ALL_LINKING.copy()
FLD_START_ALL_LINKING_ACK.append(MessageField("ack", 1, AckNak))

# Cancel All-Linking 0x65
FLD_CANCEL_ALL_LINKING = []
FLD_CANCEL_ALL_LINKING_ACK = [MessageField("ack", 1, AckNak)]

# Set Host Device Category 0x66
FLD_SET_HOST_DEVICE_CATEGORY = [
    MessageField("cat", 1, DeviceCategory),
    MessageField("subcat", 1, int),
    MessageField("firmware", 1, int),
]
FLD_SET_HOST_DEVICE_CATEGORY_ACK = FLD_SET_HOST_DEVICE_CATEGORY.copy()
FLD_SET_HOST_DEVICE_CATEGORY_ACK.append(MessageField("ack", 1, AckNak))

# Reset the IM 0x67
FLD_RESET_IM = []
FLD_RESET_IM_ACK = [MessageField("ack", 1, AckNak)]

# Set INSTEON ACK/NAK Message Byte 0x68/0x70
FLD_SET_ACK_NAK_BYTE = [MessageField("cmd2", 1, int)]
FLD_SET_ACK_NAK_BYTE_ACK = FLD_SET_ACK_NAK_BYTE.copy()
FLD_SET_ACK_NAK_BYTE_ACK.append(MessageField("ack", 1, AckNak))

# Get First ALL-Link Record 0x69
FLD_GET_FIRST_ALL_LINK_RECORD = []
FLD_GET_FIRST_ALL_LINK_RECORD_ACK = [MessageField("ack", 1, AckNak)]

# Get Next ALL-Link Record 0x6A
FLD_GET_NEXT_ALL_LINK_RECORD = []
FLD_GET_NEXT_ALL_LINK_RECORD_ACK = [MessageField("ack", 1, AckNak)]

# Set IM Configuration 0x6B
FLD_SET_IM_CONFIG = [MessageField("flags", 1, IMConfigurationFlags)]
FLD_SET_IM_CONFIG_ACK = FLD_SET_IM_CONFIG.copy()
FLD_SET_IM_CONFIG_ACK.append(MessageField("ack", 1, AckNak))

# Get All-Link Record for Sender 0x6C
FLD_GET_ALL_LINK_REC_FOR_SENDER = []
FLD_GET_ALL_LINK_REC_FOR_SENDER_ACK = [MessageField("ack", 1, AckNak)]

# LED On/Off 0x6D / 0x6E
FLD_LED_ON_OFF = []
FLD_LED_ON_OFF_ACK = [MessageField("ack", 1, AckNak)]

# Manage All-Link Record 0x6F
FLD_MANAGE_ALL_LINK_RECORD = [
    MessageField("action", 1, ManageAllLinkRecordAction),
    MessageField("flags", 1, AllLinkRecordFlags),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
    MessageField("data1", 1, int),
    MessageField("data2", 1, int),
    MessageField("data3", 1, int),
]
FLD_MANAGE_ALL_LINK_RECORD_ACK = FLD_MANAGE_ALL_LINK_RECORD.copy()
FLD_MANAGE_ALL_LINK_RECORD_ACK.append(MessageField("ack", 1, AckNak))

# Set INSTEON NAK Message Byte see 0x68
# Set INSTEON ACK Message Two Bytes 0x71
FLD_SET_ACK_TWO_BYTES = [MessageField("cmd1", 1, int), MessageField("cmd2", 1, int)]
FLD_SET_ACK_TWO_BYTES_ACK = FLD_SET_ACK_TWO_BYTES.copy()
FLD_SET_ACK_TWO_BYTES_ACK.append(MessageField("ack", 1, AckNak))

# RF Sleep 0x72
FLD_RF_SLEEP = []
FLD_RF_SLEEP_ACK = [MessageField("ack", 1, AckNak)]

# Get IM Configuration 0x73
FLD_GET_IM_CONFIG = []
FLD_GET_IM_CONFIG_ACK = [
    MessageField("flags", 1, IMConfigurationFlags),
    MessageField("spare1", 1, int),
    MessageField("spare2", 1, int),
    MessageField("ack", 1, AckNak),
]

FLD_GET_IM_CONFIG_ACK = [
    MessageField("flags", 1, IMConfigurationFlags),
    MessageField("spare1", 1, int),
    MessageField("spare2", 1, int),
    MessageField("ack", 1, AckNak),
]

# Get IM Configuration 0x75
FLD_READ_EEPROM = [
    MessageField("mem_hi", 1, int),
    MessageField("mem_low", 1, int),
]
FLD_READ_EEPROM_ACK = FLD_READ_EEPROM.copy()
FLD_READ_EEPROM_ACK.append(MessageField("ack", 1, AckNak))

# Write to EEPROM 0x76
FLD_WRITE_EEPROM = [
    MessageField("mem_hi", 1, int),
    MessageField("mem_low", 1, int),
    MessageField("flags", 1, AllLinkRecordFlags),
    MessageField("group", 1, int),
    MessageField("target", 3, Address),
    MessageField("data1", 1, int),
    MessageField("data2", 1, int),
    MessageField("data3", 1, int),
]
FLD_WRITE_EEPROM_ACK = FLD_WRITE_EEPROM.copy()
FLD_WRITE_EEPROM_ACK.append(MessageField("ack", 1, AckNak))

INBOUND_MSG_DEF = {}
INBOUND_MSG_DEF[MessageId.STANDARD_RECEIVED] = MessageDefinition(
    MessageId.STANDARD_RECEIVED, FLD_STD_REC
)
INBOUND_MSG_DEF[MessageId.EXTENDED_RECEIVED] = MessageDefinition(
    MessageId.EXTENDED_RECEIVED, FLD_EXT_REC
)
INBOUND_MSG_DEF[MessageId.X10_RECEIVED] = MessageDefinition(
    MessageId.X10_RECEIVED, FLD_X10_SEND_REC
)
INBOUND_MSG_DEF[MessageId.ALL_LINKING_COMPLETED] = MessageDefinition(
    MessageId.ALL_LINKING_COMPLETED, FLD_ALL_LINK_COMPLETE
)
INBOUND_MSG_DEF[MessageId.BUTTON_EVENT_REPORT] = MessageDefinition(
    MessageId.BUTTON_EVENT_REPORT, FLD_IM_BTN_EVENT_REPORT_REC
)
INBOUND_MSG_DEF[MessageId.USER_RESET_DETECTED] = MessageDefinition(
    MessageId.USER_RESET_DETECTED, FLD_USER_RESET_REC
)
INBOUND_MSG_DEF[MessageId.ALL_LINK_CLEANUP_FAILURE_REPORT] = MessageDefinition(
    MessageId.ALL_LINK_CLEANUP_FAILURE_REPORT, FLD_ALL_LINK_CLEANUP_FAILURE
)
INBOUND_MSG_DEF[MessageId.ALL_LINK_RECORD_RESPONSE] = MessageDefinition(
    MessageId.ALL_LINK_RECORD_RESPONSE, FLD_ALL_LINK_RECORD_RESP
)
INBOUND_MSG_DEF[MessageId.ALL_LINK_CLEANUP_STATUS_REPORT] = MessageDefinition(
    MessageId.ALL_LINK_CLEANUP_STATUS_REPORT, FLD_ALL_LINK_CLEANUP_REPORT_ACK
)
INBOUND_MSG_DEF[MessageId.READ_EEPROM_RESPONSE] = MessageDefinition(
    MessageId.READ_EEPROM_RESPONSE, FLD_READ_EEPROM_RESPONSE
)
INBOUND_MSG_DEF[MessageId.GET_IM_INFO] = MessageDefinition(
    MessageId.GET_IM_INFO, FLD_GET_IM_INFO_REC
)
INBOUND_MSG_DEF[MessageId.SEND_ALL_LINK_COMMAND] = MessageDefinition(
    MessageId.SEND_ALL_LINK_COMMAND, FLD_SEND_ALL_LINK_CMD_ACK
)
INBOUND_MSG_DEF[MessageId.SEND_STANDARD] = MessageDefinition(
    MessageId.SEND_STANDARD, FLD_STD_SEND_ACK
)
INBOUND_MSG_DEF[MessageId.X10_SEND] = MessageDefinition(
    MessageId.X10_SEND, FLD_X10_SEND_REC_ACK
)
INBOUND_MSG_DEF[MessageId.START_ALL_LINKING] = MessageDefinition(
    MessageId.START_ALL_LINKING, FLD_START_ALL_LINKING_ACK
)
INBOUND_MSG_DEF[MessageId.CANCEL_ALL_LINKING] = MessageDefinition(
    MessageId.CANCEL_ALL_LINKING, FLD_CANCEL_ALL_LINKING_ACK
)
INBOUND_MSG_DEF[MessageId.SET_HOST_DEVICE_CATEGORY] = MessageDefinition(
    MessageId.SET_HOST_DEVICE_CATEGORY, FLD_SET_HOST_DEVICE_CATEGORY_ACK
)
INBOUND_MSG_DEF[MessageId.RESET_IM] = MessageDefinition(
    MessageId.RESET_IM, FLD_RESET_IM_ACK
)
INBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_BYTE] = MessageDefinition(
    MessageId.SET_ACK_MESSAGE_BYTE, FLD_SET_ACK_NAK_BYTE_ACK
)
INBOUND_MSG_DEF[MessageId.GET_FIRST_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.GET_FIRST_ALL_LINK_RECORD, FLD_GET_FIRST_ALL_LINK_RECORD_ACK
)
INBOUND_MSG_DEF[MessageId.GET_NEXT_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.GET_NEXT_ALL_LINK_RECORD, FLD_GET_NEXT_ALL_LINK_RECORD_ACK
)
INBOUND_MSG_DEF[MessageId.SET_IM_CONFIGURATION] = MessageDefinition(
    MessageId.SET_IM_CONFIGURATION, FLD_SET_IM_CONFIG_ACK
)
INBOUND_MSG_DEF[MessageId.GET_ALL_LINK_RECORD_FOR_SENDER] = MessageDefinition(
    MessageId.GET_ALL_LINK_RECORD_FOR_SENDER, FLD_GET_ALL_LINK_REC_FOR_SENDER_ACK
)
INBOUND_MSG_DEF[MessageId.LED_ON] = MessageDefinition(
    MessageId.LED_ON, FLD_LED_ON_OFF_ACK
)
INBOUND_MSG_DEF[MessageId.LED_OFF] = MessageDefinition(
    MessageId.LED_OFF, FLD_LED_ON_OFF_ACK
)
INBOUND_MSG_DEF[MessageId.MANAGE_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.MANAGE_ALL_LINK_RECORD, FLD_MANAGE_ALL_LINK_RECORD_ACK
)
INBOUND_MSG_DEF[MessageId.SET_NAK_MESSAGE_BYTE] = MessageDefinition(
    MessageId.SET_NAK_MESSAGE_BYTE, FLD_SET_ACK_NAK_BYTE_ACK
)
INBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_TWO_BYTES] = MessageDefinition(
    MessageId.SET_ACK_MESSAGE_TWO_BYTES, FLD_SET_ACK_TWO_BYTES_ACK
)
INBOUND_MSG_DEF[MessageId.RF_SLEEP] = MessageDefinition(
    MessageId.RF_SLEEP, FLD_RF_SLEEP_ACK
)
INBOUND_MSG_DEF[MessageId.GET_IM_CONFIGURATION] = MessageDefinition(
    MessageId.GET_IM_CONFIGURATION, FLD_GET_IM_CONFIG_ACK
)
INBOUND_MSG_DEF[MessageId.READ_EEPROM] = MessageDefinition(
    MessageId.READ_EEPROM, FLD_READ_EEPROM_ACK
)
INBOUND_MSG_DEF[MessageId.WRITE_EEPROM] = MessageDefinition(
    MessageId.WRITE_EEPROM, FLD_WRITE_EEPROM_ACK
)

OUTBOUND_MSG_DEF = {}
OUTBOUND_MSG_DEF[MessageId.GET_IM_INFO] = MessageDefinition(
    MessageId.GET_IM_INFO, FLD_GET_IM_INFO_SEND
)
OUTBOUND_MSG_DEF[MessageId.SEND_ALL_LINK_COMMAND] = MessageDefinition(
    MessageId.SEND_ALL_LINK_COMMAND, FLD_SEND_ALL_LINK_CMD
)
OUTBOUND_MSG_DEF[MessageId.SEND_STANDARD] = MessageDefinition(
    MessageId.SEND_STANDARD, FLD_STD_SEND
)
OUTBOUND_MSG_DEF[MessageId.X10_SEND] = MessageDefinition(
    MessageId.X10_SEND, FLD_X10_SEND_REC
)
OUTBOUND_MSG_DEF[MessageId.START_ALL_LINKING] = MessageDefinition(
    MessageId.START_ALL_LINKING, FLD_START_ALL_LINKING
)
OUTBOUND_MSG_DEF[MessageId.CANCEL_ALL_LINKING] = MessageDefinition(
    MessageId.CANCEL_ALL_LINKING, FLD_CANCEL_ALL_LINKING
)
OUTBOUND_MSG_DEF[MessageId.SET_HOST_DEVICE_CATEGORY] = MessageDefinition(
    MessageId.SET_HOST_DEVICE_CATEGORY, FLD_SET_HOST_DEVICE_CATEGORY
)
OUTBOUND_MSG_DEF[MessageId.RESET_IM] = MessageDefinition(
    MessageId.RESET_IM, FLD_RESET_IM
)
OUTBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_BYTE] = MessageDefinition(
    MessageId.SET_ACK_MESSAGE_BYTE, FLD_SET_ACK_NAK_BYTE
)
OUTBOUND_MSG_DEF[MessageId.GET_FIRST_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.GET_FIRST_ALL_LINK_RECORD, FLD_GET_FIRST_ALL_LINK_RECORD
)
OUTBOUND_MSG_DEF[MessageId.GET_NEXT_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.GET_NEXT_ALL_LINK_RECORD, FLD_GET_NEXT_ALL_LINK_RECORD
)
OUTBOUND_MSG_DEF[MessageId.SET_IM_CONFIGURATION] = MessageDefinition(
    MessageId.SET_IM_CONFIGURATION, FLD_SET_IM_CONFIG
)
OUTBOUND_MSG_DEF[MessageId.GET_ALL_LINK_RECORD_FOR_SENDER] = MessageDefinition(
    MessageId.GET_ALL_LINK_RECORD_FOR_SENDER, FLD_GET_ALL_LINK_REC_FOR_SENDER
)
OUTBOUND_MSG_DEF[MessageId.LED_ON] = MessageDefinition(MessageId.LED_ON, FLD_LED_ON_OFF)
OUTBOUND_MSG_DEF[MessageId.LED_OFF] = MessageDefinition(
    MessageId.LED_OFF, FLD_LED_ON_OFF
)
OUTBOUND_MSG_DEF[MessageId.MANAGE_ALL_LINK_RECORD] = MessageDefinition(
    MessageId.MANAGE_ALL_LINK_RECORD, FLD_MANAGE_ALL_LINK_RECORD
)
OUTBOUND_MSG_DEF[MessageId.SET_NAK_MESSAGE_BYTE] = MessageDefinition(
    MessageId.SET_NAK_MESSAGE_BYTE, FLD_SET_ACK_NAK_BYTE
)
OUTBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_TWO_BYTES] = MessageDefinition(
    MessageId.SET_ACK_MESSAGE_TWO_BYTES, FLD_SET_ACK_TWO_BYTES
)
OUTBOUND_MSG_DEF[MessageId.RF_SLEEP] = MessageDefinition(
    MessageId.RF_SLEEP, FLD_RF_SLEEP
)
OUTBOUND_MSG_DEF[MessageId.GET_IM_CONFIGURATION] = MessageDefinition(
    MessageId.GET_IM_CONFIGURATION, FLD_GET_IM_CONFIG
)

OUTBOUND_MSG_DEF[MessageId.READ_EEPROM] = MessageDefinition(
    MessageId.READ_EEPROM, FLD_READ_EEPROM
)

OUTBOUND_MSG_DEF[MessageId.WRITE_EEPROM] = MessageDefinition(
    MessageId.WRITE_EEPROM, FLD_WRITE_EEPROM
)
