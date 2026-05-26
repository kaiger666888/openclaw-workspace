#!/bin/bash

# Knowledge Visualizer - 核心编排脚本
# 将知识文档自动转化为可视化教学资产

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
  cat << EOF
Knowledge Visualizer - 将知识文档转化为可视化教学资产

用法:
  $0 --input <文档.md> --output <输出目录> [选项]

选项:
  --input, -i      输入的 Markdown 文档路径
  --output, -o     输出目录（默认: ./output）
  --style, -s      视觉风格 (educational|minimal|colorful)
  --format, -f     输出格式 (html|video|all)
  --verbose, -v    详细输出
  --help, -h       显示帮助信息

示例:
  $0 --input doc.md --output ./lesson
  $0 -i doc.md -o ./lesson -f all -v

EOF
}

# 默认配置
INPUT=""
OUTPUT="./output"
STYLE="educational"
FORMAT="html"
VERBOSE=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --input|-i)
      INPUT="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT="$2"
      shift 2
      ;;
    --style|-s)
      STYLE="$2"
      shift 2
      ;;
    --format|-f)
      FORMAT="$2"
      shift 2
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      echo -e "${RED}未知参数: $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

# 检查输入
if [ -z "$INPUT" ]; then
  echo -e "${RED}错误: 必须指定输入文档${NC}"
  show_help
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo -e "${RED}错误: 文件不存在: $INPUT${NC}"
  exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT"

# 日志函数
log() {
  if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
  fi
}

log_step() {
  echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"
}

# ========================================
# Step 1: 解析知识文档
# ========================================
log_step "Step 1/4: 解析知识文档..."

PARSED_JSON="$OUTPUT/parsed.json"

# 这里应该调用 knowledge-parser skill
# 目前使用模拟数据
log "调用 knowledge-parser..."

# 模拟解析结果（实际应调用 Claude Code）
cat > "$PARSED_JSON" << 'EOF'
{
  "metadata": {
    "title": "RESTful API 设计原则",
    "summary": "REST 架构风格及其 API 设计最佳实践",
    "difficulty": "intermediate"
  },
  "concepts": [
    {
      "id": "resource",
      "name": "资源 (Resource)",
      "importance": 1.0
    },
    {
      "id": "uniform-interface",
      "name": "统一接口",
      "importance": 0.9
    },
    {
      "id": "stateless",
      "name": "无状态性",
      "importance": 0.9
    }
  ],
  "processes": [
    {
      "id": "design-process",
      "name": "RESTful API 设计流程",
      "type": "linear",
      "steps": [
        {"id": "s1", "description": "识别资源", "next": ["s2"]},
        {"id": "s2", "description": "定义 URI", "next": ["s3"]},
        {"id": "s3", "description": "选择 HTTP 方法", "next": ["s4"]},
        {"id": "s4", "description": "设计响应格式", "next": []}
      ]
    }
  ],
  "visualization": {
    "recommendedCharts": ["flowchart", "mindmap"],
    "focusAreas": ["资源", "统一接口", "无状态性"],
    "suggestedPacing": "medium"
  }
}
EOF

log "解析完成: $PARSED_JSON"

# ========================================
# Step 2: 生成 PlantUML
# ========================================
log_step "Step 2/4: 生成 PlantUML 图表..."

PLANTUML_DIR="$OUTPUT/plantuml"
mkdir -p "$PLANTUML_DIR"

log "调用 uml-designer..."

# 生成流程图
cat > "$PLANTUML_DIR/design-flow.puml" << 'EOF'
@startuml
title RESTful API 设计流程

skinparam activity {
  BackgroundColor #E3F2FD
  BorderColor #1976D2
  FontSize 14
}

|资源设计|
start
:识别资源;
note right
  分析业务需求
  提取核心对象
end note

:定义 URI;
note right
  使用名词
  层级清晰
end note

|接口设计|
:选择 HTTP 方法;
note right
  GET/POST/PUT/DELETE
  语义对应操作
end note

:设计响应格式;
note right
  统一数据结构
  错误处理规范
end note

stop
@enduml
EOF

log "PlantUML 生成完成: $PLANTUML_DIR"

# ========================================
# Step 3: 渲染 SVG 和 HTML
# ========================================
log_step "Step 3/4: 渲染 SVG 和 HTML..."

SVG_DIR="$OUTPUT/svg"
HTML_DIR="$OUTPUT/html"
mkdir -p "$SVG_DIR" "$HTML_DIR"

log "调用 plantuml-server 渲染 SVG..."
for puml in "$PLANTUML_DIR"/*.puml; do
  filename=$(basename "$puml" .puml)
  ./subskills/plantuml-server/render.sh "$puml" "$SVG_DIR/${filename}.svg"
done

log "调用 html-renderer 生成 HTML..."
for svg in "$SVG_DIR"/*.svg; do
  filename=$(basename "$svg" .svg)
  ./subskills/html-renderer/render.sh "$svg" "$HTML_DIR/${filename}.html" "${TITLE:-知识可视化}"
done

HTML_OUTPUT="$HTML_DIR/$(ls $HTML_DIR | head -1)"

log "SVG 和 HTML 渲染完成"

# 创建一个合并的 HTML（简化版，保留原逻辑作为 fallback）
if [ ! -f "$HTML_OUTPUT" ]; then
cat > "$HTML_OUTPUT" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RESTful API 设计原则 - 可视化教程</title>
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
      max-width: 900px;
      width: 100%;
    }

    .title {
      font-size: 2rem;
      margin-bottom: 1.5rem;
      color: #1a1a1a;
      text-align: center;
    }

    .step {
      margin: 1.5rem 0;
      padding: 1.5rem;
      background: #f8f9fa;
      border-radius: 12px;
      border-left: 4px solid #1976D2;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.6s ease-out;
    }

    .step.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .step-number {
      display: inline-block;
      width: 32px;
      height: 32px;
      background: #1976D2;
      color: white;
      border-radius: 50%;
      text-align: center;
      line-height: 32px;
      font-weight: bold;
      margin-right: 1rem;
    }

    .step-title {
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      display: inline;
    }

    .step-note {
      margin-top: 0.75rem;
      padding: 0.75rem;
      background: #e3f2fd;
      border-radius: 8px;
      font-size: 0.95rem;
      color: #555;
    }

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
      font-weight: 500;
    }

    .btn-primary {
      background: #1976D2;
      color: white;
    }

    .btn-primary:hover {
      background: #1565C0;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4);
    }

    .btn-secondary {
      background: #e0e0e0;
      color: #333;
    }

    .btn-secondary:hover {
      background: #d0d0d0;
    }

    .progress-bar {
      width: 100%;
      height: 6px;
      background: #e0e0e0;
      border-radius: 3px;
      margin-top: 1.5rem;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #1976D2, #42A5F5);
      width: 0%;
      transition: width 0.5s ease-out;
    }

    .narration {
      min-height: 3rem;
      padding: 1rem;
      background: #fff3e0;
      border-radius: 8px;
      margin-top: 1.5rem;
      font-size: 1.1rem;
      text-align: center;
      color: #e65100;
      font-weight: 500;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="title">RESTful API 设计原则</h1>

    <div class="narration" id="narration">
      👋 点击"开始学习"，让我们一起探索 RESTful API 设计
    </div>

    <div id="steps-container">
      <div class="step" data-step="1">
        <span class="step-number">1</span>
        <span class="step-title">识别资源</span>
        <div class="step-note">
          💡 分析业务需求，从用户故事中提取名词，确定系统中的核心资源
        </div>
      </div>

      <div class="step" data-step="2">
        <span class="step-number">2</span>
        <span class="step-title">定义 URI</span>
        <div class="step-note">
          💡 使用名词而非动词，保持层级清晰，例如：<code>/users</code>、<code>/articles/42</code>
        </div>
      </div>

      <div class="step" data-step="3">
        <span class="step-number">3</span>
        <span class="step-title">选择 HTTP 方法</span>
        <div class="step-note">
          💡 GET 获取、POST 创建、PUT 更新、DELETE 删除 - 遵循 HTTP 语义
        </div>
      </div>

      <div class="step" data-step="4">
        <span class="step-number">4</span>
        <span class="step-title">设计响应格式</span>
        <div class="step-note">
          💡 统一的数据结构，清晰的错误处理，让 API 易于使用
        </div>
      </div>
    </div>

    <div class="progress-bar">
      <div class="progress-fill" id="progress"></div>
    </div>

    <div class="controls">
      <button class="btn-primary" onclick="startLesson()">▶ 开始学习</button>
      <button class="btn-secondary" onclick="resetLesson()">↺ 重新开始</button>
    </div>
  </div>

  <script>
    const narrations = [
      "👋 点击"开始学习"，让我们一起探索 RESTful API 设计",
      "🎯 第一步：识别系统中的核心资源，这是 API 设计的基础",
      "🔗 第二步：为每个资源定义清晰的 URI 路径",
      "⚡ 第三步：根据操作类型选择合适的 HTTP 方法",
      "📦 第四步：设计统一的响应格式和错误处理规范",
      "✅ 恭喜！你已经掌握了 RESTful API 设计的核心流程"
    ];

    let currentStep = 0;
    const totalSteps = 4;

    function startLesson() {
      if (currentStep > 0) return;

      const steps = document.querySelectorAll('.step');
      let delay = 0;

      steps.forEach((step, index) => {
        setTimeout(() => {
          step.classList.add('visible');
          currentStep = index + 1;

          // 更新旁白
          document.getElementById('narration').textContent = narrations[index + 1];

          // 更新进度
          const progress = (currentStep / totalSteps) * 100;
          document.getElementById('progress').style.width = progress + '%';

          // 最后一步完成后
          if (currentStep === totalSteps) {
            setTimeout(() => {
              document.getElementById('narration').textContent = narrations[5];
            }, 1000);
          }
        }, delay);

        delay += 2000; // 每步间隔 2 秒
      });
    }

    function resetLesson() {
      currentStep = 0;
      const steps = document.querySelectorAll('.step');
      steps.forEach(step => step.classList.remove('visible'));
      document.getElementById('progress').style.width = '0%';
      document.getElementById('narration').textContent = narrations[0];
    }
  </script>
</body>
</html>
HTMLEOF
fi

# ========================================
# Step 4: 完成
# ========================================
log_step "Step 4/4: 生成完成！"

echo ""
echo -e "${GREEN}✅ 知识可视化资产已生成！${NC}"
echo ""
echo "输出文件:"
echo "  📄 解析数据: $PARSED_JSON"
echo "  📊 PlantUML: $PLANTUML_DIR/"
echo "  🎨 SVG 图片: $SVG_DIR/"
echo "  🌐 教学网页: $HTML_DIR/"
echo ""
echo "打开教学网页:"
echo "  file://$(cd "$OUTPUT" && pwd)/html/$(ls $HTML_DIR | head -1)"
echo ""
