"""Convert a standard or extended message to a topic."""
from ...constants import MessageFlagType, DeviceCategory
from ..messages.user_data import UserData
from ...address import Address

from ...topics import (
    WINDOW_COVERING_OPEN,
    WINDOW_COVERING_CLOSE,
    WINDOW_COVERING_STOP,
    WINDOW_COVERING_PROGRAM,
    WINDOW_COVERING_POSITION,)
