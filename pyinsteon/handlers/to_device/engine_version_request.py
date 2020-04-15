"""Manage outbound ON command to a device."""
from .. import direct_ack_handler
from ...topics import GET_INSTEON_ENGINE_VERSION
from ...constants import EngineVersion
from .direct_command import DirectCommandHandlerBase


class EngineVersionRequest(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(topic=GET_INSTEON_ENGINE_VERSION, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the OFF command async."""
        return await super().async_send()

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF response direct ACK."""
        try:
            version = EngineVersion(cmd2)
        except ValueError:
            version = EngineVersion.UNKNOWN
        self._call_subscribers(engine_version=version)
