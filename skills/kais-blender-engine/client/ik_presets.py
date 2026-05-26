"""IK 姿态预设 — Mixamo 骨骼 IK 链配置与目标位置

通过指定手脚的目标位置，利用 Blender IK 约束自动反算骨骼链旋转。
比 FK 预设（直接设关节角度）更自然，适合 "手够到某处" 类姿态。
"""

from typing import Dict, List, Optional, Tuple

# ── Mixamo 骨骼 IK 链定义 ─────────────────────────────────
# key: IK 约束所在末端骨骼
# chain_count: IK 影响链长度（含末端骨骼本身）
# pole_bone: 膝盖/手肘方向参考骨骼（可选）

IK_CHAINS: Dict[str, Dict] = {
    # 左臂: LeftHand ← LeftForeArm ← LeftArm
    "mixamorig:LeftHand": {
        "chain_count": 3,
        "pole_bone": "mixamorig:LeftArm",
    },
    # 右臂: RightHand ← RightForeArm ← RightArm
    "mixamorig:RightHand": {
        "chain_count": 3,
        "pole_bone": "mixamorig:RightArm",
    },
    # 左脚: LeftFoot ← LeftLeg ← LeftUpLeg
    "mixamorig:LeftFoot": {
        "chain_count": 3,
        "pole_bone": "mixamorig:LeftLeg",
    },
    # 右脚: RightFoot ← RightLeg ← RightUpLeg
    "mixamorig:RightFoot": {
        "chain_count": 3,
        "pole_bone": "mixamorig:RightLeg",
    },
    # 左手头: LeftHandThumb2（更精确的手指 IK，可选）
    "mixamorig:LeftHandThumb2": {
        "chain_count": 2,
        "pole_bone": "mixamorig:LeftHand",
    },
    # 右手头: RightHandThumb2
    "mixamorig:RightHandThumb2": {
        "chain_count": 2,
        "pole_bone": "mixamorig:RightHand",
    },
    # 头部: Head ← Neck ← Spine2（用于头部朝向控制）
    "mixamorig:Head": {
        "chain_count": 3,
        "pole_bone": "mixamorig:Neck",
    },
}

# ── IK 姿态预设 ──────────────────────────────────────────
# 每个预设: {末端骨骼: 目标位置 (x, y, z)}
# 坐标系: Mixamo 标准（Y 前方, Z 上方, 角色面向 -Y）
# 角色约 1.7m 高，原点在脚底

IK_PRESETS: Dict[str, Dict[str, Tuple[float, float, float]]] = {
    # ── 手臂预设 ────────────────────────────────────────
    "reach_forward": {
        "mixamorig:LeftHand": (0.3, -0.8, 1.4),
        "mixamorig:RightHand": (-0.3, -0.8, 1.4),
    },
    "reach_up": {
        "mixamorig:LeftHand": (0.3, 0, 2.3),
        "mixamorig:RightHand": (-0.3, 0, 2.3),
    },
    "reach_left": {
        "mixamorig:LeftHand": (0.8, 0, 1.4),
        "mixamorig:RightHand": (-0.2, -0.3, 1.4),
    },
    "reach_right": {
        "mixamorig:RightHand": (-0.8, 0, 1.4),
        "mixamorig:LeftHand": (0.2, -0.3, 1.4),
    },
    "reach_down": {
        "mixamorig:LeftHand": (0.3, -0.2, 0.5),
        "mixamorig:RightHand": (-0.3, -0.2, 0.5),
    },
    "hands_behind_head": {
        "mixamorig:LeftHand": (0.25, 0.1, 1.85),
        "mixamorig:RightHand": (-0.25, 0.1, 1.85),
    },
    "wave_left": {
        "mixamorig:LeftHand": (0.5, -0.2, 2.0),
    },
    "wave_right": {
        "mixamorig:RightHand": (-0.5, -0.2, 2.0),
    },
    "box_guard": {
        "mixamorig:LeftHand": (0.35, -0.3, 1.45),
        "mixamorig:RightHand": (-0.35, -0.3, 1.45),
    },
    "point_forward": {
        "mixamorig:RightHand": (-0.15, -0.9, 1.4),
    },
    "arms_wide": {
        "mixamorig:LeftHand": (1.0, 0.1, 1.4),
        "mixamorig:RightHand": (-1.0, 0.1, 1.4),
    },
    # ── 腿部预设 ────────────────────────────────────────
    "kick_left": {
        "mixamorig:LeftFoot": (0.2, -0.8, 0.4),
    },
    "kick_right": {
        "mixamorig:RightFoot": (-0.2, -0.8, 0.4),
    },
    "wide_stance": {
        "mixamorig:LeftFoot": (0.4, 0, 0),
        "mixamorig:RightFoot": (-0.4, 0, 0),
    },
    "lunge_left": {
        "mixamorig:LeftFoot": (0.4, -0.3, 0),
        "mixamorig:RightFoot": (-0.3, 0.2, 0),
    },
    # ── 组合预设 ────────────────────────────────────────
    "superman": {
        "mixamorig:LeftHand": (0.5, -0.7, 1.5),
        "mixamorig:RightHand": (-0.5, -0.7, 1.5),
        "mixamorig:LeftFoot": (0.15, 0.4, 0),
        "mixamorig:RightFoot": (-0.15, 0.4, 0),
    },
    "squat_reach": {
        "mixamorig:LeftHand": (0.4, -0.3, 1.0),
        "mixamorig:RightHand": (-0.4, -0.3, 1.0),
        "mixamorig:LeftFoot": (0.3, -0.1, 0),
        "mixamorig:RightFoot": (-0.3, -0.1, 0),
    },
    "taunt": {
        "mixamorig:LeftHand": (0.4, -0.4, 1.6),
        "mixamorig:RightHand": (-0.4, -0.4, 1.6),
        "mixamorig:LeftFoot": (0.25, 0, 0),
        "mixamorig:RightFoot": (-0.25, 0, 0),
    },
}


def get_ik_preset(name: str) -> Dict[str, Tuple[float, float, float]]:
    """获取 IK 姿态预设

    Args:
        name: 预设名（reach_forward, reach_up 等）

    Returns:
        IK 目标字典 {末端骨骼: (x, y, z) 目标位置}
    """
    return dict(IK_PRESETS.get(name, {}))


def get_ik_chain(bone_name: str) -> Optional[Dict]:
    """获取骨骼的 IK 链配置

    Args:
        bone_name: Mixamo 骨骼名（如 mixamorig:LeftHand）

    Returns:
        链配置 {"chain_count": int, "pole_bone": str} 或 None
    """
    return IK_CHAINS.get(bone_name)


def list_ik_presets() -> List[str]:
    """列出所有 IK 预设名称"""
    return list(IK_PRESETS.keys())
