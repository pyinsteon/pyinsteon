"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_MODE_STATUS
from ...utils import build_topic, calc_thermostat_mode
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatModeHandler(InboundHandlerBase):
    """Heat set point command inbound."""

    def __init__(self, address):
        """Init the ThermostatModeHandler class."""
        self._address = Address(address)
        super().__init__(
            topic=THERMOSTAT_MODE_STATUS,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),  # Force address
            topic=THERMOSTAT_MODE_STATUS,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the mode response from a device."""
        sys_mode, fan_mode = calc_thermostat_mode(cmd2)
        self._call_subscribers(system_mode=sys_mode, fan_mode=fan_mode)
