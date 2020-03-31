"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_MODE_STATUS
from ...constants import ThermostatMode
from ...utils import build_topic
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
    def handle_response(self, cmd1, cmd2, target, user_data):
        """Handle the mode response from a device."""
        mode = None
        if cmd2 == 0x00:
            mode = ThermostatMode.OFF
        elif cmd2 == 0x01:
            mode = ThermostatMode.HEAT
        elif cmd2 == 0x02:
            mode = ThermostatMode.COOL
        elif cmd2 == 0x03:
            mode = ThermostatMode.AUTO
        elif cmd2 == 0x04:
            mode = ThermostatMode.OFF
        elif cmd2 == 0x08:
            mode = ThermostatMode.FAN_ALWAYS_ON
        if mode is not None:
            self._call_subscribers(mode=mode)
