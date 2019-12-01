"""Manage links beteween devices."""
import asyncio
from collections import namedtuple
import logging
from ..device_types import Device
from .. import devices
from ..constants import AllLinkMode
from ..handlers.to_device.enter_linking_mode import EnterLinkingModeCommand
from ..handlers.to_device.enter_unlinking_mode import EnterUnlinkingModeCommand
from ..handlers.start_all_linking import StartAllLinkingCommandHandler
from ..handlers.all_link_completed import AllLinkCompletedHandler

link_queue = asyncio.Queue()
TIMEOUT = 3
LinkInfo = namedtuple('LinkInfo', 'controller responder group cat subcat firmware')
DefaultLink = namedtuple('DefaultLink', 'controller group dev_data1 dev_data2 dev_data3 '
                         'modem_data1 modem_data2 modem_data3')
_LOGGER = logging.getLogger(__name__)


async def async_enter_linking_mode(is_controller: bool, group: int):
    """Put the Insteon Modem into linking mode."""
    link_cmd = _set_linking_command(devices.modem)
    mode = AllLinkMode.CONTROLLER if is_controller else AllLinkMode.RESPONDER
    response = await link_cmd.async_send(mode=mode, group=group)
    _LOGGER.info('Enter linking mode response: %s', str(response))
    return response


async def async_enter_unlinking_mode(group: int):
    """Put the Insteon Modem into unlinking mode."""
    link_cmd = _set_unlinking_command(devices.modem)
    mode = AllLinkMode.DELETE
    response = await link_cmd.async_send(mode=mode, group=group)
    _LOGGER.info('Enter linking mode response: %s', str(response))
    return response


async def async_link_devices(controller: Device, responder: Device, group: int = 0):
    """Link two devices."""
    from ..handlers import ResponseStatus
    c_link_cmd = _set_linking_command(controller)
    r_link_cmd = _set_linking_command(responder)
    c_response = await _send_linking_command(c_link_cmd, AllLinkMode.CONTROLLER, group)
    if not c_response == ResponseStatus.SUCCESS:
        return False
    r_response = await _send_linking_command(r_link_cmd, AllLinkMode.RESPONDER, group)
    if not r_response == ResponseStatus.SUCCESS:
        return False
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


async def async_create_default_links(device: Device):
    """Establish default links between the modem and device."""
    modem = devices.modem
    retry = 0
    while not device.aldb.is_loaded and retry < 3:
        await device.aldb.async_load()
        retry += 1
    if not device.aldb.is_loaded:
        return False
    for link_info in device.default_links:
        is_controller = link_info.controller == AllLinkMode.CONTROLLER

        # if not _has_existing_link(modem, not is_controller, link_info.group, device.address):
        _add_link_to_device(modem, not is_controller, link_info.group, device.address,
                            link_info.modem_data1, link_info.modem_data2, link_info.modem_data3)

        # if not _has_existing_link(device, is_controller, link_info.group, device.address):
        _add_link_to_device(device, is_controller, link_info.group, modem.address,
                            link_info.dev_data1, link_info.dev_data2, link_info.dev_data3)
        result_modem = await modem.aldb.async_write_records()
        result_device = await device.aldb.async_write_records()
        _LOGGER.info('Modem: %s', str(result_modem))
        _LOGGER.info('Device: %s', str(result_device))


def _existing_link(device, is_controller, group, address):
    """Test if a link exists in a device ALDB."""
    for mem_addr in device.aldb:
        rec = device.aldb[mem_addr]
        if (rec.is_controller == is_controller and
                rec.target == device.address and
                rec.group == group):
            return rec.mem_addr
    return None


def _add_link_to_device(device, is_controller, group, target, data1, data2, data3):
    """Add a link to a device."""
    try:
        device.aldb.add(group=group, target=target, controller=is_controller,
                        data1=data1, data2=data2, data3=data3)
    except NotImplementedError:
        return False
    return True


def _set_linking_command(device):
    if device == devices.modem:
        return StartAllLinkingCommandHandler()
    cmd = EnterLinkingModeCommand(device.address)
    cmd.subscribe(_link_complete)
    return cmd


def _set_unlinking_command(device):
    if device == devices.modem:
        return StartAllLinkingCommandHandler()
    return EnterUnlinkingModeCommand(device.address)


async def _send_linking_command(cmd, mode, group):
    if isinstance(cmd, StartAllLinkingCommandHandler):
        return await cmd.async_send(mode=mode, group=group)
    return await cmd.async_send(group=group)


async def _send_unlinking_command(cmd, group):
    if isinstance(cmd, StartAllLinkingCommandHandler):
        return await cmd.async_send(mode=AllLinkMode.DELETE, group=group)
    return await cmd.async_send(group=group)


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


all_link_complete_handler = AllLinkCompletedHandler()
all_link_complete_handler.subscribe(_link_complete)
