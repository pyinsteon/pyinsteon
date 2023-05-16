"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...constants import MessageFlagType
from ...topics import EXTENDED_GET_RESPONSE
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedGetResponseHandler(InboundHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, cmd2=0x00, data1=None, data2=0x01, data3=None):
        """Init the OffInbound class."""
        super().__init__(
            topic=EXTENDED_GET_RESPONSE,
            address=address,
            message_type=MessageFlagType.DIRECT,
        )
        self._cmd2 = cmd2
        self._data1 = data1
        self._data2 = data2
        self._data3 = data3

        topic = f"handler.{self._address.id}.{EXTENDED_GET_RESPONSE}"
        for group in (cmd2, data1, data2, data3):
            if group is None:
                topic = f"{topic}.x"
            else:
                topic = f"{topic}.{group}"
        self._subscriber_topic = topic

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Extended Get response from a device."""
        # pylint: disable=too-many-boolean-expressions
        if (
            cmd2 == self._cmd2
            and (self._data1 is None or user_data["d1"] == self._data1)
            and (self._data2 is None or user_data["d2"] == self._data2)
            and (self._data3 is None or user_data["d3"] == self._data3)
        ):
            data = {}
            for item in range(2, 15):
                data[f"data{item}"] = user_data[f"d{item}"]
            self._call_subscribers(group=user_data["d1"], data=data)
