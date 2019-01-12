"""Message definitions."""

from collections import namedtuple

from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from .im_config_flags import IMConfigurationFlags
from ..constants import (MessageId, ImButtonEvents, AllLinkMode,
                         DeviceCategory, ManageAlLinkRecordAction,
                         AckNak)
from .message_flags import MessageFlags
from .user_data import UserData


MessageDataField = namedtuple("MessageDataField", "name length type")


MessageDefinition = namedtuple("MessageDefinition", "type fields")

# INSTEON Standard Message Received 0x50
FLD_STD_REC = [MessageDataField("address", 3, Address),
               MessageDataField("target", 3, Address),
               MessageDataField("flags", 1, MessageFlags),
               MessageDataField("cmd1", 1, int),
               MessageDataField("cmd2", 1, int)]

# INSTEON Extended Message Received 0x51
FLD_EXT_REC = FLD_STD_REC.copy()
FLD_EXT_REC.append(MessageDataField('userdata', 14, UserData))

# X10 Send / Received 0x63 / 0x52
FLD_X10_SEND_REC = [MessageDataField("raw_x10", 1, int),
                    MessageDataField("x10_flag", 1, int)]
FLD_X10_SEND_REC_ACK = FLD_X10_SEND_REC.copy()
FLD_X10_SEND_REC_ACK.append(MessageDataField('ack', 1, AckNak))

# ALL-Linking Completed 0x53
FLD_ALL_LINK_COMPLETE = [MessageDataField("mode", 1, AllLinkMode),
                         MessageDataField("group", 1, int),
                         MessageDataField("target", 3, Address),
                         MessageDataField("cat", 1, DeviceCategory),
                         MessageDataField("subcat", 1, int),
                         MessageDataField("firmware", 1, int)]

# IM Button Event Report 0x54
FLD_IM_BTN_EVENT_REPORT_REC = [MessageDataField("event", 1, ImButtonEvents)]

# IM User Reset Detected 0x55
FLD_USER_RESET_REC = []

# ALL-Link Cleanup Failure Report 0x56
FLD_ALL_LINK_CLEANUP_FAILURE = [MessageDataField("error", 1, int),
                                MessageDataField("group", 1, int),
                                MessageDataField("address", 3, Address)]

# ALL-Link Record Response 0x57
FLD_ALL_LINK_RECORD_RESP = [MessageDataField("flags", 1, AllLinkRecordFlags),
                            MessageDataField("group", 1, int),
                            MessageDataField("address", 3, Address),
                            MessageDataField("data1", 1, int),
                            MessageDataField("data2", 1, int),
                            MessageDataField("data3", 1, int)]

# All-Link Cleanup Status Report 0x58
FLD_All_LINK_CLEANUP_REPORT_ACK = [MessageDataField("ack", 1, int)]

# Get IM Info 0x60
FLD_GET_IM_INFO_SEND = []
FLD_GET_IM_INFO_REC = [MessageDataField('address', 3, Address),
                       MessageDataField('cat', 1, DeviceCategory),
                       MessageDataField('subcat', 1, int),
                       MessageDataField('firmware', 1, int),
                       MessageDataField('ack', 1, AckNak)]

# Send All-Link Command 0x61
FLD_SEND_ALL_LINK_CMD = [MessageDataField('group', 1, int),
                         MessageDataField('mode', 1, AllLinkMode)]
FLD_SEND_ALL_LINK_CMD_ACK = FLD_SEND_ALL_LINK_CMD.copy()
FLD_SEND_ALL_LINK_CMD_ACK.append(MessageDataField('ack', 1, AckNak))

# Send INSTEON Standard or Extended Message 0x62
FLD_STD_SEND = [MessageDataField("address", 3, Address),
                MessageDataField("flags", 1, MessageFlags),
                MessageDataField("cmd1", 1, int),
                MessageDataField("cmd2", 1, int)]
FLD_EXT_SEND = FLD_STD_SEND.copy()
FLD_EXT_SEND.append(MessageDataField('userdata', 14, UserData))

# Send INSTEON Standard or Extended Message ACK/NAK 0x62
FLD_STD_SEND_ACK = FLD_STD_SEND.copy()
FLD_STD_SEND_ACK.append(MessageDataField("ack", 1, int))
FLD_EXT_SEND_ACK = FLD_EXT_SEND.copy()
FLD_EXT_SEND_ACK.append(MessageDataField("ack", 1, int))

# Send X10 0x63 (SEE X10 Received 0x52)

# Start All-Linking 0x64
FLD_START_ALL_LINKING = [MessageDataField('mode', 1, AllLinkMode),
                         MessageDataField('group', 1, int)]
FLD_START_ALL_LINKING_ACK = FLD_START_ALL_LINKING.copy()
FLD_START_ALL_LINKING_ACK.append(MessageDataField('ack', 1, AckNak))

# Cancel All-Linking 0x65
FLD_CANCEL_ALL_LINKING = []
FLD_CANCEL_ALL_LINKING_ACK = [MessageDataField('ack', 1, AckNak)]

# Set Host Device Category 0x66
FLD_SET_HOST_DEV_CAT = [MessageDataField('cat', 1, DeviceCategory),
                       MessageDataField('subcat', 1, int),
                       MessageDataField('firmware', 1, int)]
FLD_SET_HOST_DEV_CAT_ACK = FLD_SET_HOST_DEV_CAT.copy()
FLD_SET_HOST_DEV_CAT_ACK.append(MessageDataField('ack', 1, AckNak))

# Reset the IM 0x67
FLD_RESET_IM = []
FLD_RESET_IM_ACK = [MessageDataField('ack', 1, AckNak)]

# Set INSTEON ACK/NAK Message Byte 0x68/0x70
FLD_SET_ACK_NAK_BYTE = [MessageDataField('cmd2', 1, int)]
FLD_SET_ACK_NAK_BYTE_ACK = FLD_SET_ACK_NAK_BYTE.copy()
FLD_SET_ACK_NAK_BYTE_ACK.append(MessageDataField('ack', 1, AckNak))

# Get First ALL-Link Record 0x69
FLD_GET_FIRST_ALL_LINK_RECORD = []
FLD_GET_FIRST_ALL_LINK_RECORD_ACK = [MessageDataField('ack', 1, AckNak)]

# Get Next ALL-Link Record 0x6A
FLD_GET_NEXT_ALL_LINK_RECORD = []
FLD_GET_NEXT_ALL_LINK_RECORD_ACK = [MessageDataField('ack', 1, AckNak)]

# Set IM Configuration 0x6B
FLD_SET_IM_CONFIG = [MessageDataField('flags', 1, IMConfigurationFlags)]
FLD_SET_IM_CONFIG_ACK = FLD_SET_IM_CONFIG.copy()
FLD_SET_IM_CONFIG_ACK.append(MessageDataField('ack', 1, AckNak))

# Get All-Link Record for Sender 0x6C
FLD_GET_ALL_LINK_REC_FOR_SENDER = []
FLD_GET_ALL_LINK_REC_FOR_SENDER_ACK = [MessageDataField('ack', 1, AckNak)]

# LED On/Off 0x6D / 0x6E
FLD_LED_ON_OFF = []
FLD_LED_ON_OFF_ACK = [MessageDataField('ack', 1, AckNak)]

# Manage All-Link Record 0x6F
FLD_MANAGE_ALL_LINK_RECORD = [MessageDataField('action', 1, ManageAlLinkRecordAction),
                              MessageDataField('flags', 1, AllLinkRecordFlags),
                              MessageDataField('group', 1, int),
                              MessageDataField('address', 3, Address),
                              MessageDataField("data1", 1, int),
                              MessageDataField("data2", 1, int),
                              MessageDataField("data3", 1, int)]
FLD_MANAGE_ALL_LINK_RECORD_ACK = FLD_MANAGE_ALL_LINK_RECORD.copy()
FLD_MANAGE_ALL_LINK_RECORD_ACK.append(MessageDataField('ack', 1, AckNak))

# Set INSTEON NAK Message Byte see 0x68
# Set INSTEON ACK Message Two Bytes 0x71
FLD_SET_ACK_TWO_BYTES = [MessageDataField('cmd1', 1, int),
                         MessageDataField('cmd2', 1, int)]
FLD_SET_ACK_TWO_BYTES_ACK = FLD_SET_ACK_TWO_BYTES.copy()
FLD_SET_ACK_TWO_BYTES_ACK.append(MessageDataField('ack', 1, AckNak))

# RF Sleep 0x72
FLD_RF_SLEEP = []
FLD_RF_SLEEP_ACK = [MessageDataField('ack', 1, AckNak)]

# Get IM Configuration 0x73
FLD_GET_IM_CONFIG = []
FLD_GET_IM_CONFIG_ACK = [MessageDataField('flags', 1, IMConfigurationFlags),
                         MessageDataField('spare1', 1, int),
                         MessageDataField('spare2', 1, int),
                         MessageDataField('ack', 1, AckNak)]

INBOUND_MESSAGE_DEFINITIONS = [
    MessageDefinition(MessageId.STANDARD_RECEIVED,
                      FLD_STD_REC),
    MessageDefinition(MessageId.EXTENDED_RECEIVED,
                      FLD_EXT_REC),
    MessageDefinition(MessageId.X10_RECEIVED,
                      FLD_X10_SEND_REC),
    MessageDefinition(MessageId.ALL_LINKING_COMPLETED,
                      FLD_ALL_LINK_COMPLETE),
    MessageDefinition(MessageId.BUTTON_EVENT_REPORT,
                      FLD_IM_BTN_EVENT_REPORT_REC),
    MessageDefinition(MessageId.USER_RESET_DETECTED,
                      FLD_USER_RESET_REC),
    MessageDefinition(MessageId.ALL_LINK_CEANUP_FAILURE_REPORT,
                      FLD_ALL_LINK_CLEANUP_FAILURE),
    MessageDefinition(MessageId.ALL_LINK_RECORD_RESPONSE,
                      FLD_ALL_LINK_RECORD_RESP),
    MessageDefinition(MessageId.ALL_LINK_CLEANUP_STATUS_REPORT,
                      FLD_All_LINK_CLEANUP_REPORT_ACK),
    MessageDefinition(MessageId.GET_IM_INFO,
                      FLD_GET_IM_INFO_REC),
    MessageDefinition(MessageId.SEND_ALL_LINK_COMMAND,
                      FLD_SEND_ALL_LINK_CMD_ACK),
    MessageDefinition(MessageId.SEND_STANDARD,
                      FLD_STD_SEND_ACK),
    MessageDefinition(MessageId.X10_SEND,
                      FLD_X10_SEND_REC_ACK),
    MessageDefinition(MessageId.START_ALL_LINKING,
                      FLD_START_ALL_LINKING_ACK),
    MessageDefinition(MessageId.CANCEL_ALL_LINKING,
                      FLD_CANCEL_ALL_LINKING_ACK),
    MessageDefinition(MessageId.SET_HOST_DEV_CAT,
                      FLD_SET_HOST_DEV_CAT_ACK),
    MessageDefinition(MessageId.RESET_IM,
                      FLD_RESET_IM_ACK),
    MessageDefinition(MessageId.SET_ACK_MESSAGE_BYTE,
                      FLD_SET_ACK_NAK_BYTE_ACK),
    MessageDefinition(MessageId.GET_FIRST_ALL_LINK_RECORD,
                      FLD_GET_FIRST_ALL_LINK_RECORD_ACK),
    MessageDefinition(MessageId.GET_NEXT_ALL_LINK_RECORD,
                      FLD_GET_NEXT_ALL_LINK_RECORD_ACK),
    MessageDefinition(MessageId.SET_IM_CONFIGURATION,
                      FLD_SET_IM_CONFIG_ACK),
    MessageDefinition(MessageId.GET_ALL_LINK_RECORD_FOR_SENDER,
                      FLD_GET_ALL_LINK_REC_FOR_SENDER_ACK),
    MessageDefinition(MessageId.LED_ON,
                      FLD_LED_ON_OFF_ACK),
    MessageDefinition(MessageId.LED_OFF,
                      FLD_LED_ON_OFF_ACK),
    MessageDefinition(MessageId.MANAGE_ALL_LINK_RECORD,
                      FLD_MANAGE_ALL_LINK_RECORD_ACK),
    MessageDefinition(MessageId.SET_NAK_MESSAGE_BYTE,
                      FLD_SET_ACK_NAK_BYTE_ACK),
    MessageDefinition(MessageId.SET_ACK_MESSAGE_TWO_BYTES,
                      FLD_SET_ACK_TWO_BYTES_ACK),
    MessageDefinition(MessageId.RF_SLEEP,
                      FLD_RF_SLEEP_ACK),
    MessageDefinition(MessageId.GET_IM_CONFIGURATION,
                      FLD_GET_IM_CONFIG_ACK)]

OUTBOUND_MESSAGE_DEFINITION = [
        MessageDefinition(MessageId.GET_IM_INFO,
                      FLD_GET_IM_INFO_SEND),
    MessageDefinition(MessageId.SEND_ALL_LINK_COMMAND,
                      FLD_SEND_ALL_LINK_CMD),
    MessageDefinition(MessageId.SEND_STANDARD,
                      FLD_STD_SEND),
    MessageDefinition(MessageId.X10_SEND,
                      FLD_X10_SEND_REC),
    MessageDefinition(MessageId.START_ALL_LINKING,
                      FLD_START_ALL_LINKING),
    MessageDefinition(MessageId.CANCEL_ALL_LINKING,
                      FLD_CANCEL_ALL_LINKING),
    MessageDefinition(MessageId.SET_HOST_DEV_CAT,
                      FLD_SET_HOST_DEV_CAT),
    MessageDefinition(MessageId.RESET_IM,
                      FLD_RESET_IM),
    MessageDefinition(MessageId.SET_ACK_MESSAGE_BYTE,
                      FLD_SET_ACK_NAK_BYTE),
    MessageDefinition(MessageId.GET_FIRST_ALL_LINK_RECORD,
                      FLD_GET_FIRST_ALL_LINK_RECORD),
    MessageDefinition(MessageId.GET_NEXT_ALL_LINK_RECORD,
                      FLD_GET_NEXT_ALL_LINK_RECORD),
    MessageDefinition(MessageId.SET_IM_CONFIGURATION,
                      FLD_SET_IM_CONFIG),
    MessageDefinition(MessageId.GET_ALL_LINK_RECORD_FOR_SENDER,
                      FLD_GET_ALL_LINK_REC_FOR_SENDER),
    MessageDefinition(MessageId.LED_ON,
                      FLD_LED_ON_OFF),
    MessageDefinition(MessageId.LED_OFF,
                      FLD_LED_ON_OFF),
    MessageDefinition(MessageId.MANAGE_ALL_LINK_RECORD,
                      FLD_MANAGE_ALL_LINK_RECORD),
    MessageDefinition(MessageId.SET_NAK_MESSAGE_BYTE,
                      FLD_SET_ACK_NAK_BYTE),
    MessageDefinition(MessageId.SET_ACK_MESSAGE_TWO_BYTES,
                      FLD_SET_ACK_TWO_BYTES),
    MessageDefinition(MessageId.RF_SLEEP,
                      FLD_RF_SLEEP),
    MessageDefinition(MessageId.GET_IM_CONFIGURATION,
                      FLD_GET_IM_CONFIG)]
