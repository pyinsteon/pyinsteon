"""Manage links beteween devices."""
import logging

from ...constants import AllLinkMode, LinkStatus, ResponseStatus
from ...handlers.start_all_linking import StartAllLinkingCommandHandler

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
    return response


async def async_link_devices(
    controller, responder, group: int = 0, data1=255, data2=28, data3=1
):
    """Link two devices."""

    if not hasattr(controller, "address") or not hasattr(responder, "address"):
        raise TypeError("controller and responder must be devices")
    if _add_link_to_device(
        device=controller,
        target=responder.address,
        group=group,
        is_controller=True,
        data1=int(responder.cat),
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
        _, failed_1 = await controller.aldb.async_write()
        _, failed_2 = await responder.aldb.async_write()
        if failed_1 or failed_2:
            return ResponseStatus.FAILURE
        return ResponseStatus.SUCCESS


async def async_unlink_devices(controller, responder, group: int = 0):
    """Unlink two devices."""
    if not hasattr(controller, "address") or not hasattr(responder, "address"):
        raise TypeError("controller and responder must be devices")
    if _remove_link_from_device(
        device=controller, is_controller=True, group=group, target=responder.address
    ) and _remove_link_from_device(
        device=responder, is_controller=False, group=group, target=controller.address
    ):
        _, failed_1 = await controller.aldb.async_write()
        _, failed_2 = await responder.aldb.async_write()
        if failed_1 or failed_2:
            return ResponseStatus.FAILURE
        return ResponseStatus.SUCCESS
    return ResponseStatus.FAILURE


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


def find_broken_links(devices):
    """Find proken links."""
    broken_link_list = {}
    for addr in devices:
        device = devices[addr]
        for mem_addr in device.aldb:
            rec = device.aldb[mem_addr]
            if rec.is_in_use:
                status = _test_broken(addr, rec, devices)
                if status != LinkStatus.FOUND:
                    if not broken_link_list.get(addr):
                        broken_link_list[addr] = {}
                    broken_link_list[addr][mem_addr] = (rec, status)
    return broken_link_list


def _test_broken(address, rec, devices):
    """Test if a corresponding record exists in liked device."""
    device = devices.get(rec.target)
    if not device:
        return LinkStatus.MISSING_TARGET

    if not device.aldb.is_loaded:
        return LinkStatus.TARGET_DB_NOT_LOADED

    for mem_addr in device.aldb:
        t_rec = device.aldb[mem_addr]
        if (
            t_rec.target == address
            and t_rec.group == rec.group
            and t_rec.is_controller != rec.is_controller
        ):
            return LinkStatus.FOUND
    if rec.is_controller:
        return LinkStatus.MISSING_RESPONDER
    return LinkStatus.MISSING_CONTROLLER


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
