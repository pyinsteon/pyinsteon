"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...topics import SET_OPERATING_FLAGS
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class SetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=SET_OPERATING_FLAGS, address=address)

    # pylint: disable=arguments-differ
    def send(self, cmd: int):
        """Send Get Operating Flags message."""
        super().send(cmd=cmd)

    # pylint: disable=arguments-differ
    async def async_send(self, cmd: int):
        """Send Get Operating Flags message asyncronously."""
        return await super().async_send(cmd=cmd)
