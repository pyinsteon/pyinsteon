"""Peek and poke command manager."""

from ..address import Address
from ..const import ResponseStatus
from ..handlers.to_device.peek import PeekCommand
from ..handlers.to_device.poke import PokeCommand
from ..handlers.to_device.set_msb import SetMsbCommand
from ..subscriber_base import SubscriberBase


class PeekPokeManager(SubscriberBase):
    """Peek and poke command manager."""

    def __init__(self, address):
        """Init the PeekPokeManager class."""
        self._address = Address(address)
        self._peek_cmd = PeekCommand(self._address)
        self._poke_cmd = PokeCommand(self._address)
        self._set_msb_cmd = SetMsbCommand(self._address)

    async def async_peek(self, mem_addr: int):
        """Peek a value at a memory address."""
        mem_hi = mem_addr >> 8
        mem_lo = mem_addr & 0xFF
        result = await self._set_msb_cmd.async_send(msb=mem_hi)
        if result == ResponseStatus.SUCCESS:
            result = await self._peek_cmd.async_send(lsb=mem_lo)
        return result

    async def async_poke(self, mem_addr: int, value: int):
        """Poke a value at a memory address."""
        if value > 255:
            raise ValueError("Poke value can only be one byte.")
        result = await self.async_peek(mem_addr)
        if result == ResponseStatus.SUCCESS:
            result = self._poke_cmd.async_send(value=value)
        return result
