"""Test the All-Link Record Flags."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode
from pyinsteon.data_types.all_link_record_flags import AllLinkRecordFlags
from tests import set_log_levels


class TestAllLinkRecordFlags(unittest.TestCase):
    """Test the All-Link Record Flags."""

    def setUp(self):
        """Set up the TestAllLinkRecordFlags."""
        self.hex_data_00 = "00"  # Not in use, responder, HWM
        self.hex_data_80 = "80"  # In use, responder, HWM
        self.hex_data_40 = "40"  # Not in use, controller, not HWM
        self.hex_data_02 = "02"  # Not in use, responder, not HWM
        self.hex_data_3D = "3D"  # Not in use, responder HWM, bits 5,4,3,2,0
        self.hex_data_C2 = "C2"  # In Use, controller, not HWM
        self.hex_data_FF = "FF"  # In use, controller, not HWM, bits 5,4,3,2,0

        self.flags_00 = AllLinkRecordFlags(unhexlify(self.hex_data_00))
        self.flags_80 = AllLinkRecordFlags(unhexlify(self.hex_data_80))
        self.flags_40 = AllLinkRecordFlags(unhexlify(self.hex_data_40))
        self.flags_02 = AllLinkRecordFlags(unhexlify(self.hex_data_02))
        self.flags_3D = AllLinkRecordFlags(unhexlify(self.hex_data_3D))
        self.flags_C2 = AllLinkRecordFlags(unhexlify(self.hex_data_C2))
        self.flags_FF = AllLinkRecordFlags(unhexlify(self.hex_data_FF))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_flags_00(self):
        """Test 0x00 flag."""
        self._check_flags(
            self.flags_00,
            False,
            AllLinkMode.RESPONDER,
            False,
            False,
            False,
            False,
            True,
            False,
            "00",
        )

    def test_flags_80(self):
        """Test 0x80 flag."""
        self._check_flags(
            self.flags_80,
            True,
            AllLinkMode.RESPONDER,
            False,
            False,
            False,
            False,
            True,
            False,
            "80",
        )

    def test_flags_40(self):
        """Test 0x40 flag."""
        self._check_flags(
            self.flags_40,
            False,
            AllLinkMode.CONTROLLER,
            False,
            False,
            False,
            False,
            True,
            False,
            "40",
        )

    def test_flags_02(self):
        """Test 0x02 flag."""
        self._check_flags(
            self.flags_02,
            False,
            AllLinkMode.RESPONDER,
            False,
            False,
            False,
            False,
            False,
            False,
            "02",
        )

    def test_flags_3D(self):
        """Test 0x3D flag."""
        self._check_flags(
            self.flags_3D,
            False,
            AllLinkMode.RESPONDER,
            True,
            True,
            True,
            True,
            True,
            True,
            "3D",
        )

    def test_flags_C2(self):
        """Test 0xC2 flag."""
        self._check_flags(
            self.flags_C2,
            True,
            AllLinkMode.CONTROLLER,
            False,
            False,
            False,
            False,
            False,
            False,
            "C2",
        )

    def test_flags_FF(self):
        """Test 0xFF flag."""
        self._check_flags(
            self.flags_FF,
            True,
            AllLinkMode.CONTROLLER,
            True,
            True,
            True,
            True,
            False,
            True,
            "FF",
        )

    def _check_flags(
        self, flags, in_use, link_mode, bit5, bit4, bit3, bit2, hwm, bit0, hex
    ):
        self._check_flags_in_use(flags, in_use)
        self._check_flags_mode(flags, link_mode)
        self._check_flags_bit_5(flags, bit5)
        self._check_flags_bit_3(flags, bit3)
        self._check_flags_bit_2(flags, bit2)
        self._check_flags_hwm(flags, hwm)
        self._check_flags_bit_0(flags, bit0)
        self._check_bytes(flags, unhexlify(hex))

    def _check_flags_in_use(self, flags, in_use):
        assert flags.is_in_use == in_use

    def _check_flags_mode(self, flags, link_mode):
        assert flags.link_mode == link_mode

    def _check_flags_hwm(self, flags, is_hwm):
        assert flags.is_hwm == is_hwm

    def _check_flags_bit_5(self, flags, is_bit_5_set):
        assert flags.is_bit_5_set == is_bit_5_set

    def _check_flags_bit_4(self, flags, is_bit_4_set):
        assert flags.is_bit_4_set == is_bit_4_set

    def _check_flags_bit_3(self, flags, is_bit_3_set):
        assert flags.is_bit_3_set == is_bit_3_set

    def _check_flags_bit_2(self, flags, is_bit_2_set):
        assert flags.is_bit_2_set == is_bit_2_set

    def _check_flags_bit_0(self, flags, is_bit_0_set):
        assert flags.is_bit_0_set == is_bit_0_set

    def _check_bytes(self, flags, val):
        assert bytes(flags) == val


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
