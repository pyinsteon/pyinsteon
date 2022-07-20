"""Access control device types."""


from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..groups import ON_OFF_SWITCH
from .on_off_responder_base import OnOffResponderBase


class AccessControl_Morningstar(OnOffResponderBase):
    """Access Control MorningStar device."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
        state_name=ON_OFF_SWITCH,
        on_event_name=ON_EVENT,
        off_event_name=OFF_EVENT,
        on_fast_event_name=ON_FAST_EVENT,
        off_fast_event_name=OFF_FAST_EVENT,
    ):
        """Init the OnOffResponderBase class."""
        buttons = {1: ON_OFF_SWITCH} if buttons is None else buttons
        super().__init__(
            address,
            cat,
            subcat,
            firmware,
            description,
            model,
            buttons,
            on_event_name,
            off_event_name,
            on_fast_event_name,
            off_fast_event_name,
        )

    async def async_lock(self):
        """Lock the device."""
        return await self.async_on()

    async def async_unlock(self):
        """Unlock the device."""
        return await self.async_off()
