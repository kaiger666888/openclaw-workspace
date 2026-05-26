"""骨骼姿态预设 — Mixamo 骨骼旋转数据（弧度）

Mixamo 骨骼（52 bones），旋转顺序 (X, Y, Z)，Blender XYZ Euler。
"""

# ── Mixamo 骨骼预设 ─────────────────────────────────────
MIXAMO_POSE_PRESETS = {
    "t-pose": {},
    "standing": {
        "mixamorig:LeftArm": (0, 0, 0.3),
        "mixamorig:RightArm": (0, 0, -0.3),
        "mixamorig:LeftForeArm": (0, 0, -0.1),
        "mixamorig:RightForeArm": (0, 0, 0.1),
    },
    "arms_up": {
        "mixamorig:LeftArm": (1.5, 0, 0),
        "mixamorig:RightArm": (1.5, 0, 0),
    },
    "walk_left": {
        "mixamorig:LeftUpLeg": (0.5, 0, 0),
        "mixamorig:LeftLeg": (-0.8, 0, 0),
        "mixamorig:LeftArm": (-0.3, 0, 0),
        "mixamorig:LeftForeArm": (-0.4, 0, 0),
    },
    "walk_right": {
        "mixamorig:RightUpLeg": (-0.5, 0, 0),
        "mixamorig:RightLeg": (0.8, 0, 0),
        "mixamorig:RightArm": (0.3, 0, 0),
        "mixamorig:RightForeArm": (0.4, 0, 0),
    },
    "wave": {
        "mixamorig:LeftArm": (1.5, 0, 0.2),
        "mixamorig:LeftForeArm": (2.0, 0, 0),
    },
    "sit": {
        "mixamorig:LeftUpLeg": (1.5, 0, 0),
        "mixamorig:RightUpLeg": (1.5, 0, 0),
        "mixamorig:LeftLeg": (-1.5, 0, 0),
        "mixamorig:RightLeg": (-1.5, 0, 0),
    },
    "run": {
        "mixamorig:LeftUpLeg": (0.9, 0, 0),
        "mixamorig:LeftLeg": (-1.2, 0, 0),
        "mixamorig:RightUpLeg": (-0.6, 0, 0),
        "mixamorig:RightLeg": (0.3, 0, 0),
        "mixamorig:LeftArm": (-0.5, 0, 0),
        "mixamorig:LeftForeArm": (-0.6, 0, 0),
        "mixamorig:RightArm": (0.5, 0, 0),
        "mixamorig:RightForeArm": (0.6, 0, 0),
        "mixamorig:Spine": (-0.1, 0, 0),
        "mixamorig:Spine1": (-0.1, 0, 0),
    },
    "fighting_stance": {
        "mixamorig:LeftUpLeg": (0.3, 0.1, 0),
        "mixamorig:LeftLeg": (-0.6, 0, 0),
        "mixamorig:RightUpLeg": (-0.2, -0.1, 0),
        "mixamorig:RightLeg": (-0.3, 0, 0),
        "mixamorig:LeftArm": (0.8, 0.5, 0.3),
        "mixamorig:LeftForeArm": (-1.5, 0, 0),
        "mixamorig:RightArm": (0.6, -0.3, -0.2),
        "mixamorig:RightForeArm": (-1.2, 0, 0),
        "mixamorig:Spine1": (0, 0, 0.1),
    },
    "hands_on_hips": {
        "mixamorig:LeftArm": (0, 0, 0.8),
        "mixamorig:LeftForeArm": (1.5, 0, 0),
        "mixamorig:RightArm": (0, 0, -0.8),
        "mixamorig:RightForeArm": (1.5, 0, 0),
    },
    "crossed_arms": {
        "mixamorig:LeftArm": (0, 0, 0.8),
        "mixamorig:LeftForeArm": (1.8, 0, 0),
        "mixamorig:RightArm": (0, 0, -0.8),
        "mixamorig:RightForeArm": (1.8, 0, 0),
    },
    "sitting_relaxed": {
        "mixamorig:LeftUpLeg": (1.5, 0, 0),
        "mixamorig:RightUpLeg": (1.5, 0, 0),
        "mixamorig:LeftLeg": (-1.5, 0, 0),
        "mixamorig:RightLeg": (-1.5, 0, 0),
        "mixamorig:LeftArm": (0, 0, 0.5),
        "mixamorig:LeftForeArm": (1.2, 0, 0),
        "mixamorig:RightArm": (0, 0, -0.5),
        "mixamorig:RightForeArm": (1.2, 0, 0),
        "mixamorig:Spine1": (-0.1, 0, 0),
    },
}


def get_pose_preset(name: str) -> dict:
    """获取 Mixamo 骨骼姿态预设

    Args:
        name: 预设名（t-pose, standing, walk_left 等）

    Returns:
        骨骼旋转字典 {bone_name: (rx, ry, rz)}
    """
    return dict(MIXAMO_POSE_PRESETS.get(name, {}))
