"""Check the monitor example's configuration and current callback interface."""

from pathlib import Path
import runpy
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyinsteon.constants import DeviceAction
from pyinsteon.managers.device_manager import DeviceManager

from tests.utils import async_case


@pytest.fixture
def monitor(tmp_path, monkeypatch):
    """Load the sample with a temporary configuration and no real connection."""
    (tmp_path / "secrets.yaml").write_text(
        "hub_username: test\nhub_password: test\naddress: 127.0.0.1\nport: 34567\n"
    )
    monkeypatch.chdir(tmp_path)
    return runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "samples/monitor.py")
    )


@async_case
async def test_device_callback_accepts_action(monitor, monkeypatch):
    """Subscribe through the real manager and handle its ADDED notification."""
    manager = DeviceManager()
    callback = monitor["device_added"]
    logger = MagicMock()
    monkeypatch.setitem(callback.__globals__, "_LOGGER", logger)
    manager.subscribe(callback)
    try:
        manager._call_subscribers(address="112233", action=DeviceAction.ADDED)
        logger.info.assert_called_once_with("Device added: %s", "112233")
        logger.reset_mock()
        for action in (DeviceAction.REMOVED, DeviceAction.COMPLETED):
            manager._call_subscribers(address="112233", action=action)
        logger.info.assert_not_called()
    finally:
        manager.unsubscribe(callback)


@async_case
async def test_monitor_passes_configured_port(monitor, monkeypatch):
    """Run setup using inert device calls and stop on the first monitoring wait."""

    class StopMonitoring(Exception):
        """End the sample's deliberate infinite loop."""

    namespace = monitor["run"].__globals__
    connect = AsyncMock()
    devices = MagicMock()
    devices.async_load = AsyncMock()
    devices.async_save = AsyncMock()
    devices.modem.async_get_configuration = AsyncMock()
    devices.modem.async_set_configuration = AsyncMock()
    monkeypatch.setitem(namespace, "async_connect", connect)
    monkeypatch.setitem(namespace, "devices", devices)
    monkeypatch.setitem(namespace, "set_log_levels", MagicMock())
    monkeypatch.setattr(
        namespace["asyncio"], "sleep", AsyncMock(side_effect=StopMonitoring)
    )
    with pytest.raises(StopMonitoring):
        await monitor["run"]()
    connect.assert_awaited_once_with(
        host="127.0.0.1", username="test", password="test", port=34567
    )
    devices.subscribe.assert_called_once_with(monitor["device_added"])
