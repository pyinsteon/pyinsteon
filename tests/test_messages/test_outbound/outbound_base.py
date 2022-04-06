"""Base class for testing outbound messages."""

from pyinsteon import pub
from pyinsteon.protocol.messages.outbound import (
    outbound_write_manager,
    register_outbound_handlers,
)
from tests import set_log_levels
from tests.utils import async_case


class OutboundBase:
    """Test outbound messages base object."""

    # pylint: disable=attribute-defined-outside-init
    def base_setup(self, message_id, bytes_data, **kwargs):
        """Init the OutboundBase class."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="debug",
            logger_messages="debug",
            logger_topics=True,
        )
        register_outbound_handlers()
        self.msg = None
        self.message_id = message_id
        self.bytes_data = bytes_data
        outbound_write_manager.protocol_write = self.write_message
        self.topic = self.message_id.name.lower()
        if (
            self.topic == "send_standard"
            and kwargs.get("flags")
            and kwargs.get("flags").is_extended
        ):
            self.topic = "send_extended"
        self.kwargs = kwargs

    def write_message(self, msg, priority=5):
        """Set the message from the outbound publisher."""
        self.msg = msg

    @async_case
    async def test_id(self):
        """Test the message ID matches the expected message."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.message_id == self.message_id

    @async_case
    async def test_bytes(self):
        """Test the byte representation matches the expected value."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert bytes(self.msg) == self.bytes_data
