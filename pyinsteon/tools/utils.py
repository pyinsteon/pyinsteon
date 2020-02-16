"""Utilities for the tools commands."""
import logging
import os

from .. import devices

_LOGGING = logging.getLogger(__name__)


def get_int(prompt, default=None, values=None):
    """Get an integer value."""
    value = None
    if default:
        prompt = f"{prompt} (Default {default}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
        if value:
            try:
                value = int(value)
                if values and value not in values:
                    raise ValueError()
                break
            except ValueError:
                response = "Must be a number."
                if values:
                    response = f"{response} Acceptable values {values}."
                _LOGGING.info(response)
        elif default is not None:
            value = default
            break
        else:
            response = "A number is required."
            if values:
                response = f"{response} Acceptable values {values}."
            _LOGGING.info(response)
    return value


def get_float(prompt, default=None, maximum=None, minimum=None):
    """Get an integer value."""
    value = None
    if default:
        prompt = f"{prompt} (Default {default}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
        if value:
            try:
                value = float(value)
                if value < maximum or value > maximum:
                    raise ValueError()
                break
            except ValueError:
                response = "Must be a number."
                if maximum and minimum:
                    response = f"{response} (Max: {maximum}  Min: {minimum})."
                elif maximum:
                    response = f"{response} (Max: {maximum})."
                elif maximum and minimum:
                    response = f"{response} (Min: {minimum})."
                _LOGGING.info(response)
        elif default is not None:
            value = default
            break
        else:
            response = "Must be a number."
            if maximum and minimum:
                response = f"{response} (Max: {maximum}  Min: {minimum})."
            elif maximum:
                response = f"{response} (Max: {maximum})."
            elif maximum and minimum:
                response = f"{response} (Min: {minimum})."
            _LOGGING.info(response)
    return value


def get_char(prompt, default=None, values=None):
    """Get an integer value."""
    if default:
        prompt = f"{prompt} (Default {default.upper()}): "
    else:
        prompt = f"{prompt}: "
    while True:
        value = input(prompt)
        if value:
            if not values or value.lower() in values:
                break
            _LOGGING.error("Acceptable values %s.", values)
        elif default is not None:
            value = default
            break
        else:
            response = "A response is required."
            if values:
                response = f"{response} Acceptable values {values}."
            _LOGGING.info(response)
    return value


def get_workdir():
    """Input the valeu for the workdir."""
    _LOGGING.info("The working directory stores the lsit of identified devices.")
    _LOGGING.info(
        "Enter a working directory where the saved file is (and will be saved to after loading.)"
    )
    workdir = input(f"Working directory (enter . for current director): ")
    if workdir == ".":
        return os.getcwd()
    return workdir


def get_addresses(address=None, allow_cancel=False, allow_all=True):
    """Get the address of a device or all devices."""
    prompt_addr = "Enter device address"
    prompt_cancel = "Enter device address or blank to cancel"
    prompt_all = "Enter device address or all for all devices"
    prompt_all_cancel = "Enter device address, all for all devices, or blank to cancel"

    addresses = []
    if allow_all and allow_cancel:
        prompt = f"{prompt_all_cancel}: "
    elif allow_all:
        prompt = f"{prompt_all}: "
    elif allow_cancel:
        prompt = f"{prompt_cancel}: "
    else:
        prompt = prompt_addr

    while True:
        if not address:
            address = input(prompt)
        if not address:
            if allow_cancel:
                return addresses
        elif str(address).strip("'\"").lower() == "all":
            for addr in devices:
                addresses.append(addr)
            return addresses
        elif devices[address]:
            addresses.append(address)
            return addresses
        else:
            _LOGGING.info("Device %s not found in device list.", address)
            return []


def print_aldb(device):
    """Print the All-Link Database to the log."""
    _LOGGING.info("")
    _LOGGING.info("RecID In Use Mode HWM Group Address  Data 1 Data 2 Data 3")
    _LOGGING.info("----- ------ ---- --- ----- -------- ------ ------ ------")
    for mem_addr in device.aldb:
        rec = device.aldb[mem_addr]
        in_use = "Y" if rec.is_in_use else "N"
        mode = "C" if rec.is_controller else "R"
        hwm = "Y" if rec.is_high_water_mark else "N"
        line = f" {rec.mem_addr:04x}    {in_use:s}     {mode:s}   {hwm:s}    {rec.group:3d} {rec.target}   {rec.data1:3d}   {rec.data2:3d}   {rec.data3:3d}"
        _LOGGING.info(line)
    _LOGGING.info("")
