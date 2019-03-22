"""Convert a standard or extended message to a topic."""
from ...constants import MessageFlagType, DeviceCategory
from ..messages.user_data import UserData
from ...address import Address

from ...topics import (
    ASSIGN_TO_ALL_LINK_GROUP,
    DELETE_FROM_ALL_LINK_GROUP,
    PRODUCT_DATA_REQUEST,
    FX_USERNAME,
    DEVICE_TEXT_STRING_REQUEST,
    SET_DEVICE_TEXT_STRING,
    SET_ALL_LINK_COMMAND_ALIAS,
    SET_ALL_LINK,
    ENTER_LINKING_MODE,
    ENTER_UNLINKING_MODE,
    GET_INSTEON_ENGINE_VERSION,
    PING,
    ID_REQUEST,
    ID_REQUEST_RESPONSE,
    ON,
    ON_FAST,
    OFF,
    OFF_FAST,
    BRIGHTEN_ONE_STEP,
    DIM_ONE_STEP,
    START_MANUAL_CHANGE_DOWN,
    START_MANUAL_CHANGE_UP,
    STOP_MANUAL_CHANGE,
    STATUS_REQUEST,
    STATUS_REQUEST_ALTERNATE_1,
    STATUS_REQUEST_ALTERNATE_2,
    STATUS_REQUEST_ALTERNATE_3,
    GET_OPERATING_FLAGS,
    SET_OPERATING_FLAGS,
    INSTANT_CHANGE,
    MANUALLY_TURNED_OFF,
    MANUALLY_TURNED_ON,
    REMOTE_SET_BUTTON_TAP1_TAP,
    REMOTE_SET_BUTTON_TAP2_TAP,
    SET_STATUS,
    SET_ADDRESS_MSB,
    POKE_ONE_BYTE,
    PEEK_ONE_BYTE,
    PEEK_ONE_BYTE_INTERNAL,
    POKE_ONE_BYTE_INTERNAL,
    ON_AT_RAMP_RATE,
    EXTENDED_GET_SET,
    OFF_AT_RAMP_RATE,
    EXTENDED_READ_WRITE_ALDB,
    EXTENDED_TRIGGER_ALL_LINK,
    ASSIGN_TO_COMPANION_GROUP,

    FAN_STATUS_REPORT,
    LEAK_DETECTOR_ANNOUNCE,)


def assign_to_all_link_group(message_type: MessageFlagType, cmd2: int,
                             target: Address, user_data: UserData):
    """Map the ASSIGN_TO_ALL_LINK_GROUP command to a kwargs list."""
    kwargs = {}
    kwargs['cat'] = DeviceCategory(target.high)
    kwargs['subcat'] = target.middle
    kwargs['firmware'] = target.low


def on(message_type: MessageFlagType, cmd2: int, target: Address, user_data: UserData):
    """Map the ON command to a kwargs list."""
    kwargs = {}
    kwargs['on_level'] = cmd2
    if message_type == MessageFlagType.DIRECT_ACK:
        kwargs['group'] = 0 if not user_data else user_data['d1']
    elif message_type == MessageFlagType.ALL_LINK_BROADCAST:
        kwargs['group'] = bytes(target)[2]
    return kwargs
