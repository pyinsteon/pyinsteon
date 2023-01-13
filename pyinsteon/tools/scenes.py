"""Scenes menu for pyinsteon tools."""

from .. import devices
from ..constants import DeviceCategory
from ..managers.device_link_manager import DeviceLinkSchema
from ..managers.scene_manager import (
    async_add_or_update_scene,
    async_get_scene,
    async_get_scenes,
    async_save_scene_names,
    set_scene_name,
)
from .tools_base import ToolsBase

SHOW_ADVANCED = True


class ToolsScenes(ToolsBase):
    """Command class to test interactivity."""

    async def do_list_scenes(self):
        """List all scene."""
        self._log_stdout("Number   Name")
        self._log_stdout(
            "------   -------------------------------------------------------"
        )
        scenes = await async_get_scenes()
        for scene, data in scenes.items():
            self._log_stdout(f"{scene:5}    {data['name']}")

    async def do_print_scene(
        self, scene: int = None, workdir: str = None, log_stdout=None, background=False
    ):
        """Show the details of a scene.

        Usage:
            print_scene scene

        scene: Scene number
        """
        if workdir is None:
            workdir = self.workdir if self.workdir else "."

        self.workdir = workdir

        if not self.workdir:
            if background:
                log_stdout("A value for the working directory is required.")
                return
            self.workdir = await self._get_workdir()

        if not self.workdir:
            return

        scene_list = list(await async_get_scenes(work_dir=self.workdir))

        scene = await self._ensure_int(
            value=scene,
            values=scene_list,
            name="Scene number",
            ask_value=not background,
            log_stdout=log_stdout,
        )
        if not scene:
            return

        scene_def = await async_get_scene(scene, work_dir=self.workdir)
        log_stdout(f"Scene {scene}: {scene_def['name']}")
        log_stdout("")
        log_stdout("Device     Data 1   Data 2   Data 3")
        log_stdout("--------   ------   ------   ------")
        for device, info in scene_def["devices"].items():
            data1 = f"{info.data1:5}" if info.data1 is not None else "     "
            data2 = f"{info.data2:5}" if info.data2 is not None else "     "
            data3 = f"{info.data3:5}" if info.data3 is not None else "     "
            log_stdout(f"{str(device)}   {data1}   {data2}   {data3}")

    async def do_save_scenes(self, workdir=None, log_stdout=None, background=False):
        """Save the scene names to the working directory.

        Usage:
            save_devices [--background | -b] workdir

        workdir: Directory where the saved device file is located

        This does not write the scenes to the devices. Use `write_scenes` to write the scene data
        to the devices.
        """
        if workdir is None:
            workdir = self.workdir if self.workdir else "."

        self.workdir = workdir

        if not self.workdir:
            if background:
                log_stdout("A value for the working directory is required.")
                return
            self.workdir = await self._get_workdir()

        if not self.workdir:
            return

        await async_save_scene_names(work_dir=self.workdir)

    async def do_set_scene_name(
        self, scene=None, name=None, work_dir=None, log_stdout=None, background=False
    ):
        """Set the scene name."""
        scene_list = list(await async_get_scenes(work_dir=self.workdir))

        scene = await self._ensure_int(
            value=scene,
            values=scene_list,
            name="Scene number",
            ask_value=not background,
            log_stdout=log_stdout,
        )

        name = await self._ensure_string(
            value=name,
            values=None,
            name="Scene name",
            ask_value=not background,
            log_stdout=log_stdout,
        )

        if not scene:
            return

        set_scene_name(scene_num=scene, name=name)

    async def do_add_scene(self):
        """Add a new scene.

        Usage:
            add_scene

        Note: This cannot be run in the background. It is an interactive method which will provide prompts for scene information.
        """

        scene_info = {}
        scene = None
        scene_list = list(async_get_scenes())
        while scene is None or scene in scene_list:
            scene = self._ensure_int(
                value=scene,
                values=None,
                name="Scene number",
                ask_value=True,
                log_stdout=self._log_stdout,
            )
            if scene in scene_list:
                self._log_stdout(f"Scene number {scene} already exists.")
            if not scene:
                return

        default_name = f"Scene number {scene}"
        name = await self._ensure_string(
            value=None,
            values=None,
            name="Scene Name",
            ask_value=True,
            log_stdout=self._log_stdout,
            default=default_name,
        )
        scene_info["name"] = name
        scene_devices = []
        got_addr = True
        while got_addr:
            addr = await self._ensure_address(
                address=None,
                name="Device Address",
                ask_value=True,
                log_stdout=self._log_stdout,
                allow_all=False,
                match_device=True,
            )
            if not addr:
                got_addr = False
                continue

            device = devices[addr]
            got_data = True
            if device.cat == DeviceCategory.DIMMABLE_LIGHTING_CONTROL:
                data1_values = range(0, 255)
                data2_values = range(0, 255)
            else:
                data1_values = [0, 255]
                data2_values = []
            data3_values = list(device.groups)

            device_data = []
            while got_data:
                data1 = await self._ensure_int(
                    value=None,
                    values=data1_values,
                    name="Data 1",
                    ask_value=True,
                    log_stdout=self._log_stdout,
                    default=255,
                )
                if data2_values:
                    data2 = await self._ensure_int(
                        value=None,
                        values=data2_values,
                        name="Data 2",
                        ask_value=True,
                        log_stdout=self._log_stdout,
                        default=28,
                    )
                else:
                    data2 = 0

                data3 = await self._ensure_int(
                    value=None,
                    values=data3_values,
                    name="Data 3",
                    ask_value=True,
                    log_stdout=self._log_stdout,
                    default=1,
                )
                data = {
                    "address": device.address.id,
                    "data1": data1,
                    "data2": data2,
                    "data3": data3,
                }
                device_data.append(data)
            scene_devices = DeviceLinkSchema(device_data)
        if not self.workdir:
            self.workdir = await self._get_workdir()
            if not self.workdir:
                self._log_stdout(
                    "A working directory is required to save the scene name."
                )
        if not scene_devices:
            self._log_stdout("At least one device is required")
            return
        await async_add_or_update_scene(
            scene_num=scene, links=scene_devices, name=name, work_dir=self.workdir
        )
