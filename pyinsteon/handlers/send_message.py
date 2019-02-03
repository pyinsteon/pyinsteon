"""Send message command handler."""


from .message_handler_base import MessageHandlerBase

class SendMessage(MessageHandlerBase):
    """Send a message."""

    async def execute(self, **kwargs):
        """Process the inbound message."""
        self._manager.send(self._msg)
        await self._run_next(msg=self._msg)