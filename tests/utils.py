"""Utilities for testing."""
from binascii import unhexlify
from pyinsteon.messages.inbound import create

def hex_to_inbound_message(hex_data):
    """Create an Inbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    (msg, remaining_data) = create(msg_bytes)
    return msg, msg_bytes