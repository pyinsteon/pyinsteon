"""Utilities for tests."""
import logging
import os
import shutil
import sys
from unittest.mock import patch

import pyinsteon
from pyinsteon import pub
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers.device_manager import DeviceManager

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger("pyinsteon")
_LOGGER_MESSAGES = logging.getLogger("pyinsteon.messages")
_LOGGER_TOPICS = logging.getLogger("pyinsteon.topics")
PATH = os.path.join(os.getcwd())


async def async_connect_mock(
    read_queue,
    write_queue,
    protocol,
    random_nak=True,
    always_nak=False,
    auto_ack=True,
    connect=True,
    retries=None,
):
    """Mock connection for testing."""
    # pylint: disable=import-outside-toplevel
    from .mock_transport import MockTransport

    transport = MockTransport(
        protocol,
        read_queue,
        write_queue,
        random_nak=random_nak,
        always_nak=always_nak,
        auto_ack=auto_ack,
    )
    if connect or not retries:
        protocol.connection_made(transport)
        return transport
    if retries:
        retries.pop(0)
    return None


def set_log_levels(
    logger="info", logger_pyinsteon="info", logger_messages="info", logger_topics=False
):
    """Set the log levels of the three logs."""
    try:
        assert os.environ["ALLOW_LOGGING"].lower() == "y"
    except (AssertionError, KeyError):
        return

    _setup_logger(_LOGGER, logger)
    _setup_logger(_LOGGER_PYINSTEON, logger_pyinsteon)
    _setup_logger(_LOGGER_MESSAGES, logger_messages)
    _LOGGER_TOPICS.setLevel(logging.DEBUG if logger_topics else logging.CRITICAL)


async def load_devices(devices_mgr: DeviceManager):
    """Load the device fixture into the devices list."""
    with patch.object(pyinsteon, "devices", devices_mgr):
        if not devices_mgr.modem:
            modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
            devices_mgr.modem = modem
        test_dir_path = os.path.dirname(__file__)
        fixture_file = os.path.join(test_dir_path, "devices_fixture.json")
        output_file = os.path.join(test_dir_path, "insteon_devices.json")
        shutil.copy(fixture_file, output_file)
        await devices_mgr.async_load(test_dir_path, 0, 0)
        os.remove(output_file)


def _setup_logger(logger, level):
    logger.setLevel(_text_to_log_level(level))
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


def _log_all_topics(topic=pub.AUTO_TOPIC, **kwargs):
    """Log all topics from pyinsteon."""
    _LOGGER.info("Topic: %s data: %s", topic.name, kwargs)


def _text_to_log_level(log_level_text):
    if log_level_text.lower() == "debug":
        return logging.DEBUG
    if log_level_text.lower() == "info":
        return logging.INFO
    if log_level_text.lower() == "warn":
        return logging.WARN
    if log_level_text.lower() == "warning":
        return logging.WARNING
    if log_level_text.lower() == "error":
        return logging.ERROR
    if log_level_text.lower() == "critical":
        return logging.CRITICAL
    if log_level_text.lower() == "fatal":
        return logging.FATAL
    return logging.INFO
