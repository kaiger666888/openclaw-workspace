# HTML Renderer

将 PlantUML 图表转化为带动画的交互式 HTML 页面。

## 职责

**输入**: PlantUML 代码 + 动画配置
**输出**: 可独立运行的 HTML 文件（内嵌 CSS 动画）

## 技术方案

### 核心技术栈
- **SVG.js** (轻量级 SVG 操作库)
- **CSS Keyframes** (动画)
- **PlantUML Server** (将 PlantUML 渲染为 SVG)

### 架构

```
PlantUML 代码
    ↓
[PlantUML Server] → SVG 静态图
    ↓
[SVG 解析] → 提取元素和结构
    ↓
[动画编排] → 添加时间轴和效果
    ↓
[HTML 生成] → 完整的教学页面
```

## 动画类型

### 1. 逐步显示 (Step-by-step)
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.element {
  animation: fadeIn 0.5s ease-out forwards;
}
```

### 2. 路径动画 (Path Animation)
```css
@keyframes drawPath {
  from { stroke-dashoffset: 1000; }
  to { stroke-dashoffset: 0; }
}

.path {
  stroke-dasharray: 1000;
  animation: drawPath 2s ease-in-out forwards;
}
```

### 3. 高亮脉冲 (Pulse Highlight)
```css
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(25, 118, 210, 0.7); }
  50% { box-shadow: 0 0 0 10px rgba(25, 118, 210, 0); }
}

.highlight {
  animation: pulse 2s infinite;
}
```

## 动画编排格式

```json
{
  "timeline": [
    {
      "time": 0,
      "elements": ["node-1"],
      "animation": "fadeIn",
      "duration": 1000,
      "narration": "首先，我们看第一个概念..."
    },
    {
      "time": 1500,
      "elements": ["node-2"],
      "animation": "fadeIn",
      "duration": 1000
    },
    {
      "time": 3000,
      "elements": ["edge-1"],
      "animation": "drawPath",
      "duration": 1500,
      "narration": "然后，连接这两个概念..."
    }
  ],
  "totalDuration": 10000
}
```

## HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }

    .container {
      background: white;
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      padding: 2rem;
      max-width: 1200px;
      width: 100%;
    }

    .title {
      font-size: 2rem;
      margin-bottom: 1.5rem;
      color: #1a1a1a;
      text-align: center;
    }

    .diagram-container {
      position: relative;
      width: 100%;
      min-height: 500px;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .diagram {
      max-width: 100%;
      height: auto;
    }

    /* 隐藏初始状态 */
    .diagram * {
      opacity: 0;
    }

    /* 动画类 */
    .fade-in {
      animation: fadeIn 0.8s ease-out forwards;
    }

    .draw-path {
      stroke-dasharray: 1000;
      stroke-dashoffset: 1000;
      animation: drawPath 1.5s ease-in-out forwards;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes drawPath {
      to { stroke-dashoffset: 0; }
    }

    /* 控制面板 */
    .controls {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin-top: 2rem;
    }

    button {
      padding: 0.75rem 2rem;
      font-size: 1rem;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .btn-primary {
      background: #1976D2;
      color: white;
    }

    .btn-primary:hover {
      background: #1565C0;
      transform: translateY(-2px);
    }

    /* 进度条 */
    .progress-bar {
      width: 100%;
      height: 4px;
      background: #e0e0e0;
      border-radius: 2px;
      margin-top: 1rem;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #1976D2, #42A5F5);
      width: 0%;
      transition: width 0.3s;
    }

    /* 旁白文本 */
    .narration {
      min-height: 3rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 8px;
      margin-top: 1rem;
      font-size: 1.1rem;
      text-align: center;
      color: #333;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="title">{title}</h1>

    <div class="diagram-container">
      <!-- SVG 内容将插入这里 -->
      <div class="diagram" id="diagram">
        {svg_content}
      </div>
    </div>

    <div class="narration" id="narration">
      点击播放开始学习
    </div>

    <div class="progress-bar">
      <div class="progress-fill" id="progress"></div>
    </div>

    <div class="controls">
      <button class="btn-primary" onclick="playAnimation()">
        ▶ 播放
      </button>
      <button onclick="resetAnimation()">
        ↺ 重置
      </button>
    </div>
  </div>

  <script>
    // 动画配置
    const timeline = {timeline_json};

    let currentTime = 0;
    let isPlaying = false;
    let animationFrame;

    function playAnimation() {
      if (isPlaying) return;
      isPlaying = true;

      timeline.forEach((step, index) => {
        setTimeout(() => {
          // 应用动画
          step.elements.forEach(selector => {
            const el = document.querySelector(selector);
            if (el) {
              el.classList.add(step.animation);
            }
          });

          // 更新旁白
          if (step.narration) {
            document.getElementById('narration').textContent = step.narration;
          }

          // 更新进度
          const progress = ((index + 1) / timeline.length) * 100;
          document.getElementById('progress').style.width = progress + '%';

        }, step.time);
      });

      // 动画结束
      setTimeout(() => {
        isPlaying = false;
      }, timeline.totalDuration);
    }

    function resetAnimation() {
      isPlaying = false;
      currentTime = 0;

      // 重置所有元素
      document.querySelectorAll('.diagram *').forEach(el => {
        el.classList.remove('fade-in', 'draw-path');
        el.style.opacity = '0';
      });

      document.getElementById('progress').style.width = '0%';
      document.getElementById('narration').textContent = '点击播放开始学习';
    }
  </script>
</body>
</html>
```

## 实现步骤

1. **解析 PlantUML** → 调用 PlantUML Server 获取 SVG
2. **提取元素** → 给 SVG 元素添加唯一 ID
3. **生成时间轴** → 根据图表类型自动编排动画
4. **注入 HTML** → 生成完整的教学页面

## 调用示例

```bash
claude-code --skill html-renderer \
  --input diagram.puml \
  --output lesson.html \
  --style educational \
  --auto-play false
```

---

*版本: 0.1.0*
