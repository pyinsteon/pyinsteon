"""Start All-Linking."""
from . import ResponseStatus, response_handler, ack_handler
from .response_command import ResponseCommandHandlerBase
from ..topics import START_ALL_LINKING, ALL_LINKING_COMPLETED
from ..constants import AllLinkMode


#pylint: disable=arguments-differ
class StartAllLinkingCommandHandler(ResponseCommandHandlerBase):
    """Start All-Linking Command."""

    def __init__(self):
        """Init the StartAllLinkingCommandHandler class."""
        super().__init__(topic=START_ALL_LINKING)

    def send(self, mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        super().send(mode=mode, group=group)

    async def async_send(self, mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        await super().async_send(mode=mode, group=group)

    @ack_handler
    def handle_ack(self, mode, group):
        """Handle the messack ACK."""

    @response_handler(ALL_LINKING_COMPLETED)
    def handle_response(self, mode, group, address, cat, subcat, firmware):
        """Link process is complete."""
        from ..address import Address
        if not self.response_lock.locked():
            # Get ID Request not called therefore
            # this is not meant for us
            return
        address = Address(address)
        mode = AllLinkMode(mode)
        for subscriber in self._subscribers:
            subscriber(address=self._address, cat=cat, subcat=subcat,
                       firmware=firmware, group=group, mode=mode)
        if self.response_lock.locked():
            self.message_response.put_nowait(ResponseStatus.SUCCESS)
