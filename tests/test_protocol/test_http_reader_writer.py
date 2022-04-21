"""Test the HTTP Reader/Writer class."""
import asyncio
import json
from functools import partial
from unittest import TestCase
from unittest.mock import patch

import aiofiles
from aiohttp.client_exceptions import ClientError

import pyinsteon
from pyinsteon.protocol.http_reader_writer import (
    HttpReaderWriter,
    HubConnectionException,
)

from ..utils import MockHttpResponse, async_case, create_mock_http_client

FILE = "http_buffer.json"


async def import_commands(file_name):
    """Import and parse the commands to test."""
    from os import path

    curr_path = path.dirname(path.abspath(__file__))
    command_file = path.join(curr_path, file_name)
    async with aiofiles.open(command_file, "r") as afp:
        json_file = ""
        json_file = await afp.read()
    return json.loads(json_file)


class TestHttpReaderWriter(TestCase):
    """Test the HTTP Reader/Writer class."""

    @async_case
    async def test_test_connection_success(self):
        """Test the test connection method success."""

        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            create_mock_http_client,
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_test_connection("some_url")
            assert result

    @async_case
    async def test_test_connection_status_errors(self):
        """Test the test connection method for status errors."""
        for error in [401, 404, 505, 999]:
            with patch.object(
                pyinsteon.protocol.http_reader_writer,
                "ClientSession",
                partial(create_mock_http_client, status=error),
            ):
                http_reader_writer = HttpReaderWriter(None)
                result = await http_reader_writer.async_test_connection("some_url")
                assert not result

    @async_case
    async def test_test_connection_timeout(self):
        """Test the test connection method with timeout error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=asyncio.TimeoutError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_test_connection("some_url")
            assert not result

    @async_case
    async def test_test_connection_client_error(self):
        """Test the test connection method with a client error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=ClientError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_test_connection("some_url")
            assert not result

    @async_case
    async def test_reader(self):
        """Test the HTTP reader method."""
        test_cases = await import_commands(FILE)
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            create_mock_http_client,
        ):
            http_reader_writer = HttpReaderWriter(None)
            for test_case in test_cases:
                buffer = test_cases[test_case]["buffer"]
                MockHttpResponse.buffer = buffer
                expected = test_cases[test_case]["expected"]
                result = await http_reader_writer.async_read("some_url")
                try:
                    assert result == expected
                except AssertionError:
                    raise AssertionError(f"Failed in test {test_case}: result={result}")

    @async_case
    async def test_reader_status_errors(self):
        """Test the test connection method for status errors."""
        for error in [401, 404, 505, 999]:
            with patch.object(
                pyinsteon.protocol.http_reader_writer,
                "ClientSession",
                partial(create_mock_http_client, status=error),
            ):
                http_reader_writer = HttpReaderWriter(None)
                try:
                    await http_reader_writer.async_read("some_url")
                    assert False
                except HubConnectionException:
                    assert True

    @async_case
    async def test_reader_timeout(self):
        """Test the test connection method with timeout error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=asyncio.TimeoutError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            try:
                await http_reader_writer.async_read("some_url")
                assert False
            except HubConnectionException:
                assert True

    @async_case
    async def test_reader_client_error(self):
        """Test the test connection method with a client error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=ClientError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            try:
                await http_reader_writer.async_read("some_url")
                assert False
            except HubConnectionException:
                assert True

    @async_case
    async def test_reader_cancel_error(self):
        """Test the test connection method with a client error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=asyncio.CancelledError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            try:
                await http_reader_writer.async_read("some_url")
                assert False
            except asyncio.CancelledError:
                assert True

    @async_case
    async def test_reader_generator(self):
        """Test the test connection method with generatorexit error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=GeneratorExit),
        ):
            http_reader_writer = HttpReaderWriter(None)
            try:
                await http_reader_writer.async_read("some_url")
                assert False
            except GeneratorExit:
                assert True

    @async_case
    async def test_writer_success(self):
        """Test the test connection method success."""

        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            create_mock_http_client,
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_write("some_url")
            assert result == 200

    @async_case
    async def test_writer_status_errors(self):
        """Test the test connection method for status errors."""
        for error in [401, 404, 505, 999]:
            with patch.object(
                pyinsteon.protocol.http_reader_writer,
                "ClientSession",
                partial(create_mock_http_client, status=error),
            ):
                http_reader_writer = HttpReaderWriter(None)
                result = await http_reader_writer.async_write("some_url")
                assert result == error

    @async_case
    async def test_writer_timeout(self):
        """Test the test connection method with timeout error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=asyncio.TimeoutError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_write("some_url")
            assert result == 500

    @async_case
    async def test_writer_client_error(self):
        """Test the test connection method with a client error."""
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            partial(create_mock_http_client, exception_error=ClientError),
        ):
            http_reader_writer = HttpReaderWriter(None)
            result = await http_reader_writer.async_write("some_url")
            assert result == 500
