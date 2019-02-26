"""Modem command to get next ALDB record."""

from ... import pub
from ...address import Address
from ...messages.outbound import get_next_all_link_record


class GetNextRecord():
    """Handle Get Next All Link Record commands"""

    def __init__(self, address: Address):
        """Init the GetNextAldbRecordNak class."""
        self._retries = 0
        self._address_id = address.id
        topic = '{}.aldb.get_next_record'.format(self._address_id)
        pub.subscribe(self.receive_nak, 'nak.{}'.format(topic))
        pub.subscribe(self.receive_ack, 'ack.{}'.format(topic))
        pub.subscribe(self.send, 'modem.aldb.get_next_record')

    #pylint: disable=no-self-use
    def send(self, sender='modem'):
        """Send the Get Next ALDB Record."""
        msg = get_next_all_link_record()
        pub.sendMessage('send.get_next_all_link_record', msg=msg)

    def receive_nak(self):
        """Receive the NAK message and retry up to 3 times."""
        if self._retries < 3:
            self.send()
            self._retries += 1

    def receive_ack(self):
        """Receive the ACK message and reset the retry count."""
        self._retries = 0
