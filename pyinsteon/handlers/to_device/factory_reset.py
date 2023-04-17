"""Factory reset command handler."""

from ...constants import DeviceCategory, ResponseStatus
from ...topics import FACTORY_RESET
from .direct_command import DirectCommandHandlerBase


class FactoryResetCommand(DirectCommandHandlerBase):
    """Manage an outbound FACTORY RESET command to a device."""

    def __init__(self, address, cat: DeviceCategory, subcat: int):
        """Init the OnLevelCommand class."""
        super().__init__(topic=FACTORY_RESET, address=address)
        self._cat = DeviceCategory(cat)
        self._subcat = int(subcat)

    # pylint: disable=arguments-differ
    async def async_send(self) -> ResponseStatus:
        """Send the OFF command async."""
        return await super().async_send(cat=self._cat, subcat=self._subcat)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers()
