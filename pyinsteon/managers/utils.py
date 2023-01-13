"""Utilities for managers."""
from ..device_types.ipdb import IPDB
from .device_id_manager import DeviceId


def create_device(device_id: DeviceId):
    """Create an Insteon Device from a DeviceId named Tuple."""

    ipdb = IPDB()
    product = ipdb[[device_id.cat, device_id.subcat]]
    deviceclass = product.deviceclass
    if deviceclass is not None:
        return deviceclass(
            device_id.address,
            device_id.cat,
            device_id.subcat,
            device_id.firmware,
            product.description,
            product.model,
        )
    return None


def create_x10_device(
    housecode: str,
    unitcode: int,
    x10_feature: str,
    steps: int = 22,
    max_level: int = 255,
):
    """Create an Insteon Device from a DeviceId named Tuple."""
    ipdb = IPDB()
    product = ipdb.x10(x10_feature)
    deviceclass = product.deviceclass
    if deviceclass is not None:
        if x10_feature == "dimmable":
            return deviceclass(housecode, unitcode, steps, max_level)
        return deviceclass(housecode, unitcode)
    return None
