"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_TEMPERATURE_STATUS
from ...utils import build_topic
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatTemperatureHandler(InboundHandlerBase):
    """Heat set point command inbound."""

    def __init__(self, address):
        """Init the ThermostatTemperatureHandler class."""
        self._address = Address(address)
        super().__init__(
            topic=THERMOSTAT_TEMPERATURE_STATUS,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),  # Force address
            topic=THERMOSTAT_TEMPERATURE_STATUS,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Temperature response from a device."""
        self._call_subscribers(degrees=int(round(cmd2 / 2, 0)))
