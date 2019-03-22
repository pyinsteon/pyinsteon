"""Convert a standard or extended message to a topic."""
from ...constants import MessageFlagType, DeviceCategory
from ..messages.user_data import UserData
from ...address import Address

from ...topics import (
    DOOR_MOVE_RAISE_DOOR,
    DOOR_MOVE_LOWER_DOOR,
    DOOR_MOVE_OPEN_DOOR,
    DOOR_MOVE_CLOSE_DOOR,
    DOOR_MOVE_STOP_DOOR,
    DOOR_MOVE_SINGLE_DOOR_OPEN,
    DOOR_MOVE_SINGLE_DOOR_CLOSE,
    DOOR_STATUS_REPORT_RAISE_DOOR,
    DOOR_STATUS_REPORT_LOWER_DOOR,
    DOOR_STATUS_REPORT_OPEN_DOOR,
    DOOR_STATUS_REPORT_CLOSE_DOOR,
    DOOR_STATUS_REPORT_STOP_DOOR,
    DOOR_STATUS_REPORT_SINGLE_DOOR_OPEN,
    DOOR_STATUS_REPORT_SINGLE_DOOR_CLOSE,)
