# Client
该目录包含 ActionRecorder 客户端库。

## 使用方式

```python
import sys
sys.path.insert(0, "/home/kai/.openclaw/workspace/skills/kais-blender-action/client")
from action_recorder import ActionRecorder

rec = ActionRecorder("http://192.168.71.38:8080")
result = rec.record(
    character="hero.fbx",
    motion="walk.fbx",
    duration_ms=2000,
    camera={"azimuth": 45, "elevation": 10, "distance": 3.0},
    output_name="walk_ref",
)
```

## 文件说明

- `action_recorder.py` — 核心客户端，包含镜头预设、帧范围计算、Blender 脚本生成
