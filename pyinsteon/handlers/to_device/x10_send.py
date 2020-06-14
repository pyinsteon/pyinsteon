"""Send an X10 command."""

from .. import ack_handler, nak_handler
from ...constants import ResponseStatus, X10Commands, X10CommandType
from ...topics import X10_SEND
from ...x10_address import X10Address
from ..outbound_base import OutboundHandlerBase


class X10CommandSend(OutboundHandlerBase):
    """Send an X10 command."""

    def __init__(self, address, x10_cmd: X10Commands):
        """Send an X10 command."""
        super().__init__(topic=X10_SEND)
        self._address = X10Address(address)
        self._cmd = x10_cmd

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the command."""
        if self._cmd in [
            X10Commands.ALL_LIGHTS_OFF,
            X10Commands.ALL_LIGHTS_ON,
            X10Commands.ALL_UNITS_OFF,
        ]:
            cmd_int = int(self._cmd)
            raw_x10 = (self._address.housecode_byte << 4) + cmd_int
            return await super().async_send(
                raw_x10=raw_x10, x10_flag=X10CommandType.COMMAND
            )

        raw_x10 = bytes(self._address)
        uc_result = await super().async_send(
            raw_x10=raw_x10, x10_flag=X10CommandType.UNITCODE
        )

        if uc_result != ResponseStatus.SUCCESS:
            return uc_result

        cmd_int = int(self._cmd)
        raw_x10 = (self._address.housecode_byte << 4) + cmd_int
        return await super().async_send(
            raw_x10=raw_x10, x10_flag=X10CommandType.COMMAND
        )

    @ack_handler(wait_response=False)
    def handle_ack(self, raw_x10, x10_flag):
        """Handle the X10 message ACK."""

    @nak_handler
    def handle_nak(self, raw_x10, x10_flag):
        """Handle the X10 message NAK.

        If the message NAKs it is likely the modem does not support X10 messages.
        The device will try to send the X10 message 3 times to ensure it is not a
        modem ready issue.

        This handler ensures the modem does not try to resend the message constantly.

        """
