"""Utilities for testing."""
from binascii import unhexlify
from pyinsteon.messages.inbound import create

def hex_to_inbpund_message(hex_data):
    """Create an outbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    msg = create(msg_bytes)
    return msg, msg_bytes