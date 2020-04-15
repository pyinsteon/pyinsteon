"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_SET_POINT_RESPONSE
from ...utils import build_topic
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatSetPointResponseHandler(InboundHandlerBase):
    """Humidity set point command inbound."""

    def __init__(self, address):
        """Init the ThermostatSetPointResponseHandler class."""
        self._address = Address(address)
        super().__init__(
            topic=THERMOSTAT_SET_POINT_RESPONSE,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),  # Force address
            topic=THERMOSTAT_SET_POINT_RESPONSE,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Humidity set point response from a device."""
        stage_1_on_minutes = user_data["d3"]
        humidity_high = user_data["d4"]
        humidity_low = user_data["d5"]
        firmwire = user_data["d6"]
        cool_set_point = user_data["d7"]
        heat_set_point = user_data["d8"]
        rf_offset = user_data["d9"]
        self._call_subscribers(
            stage_1_on_minutes=stage_1_on_minutes,
            humidity_high=humidity_high,
            humidity_low=humidity_low,
            firmwire=firmwire,
            cool_set_point=cool_set_point,
            heat_set_point=heat_set_point,
            rf_offset=rf_offset,
        )
