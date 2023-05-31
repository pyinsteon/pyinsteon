"""Receive an All-Link record for an Insteon Modem."""

import logging

from . import inbound_handler
from ..address import Address
from ..constants import AllLinkMode
from ..data_types.all_link_record_flags import AllLinkRecordFlags
from ..topics import MODEM, READ_EEPROM_RESPONSE
from .inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReadEepromResponseHandler(InboundHandlerBase):
    """Receive a READ EEPROM response for an Insteon Modem."""

    arg_spec = {
        "mem_hi": "int - MSB of the memory address of the ALDB record.",
        "mem_lo": "int - LSB of the mMemory address of the ALDB record.",
        "in_use": "bool - Indicates if the ALDB record is in use.",
        "high_water_mark": "bool - Indicates if the ALDB record is the high water mark.",
        "controller": "bool - Indicates if the ALDB record is a controller record (True = controller, False = responder).",
        "group": "int - Group number of the ALDB record.",
        "target": "Address - Device address of the target device.",
        "data1": "int - Data field 1 of the ALDB record.",
        "data2": "int - Data field 2 of the ALDB record.",
        "data3": "int - Data field 3 of the ALDB record.",
        "bit5": "bool - Indicates if bit 5 of the control flag is set.",
        "bit4": "bool - Indicates if bit 4 of the control flag is set.",
    }

    def __init__(self):
        """Init the AllLinkRecordResponse class."""
        super().__init__(topic=READ_EEPROM_RESPONSE, address=MODEM)
        self._has_subscriber = False

    def subscribe(self, callback, force_strong_ref=False):
        """Subscribe listeners to the topic.

        We only want one modem to be subsribed to this method. The first one
        will always be the one we want subscribed so reject the others.
        """
        if self._has_subscriber:
            return
        self._has_subscriber = True
        super().subscribe(callback, force_strong_ref=force_strong_ref)

    @inbound_handler
    def receive_record(
        self,
        mem_hi: int,
        mem_low: int,
        flags: AllLinkRecordFlags,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
    ):
        """Recieve an all link record."""
        controller = flags.link_mode == AllLinkMode.CONTROLLER
        mem_addr = (mem_hi << 8) + mem_low + 7
        self._call_subscribers(
            mem_addr=mem_addr,
            in_use=flags.is_in_use,
            high_water_mark=flags.is_hwm,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            bit5=flags.is_bit_5_set,
            bit4=flags.is_bit_4_set,
        )
