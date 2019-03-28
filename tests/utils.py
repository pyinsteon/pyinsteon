"""Utilities for testing."""
import asyncio
from binascii import unhexlify
from collections import namedtuple
import logging
import sys
from pyinsteon.protocol.messages.inbound import create
from pyinsteon import pub
from tests import _LOGGER


def hex_to_inbound_message(hex_data):
    """Create an Inbound message from a hex string."""
    msg_bytes = bytearray(unhexlify(hex_data))
    (msg, _) = create(msg_bytes)
    return msg, msg_bytes


def check_fields_match(msg1, msg2):
    """Check fields in msg1 match fields in msg2."""
    def _check_eq_or_none(fld1, fld2):
        # _LOGGER.error(fld1 is None or
        #               fld2 is None or
        #               fld1 == fld2)
        return (fld1 is None or
                fld2 is None or
                fld1 == fld2)
    match = True
    for field in msg1.fields:
        fld1 = getattr(msg1, field.name)
        fld2 = getattr(msg2, field.name)
        # _LOGGER.error(fld1)
        # _LOGGER.error(fld2)
        match = match & _check_eq_or_none(fld1, fld2)
    return match


def async_case(f):
    """Wrap a test cast around a wrapper to execute the test."""
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper

TopicItem = namedtuple('TopicItem', 'topic, kwargs, delay')

async def async_send_topics(topic_items):
    """Publish a topic message to interact with a test case."""
    _LOGGER.debug('Sending message')
    for item in topic_items:
        await asyncio.sleep(item.delay)
        _LOGGER.debug('RX: %s  %s', item.topic, item.kwargs)
        pub.sendMessage(item.topic, **item.kwargs)
        
def cmd_kwargs(cmd2, user_data, target=None):
    """Return a kwargs dict for a standard messsage command."""
    if target:
        return {'cmd2': cmd2,
                'target': target,
                'user_data': user_data}
    return {'cmd2': cmd2,
            'user_data': user_data}
    