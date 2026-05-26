---
name: kais-blender-assets
version: 0.1.0
description: "3D 资产获取与管理管线。自动搜索、下载、组织 Blender 渲染所需资产（Mixamo 角色/动画、Poly Haven 模型/HDRI/纹理、ambientCG 纹理）。触发词：下载资产, 获取模型, 找HDRI, 找模型, 搜索资产, asset download, mixamo下载, polyhaven, 找角色, 找动画, 3D资产, 资产管理, 资产入库"
---

# kais-blender-assets — 3D 资产获取与管理管线

> 自动化搜索、下载、组织 Blender 渲染所需的所有 3D 资产。
> 让 kais-blender-world / layout / engine 能按需获取素材，无需人工干预。

## 资产目录结构（Windows 端）

```
D:\BlenderAgent\
├── assets\                        # 场景素材
│   ├── polyhaven\
│   │   ├── hdris\                 # HDRI 环境光
│   │   │   ├── kloppenheim_06_4k.hdr
│   │   │   └── ...
│   │   ├── models\                # 3D 模型
│   │   │   ├── sofa_02\
│   │   │   └── ...
│   │   └── textures\              # PBR 纹理
│   │       └── ...
│   └── ambientcg\
│       └── textures\              # PBR 纹理
│           └── ...
├── animations\                    # Mixamo 资源
│   ├── characters\                # 角色 FBX（带骨骼）
│   │   ├── hero.fbx
│   │   └── ...
│   └── motions\                   # 动画 FBX（Without Skin）
│       ├── walk.fbx
│       ├── run.fbx
│       └── ...
├── cache\                         # 缓存/模板场景
│   └── full_scene.blend
└── outputs\                       # 渲染输出
```

---

## 资产来源

### 1. Mixamo（角色 + 动画）

**网站**：https://www.mixamo.com/

#### 下载角色 FBX

1. 上传角色模型（OBJ/FBX）→ Auto-Rig
2. 下载格式：**FBX for Blender**，FBX 2019，**With Skin**
3. 放入 `D:\BlenderAgent\animations\characters\`
4. 命名规范：`{角色名}.fbx`（小写+下划线，如 `hero_knight.fbx`）

#### 下载动画 FBX

1. 选择角色 → 选择动画
2. 下载格式：**FBX for Blender**，**Without Skin**，**In Place**，FBX 2019
3. 放入 `D:\BlenderAgent\animations\motions\`
4. 命名规范：`{动作名}.fbx`（小写+下划线，如 `walk_forward.fbx`）

#### 关键经验

| 要点 | 说明 |
|------|------|
| **With Skin vs Without Skin** | 角色 FBX 用 With Skin（带 mesh），动画 FBX 用 Without Skin（纯动画，可复用） |
| **In Place** | 动画下载必须选 In Place，否则角色会移动偏离场景 |
| **FBX 2019** | Blender 5.1 对 FBX 2019 兼容性最好 |
| **角色比例** | Mixamo 角色默认 ~1.8m，Poly Haven 家具比例偏小（如沙发 0.71m），需要缩放家具而非角色 |
| **骨骼结构** | Mixamo 统一骨骼命名（Hips, Spine, LeftArm...），动画可在不同角色间复用 |

#### 常用动画推荐

**坐姿类**：
- `sitting_while_laughing_inplace_withskin` — 坐着笑
- `sitting_talking_inplace` — 坐着说话
- `sitting_idle` — 坐着待机

**站姿类**：
- `idle_inplace_withskin` — 站立待机
- `standing_to_sitting` — 站到坐过渡
- `talking_inplace` — 站着说话

**运动类**：
- `walk_forward_inplace` — 行走
- `run_forward_inplace` — 跑步
- `fighting_idle` — 格斗待机

### 2. Poly Haven（模型 + HDRI + 纹理）

**网站**：https://polyhaven.com/

#### HDRI 环境光

- 用途：场景全局光照和背景
- 格式：`.hdr`（4K 推荐）
- 路径：`D:\BlenderAgent\assets\polyhaven\hdris\`
- 命名：`{名称}_4k.hdr`

**推荐 HDRI**：

| 氛围 | 推荐文件名 | 说明 |
|------|-----------|------|
| 温馨室内 | `kloppenheim_06_4k` | 暖色调，适合客厅 |
| 工作室 | `studio_small_03_4k` | 中性，适合角色展示 |
| 户外 | `urban_street_01_4k` | 城市场景 |
| 戏剧性 | `night_roads_02_4k` | 夜景，高对比 |
| 自然 | `spruit_sunrise_4k` | 日出，暖色 |

#### 3D 模型

- 用途：家具、道具、环境物体
- 格式：Blend 文件（Poly Haven 原生格式）
- 路径：`D:\BlenderAgent\assets\polyhaven\models\{模型名}\`
- 下载：直接下载 ZIP → 解压到对应目录

**已知模型 + 比例经验**：

| 模型 | 原始尺寸 | 与 Mixamo 角色比例 | 建议缩放 |
|------|---------|-------------------|---------|
| `sofa_02` | ~0.71m | 太小（角色 1.8m） | **1.34x** |
| `arm_chair_01` | ~0.85m | 偏小 | ~1.2x |
| `desk_01` | ~0.75m | 偏小 | ~1.1x |

⚠️ **重要**：Poly Haven 模型比例普遍偏小，与 Mixamo 角色搭配时需要按实际情况缩放。不要拆分模型的子组件（如沙发座垫从底座拆出会悬浮）。

#### PBR 纹理

- 用途：材质贴图
- 路径：`D:\BlenderAgent\assets\polyhaven\textures\{纹理名}\`

### 3. ambientCG（PBR 纹理）

**网站**：https://ambientcg.com/

- 用途：免费 PBR 纹理（CC0）
- 路径：`D:\BlenderAgent\assets\ambientcg\textures\{纹理名}\`
- 与 Poly Haven 纹理互补

---

## 索引刷新

资产下载或删除后，需要刷新索引：

### 动画索引

```bash
# 通过 engine API
curl http://<IP>:8080/animations/rebuild
```

### 场景素材索引

```bash
# 通过 engine API
curl http://<IP>:8080/assets/rebuild
```

### 查询现有资产

```bash
# 查看所有角色和动画
curl http://<IP>:8080/animations

# 查看素材统计
curl http://<IP>:8080/assets/stats

# 查看完整素材列表
curl http://<IP>:8080/assets
```

---

## 资产搜索策略

当场景蓝图需要某个 `model_hint` 时，按以下优先级搜索：

1. **本地已下载** — 查询 engine 索引，检查是否已存在
2. **Poly Haven** — 免费 CC0，质量高，模型+HDRI+纹理全覆盖
3. **ambientCG** — 免费 CC0，PBR 纹理
4. **Sketchfab** — 社区模型丰富，注意许可证（部分需商用授权）
5. **Mixamo 内置** — Mixamo 自带的基础角色可直接使用

### 搜索关键词映射

| 场景蓝图需求 | 搜索关键词 | 推荐来源 |
|-------------|-----------|---------|
| 沙发 | `sofa`, `couch` | Poly Haven |
| 桌子 | `desk`, `table` | Poly Haven |
| 椅子 | `chair`, `armchair` | Poly Haven |
| 战士角色 | `warrior`, `knight` | Mixamo 上传 |
| 行走动画 | `walk` | Mixamo |
| 室内光照 | `indoor`, `studio` | Poly Haven HDRI |
| 地板纹理 | `wood floor`, `marble` | Poly Haven / ambientCG |

---

## 下载脚本

### 批量下载 Poly Haven 资产

```bash
# 下载 HDRI
python3 scripts/download_polyhaven.py --type hdri --names kloppenheim_06,studio_small_03

# 下载模型
python3 scripts/download_polyhaven.py --type model --names sofa_02,desk_01

# 下载纹理
python3 scripts/download_polyhaven.py --type texture --names wood_floor_01
```

### Mixamo 动画批量查询

```bash
# 列出已下载的动画
curl -s http://<IP>:8080/animations | python3 -m json.tool | grep name
```

---

## 与其他 Skill 的协作

```
kais-blender-world (总调度)
  ├── kais-blender-assets (本skill) — 资产获取+管理
  ├── kais-blender-layout — 场景规划+布局渲染
  └── kais-blender-engine — 渲染执行+资产管理API
```

**调用关系**：
- world 拿到场景蓝图后，先调 **assets** 获取缺失资产
- assets 下载完成后，调 engine `/animations/rebuild` 和 `/assets/rebuild` 刷新索引
- 之后 layout 和 engine 才能使用这些资产

## 注意事项

- 所有资产下载到 **Windows 端**（`D:\BlenderAgent\`），本 skill 在 Linux 端编排下载流程
- Mixamo 需要 Adobe 账号，部分操作可能需要浏览器自动化
- 注意资产许可证：Poly Haven/ambientCG 是 CC0，Sketchfab 需确认
- 下载后**必须刷新索引**，否则 engine 查不到新资产
- 大文件下载注意磁盘空间，Poly Haven 4K HDRI 约 50-100MB/个
