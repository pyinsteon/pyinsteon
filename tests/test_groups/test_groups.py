"""Test the functionality of group types."""
from unittest import TestCase

from pyinsteon.groups.fan import FanOnLevel
from pyinsteon.groups.on_level import OnLevel
from pyinsteon.groups.on_off import Heartbeat, LowBattery, OnOff
from pyinsteon.groups.open_close import NormallyClosed, NormallyOpen
from pyinsteon.groups.thermostat import Temperature
from pyinsteon.groups.wet_dry import Dry, Wet

from ..utils import random_address


class TestGroups(TestCase):
    """Test group types."""

    def test_is_dimmable(self):
        """Test if an `is_dimmable` property is set correctly."""

        group_values = {
            FanOnLevel: True,
            OnOff: False,
            OnLevel: True,
            LowBattery: False,
            Heartbeat: False,
            NormallyOpen: False,
            NormallyClosed: False,
            Temperature: True,
            Wet: False,
            Dry: False,
        }

        for group_type, is_dimmable in group_values.items():
            group = group_type(
                name="dummy", address=random_address(), group=1, default=None
            )
            assert group.is_dimmable == is_dimmable
