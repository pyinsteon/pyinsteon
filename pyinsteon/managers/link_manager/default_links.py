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
        result = await async_link_devices(
            controller, responder, group, data1, data2, data3
        )
        results.append(result)
    return multiple_status(*results)
