"""Message definitions."""

from collections import namedtuple

from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from ..constants import MessageId, ImButtonEvents, AllLinkMode, DeviceCategory
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

# X10 Received 0x52
FLD_X10_REC = [MessageDataField("rawx10", 1, int),
               MessageDataField("x10flag", 1, int)]

# ALL-Linking Completed 0x53
FLD_ALL_LINK_COMPLETE = [MessageDataField("mode", 1, AllLinkMode),
                         MessageDataField("group", 1, int),
                         MessageDataField("target", 3, Address),
                         MessageDataField("dev_cat", 1, DeviceCategory),
                         MessageDataField("dev_subcat", 1, int),
                         MessageDataField("firmware", 1, int)]

# IM Button Event Report 0x54
FLD_IM_BTN_EVENT_REPORT_REC = [MessageDataField("event", 1, ImButtonEvents)]

# IM User Reset Detected 0x55
FLD_IM_RESET_REC = []

# ALL-Link Cleanup Failure Report 0x56
FLD_ALL_LINK_CLEANUP_FAILURE = [MessageDataField("group", 1, int),
                                MessageDataField("address", 3, Address)]

# ALL-Link Record Response 0x57
FLD_ALL_LINK_RECORD_RESP = [MessageDataField("flags", 1, AllLinkRecordFlags),
                            MessageDataField("group", 1, int),
                            MessageDataField("address", 3, Address),
                            MessageDataField("data1", 1, int),
                            MessageDataField("data2", 1, int),
                            MessageDataField("data3", 1, int)]

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

INBOUND_MESSAGE_DEFINITIONS = [
    MessageDefinition(MessageId.STANDARD_RECEIVED, FLD_STD_REC),
    MessageDefinition(MessageId.EXTENDED_RECEIVED, FLD_EXT_REC),
    MessageDefinition(MessageId.SEND_STANDARD, FLD_STD_SEND_ACK)]
