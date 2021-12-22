"""Handle sending a read request for ALDB records."""
import logging

from pyinsteon.constants import ResponseStatus

from ...address import Address
from ...topics import EXTENDED_GET_SET
from .. import ack_handler
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedSetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address, data1=None, data2=None):
        """Init the ReadALDBCommandHandler."""
        if data2 in [0, 1]:
            _LOGGER.error("Extended Set sent with bad action number: %d", data1)
            raise (ValueError("Error creating extended set command"))
        super().__init__(topic=EXTENDED_GET_SET, address=address, group=0)
        self._data1 = data1
        self._data2 = data2

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        data3=0,
        data4=0,
        data5=0,
        data6=0,
        data7=0,
        data8=0,
        data9=0,
        data10=0,
        data11=0,
        data12=0,
        data13=0,
        data14=0,
        priority=5,
    ):
        """Send Get Operating Flags message asyncronously."""
        kwargs = {"data1": self._data1, "data2": self._data2}
        loc = locals()
        for item in range(3, 15):
            try:
                data = int(loc["data{}".format(item)])
            except ValueError:
                _LOGGER.error("Property value must be an integer: %s", str(item))
            else:
                kwargs["data{}".format(item)] = data
        return await super().async_send(priority=5, **kwargs)

    @ack_handler
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK."""
        if user_data["d1"] == self._data1 and user_data["d2"] == self._data2:
            self._message_response.put_nowait(ResponseStatus.SUCCESS)
