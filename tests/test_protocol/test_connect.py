"""Test the connect method."""
import asyncio
from unittest import TestCase
from unittest.mock import patch

import pyinsteon
import pyinsteon.protocol.http_transport
import pyinsteon.protocol.serial_transport
from pyinsteon.constants import ResponseStatus
from pyinsteon.protocol import async_modem_connect
from pyinsteon.subscriber_base import SubscriberBase
from tests.utils import MockSerial, async_case, random_address


class MockGetImInfoSuccess(SubscriberBase):
    """Mock Get IM Info command returning a successful result."""

    def __init__(self):
        """Init the MockGetImInfoSuccess class."""
        super().__init__(subscriber_topic="get_im_info")

    async def async_send(self):
        """Send the mock command."""
        await asyncio.sleep(0.1)
        self._call_subscribers(
            address=random_address(), cat=0x03, subcat=0x01, firmware=0x02
        )
        return ResponseStatus.SUCCESS


class MockGetImInfoFailure(SubscriberBase):
    """Mock Get IM Info command returning a failure result."""

    def __init__(self):
        """Init the MockGetImInfoFailure class."""
        super().__init__(subscriber_topic="get_im_info")

    async def async_send(self):
        """Send the mock command."""
        await asyncio.sleep(0.3)
        return ResponseStatus.FAILURE


class MockGetImInfoDelayed(SubscriberBase):
    """Mock Get IM Info command returning a failure result."""

    def __init__(self):
        """Init the MockGetImInfoFailure class."""
        super().__init__(subscriber_topic="get_im_info")
        self._call_count = 0

    async def async_send(self):
        """Send the mock command."""
        await asyncio.sleep(0.1)
        if self._call_count == 3:
            self._call_subscribers(
                address=random_address(), cat=0x03, subcat=0x01, firmware=0x02
            )
            return ResponseStatus.SUCCESS
        self._call_count += 1
        return ResponseStatus.FAILURE


class TestConnectMethod(TestCase):
    """Test the connect method."""

    @async_case
    async def test_create_serial_connection(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        device = "some_device_path"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            modem = await async_modem_connect(device=device)
            assert mock_serial.call_count == 1
            assert mock_serial.kwargs.get("url") == device
            assert mock_serial.kwargs.get("host") is None
            modem.protocol.close()
            await asyncio.sleep(0.01)

    @async_case
    async def test_create_socket_connection(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        host = "some_host"
        hub_version = 1
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            modem = await async_modem_connect(host=host, hub_version=hub_version)
            assert mock_serial.call_count == 1
            assert mock_serial.kwargs.get("url") == f"socket://{host}:9761"
            modem.protocol.close()
            await asyncio.sleep(0.01)

    @async_case
    async def test_create_http_connection(self):
        """Test creating a serial modem connection."""

        class MockHttp:
            """Mock the HTTP connection."""

            def __init__(self):
                """Init the MockHttp class."""
                self.kwargs = None
                self.call_count = 0

            def __call__(self, *args, **kwargs):
                """Call the class."""
                self.kwargs = kwargs
                self.call_count += 1
                return self

            def start_reader(self, *args, **kwargs):
                """Mock the start reader method."""

            def close(self, *args, **kwargs):
                """Mock the close method."""

            def is_closing(self):
                """Mock the is_closing method."""
                return False

            async def async_test_connection(self):
                """Mock the http test connection."""
                return True

        mock_http = MockHttp()

        host = "some_host"
        username = "my_user"
        password = "my_password"
        with patch.object(
            pyinsteon.protocol.http_transport, "HttpTransport", mock_http
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            modem = await async_modem_connect(
                host=host, username=username, password=password
            )
            assert mock_http.call_count == 1
            assert mock_http.kwargs.get("host") == host
            assert mock_http.kwargs.get("username") == username
            assert mock_http.kwargs.get("password") == password
            assert mock_http.kwargs.get("port") == 25105
            modem.protocol.close()
            await asyncio.sleep(0.01)

    @async_case
    async def test_no_device_id(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        device = "some_device_path"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoFailure):
            try:
                await async_modem_connect(device=device)
                assert False
            except ConnectionError:
                assert True
            await asyncio.sleep(0.01)

    @async_case
    async def test_delayed_device_id(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        device = "some_device_path"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoDelayed):
            try:
                modem = await async_modem_connect(device=device)
                assert True
            except ConnectionError:
                assert False
            modem.protocol.close()
            await asyncio.sleep(0.01)

    @async_case
    async def test_invalid_params(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        username = "my_user"
        password = "my_password"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoDelayed):
            try:
                await async_modem_connect(username=username, password=password)
                assert False
            except ValueError:
                assert True
            await asyncio.sleep(0.01)

    @async_case
    async def do_not_test_connection_error(self):
        """Test creating a serial modem connection."""

        async def mock_async_connect_serial(*args, **kwargs):
            """Mock the async_connect_serial method."""
            raise ConnectionError

        device = "some_device"
        with patch.object(
            pyinsteon.protocol,
            "async_connect_serial",
            mock_async_connect_serial,
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoDelayed):
            try:
                await async_modem_connect(device=device)
                assert False
            except ConnectionError:
                assert True
            await asyncio.sleep(0.01)
