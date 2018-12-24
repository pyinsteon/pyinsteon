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
        self._start_code = data[_slices[0]]
        self._type = data[_slices[1]]
        curr_slice = 2
        for field in fields:
            val = field.type(data[_slices[curr_slice]])
            _LOGGER.debug('slice: %s', _slices[curr_slice])
            _LOGGER.debug('Field %s value %s', field.name, val)
            setattr(self, field.name, val)
            curr_slice += 1

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
        data = bytearray()
        data.append(self._start_code)
        data.append(self._type)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return data

    @property
    def hex(self):
        """Emit the message in hex."""
        return binascii.hexlify(self.bytes)
