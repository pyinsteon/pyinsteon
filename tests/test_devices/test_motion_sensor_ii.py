"""Test the motion sensor II device."""
from unittest import TestCase

from pyinsteon.device_types.security_health_safety import (
    SecurityHealthSafety_MotionSensorII,
)

from ..utils import random_address


class TestMotionSensorII(TestCase):
    """Test the Motion Sensor II device."""

    def test_create_device(self):
        """Test creating the motion sensor II device."""
        address = random_address()
        device = SecurityHealthSafety_MotionSensorII(
            address, 0x10, 0x16, 0x00, "Motion sensor II", "Model"
        )
        print(device.description)
