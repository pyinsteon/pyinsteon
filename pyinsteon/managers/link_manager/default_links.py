"""Manage creation of default links for a device."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...constants import ResponseStatus

if TYPE_CHECKING:
    from ...device_types.device_base import Device

TIMEOUT = 3
_LOGGER = logging.getLogger(__name__)


async def async_add_default_links(device: Device):
    """Establish default links between the modem and device."""
    # pylint: disable=import-outside-toplevel
    from ... import devices

    if not device.aldb.is_loaded:
        await device.aldb.async_load()

    if not device.aldb.is_loaded:
        return ResponseStatus.UNSENT

    modem = devices.modem

    for link_info in device.default_links:
        is_controller = link_info.is_controller
        group = link_info.group
        device.aldb.add(
            group=group,
            target=modem.address,
            controller=is_controller,
            data1=int(modem.cat),
            data2=int(modem.subcat),
            data3=modem.firmware,
        )
        modem.aldb.add(
            group=group,
            target=device.address,
            controller=not is_controller,
            data1=int(device.cat),
            data2=int(device.subcat),
            data3=int(device.firmware),
        )
    _, failed_device = await device.aldb.async_write()
    _, failed_modem = await modem.aldb.async_write()
    if failed_modem == 0 and failed_device == 0:
        return ResponseStatus.SUCCESS
    return ResponseStatus.FAILURE
