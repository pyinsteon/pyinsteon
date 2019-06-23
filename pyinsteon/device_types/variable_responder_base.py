"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..handlers.to_device.off import OffCommand
from ..handlers.to_device.off_fast import OffFastCommand
from ..handlers.to_device.on_fast import OnFastCommand
from ..handlers.to_device.on_level import OnLevelCommand
from .commands import (OFF_COMMAND, OFF_FAST_COMMAND, ON_COMMAND,
                       ON_FAST_COMMAND)
from .variable_controller_base import VariableControllerBase


class VariableResponderBase(VariableControllerBase):
    """Variable Responder Base Device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=1):
        """Init the VariableResponderBase class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons)
        for button in range(1, buttons + 1):
            self._setup_button(button)

    def on(self, on_level=0xff, group=0, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default 0xff (full on). Set the device on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        self._handlers[command].send(on_level=on_level, group=group)

    async def async_on(self, on_level=0xff, group=0, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default 0xff (full on). Set the device on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        return await self._handlers[command].async_send(on_level=on_level, group=group)

    def off(self, group=0, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[command].send(group=group)

    async def async_off(self, group=0, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        return await self._handlers[command].async_send(group=group)

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[ON_COMMAND] = OnLevelCommand(self._address)
        self._handlers[OFF_COMMAND] = OffCommand(self._address)

        self._handlers[ON_FAST_COMMAND] = OnFastCommand(self._address)
        self._handlers[OFF_FAST_COMMAND] = OffFastCommand(self._address)

    def _setup_button(self, group):
        super()._setup_button(group)
        state = self._states[group]
        state.add_handler(self._handlers[ON_COMMAND])
        state.add_handler(self._handlers[OFF_COMMAND])
        state.add_handler(self._handlers[ON_FAST_COMMAND])
        state.add_handler(self._handlers[OFF_FAST_COMMAND])
