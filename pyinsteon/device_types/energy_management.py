"""Energy Management Control devices (CATEGORY 0x09)."""

from ..config import LOAD_SENSE_ON, PROGRAM_LOCK_ON
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..groups import LOAD_SENSOR, ON_OFF_SWITCH
from .device_commands import STATUS_COMMAND
from .on_off_responder_base import OnOffResponderBase


class EnergyManagement_LoadController(OnOffResponderBase):
    """Load Controller device."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
        state_name=ON_OFF_SWITCH,
        on_event_name=ON_EVENT,
        off_event_name=OFF_EVENT,
        on_fast_event_name=ON_FAST_EVENT,
        off_fast_event_name=OFF_FAST_EVENT,
    ):
        """Init the EnergyManagement_LoadController class."""
        buttons = (
            {1: (ON_OFF_SWITCH, 0), 2: (LOAD_SENSOR, 1)} if buttons is None else buttons
        )
        super().__init__(
            address,
            cat,
            subcat,
            firmware,
            description,
            model,
            buttons,
            on_event_name,
            off_event_name,
            on_fast_event_name,
            off_fast_event_name,
        )

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LOAD_SENSE_ON, 0, 5, 6, 7)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].add_status_type(1, self._sensor_status)

    def _sensor_status(self, db_version, status):
        """Set the sensor status value."""
        self._groups[2].set_value(status)
