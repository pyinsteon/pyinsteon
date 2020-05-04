"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..handlers.to_device.off import OffCommand
from ..handlers.to_device.off_fast import OffFastCommand
from ..handlers.to_device.on_fast import OnFastCommand
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.to_device.status_request import StatusRequestCommand
from .commands import (
    OFF_COMMAND,
    OFF_FAST_COMMAND,
    ON_COMMAND,
    ON_FAST_COMMAND,
    STATUS_COMMAND,
)
from .variable_controller_base import VariableControllerBase


class VariableResponderBase(VariableControllerBase):
    """Variable Responder Base Device."""

    def on(self, on_level=0xFF, group=0, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default 0xff (full on). Set the device on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        """
        group = 1 if not group else group
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        self._handlers[group][command].send(on_level=on_level)

    async def async_on(self, on_level=0xFF, group=0, fast=False):
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
        group = 1 if not group else group
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        return await self._handlers[group][command].async_send(on_level)

    def off(self, group=0, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        """
        group = 1 if not group else group
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[group][command].send()

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
        group = 1 if not group else group
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        return await self._handlers[group][command].async_send()

    async def async_status(self):
        """Get the status of the device state."""
        return await self._handlers[STATUS_COMMAND].async_send()

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)
        for group in self._buttons:
            if self._handlers.get(group) is None:
                self._handlers[group] = {}
            self._handlers[group][ON_COMMAND] = OnLevelCommand(self._address, group)
            self._handlers[group][OFF_COMMAND] = OffCommand(self._address, group)
            self._handlers[group][ON_FAST_COMMAND] = OnFastCommand(self._address, group)
            self._handlers[group][OFF_FAST_COMMAND] = OffFastCommand(
                self._address, group
            )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        for group in self._buttons:
            state = self._groups[group]

            self._handlers[group][ON_COMMAND].subscribe(state.set_value)
            self._handlers[group][OFF_COMMAND].subscribe(state.set_value)
            self._handlers[group][ON_FAST_COMMAND].subscribe(state.set_value)
            self._handlers[group][OFF_FAST_COMMAND].subscribe(state.set_value)
