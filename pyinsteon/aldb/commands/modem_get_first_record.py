"""Modem command handler for get first ALDB record."""

from ... import pub
from ...address import Address
from ...messages.outbound import get_first_all_link_record


class GetFirstRecord():
    """Recieve acknowledgement that the Get First All Link record was sent."""

    def __init__(self, address: Address):
        """Init the ReceiveGetFirstAldbRecordNak class."""
        self._retries = 0
        self._address_id = address.id
        topic = '{}{}'.format(self._address_id, '.get_first_all_link_record')
        pub.subscribe(self.receive_nak, 'nak.{}'.format(topic))
        pub.subscribe(self.receive_ack, 'ack.{}'.format(topic))
        pub.subscribe(self.send, 'modem.aldb.load')

    #pylint: disable=no-self-use
    def send(self, sender='modem'):
        """Send the Get First ALDB Record."""
        msg = get_first_all_link_record()
        pub.sendMessage('send.get_first_all_link_record', msg=msg)

    def receive_nak(self):
        """Receive the NAK message and retry up to 3 times."""
        if self._retries < 3:
            self.send()
            self._retries += 1

    def receive_ack(self):
        """Receive the ACK message and reset the retry count."""
        self._retries = 0
