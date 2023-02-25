"""Energy Management Control devices (CATEGORY 0x09)."""

from ..config import LOAD_SENSE_ON, PROGRAM_LOCK_ON
from ..groups import LOAD_SENSOR, ON_OFF_SWITCH
from ..handlers.to_device.status_request import StatusRequestCommand
from ..utils import multiple_status
from .device_commands import STATUS_COMMAND_LOAD
from .on_off_responder_base import OnOffResponderBase


class EnergyManagement_LoadController(OnOffResponderBase):
    """Load Controller device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the EnergyManagement_LoadController class."""
        responders = {1: ON_OFF_SWITCH}
        controllers = {2: LOAD_SENSOR}
        super().__init__(
            address,
            cat,
            subcat,
            firmware,
            description,
            model,
            responders=responders,
            controllers=controllers,
        )

    async def async_status(self, group=None):
        """Request the status of the device."""
        result1 = result2 = None
        if group in [0, 1, None]:
            result1 = await super().async_status()
        if group in [2, None]:
            result2 = await self._handlers[STATUS_COMMAND_LOAD].async_send()
        return multiple_status(result1, result2)

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LOAD_SENSE_ON, 0, 5, 6, 7)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND_LOAD] = StatusRequestCommand(
            self._address, status_type=1
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND_LOAD].subscribe(self._sensor_status)

    def _sensor_status(self, db_version, status):
        """Set the sensor status value."""
        self._groups[2].set_value(status)
