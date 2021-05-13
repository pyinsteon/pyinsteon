"""Manage creation of default links for a device."""

import logging

from ...constants import ResponseStatus
from ...utils import multiple_status
from . import async_link_devices

TIMEOUT = 3
_LOGGER = logging.getLogger(__name__)


async def async_add_default_links(device):
    """Establish default links between the modem and device."""
    from ... import devices

    if not device.aldb.is_loaded:
        await device.aldb.async_load()

    if not device.aldb.is_loaded:
        return ResponseStatus.UNSENT

    results = []
    for link_info in device.default_links:
        is_controller = link_info.is_controller
        group = link_info.group
        if is_controller:
            controller = device
            responder = devices.modem
            data1 = link_info.modem_data1
            data2 = link_info.modem_data2
            data3 = link_info.modem_data3
        else:
            controller = devices.modem
            responder = device
            data1 = link_info.dev_data1
            data2 = link_info.dev_data2
            data3 = link_info.dev_data3
        if not _link_exists(controller, responder, group):
            result = await async_link_devices(
                controller, responder, group, data1, data2, data3
            )
            results.append(result)
    if not results:
        results.append(ResponseStatus.SUCCESS)
    return multiple_status(*results)


def _link_exists(controller, responder, group: int)-> bool:
    """Test if a link exists for a group in both the controller and the responder."""
    controller_exists = False
    responder_exists = False
    for mem_addr in controller.aldb:
        rec = controller.aldb[mem_addr]
        if rec.is_controller and rec.target == responder.address and rec.group == group:
            controller_exists = True
            break

    for mem_addr in responder.aldb:
        rec = responder.aldb[mem_addr]
        if not rec.is_controller and rec.target == responder.address and rec.group == group:
            responder_exists = True
            break

    return controller_exists and responder_exists
