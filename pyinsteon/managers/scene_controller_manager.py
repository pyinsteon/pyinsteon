"""Persist and reconcile device-controlled scenes."""

import asyncio
import json
import logging
from os import path

import aiofiles
import aiofiles.os
import voluptuous as vol

from .. import devices
from ..address import Address
from ..aldb.no_aldb import NoALDB
from ..config import ON_LEVEL, RAMP_RATE
from ..config.radio_button import button_masks, off_mask_name, on_mask_name
from ..constants import DeviceCategory, ResponseStatus

SCENE_CONTROLLERS_FILE = "insteon_scene_controllers.json"
# Lighting devices whose buttons respond to scenes (loads or keypad indicators).
RESPONDING_CONTROLLER_CATEGORIES = {
    DeviceCategory.DIMMABLE_LIGHTING_CONTROL,
    DeviceCategory.SWITCHED_LIGHTING_CONTROL,
}
DEFAULT_ON_LEVEL = 255
DEFAULT_RAMP_RATE = 28
ControllerSchema = vol.Schema(
    [
        {
            vol.Required("address"): str,
            vol.Required("group"): vol.All(int, vol.Range(min=1, max=255)),
        }
    ]
)
_LOGGER = logging.getLogger(__name__)
_scenes = {}
_state_lock = asyncio.Lock()
_byte = vol.All(int, vol.Range(min=0, max=255))
_link = {
    vol.Required("address"): str,
    vol.Required("data1"): _byte,
    vol.Required("data2"): _byte,
    vol.Required("data3"): _byte,
}
_metadata_schema = vol.Schema(
    {
        vol.Required("controllers"): ControllerSchema,
        vol.Required("links"): [_link],
        vol.Required("records"): [
            {
                **_link,
                vol.Required("controller"): bool,
                vol.Required("group"): vol.All(int, vol.Range(min=1, max=255)),
                vol.Required("target"): str,
            }
        ],
        vol.Required("name"): str,
        vol.Required("pending"): bool,
    }
)


class SceneControllerError(ValueError):
    """A scene cannot be safely written."""


def controller_groups(device):
    """Return groups which the device can transmit as a controller."""
    if isinstance(device.aldb, NoALDB):
        return []
    return sorted(
        {
            link.group
            for link in device.default_links
            if link.is_controller and link.group
        }
    )


async def async_load(work_dir):
    """Load associations and any interrupted write journal."""
    async with _state_lock:
        await _async_load(work_dir)


async def _async_load(work_dir):
    if not work_dir:
        return
    filename = path.join(work_dir, SCENE_CONTROLLERS_FILE)
    try:
        async with aiofiles.open(filename) as file:
            contents = await file.read()
    except FileNotFoundError:
        _scenes.clear()
        return
    try:
        data = json.loads(contents)
        if data["version"] != 1 or not isinstance(data["scenes"], dict):
            raise ValueError("Unsupported scene controller metadata")
        loaded = {}
        for group, scene in data["scenes"].items():
            _metadata_schema(scene)
            for record in scene["records"]:
                Address(record["address"])
                Address(record["target"])
            for link in scene["links"]:
                Address(link["address"])
            for controller in scene["controllers"]:
                Address(controller["address"])
            if not 1 <= int(group) <= 255:
                raise ValueError("Invalid scene group")
            loaded[int(group)] = scene
    except (ValueError, KeyError, TypeError, vol.Error) as exc:
        raise SceneControllerError(f"Cannot load {filename}: {exc}") from exc
    _scenes.clear()
    _scenes.update(loaded)


async def _async_save(work_dir):
    if not work_dir:
        raise SceneControllerError(
            "A working directory is required for device-controlled scenes"
        )
    filename = path.join(work_dir, SCENE_CONTROLLERS_FILE)
    temporary = filename + ".tmp"
    async with aiofiles.open(temporary, "w") as file:
        await file.write(json.dumps({"version": 1, "scenes": _scenes}, indent=2))
        await file.flush()
    await aiofiles.os.replace(temporary, filename)


def scene_metadata(scene_num):
    """Return the persisted state of a logical scene."""
    return _scenes.get(scene_num)


def scene_numbers():
    """Return managed modem scene groups, including interrupted creations."""
    return set(_scenes)


def _device(address):
    device = devices[address]
    if device is None:
        raise SceneControllerError(f"Insteon device {address} was not found")
    return device


def _key(record):
    output = None
    if not record["controller"]:
        device = devices[record["address"]]
        output = record["data3"]
        if device is not None:
            output = _responder_output(device, output)
    return (
        Address(record["address"]).id,
        record["controller"],
        record["group"],
        Address(record["target"]).id,
        output,
    )


def _record(address, controller, group, target, data1, data2, data3):
    return {
        "address": Address(address).id,
        "controller": controller,
        "group": group,
        "target": Address(target).id,
        "data1": data1,
        "data2": data2,
        "data3": data3,
    }


def _local_setting(device, name, default):
    prop = device.properties.get(name)
    if prop is None or not prop.is_loaded or prop.value is None:
        return default
    return int(prop.value)


def _responds(device):
    return not device.is_battery and device.cat in RESPONDING_CONTROLLER_CATEGORIES


def valid_output(device, data3):
    """Return whether data3 selects an output of the responder."""
    return (
        not device.groups
        or data3 in device.groups
        or (len(device.groups) == 1 and data3 == 0)
    )


def _controller_link(controller):
    """Return the responder link that keeps a controller button in the scene."""
    device = _device(controller["address"])
    if not _responds(device):
        return None
    on_level, ramp_rate = DEFAULT_ON_LEVEL, DEFAULT_RAMP_RATE
    if controller["group"] == 1:
        # Match a button press, which uses the load's local settings.
        on_level = _local_setting(device, ON_LEVEL, on_level) or DEFAULT_ON_LEVEL
        ramp_rate = _local_setting(device, RAMP_RATE, ramp_rate)
    return {
        "address": device.address.id,
        "data1": on_level,
        "data2": ramp_rate,
        "data3": controller["group"],
    }


def _scene_links(links, controllers):
    """Add controller buttons as responders unless explicitly configured."""
    explicit = {(Address(link["address"]).id, link["data3"]) for link in links}
    implied = []
    for controller in controllers:
        link = _controller_link(controller)
        if link and (link["address"], link["data3"]) not in explicit:
            implied.append(link)
    return [*links, *implied]


def _records(scene_num, links, controllers):
    records = {}
    sources = [{"address": devices.modem.address.id, "group": scene_num}, *controllers]
    for source in sources:
        for link in _scene_links(links, controllers):
            responder = _device(link["address"])
            if responder.address == Address(source["address"]):
                # A physical button controls its own load using its local settings.
                continue
            responder_record = _record(
                responder.address,
                False,
                source["group"],
                source["address"],
                link["data1"],
                link["data2"],
                link["data3"],
            )
            controller_record = _record(
                source["address"],
                True,
                source["group"],
                responder.address,
                int(responder.cat),
                responder.subcat,
                responder.firmware or 0,
            )
            records[_key(responder_record)] = responder_record
            records[_key(controller_record)] = controller_record
    return records


def _validate_controllers(scene_num, controllers, previous, *, adopt=False):
    try:
        ControllerSchema(controllers)
    except vol.Error as exc:
        raise SceneControllerError(f"Invalid scene controllers: {exc}") from exc
    seen = set()
    previous_pairs = {
        (Address(item["address"]).id, item["group"])
        for item in previous.get("controllers", [])
    }
    # Records retained after a failed controller removal still own that group.
    previous_pairs.update(
        (record["address"], record["group"])
        for record in previous.get("records", [])
        if record["controller"] and Address(record["address"]) != devices.modem.address
    )
    normalized = []
    for item in controllers:
        device = _device(item["address"])
        if not device.aldb.is_loaded:
            raise SceneControllerError(
                f"Read the complete All-Link Database for {device.address} before saving"
            )
        pair = (device.address.id, item["group"])
        if pair in seen:
            raise SceneControllerError(
                "A controller button was selected more than once"
            )
        seen.add(pair)
        if device == devices.modem or item["group"] not in controller_groups(device):
            raise SceneControllerError(
                f"{device.address} cannot control group {item['group']}"
            )
        for other_num, other in _scenes.items():
            if other_num == scene_num:
                continue
            other_pairs = {
                (Address(ctrl["address"]).id, ctrl["group"])
                for ctrl in other["controllers"]
            }
            other_pairs.update(
                (rec["address"], rec["group"])
                for rec in other["records"]
                if rec["controller"]
            )
            if pair in other_pairs:
                raise SceneControllerError(
                    f"{device.address} group {item['group']} belongs to scene {other_num}"
                )
        # Imports adopt the hand-made links that were found for these buttons.
        if pair not in previous_pairs and not adopt:
            if any(
                rec.target != devices.modem.address
                for rec in device.aldb.find(
                    group=item["group"], is_controller=True, in_use=True
                )
            ):
                raise SceneControllerError(
                    f"{device.address} group {item['group']} already controls other devices"
                )
            for address in devices:
                if address == devices.modem.address:
                    continue
                if any(
                    devices[address].aldb.find(
                        target=device.address,
                        group=item["group"],
                        is_controller=False,
                        in_use=True,
                    )
                ):
                    raise SceneControllerError(
                        f"{device.address} group {item['group']} has existing responder links"
                    )
        normalized.append({"address": device.address.id, "group": item["group"]})
    return normalized


def _matching(device, record):
    output = (
        None if record["controller"] else _responder_output(device, record["data3"])
    )
    return [
        rec
        for rec in device.aldb.find(
            group=record["group"],
            target=record["target"],
            is_controller=record["controller"],
            in_use=True,
        )
        if output is None or _responder_output(device, rec.data3) == output
    ]


def _validate_databases(owned, desired):
    affected = {_key(record)[0] for record in owned.values()}
    for address in affected:
        device = _device(address)
        if not device.aldb.is_loaded:
            raise SceneControllerError(
                f"Read the complete All-Link Database for {device.address} before saving"
            )
        for pending in device.aldb.pending_changes.values():
            key = _key(
                _record(
                    address,
                    pending.is_controller,
                    pending.group,
                    pending.target,
                    pending.data1,
                    pending.data2,
                    pending.data3,
                )
            )
            if key not in owned:
                raise SceneControllerError(
                    f"{device.address} has unrelated pending All-Link Database changes"
                )
        hwm = device.aldb.high_water_mark_mem_addr
        if hwm is not None:
            free = sum(
                not rec.is_in_use and not rec.is_high_water_mark
                for _, rec in device.aldb.items()
            )
            required = 0
            for key, record in owned.items():
                if key[0] != address:
                    continue
                matches = _matching(device, record)
                if key in desired:
                    required += not matches
                    free += max(0, len(matches) - 1)
                else:
                    free += len(matches)
            # Leave room for a high-water-mark record below appended links.
            if required > free + hwm // 8:
                raise SceneControllerError(
                    f"The All-Link Database for {device.address} is full"
                )


def _stage(owned, desired):
    affected = {}
    for key, record in owned.items():
        device = _device(record["address"])
        affected[device.address.id] = device
        for mem_addr, pending in list(device.aldb.pending_changes.items()):
            pending_key = _key(
                _record(
                    device.address,
                    pending.is_controller,
                    pending.group,
                    pending.target,
                    pending.data1,
                    pending.data2,
                    pending.data3,
                )
            )
            if pending_key == key:
                device.aldb.pending_changes.pop(mem_addr)
        matches = _matching(device, record)
        wanted = desired.get(key)
        if wanted is None:
            for rec in matches:
                device.aldb.remove(rec.mem_addr)
            continue
        for duplicate in matches[1:]:
            device.aldb.remove(duplicate.mem_addr)
        if matches:
            rec = matches[0]
            # Controller data bytes are informational; rewriting them would only
            # cost writes, such as waking a remote whose links already exist.
            if not wanted["controller"] and (
                rec.data1,
                rec.data2,
                _responder_output(device, rec.data3),
            ) != (
                wanted["data1"],
                wanted["data2"],
                _responder_output(device, wanted["data3"]),
            ):
                device.aldb.modify(
                    rec.mem_addr,
                    data1=wanted["data1"],
                    data2=wanted["data2"],
                    data3=wanted["data3"],
                )
        else:
            device.aldb.add(
                group=wanted["group"],
                target=wanted["target"],
                controller=wanted["controller"],
                data1=wanted["data1"],
                data2=wanted["data2"],
                data3=wanted["data3"],
            )
    return affected


async def async_save(
    scene_num, links, controllers, current_links, work_dir, name, *, adopt=False
):
    """Journal a desired scene, then write only its owned ALDB records."""
    async with _state_lock:
        return await _async_save_scene(
            scene_num, links, controllers, current_links, work_dir, name, adopt=adopt
        )


async def _async_save_scene(
    scene_num, links, controllers, current_links, work_dir, name, *, adopt=False
):
    if not work_dir:
        raise SceneControllerError(
            "A working directory is required for device-controlled scenes"
        )
    previous = _scenes.get(scene_num, {})
    controllers = _validate_controllers(scene_num, controllers, previous, adopt=adopt)
    desired = _records(scene_num, links, controllers)
    owned = _records(scene_num, current_links, previous.get("controllers", []))
    owned.update({_key(record): record for record in previous.get("records", [])})
    owned.update(desired)
    _validate_databases(owned, desired)
    state = {
        "controllers": controllers,
        "links": links,
        "records": list(owned.values()),
        "name": name,
        "pending": True,
    }
    _scenes[scene_num] = state
    await _async_save(work_dir)
    affected = _stage(owned, desired)
    failed = False
    for device in affected.values():
        if not device.aldb.pending_changes:
            continue
        if device.is_battery:
            awake = await device.async_keep_awake()
            if awake != ResponseStatus.SUCCESS:
                _LOGGER.error(
                    "Scene %s controller %s must be awake before writing",
                    scene_num,
                    device.address,
                )
                failed = True
                continue
            _, count = await device.aldb.async_write_on_wake()
        else:
            _, count = await device.aldb.async_write()
        if count:
            _LOGGER.error(
                "Scene %s could not be written to %s; wake battery devices and retry",
                scene_num,
                device.address,
            )
            failed = True
    if failed:
        return ResponseStatus.FAILURE
    state["records"] = list(desired.values())
    state["pending"] = False
    await _async_save(work_dir)
    return ResponseStatus.SUCCESS


async def async_delete(scene_num, current_links, work_dir):
    """Remove owned records, retaining the journal if any device fails."""
    async with _state_lock:
        previous = _scenes[scene_num]
        result = await _async_save_scene(
            scene_num, [], [], current_links, work_dir, previous["name"]
        )
        if result == ResponseStatus.SUCCESS:
            _scenes.pop(scene_num)
            await _async_save(work_dir)
        return result


def _managed_pairs():
    pairs = set()
    for scene in _scenes.values():
        pairs.update(
            (Address(item["address"]).id, item["group"])
            for item in scene["controllers"]
        )
        pairs.update(
            (record["address"], record["group"])
            for record in scene["records"]
            if record["controller"]
            and Address(record["address"]) != devices.modem.address
        )
    return pairs


def _scan_buttons():
    """Collect hand-made links by controller button from loaded databases."""
    buttons = {}

    def button(address, group):
        return buttons.setdefault(
            (Address(address).id, group), {"outputs": {}, "targets": set()}
        )

    for address in devices:
        device = devices[address]
        if device == devices.modem or not device.aldb.is_loaded:
            continue
        for rec in device.aldb.find(in_use=True):
            if rec.group == 0 or rec.target in (devices.modem.address, device.address):
                continue
            if rec.is_controller:
                button(device.address, rec.group)["targets"].add(rec.target.id)
            else:
                outputs = button(rec.target, rec.group)["outputs"]
                outputs.setdefault(
                    (device.address.id, _responder_output(device, rec.data3)), set()
                ).add((rec.data1, rec.data2))
    for (address, group), info in buttons.items():
        device = devices[address]
        for output, level in _keypad_outputs(device, group).items():
            info["outputs"].setdefault(output, set()).add(level)
    return buttons


def _mask_properties(device, group):
    """Return a keypad button's on and off mask properties, if it has them."""
    if device is None:
        return None
    on_mask = device.properties.get(on_mask_name(group))
    off_mask = device.properties.get(off_mask_name(group))
    if on_mask is None or off_mask is None:
        return None
    return on_mask, off_mask


def _keypad_outputs(device, group):
    """Return the keypad's own outputs that a button press sets.

    A keypad button turns off the buttons in its off mask. The load follows the
    button at the button's on-level and ramp rate when it is in the on mask, and
    other buttons in the on mask turn on. These settings are kept in the keypad
    rather than its All-Link Database.
    """
    masks = button_masks(device, group) if device is not None else None
    if masks is None:
        return {}
    turns_on, turns_off = masks
    suffix = "" if group == 1 else f"_{group}"
    on_level = _local_setting(device, f"{ON_LEVEL}{suffix}", DEFAULT_ON_LEVEL)
    ramp_rate = _local_setting(device, f"{RAMP_RATE}{suffix}", DEFAULT_RAMP_RATE)
    outputs = {}
    for output in device.groups:
        if output == group:
            continue
        is_on = output in turns_on
        is_off = output in turns_off
        if output == 1 and (is_on or is_off):
            level = (on_level if is_on else 0, ramp_rate)
        elif is_off:
            level = (0, DEFAULT_RAMP_RATE)
        elif is_on:
            level = (DEFAULT_ON_LEVEL, DEFAULT_RAMP_RATE)
        else:
            continue
        outputs[(device.address.id, output)] = level
    return outputs


def _responder_output(device, data3):
    """Return the output a responder link selects.

    Links made by pressing set buttons often store 0 on single-output devices.
    """
    if data3 == 0 and len(device.groups) == 1:
        return next(iter(device.groups))
    return data3


def _button_issues(address, group, info, *, conflicts=True):
    device = devices[address]
    if device is None:
        return [f"{Address(address)} is not a known Insteon device"]
    issues = []
    if group not in controller_groups(device):
        issues.append(f"{device.address} group {group} is not a controller button")
    if not device.aldb.is_loaded:
        issues.append(f"Read the complete All-Link Database for {device.address}")
    masks = _mask_properties(device, group)
    if masks is not None and not all(mask.is_loaded for mask in masks):
        issues.append(f"Read the properties of {device.address}")
    responders = {output[0] for output in info["outputs"]}
    for target in sorted(info["targets"] - responders):
        responder = devices[target]
        # Links to unknown devices, such as a replaced modem, are left unchanged.
        if responder is not None and not responder.aldb.is_loaded:
            issues.append(f"Read the complete All-Link Database for {Address(target)}")
    for (target, data3), levels in sorted(info["outputs"].items()):
        if conflicts and len(levels) > 1:
            issues.append(f"{Address(target)} has conflicting links to this button")
        if not valid_output(devices[target], data3):
            issues.append(f"{Address(target)} has no output {data3}")
    return issues


def _candidate(members, buttons, issues):
    outputs = {}
    for member in members:
        for output, levels in buttons[member]["outputs"].items():
            outputs.setdefault(output, set()).update(levels)
    if not issues and any(len(levels) > 1 for levels in outputs.values()):
        return None
    links = [
        {
            "address": address,
            "data1": data1,
            "data2": data2,
            "data3": data3,
        }
        for (address, data3), levels in sorted(outputs.items())
        for data1, data2 in levels
    ]
    if not links:
        issues = [*issues, "The button has no responders"]
    return {
        "controllers": [
            {"address": address, "group": group} for address, group in sorted(members)
        ],
        "links": links,
        "issues": issues,
        "importable": not issues,
    }


def _linked_scene(members, buttons):
    """Return a candidate for buttons that turn each other on, if consistent.

    Remotes commonly light the keypad button of the same scene and turn off the
    keypad's load and other buttons. Those links are part of the scene; every
    other responder must be set identically by every button.
    """
    owners = {address for address, _ in members}
    responders = [pair for pair in members if _responds(devices[pair[0]])]
    for responder in responders:
        for member in members:
            levels = buttons[member]["outputs"].get(responder, ())
            if member[0] != responder[0] and not any(data1 for data1, _ in levels):
                return None
    external = {
        frozenset(o for o in buttons[member]["outputs"] if o[0] not in owners)
        for member in members
    }
    if len(external) != 1:
        return None
    links = []
    issues = []
    outputs = {o for member in members for o in buttons[member]["outputs"]}
    for address, data3 in sorted(outputs):
        shared = None
        for member in members:
            levels = buttons[member]["outputs"].get((address, data3))
            if levels is not None:
                shared = set(levels) if shared is None else shared & levels
        if not shared:
            return None
        if len(shared) > 1:
            issues.append(f"{Address(address)} has conflicting links to this button")
        # A duplicate link that the other buttons agree on imports at their level.
        data1, data2 = sorted(shared)[0]
        links.append(
            {"address": address, "data1": data1, "data2": data2, "data3": data3}
        )
    for member in members:
        issues.extend(_button_issues(*member, buttons[member], conflicts=False))
    issues = list(dict.fromkeys(issues))
    return {
        "controllers": [
            {"address": address, "group": group} for address, group in sorted(members)
        ],
        "links": links,
        "issues": issues,
        "importable": not issues,
    }


def _linked_candidates(buttons):
    """Return candidates for buttons that turn on another lighting button."""
    parent = {pair: pair for pair in buttons}

    def root(pair):
        while parent[pair] != pair:
            parent[pair] = parent[parent[pair]]
            pair = parent[pair]
        return pair

    known = {pair for pair in buttons if devices[pair[0]] is not None}
    for pair in known:
        for output, levels in buttons[pair]["outputs"].items():
            # A keypad's own buttons are part of each of its scenes, not linked ones.
            if (
                output in known
                and output[0] != pair[0]
                and _responds(devices[output[0]])
                and any(data1 for data1, _ in levels)
            ):
                parent[root(output)] = root(pair)
    components = {}
    for pair in sorted(buttons):
        components.setdefault(root(pair), []).append(pair)
    candidates = []
    for members in components.values():
        if len(members) > 1:
            candidate = _linked_scene(members, buttons)
            if candidate is not None:
                candidates.append(candidate)
    return candidates


def find_device_scenes():
    """Return hand-made device-controlled scenes which can be imported.

    Buttons that turn on another lighting button, such as remotes lighting a
    keypad button, form one scene when they set every other responder the same.
    Other buttons are grouped when they control the same set of outputs
    (including each other) with the same settings, as created by Insteon Director.
    """
    managed = _managed_pairs()
    buttons = {
        pair: info for pair, info in _scan_buttons().items() if pair not in managed
    }
    candidates = _linked_candidates(buttons)
    linked = {
        (item["address"], item["group"])
        for candidate in candidates
        for item in candidate["controllers"]
    }
    groups = {}
    for (address, group), info in sorted(buttons.items()):
        if (address, group) in linked:
            continue
        issues = _button_issues(address, group, info)
        if issues:
            candidates.append(_candidate([(address, group)], buttons, issues))
            continue
        outputs = set(info["outputs"])
        if _responds(devices[address]):
            outputs.add((address, group))
        groups.setdefault(frozenset(outputs), []).append((address, group))
    for members in groups.values():
        combined = _candidate(members, buttons, [])
        if combined is not None:
            candidates.append(combined)
            continue
        candidates.extend(_candidate([member], buttons, []) for member in members)
    return sorted(
        candidates,
        key=lambda item: [(c["address"], c["group"]) for c in item["controllers"]],
    )
