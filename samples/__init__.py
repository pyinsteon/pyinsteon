"""Sample programs to demonstrate pyinsteon."""
import logging
import os
import sys

import yaml

from pyinsteon import pub

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "pyinsteon"))
_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger("pyinsteon")
_LOGGER_MESSAGES = logging.getLogger("pyinsteon.messages")
_LOGGER_TOPICS = logging.getLogger("topics")
PATH = os.getcwd()


def set_log_levels(
    logger="info", logger_pyinsteon="info", logger_messages="info", logger_topics=False
):
    """Set the log levels of the three logs."""
    _setup_logger(_LOGGER, logger)
    _setup_logger(_LOGGER_PYINSTEON, logger_pyinsteon)
    _setup_logger(_LOGGER_MESSAGES, logger_messages)
    if logger_topics:
        _setup_logger(_LOGGER_TOPICS, "info")
        pub.subscribe(_log_all_topics, pub.ALL_TOPICS)
    else:
        _setup_logger(_LOGGER_TOPICS, "fatal")
        pub.unsubscribe(_log_all_topics, pub.ALL_TOPICS)


def _log_all_topics(topic=pub.AUTO_TOPIC, **kwargs):
    """Log all topics from pyinsteon."""
    _LOGGER.info("Topic: %s data: %s", topic.name, kwargs)


def _setup_logger(logger, level):
    logger.setLevel(_text_to_log_level(level))
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


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


def get_hub_config():
    """Read the secrets file and return the username, password and address."""
    with open("secrets.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            _LOGGER.error(exc)
        return (
            config.get("hub_username"),
            config.get("hub_password"),
            config.get("address"),
            int(config.get("port")),
        )
