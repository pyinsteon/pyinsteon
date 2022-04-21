"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...constants import AllLinkMode
from ...data_types.all_link_record_flags import AllLinkRecordFlags
from ...topics import ALDB_RECORD_RECEIVED, EXTENDED_READ_WRITE_ALDB
from ...utils import build_topic
from .. import inbound_handler
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReceiveALDBRecordHandler(InboundHandlerBase):
    """Receive an ALDB record direct inbound message."""

    def __init__(self, address: Address):
        """Init the ReceiveALDBRecordHandler class."""
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=address)
        self._subscriber_topic = build_topic(
            prefix="handler",
            address=self._address,
            topic=ALDB_RECORD_RECEIVED,
            message_type="direct",
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the inbound message."""
        _LOGGER.debug("ALDB Read direct message received")
        if user_data is not None and user_data["d2"] == 0x01:
            memhi = user_data["d3"]
            memlo = user_data["d4"]
            memory = memhi << 8 | memlo

            control_flags = AllLinkRecordFlags(user_data["d6"])

            group = user_data["d7"]

            addrhi = user_data["d8"]
            addrmed = user_data["d9"]
            addrlo = user_data["d10"]
            target = Address(bytearray([addrhi, addrmed, addrlo]))

            data1 = user_data["d11"]
            data2 = user_data["d12"]
            data3 = user_data["d13"]

            self._call_subscribers(
                memory=memory,
                controller=control_flags.link_mode == AllLinkMode.CONTROLLER,
                group=group,
                target=target,
                data1=data1,
                data2=data2,
                data3=data3,
                in_use=control_flags.is_in_use,
                high_water_mark=control_flags.is_hwm,
                bit5=control_flags.is_bit_5_set,
                bit4=control_flags.is_bit_4_set,
            )
