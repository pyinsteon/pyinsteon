"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from . import Device
from ..handlers.to_device.on_level import OnLevelCommand
from ..handlers.from_device.on_level import OnLevelInbound
from ..handlers.to_device.off import OffCommand
from ..handlers.from_device.off import OffInbound
from ..handlers.to_device.on_fast import OnFastCommand
from ..handlers.from_device.on_fast import OnFastInbound
from ..handlers.to_device.off_fast import OffFastCommand
from ..handlers.from_device.off_fast import OffFastInbound
from ..handlers.to_device.status_request import (StatusRequestCommand,
                                                 StatusRequest3Command)
from ..states import DIMMABLE_LIGHT_STATE, DIMMABLE_FAN_STATE
from ..states.on_level import OnLevel
from ..events import (Event, ON_EVENT, ON_FAST_EVENT, OFF_EVENT, OFF_FAST_EVENT)  # ,
#                      FAN_ON_EVENT, FAN_ON_FAST_EVENT, FAN_OFF_EVENT,
#                      FAN_OFF_FAST_EVENT)
from ..constants import FanSpeed


ON_COMMAND = 'on_command'
ON_INBOUND = 'on_inbound'
OFF_COMMAND = 'off_command'
OFF_INBOUND = 'off_inbound'
ON_FAST_COMMAND = 'on_fast_command'
ON_FAST_INBOUND = 'on_fast_inbound'
OFF_FAST_COMMAND = 'off_fast_command'
OFF_FAST_INBOUND = 'off_fast_inbound'
STATUS_COMMAND = 'status_command'
STATUS_3_COMMAND = 'status_3_command'


class DimmableLightingControl(Device):
    """Dimmable Lighting Control Device."""

    def on(self, on_level=0xff, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default 0xff (full on). Set the device on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        self._handlers[command].send(on_level=on_level, group=0)

    async def async_on(self, on_level=0xff, fast=False):
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
        return await self._handlers[command].async_send(on_level=on_level, group=0)

    def off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[command].send()

    async def async_off(self, fast=False):
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
        return await self._handlers[command].async_send()

    def status(self):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send()

    async def async_status(self):
        """Request the status of the device.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        await self._handlers[STATUS_COMMAND].async_send()

    def _register_default_links(self):
        pass

    def _register_handlers(self):
        self._handlers[ON_COMMAND] = OnLevelCommand(self._address)
        self._handlers[ON_INBOUND] = OnLevelInbound(self._address)
        self._handlers[OFF_COMMAND] = OffCommand(self._address)
        self._handlers[OFF_INBOUND] = OffInbound(self._address)

        self._handlers[ON_FAST_COMMAND] = OnFastCommand(self._address)
        self._handlers[ON_FAST_INBOUND] = OnFastInbound(self._address)
        self._handlers[OFF_FAST_COMMAND] = OffFastCommand(self._address)
        self._handlers[OFF_FAST_INBOUND] = OffFastInbound(self._address)

        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)

    def _register_states(self):
        self._states[DIMMABLE_LIGHT_STATE] = OnLevel(
            name=DIMMABLE_LIGHT_STATE,
            address=self._address,
            handlers=[self._handlers[ON_COMMAND],
                      self._handlers[ON_INBOUND],
                      self._handlers[OFF_COMMAND],
                      self._handlers[OFF_INBOUND],
                      self._handlers[ON_FAST_COMMAND],
                      self._handlers[ON_FAST_INBOUND],
                      self._handlers[OFF_FAST_COMMAND],
                      self._handlers[OFF_FAST_INBOUND]],
            group=0)
        self._handlers[STATUS_COMMAND].subscribe(self._set_status)

    def _register_events(self):
        self._events[ON_EVENT] = Event(name=ON_EVENT,
                                       address=self._address,
                                       handlers=[self._handlers[ON_COMMAND],
                                                 self._handlers[ON_INBOUND]])
        self._events[OFF_EVENT] = Event(name=OFF_EVENT,
                                        address=self._address,
                                        handlers=[self._handlers[OFF_COMMAND],
                                                  self._handlers[OFF_INBOUND]])
        self._events[ON_FAST_EVENT] = Event(name=ON_FAST_EVENT,
                                            address=self._address,
                                            handlers=[self._handlers[ON_FAST_COMMAND],
                                                      self._handlers[ON_FAST_INBOUND]])
        self._events[OFF_FAST_EVENT] = Event(name=OFF_FAST_EVENT,
                                             address=self._address,
                                             handlers=[self._handlers[OFF_FAST_COMMAND],
                                                       self._handlers[OFF_FAST_INBOUND]])

    def _set_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[DIMMABLE_LIGHT_STATE].value = status


class DimmableLightingControl_2475F(DimmableLightingControl):
    """FanLinc model 2475F Dimmable Lighting Control.

    Device Class 0x01 subcat 0x2e
    """
    def fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the fan.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        # The send command converts to int
        self._handlers[command].send(on_level=on_level, group=2)

    async def async_fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass fan ramp rate otherwise
            turn on at the ramp rate.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        # The send command converts to int
        return await self._handlers[command].async_send(on_level=on_level, group=2)

    def fan_off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[command].send(group=2)

    async def async_fan_off(self, fast=False):
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
        return await self._handlers[command].async_send(group=2)

    def status(self):
        """Request the status of the light and the fan."""
        super().status()
        self.fan_status()

    async def async_status(self):
        """Request the status fo the light and the fan."""
        from ..handlers import ResponseStatus
        light_status = await super().async_status()
        fan_status = await self.async_fan_status()
        if light_status == fan_status == ResponseStatus.SUCCESS:
            return ResponseStatus.SUCCESS
        if light_status == ResponseStatus.UNCLEAR or fan_status == ResponseStatus.UNCLEAR:
            return ResponseStatus.UNCLEAR
        return ResponseStatus.FAILURE

    def light_status(self):
        """Request the status of the light."""
        super().status()

    async def async_light_status(self):
        """Request the status of the light."""
        return await super().async_status()

    def fan_status(self):
        """Request the status of the fan."""
        self._handlers[STATUS_3_COMMAND].send()

    async def async_fan_status(self):
        """Request the status of the fan.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        await self._handlers[STATUS_3_COMMAND].async_send()

    #pylint: disable=useless-super-delegation
    def _register_default_links(self):
        """Register default links."""
        super()._register_default_links()

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[STATUS_3_COMMAND] = StatusRequest3Command(self._address)

    def _register_states(self):
        super()._register_states()
        self._states[DIMMABLE_FAN_STATE] = OnLevel(
            name=DIMMABLE_FAN_STATE,
            address=self._address,
            handlers=[self._handlers[ON_COMMAND],
                      self._handlers[ON_INBOUND],
                      self._handlers[OFF_COMMAND],
                      self._handlers[OFF_INBOUND],
                      self._handlers[ON_FAST_COMMAND],
                      self._handlers[ON_FAST_INBOUND],
                      self._handlers[OFF_FAST_COMMAND],
                      self._handlers[OFF_FAST_INBOUND]],
            group=2)
        self._handlers[STATUS_3_COMMAND].subscribe(self._set_fan_status)

    def _register_events(self):
        super()._register_events()

    def _set_fan_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[DIMMABLE_FAN_STATE].value = status

#                                                         DimmableLightingControl_2334_222_6,
#                                                         DimmableLightingControl_2334_222_8)
