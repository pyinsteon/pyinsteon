"""Receive an X10 message."""

from ... import pub
from ...constants import X10Commands, X10CommandType
from ...topics import X10_RECEIVED
from ...utils import byte_to_command, byte_to_unitcode, parse_x10
from ...x10_address import create
from .. import inbound_handler
from ..inbound_base import InboundHandlerBase


class X10Received(InboundHandlerBase):
    """Receive an X10 message."""

    def __init__(self):
        """Init the X10Received class."""
        super().__init__(topic=X10_RECEIVED)
        self._last_housecode = None
        self._last_unitcode = None

    @inbound_handler
    def handle_x10_received(self, raw_x10, x10_flag):
        """Manage X10 inbound messages."""
        housecode, uc_or_cmd = parse_x10(raw_x10)
        if x10_flag == X10CommandType.COMMAND:
            self._notify_subscribers(housecode, uc_or_cmd)
        else:
            self._last_housecode = housecode
            self._last_unitcode = byte_to_unitcode(uc_or_cmd)

    def _notify_subscribers(self, housecode, uc_or_cmd):
        """Notify subscribes that a command was received."""
        cmd = byte_to_command(uc_or_cmd)
        topic = ""
        if cmd in [
            X10Commands.ALL_LIGHTS_OFF,
            X10Commands.ALL_LIGHTS_ON,
            X10Commands.ALL_UNITS_OFF,
        ]:
            topic = f"x10{housecode.lower()}.{str(cmd).lower()}"
        if self._last_housecode == housecode and self._last_unitcode is not None:
            address = create(housecode, self._last_unitcode)
            topic = f"{address.id}.{str(cmd).lower()}"
        if topic:
            pub.sendMessage(topic)
            self._last_housecode = None
            self._last_unitcode = None
