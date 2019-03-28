"""Convert a standard or extended message to a topic."""
from ...constants import MessageFlagType, DeviceCategory
from ..messages.user_data import UserData
from ...address import Address

from ...topics import (
    POOL_DEVICE_ON,
    POOL_DEVICE_OFF,
    POOL_TEMPERATURE_UP,
    POOL_TEMPERATURE_DOWN,
    POOL_LOAD_INITIALIZATION_VALUES,
    POOL_LOAD_EEPROM_FROM_RAM,
    POOL_GET_POOL_MODE,
    POOL_GET_AMBIENT_TEMPERATURE,
    POOL_GET_WATER_TEMPERATURE,
    POOL_GET_PH,
    POOL_SET_DEVICE_TEMPERATURE,
    POOL_SET_DEVICE_HYSTERESIS,)
    