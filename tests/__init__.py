import os
import sys
import logging


_LOGGER = logging.getLogger(__name__)
_LOGGER_INSTEON = logging.getLogger('pyinsteon')
_LOGGER_MSG = logging.getLogger('pyinsteon.messages')


def set_log_levels(logger='info', logger_insteon='info', logger_msg='info'):
    logger_level = _text_to_log_level(logger)
    logger_insteon_level = _text_to_log_level(logger_insteon)
    logger_msg_level = _text_to_log_level(logger_msg)

    # stream_handler = logging.StreamHandler(sys.stdout)

    # _LOGGER.addHandler(stream_handler)
    # _LOGGER_INSTEON.addHandler(stream_handler)
    # _LOGGER_MSG.addHandler(stream_handler)

    _LOGGER.setLevel(logger_level)
    _LOGGER_INSTEON.setLevel(logger_insteon_level)
    _LOGGER_MSG.setLevel(logger_msg_level)


def _text_to_log_level(log_level_text):
    if log_level_text.lower() == 'debug':
        return logging.DEBUG
    if log_level_text.lower() == 'info':
        return logging.INFO
    if log_level_text.lower() == 'warn':
        return logging.WARN
    if log_level_text.lower() == 'warning':
        return logging.WARNING
    if log_level_text.lower() == 'error':
        return logging.ERROR
    if log_level_text.lower() == 'critical':
        return logging.CRITICAL
    if log_level_text.lower() == 'fatal':
        return logging.FATAL
    return logging.INFO