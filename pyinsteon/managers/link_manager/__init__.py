"""Manage links beteween devices."""
from __future__ import annotations

import asyncio
import logging
from typing import Union

import async_timeout

from ...address import Address
from ...constants import AllLinkMode, EngineVersion, LinkStatus, ResponseStatus
from ...handlers.cancel_all_linking import CancelAllLinkingCommandHandler
from ...handlers.start_all_linking import StartAllLinkingCommandHandler
from ...handlers.to_device.engine_version_request import EngineVersionRequest
from ...handlers.to_device.enter_linking_mode import EnterLinkingModeCommand
from ...handlers.to_device.enter_unlinking_mode import EnterUnlinkingModeCommand

TIMEOUT = 3
_LOGGER = logging.getLogger(__name__)
_engine_version_queue = asyncio.Queue()


async def _handle_engine_version(engine_version):
    """Handle the engine version response."""
    await _engine_version_queue.put(engine_version)


async def _get_engine_version(address):
    """Get the engine version of the device."""

    while not _engine_version_queue.empty():
        _engine_version_queue.get_nowait()

    address = Address(address)
    cmd = EngineVersionRequest(address=address)
    cmd.subscribe(_handle_engine_version)
    retries = 3
    response = None
    while (
        response
        not in [
            ResponseStatus.SUCCESS,
            ResponseStatus.DIRECT_NAK_ALDB,
            ResponseStatus.DIRECT_NAK_PRE_NAK,
        ]
        and retries
    ):
        response = await cmd.async_send()
        retries -= 1
    if response == ResponseStatus.SUCCESS:
        try:
            async with async_timeout.timeout(2):
                return await _engine_version_queue.get()
        except asyncio.TimeoutError:
            pass
    elif response in [
        ResponseStatus.DIRECT_NAK_ALDB,
        ResponseStatus.DIRECT_NAK_PRE_NAK,
    ]:
        return EngineVersion.I2CS
    return EngineVersion.UNKNOWN


async def async_enter_linking_mode(
    link_mode: AllLinkMode, group: int, address: Address = None
):
    """Put the Insteon Modem into linking mode."""

    if address is not None:
        address = Address(address)
        engine_version = await _get_engine_version(address)

    link_cmd = StartAllLinkingCommandHandler()
    response_modem = await link_cmd.async_send(link_mode=link_mode, group=group)
    _LOGGER.debug("Enter linking mode modem response: %s", str(response_modem))

    response_device = None
    if address is not None:
        extended = engine_version == EngineVersion.I2CS
        device_link_cmd = EnterLinkingModeCommand(address)
        response_device = await device_link_cmd.async_send(
            group=group, extended=extended
        )
        if response_device != ResponseStatus.SUCCESS:
            response_device = await device_link_cmd.async_send(
                group=group, extended=not extended
            )
        _LOGGER.debug("Enter linking mode device response: %s", str(response_device))
    return response_modem, response_device


async def async_enter_unlinking_mode(group: int, address: Address = None):
    """Put the Insteon Modem into unlinking mode."""
    if address is not None:
        address = Address(address)
        engine_version = await _get_engine_version(address)
    modem_link_cmd = StartAllLinkingCommandHandler()
    link_mode = AllLinkMode.DELETE
    response_modem = await modem_link_cmd.async_send(link_mode=link_mode, group=group)

    _LOGGER.debug("Enter linking mode modem response: %s", str(response_modem))

    response_device = None
    if address is not None:
        extended = engine_version == EngineVersion.I2CS
        device_link_cmd = EnterUnlinkingModeCommand(address)
        await device_link_cmd.async_send(group=group, extended=extended)
        if response_device != ResponseStatus.SUCCESS:
            response_device = await device_link_cmd.async_send(
                group=group, extended=not extended
            )
        _LOGGER.debug("Enter linking mode device response: %s", str(response_device))

    return response_modem, response_device


async def async_link_devices(
    controller, responder, group: int = 0, data1=255, data2=28, data3=1
):
    """Link two devices."""

    failed_1 = 0
    failed_2 = 0

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
    ):
        _, failed_1 = await controller.aldb.async_write()

    if _add_link_to_device(
        device=responder,
        target=controller.address,
        group=group,
        is_controller=False,
        data1=data1,
        data2=data2,
        data3=data3,
    ):
        _, failed_2 = await responder.aldb.async_write()

    if failed_1 or failed_2:
        return ResponseStatus.FAILURE
    return ResponseStatus.SUCCESS


async def async_cancel_linking_mode():
    """Cancel an All-Link session with the modem."""
    cmd = CancelAllLinkingCommandHandler()
    return await cmd.async_send()


async def async_unlink_devices(device1, device2, group: Union(int, None) = None):
    """Unlink two devices.

    `device2` can be passed as `Device` or `Address`. When `device2` are passed as `Address`, only the links in `device1` will be removed.

    `group` can be passed as an `int` or `None`. When `group` is `None` all links between the two devices will be removed. When
    `group` is an `int`, only that group wil be removed.
    """
    try:
        addr1 = device1.address
    except AttributeError as ex:
        raise TypeError("device1 must be a Device") from ex

    device2_is_device = True
    try:
        addr2 = device2.address
    except AttributeError:
        try:
            addr2 = Address(device2)
            device2_is_device = False
        except TypeError as ex:
            raise TypeError("device2 must be a Device or an Address") from ex

    failed_1 = 0
    failed_2 = 0

    for rec in device1.aldb.find(target=addr2, group=group):
        device1.aldb.modify(mem_addr=rec.mem_addr, in_use=False)
        _, failed_1 = await device1.aldb.async_write()

    if device2_is_device:
        for rec in device2.aldb.find(target=addr1, group=group):
            device2.aldb.modify(mem_addr=rec.mem_addr, in_use=False)
            _, failed_2 = await device2.aldb.async_write()

    if failed_1 or failed_2:
        return ResponseStatus.FAILURE
    return ResponseStatus.SUCCESS


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
    """Add a link to a device.

    If the link already exists it will not be added.
    """
    for rec in device.aldb.find(
        target=Address(target), group=group, is_controller=is_controller
    ):
        try:
            device.aldb.modify(
                mem_addr=rec.mem_addr,
                in_use=True,
                group=group,
                controller=is_controller,
                target=target,
                data1=data1,
                data2=data2,
                data3=data3,
            )
            return True
        except NotImplementedError:
            return False
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
