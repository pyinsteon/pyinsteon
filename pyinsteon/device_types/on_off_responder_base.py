"""Switched Lighting Control devices (CATEGORY 0x02)."""
from .on_off_controller_base import OnOffControllerBase
from .commands import ON_COMMAND, OFF_COMMAND
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.to_device.off import OffCommand



class OnOffResponderBase(OnOffControllerBase):
    """Switched Lighting Control device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=1):
        """Init the OnOffResponderBase class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons)
        for button in range(1, buttons + 1):
            self._setup_button(button)

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

    def _setup_button(self, group):
        super()._setup_button(group)
        state = self._states[group]
        state.add_handler(self._handlers[ON_COMMAND])
        state.add_handler(self._handlers[OFF_COMMAND])

    #pylint: disable=no-self-use
    def _set_name(self, name, group):
        if group > 1:
            return '{}_{}'.format(name, group)
        return name
