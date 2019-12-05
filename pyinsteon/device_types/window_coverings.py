"""Window Covering devices."""

from .open_close_responder_base import OpenCloseResponderBase
from ..states import COVER


class WindowCovering(OpenCloseResponderBase):
    """Window Covering device."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
    ):
        """Init the WindowCovering class."""
        buttons = {1: COVER}
        super().__init__(address, cat, subcat, firmware, description, model, buttons)

    def _register_operating_flags(self):
        """Register the operating and properties."""
        from ..extended_property import (
            ON_LEVEL,
            RAMP_RATE,
            LED_BRIGHTNESS,
            X10_HOUSE,
            X10_UNIT,
            DURATION_HIGH,
            DURATION_LOW,
        )
        from ..operating_flag import (
            PROGRAM_LOCK_ON,
            LED_BLINK_ON_TX_ON,
            RESUME_DIM_ON,
            LED_ON,
            KEY_BEEP_ON,
            RF_DISABLE_ON,
            INSTEON_OFF,
            TEND_ON,
            X10_OFF,
            LED_BLINK_ON_ERROR_OFF,
            CLEANUP_REPORT_OFF,
            CHECKSUM_OFF,
            STANDARD_HOLDOFF,
            DUAL_LINE_ON,
            MOMENTARY_LINE_ON,
            NOT_3_WAY,
            SMART_HOPS_ON,
            FORWARD_ON,
        )

        super()._register_operating_flags()
        self._remove_operating_flag("bit0", 0)  # 01
        self._remove_operating_flag("bit1", 0)  # 02
        self._remove_operating_flag("bit4", 0)  # 02
        self._remove_operating_flag("bit5", 0)  # 10

        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 0x0a, 0x0b)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0c, 0x0d)

        self._add_operating_flag(LED_BLINK_ON_ERROR_OFF, 2, 3, 0x15, 0x16)

        self._add_operating_flag(DUAL_LINE_ON, 3, 0, 0x1e, 0x1f)
        self._add_operating_flag(MOMENTARY_LINE_ON, 3, 1, 0x20, 0x21)
        self._add_operating_flag(NOT_3_WAY, 3, 3, 0x22, 0x23)
        self._add_operating_flag(FORWARD_ON, 3, 4, 0x24, 0x25)

        self._add_property(X10_HOUSE, 5, None)  # 4
        self._add_property(X10_UNIT, 6, None)  # 4
        self._add_property(RAMP_RATE, 7, 5)

        # Need to verify use_data position
        self._add_property(ON_LEVEL, 8, 6)
        self._add_property(DURATION_HIGH, 9, None)  # 0x10
        self._add_property(DURATION_LOW, 10, None)  # 0x10