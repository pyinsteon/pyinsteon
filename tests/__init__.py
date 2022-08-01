"""Utilities for tests."""
import logging
import os
import shutil
import sys

from pyinsteon import devices, pub

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger("pyinsteon")
_LOGGER_MESSAGES = logging.getLogger("pyinsteon.messages")
_LOGGER_TOPICS = logging.getLogger("topics")
PATH = os.path.join(os.getcwd())


async def async_connect_mock(
    read_queue,
    write_queue,
    protocol,
    random_nak=True,
    auto_ack=True,
    connect=True,
    retries=None,
):
    """Mock connection for testing."""
    from .mock_transport import MockTransport

    transport = MockTransport(
        protocol, read_queue, write_queue, random_nak=random_nak, auto_ack=auto_ack
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
    if logger_topics:
        _setup_logger(_LOGGER_TOPICS, "info")
        pub.subscribe(_log_all_topics, pub.ALL_TOPICS)
    else:
        _setup_logger(_LOGGER_TOPICS, "fatal")
        pub.unsubscribe(_log_all_topics, pub.ALL_TOPICS)


async def load_devices():
    """Load the device fixture into the devices list."""
    test_dir_path = os.path.dirname(__file__)
    fixture_file = os.path.join(test_dir_path, "devices_fixture.json")
    output_file = os.path.join(test_dir_path, "insteon_devices.json")
    shutil.copy(fixture_file, output_file)
    await devices.async_load(test_dir_path, 0, 0)
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
