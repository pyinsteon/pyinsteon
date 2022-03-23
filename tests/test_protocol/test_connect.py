"""Test the connect method."""
import asyncio
from time import sleep
from unittest import TestCase
from unittest.mock import AsyncMock, patch, Mock

import pyinsteon
from pyinsteon.constants import ResponseStatus
import pyinsteon.protocol.serial_transport
import pyinsteon.protocol.http_transport
from pyinsteon.protocol import async_modem_connect
from pyinsteon.subscriber_base import SubscriberBase

from tests.mock_transport import MockTransport
from tests.utils import async_case, random_address


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


class MockSerial:
    """Mock serial connection."""
    
    def __init__(self):
        """Init the MockSerial class."""
        self.serial_for_url = Mock()
        
        
class MockHttp(Mock):
    """Mock the HTTP connection."""
    
    async def async_test_connection(self):
        """Mock the http test connection."""
        await asyncio.sleep(0.1)
        return True


class TestConnectMethod(TestCase):
    """Test the connect method."""

    @async_case
    async def test_create_serial_connection(self):
        """Test creating a serial modem connection."""

        transport_connect_method = AsyncMock()
        mock_serial = MockSerial()
        device = "some_device_path"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            await async_modem_connect(device=device)
            assert mock_serial.serial_for_url.call_count == 1
            assert mock_serial.serial_for_url.call_args.kwargs.get("url") == device
            assert mock_serial.serial_for_url.call_args.kwargs.get("host") is None

    @async_case
    async def test_create_socket_connection(self):
        """Test creating a serial modem connection."""

        mock_serial = MockSerial()
        host = "some_host"
        hub_version = 1
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            await async_modem_connect(host=host, hub_version=hub_version)
            assert mock_serial.serial_for_url.call_count == 1
            assert mock_serial.serial_for_url.call_args.kwargs.get("url") == f"socket://{host}:9761"

    @async_case
    async def test_create_http_connection(self):
        """Test creating a serial modem connection."""
        
        async def mock_test_connection():
            """Mock the test connection method."""
            return True

        mock_http = MockHttp()
        mock_http.async_test_connection = mock_test_connection
        
        host = "some_host"
        username = "my_user"
        password = "my_password"
        with patch.object(
            pyinsteon.protocol.http_transport, "HttpTransport", mock_http
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoSuccess):
            await async_modem_connect(host=host, username=username, password=password)
            assert mock_http.call_count == 1
            assert mock_http.call_args.kwargs.get("host") == host
            assert mock_http.call_args.kwargs.get("username") == username
            assert mock_http.call_args.kwargs.get("password") == password
            assert mock_http.call_args.kwargs.get("port") == 25105
            
    @async_case
    async def test_no_device_id(self):
        """Test creating a serial modem connection."""

        transport_connect_method = AsyncMock()
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
            
    @async_case
    async def test_delayed_device_id(self):
        """Test creating a serial modem connection."""

        transport_connect_method = AsyncMock()
        mock_serial = MockSerial()
        device = "some_device_path"
        with patch.object(
            pyinsteon.protocol.serial_transport, "serial", mock_serial
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoDelayed):
            try:
                await async_modem_connect(device=device)
                assert True
            except ConnectionError:
                assert False

    @async_case
    async def test_invalid_params(self):
        """Test creating a serial modem connection."""

        transport_connect_method = AsyncMock()
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

    @async_case
    async def test_connection_error(self):
        """Test creating a serial modem connection."""

        device = "some_device"
        with patch.object(
            pyinsteon.protocol, "async_connect_serial", AsyncMock(side_effect=ConnectionError)
        ), patch.object(pyinsteon.protocol, "GetImInfoHandler", MockGetImInfoDelayed):
            try:
                await async_modem_connect(device=device)
                assert False
            except ConnectionError:
                assert True
