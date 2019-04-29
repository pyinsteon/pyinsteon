"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from . import Device
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.from_device.on_level import OnLevelInbound
from ..handlers.to_device.off import OffCommand
from ..handlers.from_device.off import OffInbound
from ..handlers.to_device.status_request import StatusRequestCommand
from ..states.on_level import OnLevel

ON_COMMAND = 'on_command'
ON_INBOUND = 'on_inbound'
OFF_COMMAND = 'off_command'
OFF_INBOUND = 'off_inbound'
STATUS_COMMAND = 'status_command'


class DimmableLightingControl(Device):
    """Dimmable Lighting Control Device."""

    def on(self, on_level=0xff, group=0):
        """Turn on the device."""
        self._handlers[ON_COMMAND].send(on_level=on_level, group=group)

    async def async_on(self, on_level=0xff, group=0):
        """Turn on the device."""
        return await self._handlers[ON_COMMAND].async_send(on_level=on_level, group=group)

    def off(self):
        """Turn off the device."""
        self._handlers[OFF_COMMAND].send()

    async def async_off(self):
        """Turn off the device."""
        return await self._handlers[OFF_COMMAND].async_send()

    def status(self):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self):
        """Request the status of the device."""
        await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers(self):
        self._handlers[ON_COMMAND] = OnLevelCommand(self._address)
        self._handlers[ON_INBOUND] = OnLevelInbound(self._address)
        self._handlers[OFF_COMMAND] = OffCommand(self._address)
        self._handlers[OFF_INBOUND] = OffInbound(self._address)
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)

    def _register_states(self):
        self._states[0] = OnLevel('dimmable_switch', [self._handlers[ON_COMMAND],
                                                      self._handlers[ON_INBOUND],
                                                      self._handlers[OFF_COMMAND],
                                                      self._handlers[OFF_INBOUND]])
        self._handlers[STATUS_COMMAND].subscribe(self._set_status)

    def _set_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[0].set_value(status)
