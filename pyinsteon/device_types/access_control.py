"""Access control device types."""

from .on_off_responder_base import OnOffResponderBase


class AccessControl_Morningstar(OnOffResponderBase):
    """Access Control MorningStar device."""

    async def async_lock(self):
        """Lock the device."""
        return await self.async_on()

    async def async_unlock(self):
        """Unlock the device."""
        return await self.async_off()
