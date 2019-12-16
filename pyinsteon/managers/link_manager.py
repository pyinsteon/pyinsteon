"""Manage links beteween devices."""
import logging
from ..device_types.device_base import Device
from .. import devices
from ..constants import AllLinkMode, ResponseStatus
from ..handlers.to_device.enter_linking_mode import EnterLinkingModeCommand
from ..handlers.to_device.enter_unlinking_mode import EnterUnlinkingModeCommand
from ..handlers.start_all_linking import StartAllLinkingCommandHandler
from ..handlers.all_link_completed import AllLinkCompletedHandler
from ..utils import multiple_status
from ..aldb import ALDBRecord


TIMEOUT = 3
_LOGGER = logging.getLogger(__name__)


async def async_enter_linking_mode(is_controller: bool, group: int):
    """Put the Insteon Modem into linking mode."""
    link_cmd = StartAllLinkingCommandHandler()
    mode = AllLinkMode.CONTROLLER if is_controller else AllLinkMode.RESPONDER
    response = await link_cmd.async_send(mode=mode, group=group)
    _LOGGER.debug("Enter linking mode response: %s", str(response))
    return response


async def async_enter_unlinking_mode(group: int):
    """Put the Insteon Modem into unlinking mode."""
    link_cmd = StartAllLinkingCommandHandler()
    mode = AllLinkMode.DELETE
    response = await link_cmd.async_send(mode=mode, group=group)
    _LOGGER.info("Enter linking mode response: %s", str(response))
    return response


async def async_link_devices(
    controller: Device, responder: Device, group: int = 0, data1=255, data2=28, data3=1
):
    """Link two devices."""
    from ..handlers import ResponseStatus

    if _add_link_to_device(
        device=controller,
        target=responder.address,
        group=group,
        is_controller=True,
        data1=responder.cat,
        data2=responder.subcat,
        data3=responder.firmware,
    ) and _add_link_to_device(
        device=responder,
        target=controller.address,
        group=group,
        is_controller=False,
        data1=data1,
        data2=data2,
        data3=data3,
    ):
        written_1, failed_1 = await controller.aldb.async_write()
        written_2, failed_2 = await responder.aldb.async_write()
        if failed_1 or failed_2:
            return ResponseStatus.FAILURE
        return ResponseStatus.SUCCESS


async def async_unlink_devices(controller: Device, responder: Device, group: int = 0):
    """Unlink two devices."""
    if _remove_link_from_device(
        device=controller, is_controller=True, group=group, target=responder.address
    ) and _remove_link_from_device(
        device=responder, is_controller=False, group=group, target=controller.address
    ):
        write_1, failed_1 = await controller.aldb.async_write()
        write_2, failed_2 = await responder.aldb.async_write()
        if failed_1 or failed_2:
            return ResponseStatus.FAILURE
        return ResponseStatus.SUCCESS
    return ResponseStatus.FAILURE


async def async_add_default_links(device: Device):
    """Setup the default links for a device."""
    for link in device.default_links:
        if link.is_controller:
            controller = device
            responder = devices.modem
            data1 = link.modem_data1
            data2 = link.modem_data2
            data3 = link.modem_data3
        else:
            controller = devices.modem
            responder = device
            data1 = link.dev_data1
            data2 = link.dev_data2
            data3 = link.dev_data3
        await async_link_devices(controller, responder, link.group, data1, data2, data3)


def _remove_link_from_device(device, is_controller, group, target):
    found_rec = None
    for addr in device.aldb:
        rec = device.aldb[addr]
        if (
            rec.target == target
            and rec.is_controller == is_controller
            and rec.group == group
        ):
            found_rec = rec
    if found_rec:
        device.aldb.remove(found_rec.mem_addr)
    return True


async def async_create_default_links(device: Device):
    """Establish default links between the modem and device."""

    if not device.aldb.is_loaded:
        await device.aldb.async_load()

    if not device.aldb.is_loaded:
        return False

    results = []
    for link_info in device.default_links:
        is_controller = link_info.is_controller
        group = link_info.group
        data1 = link_info.data1
        data2 = link_info.data2
        data3 = link_info.data3
        if is_controller:
            controller = device
            responder = devices.modem
        else:
            controller = devices.modem
            responder = device
        await async_link_devices(controller, responder, group, data1, data2, data3)


def _add_link_to_device(device, is_controller, group, target, data1, data2, data3):
    """Add a link to a device."""
    try:
        device.aldb.add(
            group=group,
            target=target,
            controller=is_controller,
            data1=data1,
            data2=data2,
            data3=data3,
        )
    except NotImplementedError:
        return False
    return True
