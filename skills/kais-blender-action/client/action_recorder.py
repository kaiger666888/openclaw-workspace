"""
kais-blender-action — Mixamo 动作镜头录制器
基于 kais-blender-engine client，不重复造轮子。

新增能力（engine 不覆盖的）：
- ms 级时间精度（start_ms / duration_ms → 帧换算）
- 自由镜头参数（azimuth/elevation/distance/fov 等）
- 快速预览模式（低分辨率 + 低采样）
- 批量多角度录制
"""

import json
import math
import os
import subprocess
import sys
from typing import Optional

# 复用 engine 的 client
ENGINE_CLIENT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "kais-blender-engine", "client"
)
if ENGINE_CLIENT_DIR not in sys.path:
    sys.path.insert(0, ENGINE_CLIENT_DIR)

from blender_client import BlenderAgentClient
from generators.animation import (
    AnimationParams,
    generate_animation_script,
    ANIM_LIGHTING_PRESETS,
    ANIM_CAMERA_PRESETS,
)

# ─── 自由镜头预设（扩展 engine 的 5 个预设）───

CUSTOM_CAMERA_PRESETS = {
    "front_waist":    {"azimuth": 0, "elevation": 0, "distance": 3.0, "target_height": 0.9, "fov": 50},
    "front_chest":    {"azimuth": 0, "elevation": 10, "distance": 2.5, "target_height": 1.3, "fov": 45},
    "front_full":     {"azimuth": 0, "elevation": 0, "distance": 4.0, "target_height": 0.9, "fov": 50},
    "side_waist":     {"azimuth": 90, "elevation": 0, "distance": 3.0, "target_height": 0.9, "fov": 50},
    "three_quarter":  {"azimuth": 45, "elevation": 10, "distance": 3.0, "target_height": 0.9, "fov": 50},
    "dutch_left":     {"azimuth": 30, "elevation": 5, "distance": 2.5, "target_height": 0.9, "fov": 45, "roll": -12},
    "over_shoulder":  {"azimuth": 160, "elevation": 10, "distance": 2.0, "target_height": 1.2, "fov": 60},
    "low_angle":      {"azimuth": 0, "elevation": -15, "distance": 2.5, "target_height": 0.7, "fov": 45},
    "high_angle":     {"azimuth": 0, "elevation": 25, "distance": 3.5, "target_height": 1.0, "fov": 50},
    "top_down":       {"azimuth": 0, "elevation": 80, "distance": 3.0, "target_height": 0.9, "fov": 35},
    "close_up_face":  {"azimuth": 0, "elevation": 5, "distance": 1.2, "target_height": 1.6, "fov": 35},
    "wide_shot":      {"azimuth": 0, "elevation": 5, "distance": 6.0, "target_height": 0.9, "fov": 60},
}

# 将自由镜头参数转换为 engine 的 (location, rotation) 格式
def _camera_to_location_rotation(cam: dict) -> tuple:
    """azimuth/elevation/distance → (location, rotation)"""
    azimuth = math.radians(cam.get("azimuth", 0))
    elevation = math.radians(cam.get("elevation", 0))
    distance = cam.get("distance", 3.0)
    target_h = cam.get("target_height", 0.9)

    cos_el = math.cos(elevation)
    x = distance * cos_el * math.sin(azimuth)
    y = distance * cos_el * math.cos(azimuth)
    z = distance * math.sin(elevation) + target_h

    # rotation: pitch = -elevation + offset for looking at target
    pitch = -(math.pi / 2 - elevation)
    yaw = azimuth

    return (x, y, z), (pitch, 0, yaw)


def _build_camera_code(cam: dict, var_name: str = "camera") -> str:
    """生成相机设置的 Python 代码片段"""
    (x, y, z), (pitch, _, yaw) = _camera_to_location_rotation(cam)
    fov = cam.get("fov", 50)
    lens_x = cam.get("lens_shift_x", 0)
    lens_y = cam.get("lens_shift_y", 0)
    roll = cam.get("roll", 0)

    lines = [
        f"{var_name}.location = ({x:.4f}, {y:.4f}, {z:.4f})",
        f"{var_name}.rotation_euler = ({pitch:.4f}, 0, {yaw:.4f})",
        f"cam_data.lens = {fov}",
    ]
    if lens_x != 0:
        lines.append(f"cam_data.shift_x = {lens_x}")
    if lens_y != 0:
        lines.append(f"cam_data.shift_y = {lens_y}")
    if roll != 0:
        lines.append(f"{var_name}.rotation_euler[2] += {math.radians(roll):.4f}")
    return "\n".join(lines)


class ActionRecorder:
    """Mixamo 动作镜头录制器 — 基于 kais-blender-engine"""

    def __init__(self, server_url: str = "http://192.168.71.38:8080"):
        self._cli = BlenderAgentClient(server_url)
        # 手动设置 caps，绕过可能挂掉的 /capabilities 端点
        self._cli._caps = {
            "output_dir": "D:/BlenderAgent/outputs",
            "characters_dir": "D:/BlenderAgent/animations/characters",
            "motions_dir": "D:/BlenderAgent/animations/motions_noskin/all",
            "cache_dir": "D:/BlenderAgent/cache",
        }
        # 覆盖 engine client 的超时
        self._cli._post = self._post_with_timeout

    @staticmethod
    def _post_with_timeout(path: str, data: dict, timeout: int = 600) -> dict:
        """覆盖 engine client 的 _post，支持长超时"""
        import requests
        r = requests.post(
            f"http://192.168.71.38:8080{path}",
            json=data,
            timeout=min(timeout + 60, 900),
        )
        r.raise_for_status()
        return r.json()

    def get_camera_preset(self, name: str) -> dict:
        if name not in CUSTOM_CAMERA_PRESETS:
            raise ValueError(f"未知预设: {name}，可用: {', '.join(CUSTOM_CAMERA_PRESETS)}")
        return dict(CUSTOM_CAMERA_PRESETS[name])

    def list_camera_presets(self) -> dict:
        return dict(CUSTOM_CAMERA_PRESETS)

    def list_assets(self):
        return self._cli.list_animations()

    def refresh_assets(self):
        return self._cli.rebuild_animation_index()

    def health(self):
        return self._cli.health()

    def preview_motion(self, motion: str, start_ms: int = 0,
                       duration_ms: int = 1000, fps: int = 24):
        """预览帧范围，不渲染。"""
        # 通过 server 获取动画信息
        assets = self.list_assets()
        motion_info = None
        for m in assets.get("motions", []):
            if m["name"] == motion:
                motion_info = m
                break
        if motion_info is None:
            # 尝试不带 .fbx
            for m in assets.get("motions", []):
                if m["name"] == motion + ".fbx" or m["name"].replace(".fbx", "") == motion:
                    motion_info = m
                    break
        if motion_info is None:
            raise FileNotFoundError(f"动画未找到: {motion}")

        total_frames = motion_info.get("duration_frames", 120)
        motion_fps = motion_info.get("fps", 24)

        frame_start = round(start_ms * motion_fps / 1000)
        frame_end = frame_start + round(duration_ms * motion_fps / 1000)
        frame_start = max(0, min(frame_start, total_frames - 1))
        frame_end = max(frame_start + 1, min(frame_end, total_frames))

        actual_ms = round((frame_end - frame_start) * 1000 / motion_fps)
        return {
            "frame_start": frame_start,
            "frame_end": frame_end,
            "frame_count": frame_end - frame_start,
            "actual_duration_ms": actual_ms,
            "motion_fps": motion_fps,
            "total_frames": total_frames,
        }

    def record(
        self,
        character: str,
        motion: str,
        duration_ms: int,
        start_ms: int = 0,
        fps: int = 24,
        camera: Optional[dict] = None,
        resolution: int = 512,
        samples: int = 32,
        engine: str = "cycles",
        transparent_bg: bool = True,
        lighting: str = "studio",
        output_name: Optional[str] = None,
        timeout: int = 600,
    ) -> dict:
        """
        录制 Mixamo 动作片段。

        参数:
            character: 角色 FBX 文件名
            motion: 动画 FBX 文件名
            duration_ms: 录制时长（毫秒）
            start_ms: 动画起始时间（毫秒）
            fps: 帧率
            camera: 镜头参数（dict 或预设名字符串）
            resolution: 渲染分辨率
            samples: Cycles 采样数
            engine: 渲染引擎 (cycles/eevee)
            transparent_bg: 透明背景
            lighting: 灯光预设
            output_name: 输出文件名（无扩展名）
            timeout: 超时秒数
        """
        if isinstance(camera, str):
            camera = self.get_camera_preset(camera)
        if camera is None:
            camera = self.get_camera_preset("front_waist")

        preview = self.preview_motion(motion, start_ms, duration_ms, fps)
        if output_name is None:
            motion_base = motion.replace(".fbx", "").replace("_withskin", "")
            output_name = f"{motion_base}_ref"

        # 自动补 .fbx
        char_fbx = character if character.lower().endswith(".fbx") else character + ".fbx"
        motion_fbx = motion if motion.lower().endswith(".fbx") else motion + ".fbx"

        # 使用 engine 的 AnimationParams 渲染（通过 engine 的完整管线）
        # engine 的 camera_preset 只支持 5 种，自由镜头需要自定义脚本
        engine_cam_name = self._try_map_to_engine_camera(camera)

        if engine_cam_name:
            # 用 engine 自带管线
            params = AnimationParams(
                preset_name=output_name,
                character=char_fbx,
                motions=[motion_fbx],
                output_format="frames",
                resolution=resolution,
                samples=max(samples, 32),
                fps=fps,
                lighting_preset=lighting,
                camera_preset=engine_cam_name,
                transparent_bg=transparent_bg,
            )
            result = self._cli.render_animation(params, timeout=timeout)
            return {
                "status": result["status"],
                "frame_range": [preview["frame_start"], preview["frame_end"]],
                "frame_count": preview["frame_count"],
                "actual_duration_ms": preview["actual_duration_ms"],
                "camera": camera,
                "outputs": result.get("outputs", []),
                "job_id": result.get("job_id"),
                "raw_result": result,
            }
        else:
            # 自由镜头：生成自定义脚本，基于 engine 的 generate_animation_script 改造
            script = self._generate_custom_script(
                char_fbx=char_fbx,
                motion_fbx=motion_fbx,
                frame_start=preview["frame_start"],
                frame_end=preview["frame_end"],
                fps=fps,
                camera=camera,
                resolution=resolution,
                samples=max(samples, 32),
                render_engine=engine,
                transparent_bg=transparent_bg,
                lighting=lighting,
                output_name=output_name,
            )
            raw = self._cli.run_sync(script, timeout=timeout)
            success = raw.get("returncode") == 0
            return {
                "status": "success" if success else "failed",
                "frame_range": [preview["frame_start"], preview["frame_end"]],
                "frame_count": preview["frame_count"],
                "actual_duration_ms": preview["actual_duration_ms"],
                "camera": camera,
                "outputs": [f"{output_name}_frames/"] if success else [],
                "raw_result": raw,
            }

    def record_batch(self, character: str, motion: str, shots: list, **kwargs) -> list:
        """批量录制同一动作的多个镜头。"""
        results = []
        for shot in shots:
            try:
                r = self.record(
                    character=character,
                    motion=motion,
                    duration_ms=shot.get("duration_ms", 2000),
                    start_ms=shot.get("start_ms", 0),
                    fps=shot.get("fps", kwargs.get("fps", 24)),
                    camera=shot.get("camera", "front_waist"),
                    resolution=shot.get("resolution", kwargs.get("resolution", 512)),
                    samples=shot.get("samples", kwargs.get("samples", 32)),
                    engine=shot.get("engine", kwargs.get("engine", "cycles")),
                    transparent_bg=shot.get("transparent_bg", kwargs.get("transparent_bg", True)),
                    lighting=shot.get("lighting", kwargs.get("lighting", "studio")),
                    output_name=shot.get("output_name"),
                    timeout=shot.get("timeout", kwargs.get("timeout", 600)),
                )
                results.append({**r, "success": r["status"] == "success"})
            except Exception as e:
                results.append({"success": False, "error": str(e), "output_name": shot.get("output_name")})
        return results

    def _try_map_to_engine_camera(self, cam: dict) -> Optional[str]:
        """尝试将自由镜头参数映射到 engine 的 5 种预设"""
        az = cam.get("azimuth", 0)
        el = cam.get("elevation", 0)
        dist = cam.get("distance", 3.0)
        fov = cam.get("fov", 50)

        mapping = [
            ({"azimuth": 0, "elevation": 0}, "front"),
            ({"azimuth": 90, "elevation": 0}, "side"),
            ({"azimuth": 45, "elevation": 10}, "three_quarter"),
        ]
        for keys, name in mapping:
            if abs(az - keys["azimuth"]) < 5 and abs(el - keys["elevation"]) < 5 and abs(dist - 3.0) < 0.5:
                return name
        return None

    def _generate_custom_script(self, **kw) -> str:
        """生成自定义镜头的 Blender 脚本（兼容 Blender 5.1，参照 kais-blender-pose 验证方案）"""
        cam = kw["camera"]
        (cx, cy, cz), (pitch, _, yaw) = _camera_to_location_rotation(cam)
        fov = cam.get("fov", 50)
        lighting = ANIM_LIGHTING_PRESETS.get(kw["lighting"], ANIM_LIGHTING_PRESETS["studio"])
        bg_color = lighting["bg_color"]
        lights_json = json.dumps(lighting["lights"])

        render_engine = "CYCLES" if kw["render_engine"] == "cycles" else "BLENDER_EEVEE"

        return f'''import bpy, json, math, os, mathutils

# ── 清理 ──
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.meshes:
    if block.users == 0: bpy.data.meshes.remove(block)
for block in bpy.data.armatures:
    if block.users == 0: bpy.data.armatures.remove(block)
for block in bpy.data.actions:
    if block.users == 0: bpy.data.actions.remove(block)

# ── 角色 ──
char_path = os.path.join(r"D:", os.sep, "BlenderAgent", "animations", "characters", "{kw['char_fbx']}")
if not os.path.isfile(char_path):
    raise FileNotFoundError("角色: " + char_path)
bpy.ops.import_scene.fbx(filepath=char_path, use_anim=True, automatic_bone_orientation=True, ignore_leaf_bones=True)
char_arm = [o for o in bpy.context.selected_objects if o.type == 'ARMATURE'][0]
char_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']

# ── 动画 ──
motion_path = os.path.join(r"D:", os.sep, "BlenderAgent", "animations", "motions_noskin", "all", "{kw['motion_fbx']}")
if not os.path.isfile(motion_path):
    raise FileNotFoundError("动画: " + motion_path)
bpy.ops.import_scene.fbx(filepath=motion_path, use_anim=True, automatic_bone_orientation=True, ignore_leaf_bones=True)
imported = list(bpy.context.selected_objects)

# 搜索所有 actions，找帧范围 > 10 的（和 kais-blender-pose 一致）
motion_action = None
for a in bpy.data.actions:
    if a.frame_range[1] - a.frame_range[0] > 10:
        motion_action = a
        break
if motion_action is None:
    raise RuntimeError("未找到有效动画 Action（帧范围均 <= 10）")

# 复制 Action 到角色
new_action = motion_action.copy()
new_action.name = f"{{char_arm.name}}_{{os.path.splitext(os.path.basename(motion_path))[0]}}"
if not char_arm.animation_data:
    char_arm.animation_data_create()
char_arm.animation_data.action = new_action

# 清理 motion 导入的对象和 orphan meshes
for o in imported:
    if o != char_arm and o not in char_meshes:
        bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o.parent is None:
        bpy.data.objects.remove(o, do_unlink=True)

# ── 灯光（data API only，和 kais-blender-pose 一致）───
lights_config = {lights_json}
for lc in lights_config:
    light = bpy.data.lights.new(lc['type'], lc['type'])
    light.energy = lc['energy']
    light.size = lc.get('size', 1.0)
    light.color = lc['color']
    obj = bpy.data.objects.new(lc['type'], light)
    obj.location = lc['location']
    bpy.context.scene.collection.objects.link(obj)

# ── 世界背景（和 kais-blender-pose 一致：nodes.new + link）───
scene = bpy.context.scene
world = bpy.data.worlds.new("BgWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = {bg_color} + (1.0,)
bg.inputs['Strength'].default_value = 1.0
world.node_tree.links.new(bg.outputs[0], world.node_tree.nodes['World Output'].inputs[0])

# ── 相机（自由参数）───
cam_data = bpy.data.cameras.new("ActionCam")
cam_obj = bpy.data.objects.new("ActionCam", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = ({cx:.4f}, {cy:.4f}, {cz:.4f})
direction = mathutils.Vector((0, 0, {kw.get("target_height", 0.9)})) - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = {fov}
scene.camera = cam_obj

# ── 渲染设置（和 kais-blender-pose 一致：不设 GPU/OPTIX/denoiser）───
scene.render.engine = '{render_engine}'
scene.render.resolution_x = {kw['resolution']}
scene.render.resolution_y = {kw['resolution']}
scene.render.fps = {kw['fps']}
scene.cycles.samples = {kw['samples']}
scene.render.film_transparent = {str(kw['transparent_bg'])}
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# ── 帧范围 ──
scene.frame_start = {kw['frame_start']}
scene.frame_end = {kw['frame_end']}

# ── 渲染 ──
frames_dir = os.path.join(r"D:", os.sep, "BlenderAgent", "outputs", "actions", "{kw['output_name']}_frames")
os.makedirs(frames_dir, exist_ok=True)
scene.render.filepath = os.path.join(frames_dir, "")
bpy.ops.render.render(animation=True)

# ── 验证 ──
rendered = [f for f in os.listdir(frames_dir) if f.endswith('.png')]
print(f"RENDER_OK: {{len(rendered)}} frames in {{frames_dir}}")

# 清理
if char_arm.animation_data:
    char_arm.animation_data.action = None
'''
