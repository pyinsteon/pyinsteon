"""Test the link manager."""

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock
import warnings

from pyinsteon import devices
from pyinsteon.constants import AllLinkMode, EngineVersion, ResponseStatus
from pyinsteon.device_types.hub import Hub
from pyinsteon.managers import link_manager

from tests import load_devices, set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics

test_lock = asyncio.Lock()


def _reset_devices(addresses):
    """Reset the device ALDB pending records."""
    for addr in addresses:
        device = devices[addr]
        device.async_status = AsyncMock()
        device.aldb.clear_pending()
        device.aldb.async_write = AsyncMock()
        device.aldb.async_write.call_count = 0
        device.aldb.clear = Mock()
        device.async_status.return_value = ResponseStatus.SUCCESS


def _add_rec_to_aldb(device, record):
    """Add a record to a device ALDB."""
    hwm = None
    for rec in device.aldb.find(target="000000"):
        hwm = rec
        break

    if record.mem_addr == 0:
        record.mem_addr = hwm.mem_addr
        hwm.mem_addr = hwm.mem_addr - 8
        records = {record.mem_addr: record, hwm.mem_addr: hwm}
    else:
        records = {record.mem_addr: record}
    device.aldb.load_saved_records(device.aldb.status, records)
    return record.mem_addr


async def _load_devices(lock):
    """Set up the devices and modem."""
    async with lock:
        if not devices.modem or devices.modem.address.id != "111111":
            pass
        modem = Hub("111111", 0x03, 51, 165, "Instoen modem")
        devices.modem = modem
        await load_devices(devices)
        await asyncio.sleep(0.3)
        _reset_devices(list(devices))


class TestLinkManager(unittest.TestCase):
    """Test the LinkManager class."""

    def setUp(self) -> None:
        """Set up the tests."""
        set_log_levels(logger_topics=True, logger_messages="debug")

    @async_case
    async def test_modem_linking_mode(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        modem_link_topic = "ack.start_all_linking"
        topics = [TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5)]
        send_topics(topic_items=topics)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.UNSENT

    @async_case
    async def test_linking_with_i2c_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.I2CS), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_linking_with_i1_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.I1), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert not async_send.call_args[1]["extended"]

    @async_case
    async def test_linking_with_unknown_device_engine(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        # Easiest way to produce an unknown engine version response
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.UNKNOWN), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_linking_with_device_engine_direct_nak(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_nak = (
            f"{address.id}.get_insteon_engine_version.direct_nak"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        # Easiest way to produce an unknown engine version response
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(ResponseStatus.DIRECT_NAK_ALDB), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_nak, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_linking_with_existing_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = devices["2b2b2b"].address
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_linking_with_unresponsive_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = devices["2b2b2b"].address
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_linking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_linking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.FAILURE)
        link_manager.EnterLinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_linking_mode(
            link_mode=AllLinkMode.CONTROLLER, group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.FAILURE
        assert async_send.call_count == 6

    @async_case
    async def test_modem_unlinking_mode(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        modem_link_topic = "ack.start_all_linking"
        topics = [TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5)]
        send_topics(topic_items=topics)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(group=0)
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.UNSENT

    @async_case
    async def test_unlinking_with_i2c_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.I2CS), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_unlinking_with_i1_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.I1), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert not async_send.call_args[1]["extended"]

    @async_case
    async def test_unlinking_with_unknown_device_engine(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_ack = (
            f"{address.id}.get_insteon_engine_version.direct_ack"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        # Easiest way to produce an unknown engine version response
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(EngineVersion.UNKNOWN), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_ack, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_unlinking_with_device_engine_direct_nak(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = random_address()
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Engine version topics
        engine_version_ack = f"ack.{address.id}.get_insteon_engine_version.direct"
        engine_version_direct_nak = (
            f"{address.id}.get_insteon_engine_version.direct_nak"
        )
        engine_version_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        # Easiest way to produce an unknown engine version response
        engine_version_kwargs = cmd_kwargs(
            0x0D, int(ResponseStatus.DIRECT_NAK_ALDB), None, modem.address
        )

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(engine_version_ack, engine_version_ack_kwargs, 0.5),
            TopicItem(engine_version_direct_nak, engine_version_kwargs, 0.5),
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_unlinking_with_existing_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = devices["2b2b2b"].address
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.SUCCESS)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.SUCCESS
        assert async_send.call_args[1]["extended"]

    @async_case
    async def test_unlinking_with_unresponsive_device(self):
        """Test placing the modem into linking mode."""

        await _load_devices(test_lock)
        address = devices["2b2b2b"].address
        modem = devices.modem
        modem_link_topic = "ack.start_all_linking"

        # Device link topics
        device_link_ack = f"ack.{address.id}.enter_unlinking_mode.direct"
        device_link_ack_kwargs = cmd_kwargs(0x0D, 0x00, None)
        device_link_dir_ack = f"{address.id}.enter_unlinking_mode.direct_ack"
        device_link_dir_ack_kwargs = cmd_kwargs(0x0D, 0x00, None, modem.address)

        topics = [
            TopicItem(modem_link_topic, {"link_mode": 0x01, "group": 0}, 0.5),
            TopicItem(device_link_ack, device_link_ack_kwargs, 0.5),
            TopicItem(device_link_dir_ack, device_link_dir_ack_kwargs, 0.5),
        ]
        send_topics(topic_items=topics)

        async_send = AsyncMock(return_value=ResponseStatus.FAILURE)
        link_manager.EnterUnlinkingModeCommand.async_send = async_send

        # A RuntimeWarning is raised when creating the EnterLinkingModeCommand due to the AsyncMock above
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        modem_resp, device_resp = await link_manager.async_enter_unlinking_mode(
            group=0, address=address
        )
        assert modem_resp == ResponseStatus.SUCCESS
        assert device_resp == ResponseStatus.FAILURE
        assert async_send.call_count == 6
