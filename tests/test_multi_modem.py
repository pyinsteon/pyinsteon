"""Multi-modem test harness (P2 acceptance criteria).

Demonstrates the cross-modem outbound collision in the current architecture
and encodes the acceptance contract for the address-routed write layer.

Root cause: `outbound_write_manager` (pyinsteon/protocol/messages/outbound.py)
is a module-level singleton. Every `Protocol.__init__` / connection overwrites
`outbound_write_manager.protocol_write = self.write`, so with two connected
modems ALL outbound traffic egresses the most recently connected modem,
regardless of which Insteon network the destination device lives on.

Tests:
    test_outbound_collision_last_writer_wins
        Documents today's broken behavior. PASSES on master. When the P2
        router lands, this test MUST be updated/removed (it will fail).
    test_acceptance_outbound_routes_by_address_ownership
        The post-refactor contract. @expectedFailure until the P2
        address-routed OutboundWriteManager exists.
"""
import asyncio
import unittest
from functools import partial

from pyinsteon.address import Address
from pyinsteon.protocol.messages.outbound import outbound_write_manager
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.utils import publish_topic

from tests import async_connect_mock, set_log_levels

# Devices notionally on two different physical Insteon networks.
DEVICE_ON_MODEM_A = Address("11.AA.AA")
DEVICE_ON_MODEM_B = Address("22.BB.BB")

SETTLE = 1.5  # async_connect sleeps 0.5s; writer loop needs headroom


class _MockModem:
    """A Protocol wired to a MockTransport with inspectable queues."""

    def __init__(self, name):
        self.name = name
        self.read_queue = asyncio.Queue()
        self.write_queue = asyncio.Queue()
        self.protocol = Protocol(
            connect_method=partial(
                async_connect_mock,
                self.read_queue,
                self.write_queue,
                random_nak=False,
                auto_ack=True,
            )
        )

    async def connect(self):
        await self.protocol.async_connect(retry=False)

    def close(self):
        self.protocol.close()

    def drain_writes(self):
        """Return all raw byte payloads written to this modem's transport."""
        out = []
        while not self.write_queue.empty():
            out.append(bytes(self.write_queue.get_nowait()))
        return out


def _writes_containing(writes, address: Address):
    """Filter writes to those carrying the given destination address."""
    needle = bytes(address)
    return [w for w in writes if needle in w]


class TestMultiModemOutbound(unittest.IsolatedAsyncioTestCase):
    """Two-mock-modem outbound routing tests."""

    async def asyncSetUp(self):
        set_log_levels(logger_topics=True)
        self.modem_a = _MockModem("A")
        self.modem_b = _MockModem("B")
        await self.modem_a.connect()
        await self.modem_b.connect()  # B connects LAST -> owns the global write fn

    async def asyncTearDown(self):
        outbound_write_manager.unregister_modem("modem_a")
        outbound_write_manager.unregister_modem("modem_b")
        self.modem_a.close()
        self.modem_b.close()
        await asyncio.sleep(0.1)

    async def test_outbound_collision_last_writer_wins(self):
        """Legacy fallback preserved: with NO ownership assigned, traffic
        follows the legacy protocol_write (last connected modem). This is
        the pre-P2 behavior, intentionally kept for single-modem
        back-compat when register_modem/assign_address are never called.
        """
        publish_topic(
            "send.on", address=DEVICE_ON_MODEM_A, on_level=255, group=0
        )
        await asyncio.sleep(SETTLE)

        writes_a = self.modem_a.drain_writes()
        writes_b = self.modem_b.drain_writes()

        # The wrong modem transmitted the command.
        self.assertTrue(
            _writes_containing(writes_b, DEVICE_ON_MODEM_A),
            "Legacy fallback should route to last-connected modem when "
            "no ownership is configured.",
        )
        # And the right modem stayed silent.
        self.assertFalse(
            _writes_containing(writes_a, DEVICE_ON_MODEM_A),
            "Modem A unexpectedly transmitted; global write fn "
            "no longer last-writer-wins.",
        )

    async def test_acceptance_outbound_routes_by_address_ownership(self):
        """P2 acceptance contract: writes route by address ownership."""
        outbound_write_manager.register_modem("modem_a", self.modem_a.protocol.write)
        outbound_write_manager.register_modem("modem_b", self.modem_b.protocol.write)
        outbound_write_manager.assign_address(DEVICE_ON_MODEM_A, "modem_a")
        outbound_write_manager.assign_address(DEVICE_ON_MODEM_B, "modem_b")

        publish_topic("send.on", address=DEVICE_ON_MODEM_A, on_level=255, group=0)
        publish_topic("send.on", address=DEVICE_ON_MODEM_B, on_level=255, group=0)
        await asyncio.sleep(SETTLE)

        writes_a = self.modem_a.drain_writes()
        writes_b = self.modem_b.drain_writes()

        self.assertTrue(_writes_containing(writes_a, DEVICE_ON_MODEM_A))
        self.assertTrue(_writes_containing(writes_b, DEVICE_ON_MODEM_B))
        # Isolation: neither modem carries the other's traffic.
        self.assertFalse(_writes_containing(writes_a, DEVICE_ON_MODEM_B))
        self.assertFalse(_writes_containing(writes_b, DEVICE_ON_MODEM_A))


if __name__ == "__main__":
    unittest.main()


class TestInsteonStackOwnership(unittest.IsolatedAsyncioTestCase):
    """P1 acceptance: stacks sync router ownership automatically."""

    async def asyncSetUp(self):
        from pyinsteon.insteon_stack import InsteonStack

        set_log_levels(logger_topics=True)
        self.stacks = {}
        self.queues = {}
        for name in ("stack_a", "stack_b"):
            stack = InsteonStack(name)
            read_q, write_q = asyncio.Queue(), asyncio.Queue()
            protocol = Protocol(
                connect_method=partial(
                    async_connect_mock,
                    read_q,
                    write_q,
                    random_nak=False,
                    auto_ack=True,
                ),
                modem_id=name,
            )
            await protocol.async_connect(retry=False)
            self.stacks[name] = (stack, protocol)
            self.queues[name] = write_q

    async def asyncTearDown(self):
        for name, (_stack, protocol) in self.stacks.items():
            protocol.close()
            outbound_write_manager.unregister_modem(name)
        await asyncio.sleep(0.1)

    def _drain(self, name):
        out = []
        while not self.queues[name].empty():
            out.append(bytes(self.queues[name].get_nowait()))
        return out

    async def test_device_add_assigns_ownership_automatically(self):
        """Adding a device to a stack's DeviceManager routes its traffic.

        No manual assign_address calls: DEVICE_LIST_CHANGED subscription
        inside InsteonStack must keep the router's ownership map in sync.
        """
        from pyinsteon.managers.device_id_manager import DeviceId

        stack_a, _ = self.stacks["stack_a"]
        stack_b, _ = self.stacks["stack_b"]
        stack_a.devices[DEVICE_ON_MODEM_A] = DeviceId(
            DEVICE_ON_MODEM_A, 0x02, 0x2A, 0x45
        )
        stack_b.devices[DEVICE_ON_MODEM_B] = DeviceId(
            DEVICE_ON_MODEM_B, 0x02, 0x2A, 0x45
        )

        publish_topic("send.on", address=DEVICE_ON_MODEM_A, on_level=255, group=0)
        publish_topic("send.on", address=DEVICE_ON_MODEM_B, on_level=255, group=0)
        await asyncio.sleep(SETTLE)

        writes_a = self._drain("stack_a")
        writes_b = self._drain("stack_b")

        self.assertTrue(_writes_containing(writes_a, DEVICE_ON_MODEM_A))
        self.assertTrue(_writes_containing(writes_b, DEVICE_ON_MODEM_B))
        self.assertFalse(_writes_containing(writes_a, DEVICE_ON_MODEM_B))
        self.assertFalse(_writes_containing(writes_b, DEVICE_ON_MODEM_A))

    async def test_device_removal_releases_ownership(self):
        """Removing a device unassigns it from the router."""
        from pyinsteon.managers.device_id_manager import DeviceId
        from pyinsteon.address import Address as Addr

        stack_a, _ = self.stacks["stack_a"]
        addr = Addr("33.CC.CC")
        stack_a.devices[addr] = DeviceId(addr, 0x02, 0x2A, 0x45)
        stack_a.devices[addr] = None  # removal path
        # Ownership released: router map must not reference stack_a
        owner = outbound_write_manager._address_owner.get(str(addr))
        self.assertIsNone(owner)


class TestModemTopicNamespacing(unittest.IsolatedAsyncioTestCase):
    """P3 acceptance: modem-scoped topics are attributable per modem."""

    async def asyncSetUp(self):
        set_log_levels(logger_topics=True)
        self.events = {"stack_a": [], "stack_b": [], "legacy": []}
        self.modems = {}
        from pyinsteon.utils import subscribe_topic as sub

        def _make_x10_cb(bucket):
            def _x10_cb(raw_x10, x10_flag):
                bucket.append("x10")
            return _x10_cb

        self._make_x10_cb = _make_x10_cb

        def make_cb(bucket, label):
            def _cb(**kwargs):
                bucket.append(label)
            return _cb

        # Subscribe BEFORE connecting so connection.made is captured
        self._cbs = []
        for name in ("stack_a", "stack_b"):
            cb = make_cb(self.events[name], "connection.made")
            self._cbs.append(cb)  # strong refs; pypubsub holds weakly
            sub(cb, f"modem_{name}.connection.made")
            cbx = self._make_x10_cb(self.events[name])
            self._cbs.append(cbx)
            sub(cbx, f"modem_{name}.x10_received")
        legacy_cb = self._make_x10_cb(self.events["legacy"])
        self._cbs.append(legacy_cb)
        sub(legacy_cb, "x10_received")

        for name in ("stack_a", "stack_b"):
            rq, wq = asyncio.Queue(), asyncio.Queue()
            p = Protocol(
                connect_method=partial(
                    async_connect_mock, rq, wq, random_nak=False, auto_ack=True
                ),
                modem_id=name,
            )
            await p.async_connect(retry=False)
            self.modems[name] = p

    async def asyncTearDown(self):
        for name, p in self.modems.items():
            p.close()
            outbound_write_manager.unregister_modem(name)
        await asyncio.sleep(0.1)

    async def test_connection_made_is_attributable(self):
        """Each modem's connection.made fires only on its own namespace."""
        await asyncio.sleep(0.2)
        self.assertEqual(self.events["stack_a"].count("connection.made"), 1)
        self.assertEqual(self.events["stack_b"].count("connection.made"), 1)

    async def test_x10_inbound_attributed_to_receiving_modem(self):
        """X10 frame into modem A fires A's namespace only, plus legacy."""
        x10_frame = bytes([0x02, 0x52, 0x6E, 0x00])
        self.modems["stack_a"].data_received(x10_frame)
        await asyncio.sleep(0.5)

        self.assertIn("x10", self.events["stack_a"])
        self.assertNotIn("x10", self.events["stack_b"])
        # Back-compat: legacy unprefixed topic still fires
        self.assertIn("x10", self.events["legacy"])

    async def test_reconnect_does_not_cross_modems(self):
        """Modem A reconnecting must not signal modem B's namespace."""
        a_before = self.events["stack_a"].count("connection.made")
        b_before = self.events["stack_b"].count("connection.made")
        # Simulate transport-level reconnect on A
        self.modems["stack_a"].connection_made(self.modems["stack_a"].transport)
        await asyncio.sleep(0.2)
        self.assertEqual(
            self.events["stack_a"].count("connection.made"), a_before + 1
        )
        self.assertEqual(self.events["stack_b"].count("connection.made"), b_before)


class TestModemContextRouting(unittest.IsolatedAsyncioTestCase):
    """Modem-scoped outbound commands route via MODEM_CONTEXT.

    Modem-scoped messages (get_im_info, all-linking, X10 broadcasts)
    carry no destination address. With two non-default modems, they
    must route to the context-designated modem — this is what makes a
    second hub's connect handshake possible at all.
    """

    async def asyncSetUp(self):
        set_log_levels(logger_topics=True)
        self.modems = {}
        for name in ("ctx_a", "ctx_b"):
            rq, wq = asyncio.Queue(), asyncio.Queue()
            p = Protocol(
                connect_method=partial(
                    async_connect_mock, rq, wq, random_nak=False, auto_ack=True
                ),
                modem_id=name,
            )
            await p.async_connect(retry=False)
            self.modems[name] = (p, wq)

    async def asyncTearDown(self):
        for name, (p, _wq) in self.modems.items():
            p.close()
            outbound_write_manager.unregister_modem(name)
        await asyncio.sleep(0.1)

    def _drain(self, name):
        out = []
        wq = self.modems[name][1]
        while not wq.empty():
            out.append(bytes(wq.get_nowait()))
        return out

    async def test_modem_scoped_command_routes_by_context(self):
        """get_im_info under ctx_b's context egresses modem B only."""
        from pyinsteon.protocol.messages.outbound import MODEM_CONTEXT

        token = MODEM_CONTEXT.set("ctx_b")
        try:
            publish_topic("send.get_im_info")
            await asyncio.sleep(SETTLE)
        finally:
            MODEM_CONTEXT.reset(token)

        writes_a = self._drain("ctx_a")
        writes_b = self._drain("ctx_b")
        get_im_info = bytes([0x02, 0x60])
        self.assertTrue(any(w.startswith(get_im_info) for w in writes_b))
        self.assertFalse(any(w.startswith(get_im_info) for w in writes_a))

    async def test_modem_scoped_command_without_context_is_dropped(self):
        """No context + two modems: modem-scoped command dropped, not crossed."""
        publish_topic("send.get_im_info")
        await asyncio.sleep(SETTLE)
        get_im_info = bytes([0x02, 0x60])
        for name in ("ctx_a", "ctx_b"):
            self.assertFalse(
                any(w.startswith(get_im_info) for w in self._drain(name))
            )
