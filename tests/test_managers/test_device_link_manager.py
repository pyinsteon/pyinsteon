"""Test the device_link_manager class."""
import unittest

from pyinsteon.address import Address
from pyinsteon.managers.device_link_manager import DeviceLinkManager
from pyinsteon.topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
    DEVICE_LINK_CONTROLLER_REMOVED,
)
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics
