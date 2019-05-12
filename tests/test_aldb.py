"""Test the ALDB loading."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb import ALDB
from pyinsteon.aldb.control_flags import create_from_byte
from pyinsteon.protocol.messages.user_data import UserData
from pyinsteon.topics import EXTENDED_READ_WRITE_ALDB
from tests.utils import TopicItem, async_case, send_topics, cmd_kwargs
from tests import _LOGGER, _LOGGER_MSG, set_log_levels


class TestALDB(unittest.TestCase):
    """Test the ALDB class."""

    def setUp(self):
        """Setup the test."""
        set_log_levels(logger='info', logger_msg='info', logger_insteon='info')
        self.flags = create_from_byte(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0a)

        self.aldb = ALDB(self.address)
        self.sent = False

        self.topic = 'send.{}'.format(EXTENDED_READ_WRITE_ALDB)
        self.ack_topic = 'ack.{}.{}'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        self.rec_topic = '{}.{}.direct'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        self.dir_ack_topic = '{}.{}.direct_ack'.format(self.address.id, EXTENDED_READ_WRITE_ALDB)
        self.cmd2 = 0x00
        self.target = '4d5e6f'
        self.ud_ack = UserData(unhexlify('00000000000000000000000000d1'))

        pub.subscribe(self.send_ack_and_direct_ack, self.topic)

    @async_case
    async def test_load_aldb(self):
        """Load the ALDB."""
        _LOGGER.debug('Starting ALDB load')
        responses = self.create_messages()
        send_topics(responses)
        await self.aldb.async_load()
        _LOGGER.debug('Done LOAD function.')
        _LOGGER.debug('Status: %s', self.aldb.status.name)
        assert self.aldb.is_loaded


    def send_ack_and_direct_ack(self, address, action, mem_addr, num_recs,
                                topic=pub.AUTO_TOPIC):
        _LOGGER_MSG.debug('Received message %s', topic)
        ack_kwargs = cmd_kwargs(self.cmd2, self.ud_ack)
        dir_ack_kwargs = cmd_kwargs(self.cmd2, self.ud_ack, self.target)
        _LOGGER_MSG.debug('SENDING: %s %s', self.ack_topic, ack_kwargs)
        pub.sendMessage(self.ack_topic, **ack_kwargs)
        _LOGGER_MSG.debug('SENDING: %s %s', self.dir_ack_topic, dir_ack_kwargs)
        pub.sendMessage(self.dir_ack_topic, **dir_ack_kwargs)


    def create_messages(self):
        """Send response messages."""
        TIMER = 5
        TIMER_INCREMENT = 3

        ud1 = UserData(unhexlify('01010fff00a2003118a2ff1c0118'))
        ud2 = UserData(unhexlify('01010ff700a200191a60ff1f0175'))
        ud3 = UserData(unhexlify('01010fef00a201331a83ff1f013f'))
        ud4 = UserData(unhexlify('01010fe700e201191a60031f0140'))
        ud5 = UserData(unhexlify('01010fdf00e2012ffae4030000ee'))
        ud6 = UserData(unhexlify('01010fd700a200313e1e000000ba'))
        ud7 = UserData(unhexlify('01010fcf00e201313e1e0300007e'))
        ud8 = UserData(unhexlify('01010fc700a202462f24ff0000bd'))
        ud9 = UserData(unhexlify('01010fbf00e201462f2403000082'))
        ud10 = UserData(unhexlify('01010fb700a2003118a20000007c'))
        ud11 = UserData(unhexlify('01010faf00e2013118a20300013f'))
        ud12 = UserData(unhexlify('01010fa700000000000000000019'))

        topics = [TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud1, self.target), TIMER + TIMER_INCREMENT * 4),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud2, self.target), .1),

                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud3, self.target), TIMER + TIMER_INCREMENT * 5),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud4, self.target), .1),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud5, self.target), .1),

                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud6, self.target), TIMER + TIMER_INCREMENT * 6),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud7, self.target), 5),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud8, self.target), 1),

                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud9, self.target), TIMER + TIMER_INCREMENT * 7),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud10, self.target), .1),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud11, self.target), .1),
                  TopicItem(self.rec_topic, cmd_kwargs(self.cmd2, ud12, self.target), .1)]
        return topics


if __name__ == '__main__':
    unittest.main()
