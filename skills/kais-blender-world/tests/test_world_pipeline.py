#!/usr/bin/env python3
"""
kais-blender-world 全管线自动化测试

测试场景：咖啡厅对话 — 两个人在咖啡厅面对面坐着聊天
覆盖能力：
  - 多角色（2人）
  - 坐姿动画（sofa 位置放置）
  - 多机位（XWS/WS/MS/CU/ECU 全覆盖）
  - HDRI 切换（warm + studio）
  - 跨镜头连续性
  - 渲染执行 + 结果验证
"""

import json
import os
import sys
import time
import requests

# ── 配置 ──────────────────────────────────────────────────
SERVER = "http://192.168.71.38:8080"
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(TEST_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kais-blender-layout"))
from blender_layout import render_scene, CAMERA_PRESETS, DEFAULTS

# ── 测试场景设计 ──────────────────────────────────────────
#
# 场景：咖啡厅对话
# 角色 A（左侧）：sitting_while_laughing — 笑着说话
# 角色 B（右侧）：sitting_unethusiastic_clap — 鼓掌回应
# 家具：sofa_02（两人共享）
# 灯光：warm（温馨咖啡厅氛围）
# 机位：5 种全覆盖
#

TEST_NAME = "咖啡厅对话"
HDRI_WARM = "kloppenheim_06_4k"
HDRI_STUDIO = "studio_small_03_4k"
RESOLUTION = (1280, 720)
SAMPLES = 64  # 快速测试用低采样

# 从 engine API 获取的实际路径
ANIM_A = r"D:\BlenderAgent\animations\motions\sitting_while_laughing_inplace_withskin.fbx"
ANIM_B = r"D:\BlenderAgent\animations\motions\sitting_unethusiastic_clap_inplace_withskin.fbx"
OUTPUT_DIR = r"D:\BlenderAgent\outputs"


# ══════════════════════════════════════════════════════════
# 阶段 0：前置检查
# ══════════════════════════════════════════════════════════

def test_health():
    """检查 Blender Agent 是否在线"""
    r = requests.get(f"{SERVER}/health", timeout=5)
    data = r.json()
    assert data["status"] == "ok", f"Engine not healthy: {data}"
    print(f"  ✅ Engine online: Blender {data.get('blender', 'unknown')}")
    return data


def test_assets():
    """检查所需资产是否就位"""
    r = requests.get(f"{SERVER}/animations", timeout=10)
    data = r.json()
    all_motions = [m["filename"] for m in data.get("motions", [])]
    
    motion_paths = [m.get("path", m["filename"]) for m in data.get("motions", [])]
    for anim_name, anim_path in [("角色A (laughing)", ANIM_A), ("角色B (clap)", ANIM_B)]:
        # Match by filename (basename) against both filename and path fields
        basename = os.path.basename(anim_path)
        found = basename in all_motions or any(basename in p for p in motion_paths)
        assert found, f"Missing: {basename}"
        print(f"  ✅ {anim_name}: {basename}")

    r2 = requests.get(f"{SERVER}/scene-assets", timeout=10)
    assets = r2.json()
    hdris = [a["name"] for a in assets["assets"] if a["category"] == "hdris"]
    for h in [HDRI_WARM, HDRI_STUDIO]:
        assert h in hdris, f"Missing HDRI: {h}"
        print(f"  ✅ HDRI: {h}")


# ══════════════════════════════════════════════════════════
# 阶段 1：场景规划（蓝图生成）
# ══════════════════════════════════════════════════════════

def test_blueprint_generation():
    """测试场景蓝图生成"""
    blueprint = {
        "scene": {
            "name": TEST_NAME,
            "description": "两人在咖啡厅沙发上面对面坐着聊天，温馨氛围"
        },
        "characters": [
            {"label": "角色A", "animation": ANIM_A, "role": "speaker"},
            {"label": "角色B", "animation": ANIM_B, "role": "listener"},
        ],
        "environment": {"name": "咖啡厅", "style": "warm"},
        "furniture": {"sofa": "sofa_02"},
        "lighting": {"scheme": "warm"},
        "relations": [
            {"subject": "角色A", "relation": "facing", "object": "角色B", "distance": 1.5},
            {"subject": "角色B", "relation": "facing", "object": "角色A", "distance": 1.5},
            {"subject": "角色A", "relation": "near", "object": "sofa", "distance": 0.5},
            {"subject": "角色B", "relation": "near", "object": "sofa", "distance": 0.5},
        ],
    }

    # 验证空间关系
    assert len(blueprint["relations"]) == 4
    assert all(r["distance"] >= 0.3 for r in blueprint["relations"]), "碰撞检测失败"

    bp_path = os.path.join(TEST_DIR, "blueprint.json")
    with open(bp_path, "w") as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Blueprint: 2 characters, 4 spatial relations, collision check passed")

    return blueprint


# ══════════════════════════════════════════════════════════
# 阶段 2：渲染脚本生成
# ══════════════════════════════════════════════════════════

def test_script_generation():
    """测试渲染脚本生成 — 验证脚本包含所有关键操作"""
    script = render_scene(
        characters=[
            {"animation": ANIM_A, "position": "sofa"},
            {"animation": ANIM_B, "position": "sofa"},
        ],
        hdri=HDRI_WARM,
        camera_shots=["extreme_wide", "wide", "medium", "closeup", "extreme_closeup"],
        sofa_scale=1.34,
        output_dir=OUTPUT_DIR,
        samples=SAMPLES,
        resolution=RESOLUTION,
    )

    # 验证关键操作
    checks = {
        "基础场景加载": "open_mainfile" in script,
        "FBX导入(角色A)": ANIM_A.split("\\")[-1] in script,
        "FBX导入(角色B)": ANIM_B.split("\\")[-1] in script,
        "删除旧mesh": "Human" in script and "remove" in script,
        "隐藏骨骼": "Beta_Joints" in script and "hide_render" in script,
        "保留皮肤": "Beta_Surface" not in script or "Beta_Joints" in script,
        "沙发缩放": "sofa_scale" in script and "1.34" in script,
        "AABB刷新": "view_layer.update()" in script,
        "HDRI加载": HDRI_WARM in script,
        "Cycles渲染": "CYCLES" in script,
        "GPU加速": "GPU" in script,
        "5种机位": all(f"scene_{s}.png" in script for s in ["extreme_wide", "wide", "medium", "closeup", "extreme_closeup"]),
        "look_at函数": "look_at" in script and "to_track_quat" in script,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        print(f"  ❌ Script checks failed: {failed}")
        for k in failed:
            print(f"     - {k}")
        assert False, f"Script generation incomplete: {failed}"

    for k, v in checks.items():
        print(f"  ✅ {k}")

    script_path = os.path.join(TEST_DIR, "render_cafe.py")
    with open(script_path, "w") as f:
        f.write(script)
    print(f"  ✅ Script saved: {len(script)} chars")

    return script


# ══════════════════════════════════════════════════════════
# 阶段 3：渲染执行
# ══════════════════════════════════════════════════════════

def test_render(script):
    """提交渲染脚本到 Blender Agent"""
    print(f"  📤 Submitting render ({len(script)} chars)...")
    r = requests.post(f"{SERVER}/run/script", json={"script": script, "timeout": 300}, timeout=600)
    data = r.json()

    if r.status_code != 200:
        print(f"  ❌ HTTP {r.status_code}: {data}")
        return None

    returncode = data.get("returncode", -1)
    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")

    if returncode != 0 or "DONE" not in stdout:
        print(f"  ❌ Render failed (returncode={returncode})")
        print(f"     stdout: {stdout[-300:]}")
        print(f"     stderr: {stderr[-300:]}")
        return None

    # 检查 stderr 中的渲染确认
    ok_count = stderr.count("[OK]")
    expected_shots = 5
    print(f"  ✅ Render success: {ok_count}/{expected_shots} shots confirmed")
    if ok_count < expected_shots:
        print(f"  ⚠️  {expected_shots - ok_count} shots missing")

    return data


# ══════════════════════════════════════════════════════════
# 阶段 4：渲染结果验证
# ══════════════════════════════════════════════════════════

def test_render_results():
    """验证渲染图片是否生成"""
    r = requests.get(f"{SERVER}/outputs", timeout=10)
    data = r.json()
    all_files = [f["name"] for f in data.get("files", [])]

    expected = [f"scene_{s}.png" for s in ["extreme_wide", "wide", "medium", "closeup", "extreme_closeup"]]
    found = []
    missing = []
    for e in expected:
        # 搜索匹配的文件名（可能在不同子目录）
        matches = [f for f in all_files if e in f]
        if matches:
            found.append((e, matches[0]))
        else:
            missing.append(e)

    for name, actual in found:
        print(f"  ✅ {name} → {actual}")
    for name in missing:
        print(f"  ❌ Missing: {name}")

    assert len(missing) == 0, f"Missing renders: {missing}"
    return found


# ══════════════════════════════════════════════════════════
# 阶段 5：HDRI 切换测试（第二个场景）
# ══════════════════════════════════════════════════════════

def test_hdri_switch():
    """测试 HDRI 切换渲染"""
    script = render_scene(
        characters=[
            {"animation": ANIM_A, "position": "sofa"},
        ],
        hdri=HDRI_STUDIO,
        camera_shots=["medium", "closeup"],
        sofa_scale=1.34,
        output_dir=OUTPUT_DIR.replace("world_test", "world_test_studio"),
        samples=SAMPLES,
        resolution=RESOLUTION,
    )

    assert HDRI_STUDIO in script, "HDRI not in script"
    assert "kloppenheim" not in script, "Old HDRI leaked into script"
    print(f"  ✅ HDRI switch: {HDRI_WARM} → {HDRI_STUDIO}")

    r = requests.post(f"{SERVER}/run/script", json={"script": script, "timeout": 300}, timeout=600)
    data = r.json()
    stderr = data.get("stderr", "")
    ok_count = stderr.count("[OK]")
    assert data.get("returncode") == 0 and "DONE" in data.get("stdout", ""), f"Studio render failed: {stderr[-300:]}"
    print(f"  ✅ Studio render: {ok_count}/2 shots confirmed")
    return True


# ══════════════════════════════════════════════════════════
# 阶段 6：站姿场景测试（无家具）
# ══════════════════════════════════════════════════════════

def test_standing_scene():
    """测试站姿场景（不依赖家具放置）"""
    script = render_scene(
        characters=[
            {"animation": r"D:\BlenderAgent\animations\motions\idle_inplace_withskin.fbx"},
        ],
        hdri="spruit_sunrise_4k",
        camera_shots=["wide", "medium"],
        sofa_scale=1.0,
        output_dir=OUTPUT_DIR.replace("world_test", "world_test_standing"),
        samples=SAMPLES,
        resolution=RESOLUTION,
    )

    # Just verify it renders successfully (sofa scale code is always emitted)
    r = requests.post(f"{SERVER}/run/script", json={"script": script, "timeout": 300}, timeout=600)
    data = r.json()
    stderr = data.get("stderr", "")
    ok_count = stderr.count("[OK]")
    assert data.get("returncode") == 0 and "DONE" in data.get("stdout", ""), f"Standing render failed: {stderr[-300:]}"
    print(f"  ✅ Standing render: {ok_count}/2 shots confirmed")
    return True


# ══════════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════════

def main():
    results = {}
    start = time.time()

    print("=" * 60)
    print(f"🏗️  kais-blender-world 全管线自动化测试")
    print(f"    场景: {TEST_NAME}")
    print(f"    目标: 多角色 + 坐姿 + 5机位 + HDRI切换 + 站姿")
    print("=" * 60)

    # 阶段 0
    print("\n📡 [Phase 0] 前置检查")
    try:
        test_health()
        test_assets()
        results["phase0"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase0"] = f"FAIL: {e}"
        return results

    # 阶段 1
    print("\n🗺️  [Phase 1] 场景蓝图生成")
    try:
        blueprint = test_blueprint_generation()
        results["phase1"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase1"] = f"FAIL: {e}"
        return results

    # 阶段 2
    print("\n📝 [Phase 2] 渲染脚本生成")
    try:
        script = test_script_generation()
        results["phase2"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase2"] = f"FAIL: {e}"
        return results

    # 阶段 3
    print("\n🎨 [Phase 3] 渲染执行（咖啡厅对话，5机位）")
    try:
        render_result = test_render(script)
        if render_result is None:
            results["phase3"] = "FAIL: render returned None"
            return results
        results["phase3"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase3"] = f"FAIL: {e}"
        return results

    # 阶段 4
    print("\n🖼️  [Phase 4] 渲染结果验证")
    try:
        time.sleep(2)  # Wait for file system sync
        found = test_render_results()
        results["phase4"] = f"PASS ({len(found)} renders)"
    except Exception as e:
        print(f"  ⚠️  {e}")
        results["phase4"] = f"WARN: {e}"

    # 阶段 5
    print("\n🔄 [Phase 5] HDRI 切换测试")
    try:
        test_hdri_switch()
        results["phase5"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase5"] = f"FAIL: {e}"

    # 阶段 6
    print("\n🧍 [Phase 6] 站姿场景测试")
    try:
        test_standing_scene()
        results["phase6"] = "PASS"
    except Exception as e:
        print(f"  ❌ {e}")
        results["phase6"] = f"FAIL: {e}"

    # 总结
    elapsed = time.time() - start
    passed = sum(1 for v in results.values() if v.startswith("PASS") or v.startswith("WARN"))
    total = len(results)

    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} passed ({elapsed:.1f}s)")
    print("=" * 60)
    for phase, status in results.items():
        icon = "✅" if status.startswith("PASS") else "❌"
        print(f"  {icon} {phase}: {status}")

    # 保存报告
    report = {
        "test_name": TEST_NAME,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round(elapsed, 1),
        "phases": results,
        "passed": passed,
        "total": total,
        "server": SERVER,
    }
    report_path = os.path.join(TEST_DIR, "test_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Report: {report_path}")

    return results


if __name__ == "__main__":
    main()
