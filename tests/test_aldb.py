"""Test the ALDB loading."""
import asyncio
import sys
import unittest
from binascii import unhexlify
import logging

from pyinsteon.address import Address
from pyinsteon.aldb import ALDB
from pyinsteon.aldb.control_flags import create_from_byte
from pyinsteon.protocol.messages.user_data import UserData
from pyinsteon.topics import EXTENDED_READ_WRITE_ALDB
from tests.utils import TopicItem, async_case, async_send_topics, cmd_kwargs
from tests import _LOGGER, _INSTEON_LOGGER


class TestALDB(unittest.TestCase):
    """Test the ALDB class."""

    def setUp(self):
        """Setup the test."""
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _INSTEON_LOGGER.addHandler(stream_handler)
        _LOGGER.setLevel(logging.DEBUG)
        _INSTEON_LOGGER.setLevel(logging.DEBUG)

        self.flags = create_from_byte(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0a)

        self.aldb = ALDB(self.address)
        self.sent = False

    @async_case
    async def test_load_aldb(self):
        """Load the ALDB."""
        _LOGGER.debug('Starting ALDB load')
        asyncio.ensure_future(self.send_messages())
        await self.aldb.async_load()
        _LOGGER.debug('Done LOAD function.')
        _LOGGER.debug('Status: %s', self.aldb.status.name)
        assert self.aldb.is_loaded

    async def send_messages(self):
        """Send response messages."""
        ack_topic = 'ack.{}.{}'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        rec_topic = '{}.{}.direct'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        dir_ack_topic = '{}.{}.direct_ack'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        cmd2 = 0x00
        target = '4d5e6f'
        ud_ack = UserData(unhexlify('00000000000000000000000000d1'))
        ud5 = UserData(unhexlify('01010fff00a2003118a2ff1c0118'))
        ud6 = UserData(unhexlify('01010ff700a200191a60ff1f0175'))
        ud7 = UserData(unhexlify('01010fef00a201331a83ff1f013f'))
        ud8 = UserData(unhexlify('01010fe700e201191a60031f0140'))
        ud9 = UserData(unhexlify('01010fdf00e2012ffae4030000ee'))
        ud10 = UserData(unhexlify('01010fd700a200313e1e000000ba'))
        ud11 = UserData(unhexlify('01010fcf00e201313e1e0300007e'))
        ud12 = UserData(unhexlify('01010fc700a202462f24ff0000bd'))
        ud13 = UserData(unhexlify('01010fbf00e201462f2403000082'))
        ud14 = UserData(unhexlify('01010fb700a2003118a20000007c'))
        ud15 = UserData(unhexlify('01010faf00e2013118a20300013f'))
        ud16 = UserData(unhexlify('01010fa700000000000000000019'))

        topics = [TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 1),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 14),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 17),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 21),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 14),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud5), 3),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud6), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 25),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud7), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud8), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud9), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 29),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud10), 20),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud11), 20),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud12), 1),
                  TopicItem(ack_topic, cmd_kwargs(cmd2, target, ud_ack), 33),
                  TopicItem(dir_ack_topic, cmd_kwargs(cmd2, target, None), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud13), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud14), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud15), 1),
                  TopicItem(rec_topic, cmd_kwargs(cmd2, target, ud16), 1)]
        await async_send_topics(topics)


if __name__ == '__main__':
    unittest.main()
