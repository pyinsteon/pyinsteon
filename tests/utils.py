"""Utilities for testing."""
from binascii import unhexlify
import logging
import sys
from pyinsteon.messages.inbound import create


_LOGGER = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
_LOGGER.addHandler(stream_handler)


def hex_to_inbound_message(hex_data):
    """Create an Inbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    (msg, remaining_data) = create(msg_bytes)
    return msg, msg_bytes


def check_fields_match(msg1, msg2):
    """Check fields in msg1 match fields in msg2."""
    def _check_eq_or_none(fld1, fld2):
        # _LOGGER.error(fld1 is None or
        #               fld2 is None or
        #               fld1 == fld2)
        return (fld1 is None or
                fld2 is None or
                fld1 == fld2)
    match = True
    for field in msg1.fields:
        fld1 = getattr(msg1, field.name)
        fld2 = getattr(msg2, field.name)
        # _LOGGER.error(fld1)
        # _LOGGER.error(fld2)
        match = match & _check_eq_or_none(fld1, fld2)
    return match
        