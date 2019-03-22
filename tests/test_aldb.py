"""Test the ALDB loading."""
import asyncio
import logging
import sys
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb import ALDB
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.all_link_record_flags import AllLinkRecordFlags
from pyinsteon.protocol.messages.inbound import create
from pyinsteon.protocol.msg_to_topic import convert_to_topic

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestALDB(unittest.TestCase):
    """Test the ALDB class."""

    def setUp(self):
        """Setup the test."""
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _INSTEON_LOGGER.addHandler(stream_handler)
        # _LOGGER.setLevel(logging.DEBUG)
        # _INSTEON_LOGGER.setLevel(logging.DEBUG)

        self.hex = '0257030405060708090a'
        self.hex_bytes = bytearray(unhexlify(self.hex))
        self.message_id = MessageId(0x57)
        self.flags = AllLinkRecordFlags(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0a)

        self.msg, _ = create(self.hex_bytes)
        self.aldb = ALDB(self.address)
        pub.subscribe(self.listener_send, 'send')
        # self.aldb.load()
        self.sent = False
        #(self.topic, self.kwargs) = convert_to_topic(self.msg)
        #pub.sendMessage(self.topic, **self.kwargs)

    def listener_send(self, msg, priority=5):
        """listner to the 'send' topic."""
        _LOGGER.debug('Sent: %r', msg)
        self.sent = msg.message_id == MessageId.SEND_EXTENDED

    def test_load_sent(self):
        """Test the load menthod sent a SEND_EXTENDED message."""
        self.aldb.load()
        assert self.msg.message_id == self.message_id

    def test_load_records(self):
        """Test records received are loaded into the ALDB."""
        from tests.utils import hex_to_inbound_message
        record_hex_data = '0251{}445566{}{}{}a1a2a3a4a5a6a7a8a9aaabacadae'.format(
            self.aldb.address.id, '1f', '2f', '00')
        record_msg, _ = hex_to_inbound_message(record_hex_data)
        record_topic, kwargs = convert_to_topic(record_msg)
        #_LOGGER.debug(kwargs)
        pub.sendMessage(record_topic, **kwargs)

        assert self.aldb.get(0xa3a4)

    async def load_aldb(self):
        """Load the ALDB."""
        _LOGGER.debug('Starting ALDB load')
        await self.aldb.async_load()
        _LOGGER.debug('Done LOAD function.')
        _LOGGER.debug('Status: %s', self.aldb.status.name)
        assert self.aldb.is_loaded

    async def send_messages(self):
        """Send response messages."""
        from tests.utils import hex_to_inbound_message
        msg_ack, _ = hex_to_inbound_message(
            '0262{}{}{}{}00000000000000000000000000d106'.format(
                self.aldb.address.id, '1f', '2f', '00'))
        msg_dir_ack, _ = hex_to_inbound_message(
            '0250{}445566{}{}{}'.format(self.aldb.address.id, '20', '2f', '00'))
        msg3, _ = hex_to_inbound_message(
            '0262{}{}{}{}00000000000000000000000000d106'.format(
                self.aldb.address.id, '1f', '2f', '00'))    
        msg4, _ = hex_to_inbound_message(
            '0250{}445566{}{}{}'.format(self.aldb.address.id, '20', '2f', '00'))
        msg5, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fff00a2003118a2ff1c0118'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg6, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010ff700a200191a60ff1f0175'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg7, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fef00a201331a83ff1f013f'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg8, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fe700e201191a60031f0140'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg9, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fdf00e2012ffae4030000ee'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg10, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fd700a200313e1e000000ba'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg101, _ = hex_to_inbound_message(
            '0262{}{}{}{}00000000000000000000000000d106'.format(
                self.aldb.address.id, '1f', '2f', '00'))
        msg11, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fcf00e201313e1e0300007e'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg12, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fc700a202462f24ff0000bd'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg13, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fbf00e201462f2403000082'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg14, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fb700a2003118a20000007c'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg15, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010faf00e2013118a20300013f'.format(
                self.aldb.address.id, '15', '2f', '00'))
        msg16, _ = hex_to_inbound_message(
            '0251{}445566{}{}{}01010fa700000000000000000019'.format(
                self.aldb.address.id, '15', '2f', '00'))

        msgs = [(msg_ack, 1), (msg_dir_ack, 1),
                (msg_ack, 14), (msg_dir_ack, 1),
                (msg_ack, 17), (msg_dir_ack, 1),
                (msg_ack, 21), (msg_dir_ack, 1),
                (msg5, 3), (msg6, 1),
                (msg_ack, 25), (msg_dir_ack, 1),
                (msg7, 1), (msg8, 1), (msg9, 1),
                (msg_ack, 29), (msg_dir_ack, 1),
                (msg10, 20),  (msg11, 20), (msg12, 1),
                (msg_ack, 33), (msg_dir_ack, 1),
                (msg13, 1), (msg14, 1), (msg15, 1), (msg16, 1)]
        _LOGGER.debug('Sending response messages.')
        for msg, sleep in msgs:
            self.sent = False
            await asyncio.sleep(sleep)
            topic, kwargs = convert_to_topic(msg)
            pub.sendMessage(topic, **kwargs)

    def test_load_all(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.send_messages())
        loop.run_until_complete(self.load_aldb())


if __name__ == '__main__':
    unittest.main()
