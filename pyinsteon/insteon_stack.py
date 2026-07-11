"""Per-modem container for multi-modem Insteon deployments.

An ``InsteonStack`` bundles everything scoped to one physical modem
(PLM or Hub): its connection, its ``DeviceManager``, its link manager,
and its saved-device file. It also keeps the outbound write router's
address-ownership map in sync as devices are added and removed, so
direct messages always egress the correct modem.

Single-modem usage is unchanged: the module-level ``pyinsteon.devices``
and ``pyinsteon.async_connect`` are backed by a default stack.

Multi-modem usage:

    from pyinsteon import async_connect, devices
    from pyinsteon.insteon_stack import InsteonStack

    # Modem 1 (legacy API, modem_id "default")
    await async_connect(host="192.168.1.10", username=..., password=...)

    # Modem 2
    barn = InsteonStack("barn")
    await barn.async_connect(host="192.168.1.20", username=..., password=...)
    await barn.async_load(workdir="/config")  # insteon_devices_barn.json
"""
import asyncio
from contextlib import contextmanager
import logging

from .constants import DeviceAction
from .managers.device_link_manager import DeviceLinkManager
from .managers.device_manager import DeviceManager
from .protocol import async_modem_connect
from .protocol.messages.outbound import (
    DEVICE_MANAGER_CONTEXT,
    MODEM_CONTEXT,
    outbound_write_manager,
)
from .utils import modem_topic_prefix, subscribe_topic, unsubscribe_topic

_LOGGER = logging.getLogger(__name__)

DEFAULT_MODEM_ID = "default"
LEGACY_DEVICE_FILE = "insteon_devices.json"


class InsteonStack:
    """All state for one Insteon modem: connection, devices, links, routing."""

    def __init__(self, modem_id=DEFAULT_MODEM_ID, devices=None, link_manager=None):
        """Init the InsteonStack.

        Parameters:
            modem_id: Routing identity for this modem. Must be unique per
                stack within the process.
            devices: Optional existing DeviceManager to adopt (used by the
                module-level default stack for backward compatibility).
            link_manager: Optional existing DeviceLinkManager to adopt.
        """
        self._modem_id = modem_id
        self._devices = devices if devices is not None else DeviceManager()
        self._link_manager = (
            link_manager
            if link_manager is not None
            else DeviceLinkManager(self._devices)
        )
        self._devices.subscribe(self._device_list_changed)

    @property
    def modem_id(self):
        """Return the routing identity of this stack's modem."""
        return self._modem_id

    @property
    def devices(self):
        """Return this stack's DeviceManager."""
        return self._devices

    @property
    def link_manager(self):
        """Return this stack's DeviceLinkManager."""
        return self._link_manager

    @property
    def modem(self):
        """Return this stack's modem device (None before connect)."""
        return self._devices.modem

    @contextmanager
    def modem_context(self):
        """Route modem-scoped outbound messages to this stack's modem.

        Use around pyinsteon module-level operations that address the
        modem rather than a device (all-linking, X10 broadcasts, scene
        triggers, modem ALDB access).
        """
        token = MODEM_CONTEXT.set(self._modem_id)
        mgr_token = DEVICE_MANAGER_CONTEXT.set(self._devices)
        try:
            yield self
        finally:
            DEVICE_MANAGER_CONTEXT.reset(mgr_token)
            MODEM_CONTEXT.reset(token)

    @property
    def topic_prefix(self):
        """Return this stack's modem-scoped pubsub topic prefix."""
        return modem_topic_prefix(self._modem_id)

    def subscribe_connection_made(self, callback):
        """Subscribe to this modem's connection.made events."""
        subscribe_topic(callback, f"{self.topic_prefix}.connection.made")

    def subscribe_connection_failed(self, callback):
        """Subscribe to this modem's connection.failed events."""
        subscribe_topic(callback, f"{self.topic_prefix}.connection.failed")

    def unsubscribe_connection_made(self, callback):
        """Unsubscribe from this modem's connection.made events."""
        unsubscribe_topic(callback, f"{self.topic_prefix}.connection.made")

    def unsubscribe_connection_failed(self, callback):
        """Unsubscribe from this modem's connection.failed events."""
        unsubscribe_topic(callback, f"{self.topic_prefix}.connection.failed")

    @property
    def device_file(self):
        """Return the saved-device filename for this stack.

        The default stack keeps the legacy filename so existing
        single-modem deployments load their cache unchanged.
        """
        if self._modem_id == DEFAULT_MODEM_ID:
            return LEGACY_DEVICE_FILE
        return f"insteon_devices_{self._modem_id}.json"

    async def async_connect(
        self,
        device=None,
        host=None,
        port=None,
        username=None,
        password=None,
        hub_version=2,
        **kwargs,
    ):
        """Connect this stack to its Insteon modem.

        Accepts the same parameters as ``pyinsteon.async_connect`` and
        returns this stack.
        """
        modem = await async_modem_connect(
            device=device,
            host=host,
            port=port,
            username=username,
            password=password,
            hub_version=hub_version,
            modem_id=self._modem_id,
            **kwargs,
        )
        self._devices.modem = modem
        outbound_write_manager.assign_address(modem.address, self._modem_id)
        self._sync_ownership()
        self._devices.id_manager.start()
        await self._devices.modem.async_get_configuration()
        return self

    async def async_close(self):
        """Close this stack's connection and stop its tasks."""
        with self.modem_context():
            if self._devices.modem is not None:
                await self._devices.modem.async_close()
        for addr in self._devices:
            if self._devices[addr].is_battery:
                self._devices[addr].close()
        self._devices.id_manager.close()
        outbound_write_manager.unregister_modem(self._modem_id)
        await asyncio.sleep(0.1)

    async def async_load(self, workdir="", id_devices=1, load_modem_aldb=1):
        """Load this stack's devices from its per-modem saved-device file."""
        with self.modem_context():
            result = await self._devices.async_load(
                workdir=workdir,
                id_devices=id_devices,
                load_modem_aldb=load_modem_aldb,
                device_file=self.device_file,
            )
        self._sync_ownership()
        return result

    async def async_save(self, workdir):
        """Save this stack's devices to its per-modem saved-device file."""
        return await self._devices.async_save(
            workdir=workdir, device_file=self.device_file
        )

    def _sync_ownership(self):
        """Assign every known device address to this stack's modem."""
        for addr in self._devices:
            outbound_write_manager.assign_address(addr, self._modem_id)

    def _device_list_changed(self, address, action):
        """Keep router ownership in sync with device list changes."""
        if address is None:
            return
        if action == DeviceAction.ADDED:
            outbound_write_manager.assign_address(address, self._modem_id)
        elif action == DeviceAction.REMOVED:
            outbound_write_manager.unassign_address(address)
