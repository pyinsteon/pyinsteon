"""Test incomplete message processing."""

from binascii import unhexlify
from unittest import TestCase

from pyinsteon.protocol.messages.inbound import create


class TestIncompleteMessages(TestCase):
    """Test incomplete message processing."""

    def test_one_byte(self):
        """Test a single byte message."""
        hex_data = "02"
        msg_bytes = bytearray(unhexlify(hex_data))
        _, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == msg_bytes

    def test_partial_message(self):
        """Test partial message received."""
        hex_data = "02500304050607080999"
        msg_bytes = bytearray(unhexlify(hex_data))
        _, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == msg_bytes

    def test_partial_standard_message(self):
        """Test partial message received."""
        hex_data = "02620304050999"
        msg_bytes = bytearray(unhexlify(hex_data))
        _, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == msg_bytes

    def test_invalid_msg_id_message(self):
        """Test partial message received."""
        hex_data = "02980304050253"
        msg_bytes = bytearray(unhexlify(hex_data))
        expected_bytes = bytearray(unhexlify("0253"))
        _, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == expected_bytes

    def test_invalid_msg_def_message(self):
        """Test partial message received."""
        hex_data = "02990304050253"
        msg_bytes = bytearray(unhexlify(hex_data))
        expected_bytes = bytearray(unhexlify("0253"))
        _, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == expected_bytes

    def test_invalid_initial_data(self):
        """Test invalid data received."""
        hex_data = "9903040502520380"
        msg_bytes = bytearray(unhexlify(hex_data))
        msg, remaining_bytes = create(msg_bytes)
        assert remaining_bytes == b""
        assert msg.message_id == 0x52

    def test_extra_data(self):
        """Test extra data received."""
        hex_data = "02520380025203"
        msg_bytes = bytearray(unhexlify(hex_data))
        expected_bytes = bytearray(unhexlify("025203"))
        msg, remaining_bytes = create(msg_bytes)
        assert msg.message_id == 0x52
        assert remaining_bytes == expected_bytes
