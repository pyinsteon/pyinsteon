"""Handle sending a read request for ALDB records."""
import logging

from .. import inbound_handler
from ...address import Address
from ...protocol.messages.user_data import UserData
from ...topics import EXTENDED_READ_WRITE_ALDB
from ...utils import build_topic
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


def _create_aldb_record_from_userdata(userdata: UserData):
    """Create ALDB Record from the userdata dictionary."""


class ReceiveALDBRecordHandler(InboundHandlerBase):
    """Receive an ALDB record direct inbound message."""

    def __init__(self, address: Address):
        """Init the ReceiveALDBRecordHandler class."""
        self._address = Address(address)
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=self._address)
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),
            topic="aldb_record_received",
            message_type="direct",
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the inbound message."""
        _LOGGER.debug("ALDB Read direct message received")
        if user_data is not None and user_data.get("d2") == 0x01:
            memhi = user_data.get("d3")
            memlo = user_data.get("d4")
            memory = memhi << 8 | memlo
            control_flags = user_data.get("d6")
            if isinstance(control_flags, bytes):
                control_flags = int.from_bytes(control_flags, "big")
            in_use = bool(control_flags & 1 << 7)
            controller = bool(control_flags & 1 << 6)
            bit5 = bool(control_flags & 1 << 5)
            bit4 = bool(control_flags & 1 << 4)
            high_water_mark = not bool(control_flags & 1 << 1)
            group = user_data.get("d7")
            addrhi = user_data.get("d8")
            addrmed = user_data.get("d9")
            addrlo = user_data.get("d10")
            target = Address(bytearray([addrhi, addrmed, addrlo]))
            data1 = user_data.get("d11")
            data2 = user_data.get("d12")
            data3 = user_data.get("d13")
            self._call_subscribers(
                memory=memory,
                controller=controller,
                group=group,
                target=target,
                data1=data1,
                data2=data2,
                data3=data3,
                in_use=in_use,
                high_water_mark=high_water_mark,
                bit5=bit5,
                bit4=bit4,
            )
