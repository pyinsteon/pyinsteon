"""Peek and poke command manager."""

import asyncio
import logging

from ..address import Address
from ..constants import ResponseStatus
from ..handlers.to_device.peek import PeekCommand
from ..handlers.to_device.poke import PokeCommand
from ..handlers.to_device.set_msb import SetMsbCommand
from ..subscriber_base import SubscriberBase
from ..topics import PEEK, POKE
from ..utils import publish_topic, subscribe_topic

_instances = {}
_LOGGER = logging.getLogger(__name__)


def get_peek_poke_manager(address: Address):
    """Return a peek/poke manager for a device."""
    address = Address(address)
    instance = _instances.get(address)
    if instance:
        return instance
    instance = PeekPokeManager(address)
    _instances[address] = instance
    return instance


class PeekPokeManager(SubscriberBase):
    """Peek and poke command manager."""

    def __init__(self, address):
        """Init the PeekPokeManager class."""
        self._address = Address(address)
        super().__init__(f"{self._address.id}.manager.peek_poke")
        self._peek_cmd = PeekCommand(self._address)
        self._poke_cmd = PokeCommand(self._address)
        self._set_msb_cmd = SetMsbCommand(self._address)
        self._peek_value_queue = asyncio.Queue()
        self._poke_value_queue = asyncio.Queue()
        self._peek_cmd.subscribe(self._receive_peek_value)
        self._peek_topic = f"{self._address.id}.manager.{PEEK}"
        self._poke_topic = f"{self._address.id}.manager.{POKE}"

    async def async_peek(self, mem_addr: int, extended: bool = False):
        """Peek a value at a memory address."""
        result = await self._async_peek(mem_addr=mem_addr)
        if result == ResponseStatus.SUCCESS:
            value = await self._peek_value_queue.get()
            publish_topic(topic=self._peek_topic, mem_addr=mem_addr, value=value)
            await asyncio.sleep(0.05)
        return result

    async def async_poke(self, mem_addr: int, value: int):
        """Poke a value at a memory address."""
        if 0 > value > 255:
            raise ValueError("Poke value can only be one byte.")
        result = await self._async_peek(mem_addr)
        if result == ResponseStatus.SUCCESS:
            orig_value = await self._peek_value_queue.get()
            if orig_value == value:
                self._call_subscribers(mem_addr=mem_addr, value=value)
                return ResponseStatus.SUCCESS
            result = await self._poke_cmd.async_send(value=value)
            if result == ResponseStatus.SUCCESS:
                publish_topic(topic=self._poke_topic, mem_addr=mem_addr, value=value)
                await asyncio.sleep(0.05)
        return result

    def subscribe_peek(self, listener: callable, force_strong_ref: bool = False):
        """Subscribe to the PEEK results."""
        if force_strong_ref and listener not in self._subscribers:
            _LOGGER.debug("Adding subscriber to persistant list")
            self._subscribers.append(listener)
        subscribe_topic(listener=listener, topic_name=self._peek_topic)

    def subscribe_poke(self, listener: callable, force_strong_ref: bool = False):
        """Subscribe to the POKE results."""
        if force_strong_ref and listener not in self._subscribers:
            _LOGGER.debug("Adding subscriber to persistant list")
            self._subscribers.append(listener)
        subscribe_topic(
            listener=listener, topic_name=f"{self._address.id}.manager.{POKE}"
        )

    async def _async_peek(self, mem_addr: int):
        """Execute the peek command."""
        mem_hi = mem_addr >> 8
        mem_lo = mem_addr & 0xFF
        while not self._peek_value_queue.empty():
            await self._peek_value_queue.get()
        result = await self._set_msb_cmd.async_send(high_byte=mem_hi)
        if result == ResponseStatus.SUCCESS:
            await asyncio.sleep(0.1)
            result = await self._peek_cmd.async_send(lsb=mem_lo)
        return result

    async def _receive_peek_value(self, value):
        """Place the last peek value in the queue."""
        await self._peek_value_queue.put(value)

    async def _receive_poke_value(self, value):
        """Place the last poke value in the queue."""
        await self._poke_value_queue.put(value)
