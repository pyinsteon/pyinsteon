"""Base class for testing outbound messages."""

from pyinsteon import pub
from pyinsteon.protocol.messages.outbound import register_outbound_handlers
from tests import set_log_levels


class OutboundBase:
    """Test outbound messages base object."""

    # pylint: disable=attribute-defined-outside-init
    def base_setup(self, message_id, bytes_data, **kwargs):
        """Init the OutboundBase class."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="debug",
            logger_messages="debug",
            logger_topics=False,
        )
        register_outbound_handlers()
        self.msg = None
        self.message_id = message_id
        self.bytes_data = bytes_data
        pub.subscribe(self.receive_message, "send_message")
        topic = self.message_id.name.lower()
        if (
            topic == "send_standard"
            and kwargs.get("flags")
            and kwargs.get("flags").is_extended
        ):
            topic = "send_extended"
        pub.sendMessage("send.{}".format(topic), **kwargs)

    def receive_message(self, msg, priority=5):
        """Set the message from the outbound publisher."""
        self.msg = msg

    def test_id(self):
        """Test the message ID matches the expected message."""
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        """Test the byte representation matches the expected value."""
        assert bytes(self.msg) == self.bytes_data
