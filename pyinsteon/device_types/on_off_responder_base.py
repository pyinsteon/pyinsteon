"""Switched Lighting Control devices (CATEGORY 0x02)."""
from .on_off_controller_base import OnOffControllerBase
from .commands import ON_COMMAND, OFF_COMMAND
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.to_device.off import OffCommand
from ..states import ON_OFF_SWITCH_STATE



class OnOffResponderBase(OnOffControllerBase):
    """Switched Lighting Control device."""

    def on(self):
        """Turn on the device."""
        self._handlers[ON_COMMAND].send(on_level=0xff, group=0)

    async def async_on(self):
        """Turn on the device."""
        await self._handlers[ON_COMMAND].async_send(on_level=0xff, group=0)

    def off(self):
        """Turn off the device."""
        self._handlers[OFF_COMMAND].send()

    async def async_off(self):
        """Turn off the device."""
        await self._handlers[OFF_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[ON_COMMAND] = OnLevelCommand(self._address)
        self._handlers[OFF_COMMAND] = OffCommand(self._address)

    def _register_states(self):
        super()._register_states()
        state = self._states[ON_OFF_SWITCH_STATE]
        state.add_handler(self._handlers[ON_COMMAND])
        state.add_handler(self._handlers[OFF_COMMAND])
