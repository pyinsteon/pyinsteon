"""Modem command to get next ALDB record."""
# pylint: disable=no-self-use
import logging

from . import ack_handler, nak_handler
from ..address import Address
from ..constants import ResponseStatus
from ..data_types.all_link_record_flags import AllLinkRecordFlags
from ..topics import WRITE_EEPROM
from .outbound_base import OutboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class WriteEepromHandler(OutboundHandlerBase):
    """Handle Write EEPROM commands."""

    def __init__(self):
        """Init the ReadEepromHandler class."""
        super().__init__(topic=WRITE_EEPROM)
        _LOGGER.debug("Setup WriteEepromHandler")

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        mem_addr: int,
        in_use: bool,
        high_water_mark: bool,
        controller: bool,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
        bit5: bool,
        bit4: bool,
    ):
        """Send the Write to EEPROM message."""
        mem_array = mem_addr.to_bytes(2, "big")
        flags = AllLinkRecordFlags.create(
            in_use=in_use,
            controller=controller,
            hwm=high_water_mark,
            bit5=bit5,
            bit4=bit4,
        )
        return await super().async_send(
            mem_hi=mem_array[0],
            mem_low=mem_array[1] - 7,
            flags=flags,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

    @ack_handler
    async def async_handle_ack(
        self,
        mem_addr: int,
        flags: AllLinkRecordFlags,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
    ):
        """Send the Read from EEPROM message."""
        await self._async_handle_ack()

    @nak_handler
    async def async_handle_nak(
        self,
        mem_addr: int,
        flags: int,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
    ):
        """Receive the NAK message and return False."""
        await self._message_response.put(ResponseStatus.FAILURE)
