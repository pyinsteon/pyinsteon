"""Modem command to get next ALDB record."""
import logging

from ... import pub
from ...messages.outbound import get_next_all_link_record


_LOGGER = logging.getLogger(__name__)

class GetNextRecord():
    """Handle Get Next All Link Record commands"""

    def __init__(self):
        """Init the GetNextAldbRecordNak class."""
        self._retries = 0
        self._subscribe_topics()

    #pylint: disable=no-self-use
    def send(self, sender='modem'):
        """Send the Get Next ALDB Record."""
        _LOGGER.debug('Sending modem get next all link record')
        msg = get_next_all_link_record()
        pub.sendMessage('send.get_next_all_link_record', msg=msg)

    def receive_nak(self):
        """Receive the NAK message and retry up to 3 times."""
        if self._retries < 3:
            _LOGGER.debug('Modem ALDB load NAK received. Retrying.')
            self.send()
            self._retries += 1
        else:
            _LOGGER.debug('Modem ALDB loaded')
            pub.sendMessage('modem.aldb.loaded')

    def receive_ack(self):
        """Receive the ACK message and reset the retry count."""
        _LOGGER.debug('Modem ALDB load ACK received.')
        self._retries = 0

    def _subscribe_topics(self):
        topic = 'modem.aldb.get_next_all_link_record'
        pub.subscribe(self.send, topic)
        pub.subscribe(self.receive_nak, 'nak.{}'.format(topic))
        pub.subscribe(self.receive_ack, 'ack.{}'.format(topic))
