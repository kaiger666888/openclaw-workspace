# 双 GPU 策略调查报告

> RTX 3090 24GB + RTX 3060 Ti 8GB · 华硕 B550M-PLUS  
> 调研日期: 2026-05-02

---

## 1. 硬件拓扑

### 主板 PCIe 布局

| 插槽 | PCIe 版本 | 电气带宽 | 安装 GPU |
|------|----------|---------|---------|
| PCIe x16_1 | 4.0 x16 | **全带宽 (16 GT/s × 16)** | RTX 3090 24GB |
| PCIe x16_2 | 4.0 x4 | **限速 (16 GT/s × 4)** | RTX 3060 Ti 8GB |

> B550M-PLUS 第二插槽与 M.2 共享 PCIe 通道，电气 x4。  
> 3060 Ti 的 GPU 计算能力不受影响，但 GPU↔CPU 数据传输带宽降至 25%。

### 带宽影响分析

| 场景 | x16 (3090) | x4 (3060 Ti) | 影响程度 |
|------|-----------|-------------|---------|
| CUDA 计算（矩阵乘法、推理） | 基准 | 基准 | ✅ 无影响 |
| 模型加载（GPU→CPU 传输） | 快 | 慢 ~3-4× | ⚠️ 启动时间加长 |
| 显存 offload 到系统内存 | 可用但慢 | 极慢，不推荐 | ❌ 避免触发 |
| 纹理加载（Blender） | 快 | 慢 ~3-4× | ⚠️ 大场景会卡 |
| 视频编码/解码 | 快 | 中等 | ⚠️ 轻微影响 |
| 实时渲染输出回传 | 快 | 慢 | ⚠️ 轻微影响 |

### 功耗与散热

| 项目 | 数值 |
|------|------|
| RTX 3090 TDP | 350W |
| RTX 3060 Ti TDP | 200W |
| GPU 总功耗 | **550W** |
| 推荐电源 | ≥750W（推荐 850W 留余量） |
| 散热注意 | 双卡紧邻，3090 三风扇占 2.5 槽，注意机箱风道 |

### 安装检查清单

- [ ] 电源 ≥750W，确认有足够 8-pin/12-pin 供电线
- [ ] BIOS 确认第二插槽 PCIe 速度为 Gen4（非 Gen3/Gen2）
- [ ] 机箱空间足够（3090 三风扇 ≈ 2.5 槽位）
- [ ] 安装后 `nvidia-smi` 确认双卡识别 + PCIe 带宽
- [ ] NVIDIA 驱动最新版（两卡共用一个驱动）

---

## 2. 引擎 GPU 需求分析

### 当前引擎 VRAM 需求

| 引擎 | 当前模型 | VRAM 需求 | 带宽敏感度 | 计算密度 |
|------|---------|----------|-----------|---------|
| ACE-Step | v15-turbo (2B DiT) | ~4GB | 低 | 中 |
| TTS-Forge | Fish Speech 旧版 | ~2GB | 低 | 低 |
| FaceFusion | inswapper_128_fp16 | ~3GB | 低 | 中 |
| Blender | Cycles (CPU fallback) | 8GB+ | **高** | **高** |
| Woosh | 音效生成 | ~1GB | 低 | 低 |
| Parallax | DepthFlow + DepthAnything | ~2GB | 低 | 低 |

### 升级后 VRAM 需求

| 引擎 | 升级模型 | VRAM 需求 | 仅 3090 可用 |
|------|---------|----------|-------------|
| ACE-Step XL | 4B DiT (xl-turbo) | **12-20GB** | ✅ 必须 3090 |
| Fish Audio S2-Pro | 最新开源 TTS | **12-24GB** | ✅ 必须 3090 |
| FaceFusion | Hyperswap 256 + 增强器 | ~4-6GB | ❌ 3060 Ti 可跑 |
| Parallax | Marigold 深度模型 | ~4-6GB | ❌ 3060 Ti 可跑 |

---

## 3. GPU 分配策略

### 核心原则

**3090 做主力（重型引擎），3060 Ti 做辅助（轻量级引擎）**

- 3090 处理 VRAM 密集型和带宽敏感型任务
- 3060 Ti 处理轻量级、低 VRAM、计算为主任务
- 双卡并行执行，吞吐量 ×2

### 分配方案

```
GPU 0: RTX 3090 24GB (PCIe x16)     GPU 1: RTX 3060 Ti 8GB (PCIe x4)
┌────────────────────────────┐      ┌────────────────────────────┐
│  ACE-Step XL 4B (升级后)    │      │  ACE-Step Turbo 2B        │
│  Fish Audio S2-Pro (升级后) │      │  TTS-Forge (当前)          │
│  FaceFusion (Hyperswap)     │      │  Woosh                    │
│  Blender Cycles (大场景)     │      │  Parallax (DepthFlow)     │
│                             │      │                            │
│  Semaphore(1) — 同卡串行     │      │  Semaphore(1) — 同卡串行     │
│  双卡可同时执行 → 吞吐 ×2    │      │                            │
└────────────────────────────┘      └────────────────────────────┘
```

### 各引擎分配理由

| 引擎 | 分配 GPU | 理由 |
|------|---------|------|
| **ACE-Step XL 4B** | 3090 only | 12-20GB VRAM，3060 Ti 物理不够 |
| **Fish Audio S2-Pro** | 3090 only | 推荐 24GB，3060 Ti 物理不够 |
| **FaceFusion** | 3090 优先 | Hyperswap 256 高分辨率处理，ONNX 推理吃计算 |
| **Blender** | 3090 优先 | 大纹理加载需高带宽，复杂场景需大 VRAM |
| **ACE-Step Turbo 2B** | 3060 Ti | <4GB VRAM，纯计算不敏感带宽 |
| **TTS-Forge** | 3060 Ti | 轻量级，VRAM ~2GB |
| **Woosh** | 3060 Ti | CPU 为主，GPU 辅助 |
| **Parallax** | 3060 Ti | GLSL shader，VRAM 需求低 |

---

## 4. 并行调度机制

### 信号量设计

```python
# 当前架构（单卡串行）
self._gpu_semaphore = asyncio.Semaphore(1)  # 所有 GPU 任务互斥

# 双卡架构（按卡独立信号量）
self._gpu_semaphores = {
    0: asyncio.Semaphore(1),  # 3090 串行
    1: asyncio.Semaphore(1),  # 3060 Ti 串行
}
```

### 调度流程

```
任务入队 → 判断 GPU 需求 → 获取对应信号量 → 执行 → 释放信号量
                │
                ├─ gpu_id=0 (3090) → Semaphore(0)
                └─ gpu_id=1 (3060 Ti) → Semaphore(1)
                
双卡任务可同时执行，吞吐量翻倍
```

### ToolAdapter 数据结构扩展

```python
@dataclass
class ToolAdapter:
    name: str
    # ... 现有字段 ...
    
    # 新增 GPU 分配字段
    gpu_id: int = 0                    # 首选 GPU (0=3090, 1=3060 Ti)
    gpu_fallback: bool = False          # 首选 GPU 忙时是否溢出到另一张
    min_vram_mb: int = 0                # 最小 VRAM 需求 (MB)
```

### Docker GPU 参数

```python
# 当前
docker run --gpus all ...

# 双卡
if adapter.gpu_id is not None:
    gpu_arg = f"device={adapter.gpu_id}"
else:
    gpu_arg = "all"
docker run --gpus gpu_arg ...
```

### 溢出策略

当首选 GPU 忙时，判断是否可溢出：

```python
async def _dispatch_task(self, task, task_file):
    adapter = self._registry.get_adapter(task_type)
    
    # 尝试首选 GPU
    gpu_id = adapter.gpu_id
    if self._gpu_semaphores[gpu_id].locked():
        # 首选忙，检查是否可溢出
        if adapter.gpu_fallback:
            fallback_gpu = 1 - gpu_id
            # 检查溢出目标 VRAM 是否够
            if self._check_vram(fallback_gpu, adapter.min_vram_mb):
                gpu_id = fallback_gpu
            else:
                # VRAM 不够，等待首选
                await self._gpu_semaphores[gpu_id].acquire()
                gpu_id = None  # 标记已获取
        else:
            # 不可溢出，等待首选
            await self._gpu_semaphores[gpu_id].acquire()
            gpu_id = None
    
    if gpu_id is not None:
        await self._gpu_semaphores[gpu_id].acquire()
    
    try:
        await self._execute_task(task, task_file, gpu_id=adapter.gpu_id)
    finally:
        self._gpu_semaphores[gpu_id].release()
```

### VRAM 监控

```python
def _check_vram(self, gpu_id: int, required_mb: int) -> bool:
    """检查指定 GPU 可用 VRAM 是否满足需求"""
    result = subprocess.run(
        ["nvidia-smi", f"--query-gpu=memory.free", f"--format=csv,noheader,nounits", f"-i", str(gpu_id)],
        capture_output=True, text=True, timeout=5,
    )
    free_mb = int(result.stdout.strip())
    return free_mb >= required_mb
```

---

## 5. 引擎模型升级计划

### P0 — 立即实施（显卡装好后）

#### 5.1 ACE-Step XL 4B

| 项目 | 详情 |
|------|------|
| 当前 | `acestep-v15-turbo` (2B DiT, <4GB) |
| 升级 | `acestep-v15-xl-turbo` (4B DiT) |
| 来源 | [HuggingFace: acestep-v15-xl-turbo](https://huggingface.co/ACE-Step/acestep-v15-xl-turbo) |
| VRAM | 12GB (offload) / 20GB (推荐) |
| 速度 | RTX 3090 <5s/首, A100 <2s/首 |
| 质量提升 | 超越大部分商业音乐模型 |
| 适配工作量 | **低** — 下载模型 + 修改 adapter 默认参数 |
| GPU 分配 | 3090 only, no fallback |

```python
# adapter 修改
"model": p.get("model", "acestep-v15-xl-turbo"),  # 从 turbo 升级到 xl-turbo
```

#### 5.2 Fish Audio S2-Pro

| 项目 | 详情 |
|------|------|
| 当前 | TTS-Forge (Fish Speech 旧版) |
| 升级 | Fish Audio S2-Pro |
| 来源 | [GitHub: fishaudio/fish-speech](https://github.com/fishaudio/fish-speech) |
| 发布日期 | 2026-03-09 |
| VRAM | 12GB 起，推荐 24GB |
| 新能力 | 情感控制、80+ 语言、高级语音克隆 |
| 质量对比 | 超越 ElevenLabs (Seed-TTS Eval WER 最低) |
| 适配工作量 | **中** — 新建 Docker 镜像 + adapter |
| GPU 分配 | 3090 only, no fallback |

### P1 — 短期实施（1-2 周内）

#### 5.3 FaceFusion Hyperswap + 新 Processor

| 项目 | 详情 |
|------|------|
| 当前 | `inswapper_128_fp16` (128×128) |
| 升级 | `hyperswap_1a_256` (256×256, 2× 分辨率) |
| 适配工作量 | **低** — 下载模型 + 修改默认参数 |
| GPU 分配 | 3090 优先, fallback 3060 Ti |

新增 Processor（当前代码已注册但未启用）：
- `age_modify` — 年龄修改
- `face_edit` — Live Portrait 表情编辑
- `face_enhance` — gfpgan_1.4 面部增强
- `lip_sync` — 口型同步

#### 5.4 Parallax 深度模型升级

| 项目 | 详情 |
|------|------|
| 当前 | DepthAnything V2 (内置) |
| 升级 | Marigold v1.1 / DepthPro |
| 质量提升 | 深度图精细度大幅提升 |
| 速度影响 | ~1-2s/帧 (vs <0.5s) |
| 适配工作量 | **极低** — DepthFlow 已内置支持，改配置 |
| GPU 分配 | 3060 Ti |

### P2 — 维持现状

| 引擎 | 理由 |
|------|------|
| Blender | 仅需 GPU 分配，无需模型升级。3090 直接提升 3× 场景规模 |
| Woosh | CPU 为主，无升级价值 |

---

## 6. 代码改动清单

### 6.1 ToolAdapter 扩展 (`tool_adapter.py`)

```python
@dataclass
class ToolAdapter:
    name: str
    # ... 现有字段保持不变 ...
    
    # 新增
    gpu_id: int = 0              # 首选 GPU
    gpu_fallback: bool = False   # 是否允许溢出
    min_vram_mb: int = 0         # 最小 VRAM
```

### 6.2 Executor Docker 参数 (`executor.py`)

```python
# 修改 _run_api_container
gpu_arg = f"device={adapter.gpu_id}" if adapter.gpu_id is not None else "all"
docker_cmd = ["docker", "run", "--rm", "--gpus", gpu_arg, ...]
```

### 6.3 Guardian 双信号量 (`guardian.py`)

```python
# 替换单信号量
self._gpu_semaphores: dict[int, asyncio.Semaphore] = {
    0: asyncio.Semaphore(1),
    1: asyncio.Semaphore(1),
}

# 调度逻辑
async def _dispatch(self, task, task_file):
    adapter = self._registry.get_adapter(task_type)
    gpu_id = adapter.gpu_id
    
    if self._gpu_semaphores[gpu_id].locked() and adapter.gpu_fallback:
        fallback = 1 - gpu_id
        if self._check_vram(fallback, adapter.min_vram_mb):
            gpu_id = fallback
    
    async with self._gpu_semaphores[gpu_id]:
        await self._execute_task(task, task_file)
```

### 6.4 GpuMetrics 按卡收集 (`gpu_metrics.py`)

```python
@dataclass(frozen=True)
class GpuMetrics:
    gpu_index: int
    gpu_usage: float
    vram_used_mb: float
    vram_total_mb: float
    vram_free_mb: float

def collect_all_gpu_metrics() -> list[GpuMetrics]:
    """收集所有 GPU 的指标"""
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,memory.total",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5,
    )
    metrics = []
    for line in result.stdout.strip().split("\n"):
        idx, usage, used, total = line.split(", ")
        metrics.append(GpuMetrics(
            gpu_index=int(idx),
            gpu_usage=float(usage),
            vram_used_mb=float(used),
            vram_total_mb=float(total),
            vram_free_mb=float(total) - float(used),
        ))
    return metrics
```

### 6.5 各 Adapter GPU 配置

```python
# 3090 专用（VRAM 硬限制，不可溢出）
acestep_xl_adapter(..., gpu_id=0, gpu_fallback=False, min_vram_mb=12000)
fish_s2_pro_adapter(..., gpu_id=0, gpu_fallback=False, min_vram_mb=12000)

# 3090 优先（可溢出到 3060 Ti）
facefusion_adapter(..., gpu_id=0, gpu_fallback=True, min_vram_mb=4000)
blender_adapter(..., gpu_id=0, gpu_fallback=True, min_vram_mb=6000)

# 3060 Ti 专用
acestep_turbo_adapter(..., gpu_id=1, gpu_fallback=False, min_vram_mb=4000)
tts_forge_adapter(..., gpu_id=1, gpu_fallback=False, min_vram_mb=2000)
woosh_adapter(..., gpu_id=1, gpu_fallback=False, min_vram_mb=1000)
parallax_adapter(..., gpu_id=1, gpu_fallback=False, min_vram_mb=2000)
```

---

## 7. 性能预期

### 单卡 vs 双卡对比

| 指标 | 当前 (3060 Ti ×1) | 升级后 (3090+3060 Ti) |
|------|-------------------|---------------------|
| GPU 并行度 | 1 | **2** |
| 最大 VRAM | 8GB | **24GB** |
| 音乐生成质量 | 好 | **卓越 (XL 4B)** |
| TTS 质量 | 基础 | **卓越 (S2-Pro)** |
| 换脸分辨率 | 128×128 | **256×256 (Hyperswap)** |
| Blender 场景规模 | 小 (8GB) | **大 (24GB)** |
| 视差深度质量 | 好 | **极好 (Marigold)** |
| 整体吞吐量 | 基准 | **×2** |

### 典型工作流示例

```
时间线 (秒)
0     5     10    15    20    25    30
├─────┤├─────┤├─────┤├─────┤├─────┤├─────┤

GPU 0 (3090):
[ACE-Step XL 15s][FaceFusion 20s][Blender 25s]
                                        → 串行 60s

GPU 1 (3060 Ti):
[TTS 30s          ][Woosh 25s ][Parallax 15s]
                                        → 串行 70s

双卡并行总时间: max(60, 70) = 70s
单卡串行总时间: 60+70 = 130s
→ 吞吐量提升 1.86×
```

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| PCIe x4 带宽不足 | 3060 Ti 大纹理/模型加载慢 | 大任务只分配 3090 |
| 双卡散热问题 | 3090 降频 | 监控温度，必要时降频调度 |
| 电源不足 | 系统不稳定 | 确认 ≥750W，推荐 850W |
| 驱动兼容性 | 双卡不识别 | 安装最新 NVIDIA 驱动 |
| Docker GPU 分配失败 | 容器启动报错 | fallback 到 `--gpus all` |
| ACE-Step XL offload | 性能严重下降 | 硬限制 `min_vram_mb=12000`，不溢出 |

---

## 9. 实施时间表

| 阶段 | 内容 | 时间 | 前置条件 |
|------|------|------|---------|
| **Phase 0** | 安装 3090 + 驱动验证 | Day 0 | 硬件到货 |
| **Phase 1** | 双 GPU 调度代码改动 | Day 1 | Phase 0 完成 |
| **Phase 2** | ACE-Step XL 模型升级 | Day 2 | Phase 1 完成 |
| **Phase 3** | Fish Audio S2-Pro 集成 | Day 3-5 | Phase 1 完成 |
| **Phase 4** | FaceFusion Hyperswap + 新 Processor | Day 5-7 | Phase 1 完成 |
| **Phase 5** | Parallax Marigold 深度模型 | Day 7 | Phase 1 完成 |
| **Phase 6** | E2E 双卡并行测试 | Day 8 | Phase 2-5 完成 |

---

## 附录

### A. 参考链接

- [ACE-Step 1.5 XL](https://github.com/ace-step/ACE-Step-1.5) — 4B DiT 音乐生成
- [Fish Audio S2-Pro](https://github.com/fishaudio/fish-speech) — 开源 TTS
- [FaceFusion](https://github.com/facefusion/facefusion) — 人脸操作平台
- [DepthFlow](https://github.com/BrokenSource/DepthFlow) — 2.5D 视差引擎
- [Marigold](https://github.com/prs-eth/Marigold) — 深度估计
- [Blender Cycles GPU Rendering](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html)

### B. nvidia-smi 双卡验证命令

```bash
# 确认双卡识别
nvidia-smi --query-gpu=index,name,memory.total,pcie.link.gen.current,pcie.link.width.current --format=csv

# 期望输出:
# 0, NVIDIA GeForce RTX 3090, 24576 MiB, 4, 16
# 1, NVIDIA GeForce RTX 3060 Ti, 8192 MiB, 4, 4
```
