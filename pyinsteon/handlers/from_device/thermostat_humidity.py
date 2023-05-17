"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_HUMIDITY_STATUS
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatHumidityHandler(InboundHandlerBase):
    """Heat set point command inbound."""

    arg_spec = {"humidity": "int - Thermostat current humidity reading."}

    def __init__(self, address):
        """Init the ThermostatSetPointResponseHandler class."""
        super().__init__(
            topic=THERMOSTAT_HUMIDITY_STATUS,
            address=address,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Humidity set point response from a device."""
        self._call_subscribers(humidity=cmd2)
