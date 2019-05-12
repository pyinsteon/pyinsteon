"""Manage links beteween devices."""
import asyncio
from collections import namedtuple
from ..device_types import Device
from .. import devices
from ..constants import AllLinkMode
from ..handlers.to_device.enter_linking_mode import EnterLinkingModeCommand
from ..handlers.to_device.enter_unlinking_mode import EnterUnlinkingModeCommand
from ..handlers.start_all_linking import StartAllLinkingCommandHandler

link_queue = asyncio.Queue()
TIMEOUT = 3
LinkInfo = namedtuple('LinkInfo', 'controller responder group cat subcat firmware')

async def async_link_devices(controller: Device, responder: Device, group: int = 0):
    """Link two devices."""
    c_link_cmd = _set_linking_command(controller)
    r_link_cmd = _set_linking_command(responder)
    c_link_cmd.subscribe(_link_complete)
    r_link_cmd.subscribe(_link_complete)
    _send_linking_command(c_link_cmd, AllLinkMode.CONTROLLER, group)
    _send_linking_command(r_link_cmd, AllLinkMode.RESPONDER, group)
    try:
        response1, response2 = await asyncio.wait_for(_wait_for_link_complete(), timeout=TIMEOUT)
    except asyncio.TimeoutError:
        return None
    return _parse_responses(controller, responder, group, response1, response2)


async def async_unlink_devices(controller: Device, responder: Device, group: int = 0):
    """Unlink two devices."""
    c_link_cmd = _set_unlinking_command(controller)
    r_link_cmd = _set_unlinking_command(responder)
    c_link_cmd.subscribe(_link_complete)
    r_link_cmd.subscribe(_link_complete)
    _send_unlinking_command(c_link_cmd, group)
    await asyncio.sleep(.1)
    _send_unlinking_command(r_link_cmd, group)
    try:
        response1, response2 = asyncio.wait_for(_wait_for_link_complete(), timeout=TIMEOUT)
    except asyncio.TimeoutError:
        return None
    return _parse_responses(controller, responder, group, response1, response2)


def _set_linking_command(device):
    if device == devices.modem:
        return StartAllLinkingCommandHandler()
    return EnterLinkingModeCommand(device.address)


def _set_unlinking_command(device):
    if device == devices.modem:
        return StartAllLinkingCommandHandler()
    return EnterUnlinkingModeCommand(device.address)


def _send_linking_command(cmd, mode, group):
    if isinstance(cmd, StartAllLinkingCommandHandler):
        cmd.send(mode=mode, group=group)
    else:
        cmd.send(group=group)


def _send_unlinking_command(cmd, group):
    if isinstance(cmd, StartAllLinkingCommandHandler):
        cmd.send(mode=AllLinkMode.DELETE, group=group)
    else:
        cmd.send(group=group)


def _link_complete(**kwargs):
    """Wait for the linking command to complete."""
    link_queue.put_nowait(kwargs)


async def _wait_for_link_complete():
    response1 = await link_queue.get()
    response2 = await link_queue.get()
    return (response1, response2)


def _parse_responses(controller, responder, group, response1, response2):
    cat = response1.get('cat') if response1.get('cat') else response2.get('cat')
    subcat = response1.get('subcat') if response1.get('subcat') else response2.get('subcat')
    firmware = response1.get('firmware') if response1.get('firmware') else response2.get('firmware')
    return LinkInfo(controller, responder, group, cat, subcat, firmware)
