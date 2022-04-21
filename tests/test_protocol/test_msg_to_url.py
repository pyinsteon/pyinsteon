"""Test converting a message to a URL."""

from binascii import unhexlify
from unittest import TestCase

from pyinsteon.constants import AllLinkMode
from pyinsteon.protocol.msg_to_url import (
    cancel_all_linking_url,
    convert_to_url,
    start_all_link_url,
)


class MockMessage:
    """Mock message class."""

    link_mode = AllLinkMode.CONTROLLER
    group = 0xF0  # i.e. 240
    data = "0a0b"

    def __bytes__(self):
        """Return a bytes representation."""
        return unhexlify(self.data)


class TestMsgToUrl(TestCase):
    """Test the msg_to_url class."""

    def test_convert_to_url(self):
        """Test the convert_to_url method."""
        msg = unhexlify("02030405")
        host = "host"
        port = 8000
        url = convert_to_url(host, port, msg)
        assert url == f"http://{host}:{port}/3?{msg.hex()}=I=3"

    def test_start_all_linking_url(self):
        """Tet the start_all_linking_url method."""

        msg = MockMessage()
        host = "host1"
        port = 8001
        url = start_all_link_url(host, port, msg)
        assert url == f"http://{host}:{port}/0?09240=I=0"

        msg.link_mode = AllLinkMode.DELETE
        url = start_all_link_url(host, port, msg)
        assert url == f"http://{host}:{port}/3?0a0b=I=3"

    def test_cancel_all_linking(self):
        """Test the cancel_all_linking method."""
        msg = MockMessage()
        host = "host2"
        port = 8002
        url = cancel_all_linking_url(host, port, msg)
        assert url == f"http://{host}:{port}/0?08=I=0"
