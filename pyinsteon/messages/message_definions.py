"""Message definitions."""

from collections import namedtuple

from ..address import Address
from ..constants import MessageCode
from .message_flags import MessageFlags
from .user_data import UserData


MessageDataField = namedtuple("MessageDataField", "name length type")


MessageDefinition = namedtuple("MessageDefinition", "type fields")


FLD_STD_REC = [MessageDataField("address", 3, Address),
               MessageDataField("target", 3, Address),
               MessageDataField("flags", 1, MessageFlags),
               MessageDataField("cmd1", 1, int),
               MessageDataField("cmd2", 1, int)]

FLD_EXT_REC = FLD_STD_REC.copy()
FLD_EXT_REC.append(MessageDataField('userdata', 14, UserData))


INBOUND_MESSAGE_DEFINITIONS = [
    MessageDefinition(MessageCode.STANDARD_RECEIVED, FLD_STD_REC)]
