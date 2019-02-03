"""Receive message command handler."""

from .message_handler_base import MessageHandlerBase


class ReceiveMessage(MessageHandlerBase):
    """Receive a message."""

    async def execute(self, **kwargs):
        """Process the inbound message."""
        msg = kwargs.get('msg')
        if msg and self._can_handle(msg=msg):
            await self._run_next(msg=msg)
        else:
            await self._manager.not_handled(msg=msg)

    def _can_handle(self, **kwargs) -> bool:
        """Retrun True of this message handler should handle this message.

        Override in subclass to provide different handle logic.
        """
        msg = kwargs.get('msg')
        if msg and msg == self._msg:
            return True
        return False
