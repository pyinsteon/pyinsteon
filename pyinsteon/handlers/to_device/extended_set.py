"""Handle sending a read request for ALDB records."""
import logging

from .. import direct_ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)

class ExtendedSetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(address, EXTENDED_GET_SET)

    #pylint: disable=arguments-differ
    async def async_send(self, group, action, data3=0, data4=0, data5=0,
                         data6=0, data7=0, data8=0, data9=0, data10=0,
                         data11=0, data12=0, data13=0, data14=0):
        """Send Get Operating Flags message asyncronously."""
        if action in [0, 1]:
            _LOGGER.debug('Extended Set sent with bad action number: %d', group)
            return 0
        kwargs = {'data1': group,
                  'data2': action}
        loc = locals()
        for item in range(3, 15):
            try:
                data = int(loc['data{}'.format(item)])
            except ValueError:
                _LOGGER.error('Property value must be an integer')
            else:
                kwargs['data{}'.format(item)] = data
        return await super().async_send(**kwargs)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        from collections import OrderedDict
        if not user_data or not user_data['d2'] == 0x01:
            return
        data = OrderedDict()
        for i in range(1, 15):
            data['data{}'.format(i)] = user_data['d{}'.format(i)]
        self._call_subscribers(data=data)
