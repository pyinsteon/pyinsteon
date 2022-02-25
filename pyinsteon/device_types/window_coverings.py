"""Window Covering devices."""
from ..config import (
    DUAL_LINE_ON,
    DURATION_HIGH,
    DURATION_LOW,
    FORWARD_ON,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_OFF,
    LED_BLINK_ON_TX_ON,
    LED_OFF,
    MOMENTARY_LINE_ON,
    NOT_3_WAY,
    ON_LEVEL,
    PROGRAM_LOCK_ON,
    RAMP_RATE,
    RAMP_RATE_IN_SEC,
    X10_HOUSE,
    X10_UNIT,
)
from ..config.ramp_rate import RampRateProperty
from ..constants import PropertyType
from ..groups import COVER
from .open_close_responder_base import OpenCloseResponderBase


class WindowCovering(OpenCloseResponderBase):
    """Window Covering device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the WindowCovering class."""
        super().__init__(
            address, cat, subcat, firmware, description, model, state_name=COVER
        )

    def _register_op_flags_and_props(self):
        """Register the operating and properties."""
        super()._register_op_flags_and_props()

        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_OFF, 0, 4, 0x0A, 0x0B)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0C, 0x0D)

        self._add_operating_flag(LED_BLINK_ON_ERROR_OFF, 2, 3, 0x15, 0x16)

        self._add_operating_flag(DUAL_LINE_ON, 3, 0, 0x1E, 0x1F)
        self._add_operating_flag(MOMENTARY_LINE_ON, 3, 1, 0x20, 0x21)
        self._add_operating_flag(NOT_3_WAY, 3, 3, 0x22, 0x23)
        self._add_operating_flag(FORWARD_ON, 3, 4, 0x24, 0x25)

        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)  # 4
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)  # 4
        self._add_property(RAMP_RATE, 7, 5, prop_type=PropertyType.ADVANCED)

        # Need to verify use_data position
        self._add_property(ON_LEVEL, 8, 6)
        self._add_property(DURATION_HIGH, 9, None)  # 0x10
        self._add_property(DURATION_LOW, 10, None)  # 0x10

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )
