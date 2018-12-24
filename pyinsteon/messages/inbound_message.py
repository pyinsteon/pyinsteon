"""Insteon message data structure defintion."""
import binascii
import logging


_LOGGER = logging.getLogger(__name__)


class InboundMessage():
    """Insteon inbound message data definition."""

    def __init__(self, fields, data):
        """Init the InboundMessage class."""
        self._fields = fields
        _slices = self._create_slices(fields)
        self.start_code = data[_slices[0]]
        self.id = data[_slices[1]]
        self._len = 2
        curr_slice = 2
        for field in fields:
            val = field.type(data[_slices[curr_slice]])
            _LOGGER.debug('slice: %s', _slices[curr_slice])
            _LOGGER.debug('Field %s value %s', field.name, val)
            setattr(self, field.name, val)
            self._len += field.length
            curr_slice += 1

    def __len__(self):
        return self._len

    def _create_slices(self, fields):
        slices = []
        slices.append(slice(0, 1))
        slices.append(slice(1, 2))
        start = 2
        for field in fields:
            stop = start + field.length
            if field.length > 1:
                slices.append(slice(start, stop))
            else:
                slices.append(start)
            start = stop
        return slices

    @property
    def bytes(self):
        """Emit the message bytes."""
        from ..utils import vars_to_bytes
        data = []
        data.append(self.start_code)
        data.append(self.id)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return vars_to_bytes(data)

    @property
    def hex(self):
        """Emit the message in hex."""
        return binascii.hexlify(self.bytes).decode()
