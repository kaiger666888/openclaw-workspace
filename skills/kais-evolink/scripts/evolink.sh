#!/usr/bin/env bash
# kais-evolink: Evolink AI 视频生成脚本
# 用法: evolink.sh --prompt "描述" [--image-url URL] [--last-frame URL] [--duration 5] [--quality 720p] [--aspect-ratio 16:9] [--no-audio] [--output /path/save.mp4]

set -euo pipefail

# 加载配置
CONFIG_FILE="$HOME/.openclaw/.evolink.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 配置文件不存在: $CONFIG_FILE"
  echo "请创建配置文件，格式："
  echo '{ "apiKey": "sk-xxx", "baseUrl": "https://api.evolink.ai/v1" }'
  exit 1
fi

API_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['apiKey'])")
BASE_URL=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('baseUrl','https://api.evolink.ai/v1'))")

# 参数默认值
PROMPT=""
IMAGE_URLS=()
DURATION=5
QUALITY="720p"
ASPECT_RATIO="16:9"
GENERATE_AUDIO="true"
OUTPUT=""
MODEL="seedance-1.5-pro"

# 解析参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2 ;;
    --image-url) IMAGE_URLS+=("$2"); shift 2 ;;
    --last-frame) IMAGE_URLS+=("$2"); shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --aspect-ratio) ASPECT_RATIO="$2"; shift 2 ;;
    --no-audio) GENERATE_AUDIO="false"; shift ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    *) echo "❌ 未知参数: $1"; exit 1 ;;
  esac
done

if [ -z "$PROMPT" ]; then
  echo "❌ 必须提供 --prompt 参数"
  exit 1
fi

# 构建 JSON body
BODY=$(python3 -c "
import json
body = {
  'model': '$MODEL',
  'prompt': '''$PROMPT'''.replace(\"'''\", \"\"),
  'duration': int($DURATION),
  'quality': '$QUALITY',
  'aspect_ratio': '$ASPECT_RATIO',
  'generate_audio': $GENERATE_AUDIO
}
images = json.loads('''$(printf '%s\n' "${IMAGE_URLS[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')''')
if images:
  body['image_urls'] = images
print(json.dumps(body))
")

echo "🎬 创建视频生成任务..."
echo "   模型: $MODEL"
echo "   时长: ${DURATION}s | 质量: $QUALITY | 比例: $ASPECT_RATIO"
echo "   模式: $([ ${#IMAGE_URLS[@]} -eq 0 ] && echo '文生视频' || [ ${#IMAGE_URLS[@]} -eq 1 ] && echo '图生视频' || echo '首尾帧')"

# 创建任务
RESPONSE=$(curl -s -X POST "${BASE_URL}/videos/generations" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$BODY")

TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)

if [ -z "$TASK_ID" ]; then
  echo "❌ 任务创建失败:"
  echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','未知错误'))" 2>/dev/null || echo "$RESPONSE"
  exit 1
fi

echo "✅ 任务已创建: $TASK_ID"

# 轮询状态
echo "⏳ 等待生成中..."
sleep 10

TIMEOUT=600
ELAPSED=0
INTERVAL=15

while [ $ELAPSED -lt $TIMEOUT ]; do
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))

  STATUS_RESPONSE=$(curl -s "${BASE_URL}/tasks/${TASK_ID}" \
    -H "Authorization: Bearer ${API_KEY}")

  STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('status','unknown'))
" 2>/dev/null)

  PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('progress',0))
" 2>/dev/null)

  case "$STATUS" in
    completed)
      VIDEO_URL=$(echo "$STATUS_RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
outputs = d.get('output',{})
if isinstance(outputs, dict):
  print(outputs.get('video_url',''))
elif isinstance(outputs, list) and outputs:
  print(outputs[0].get('url',''))
" 2>/dev/null)

      if [ -n "$VIDEO_URL" ]; then
        echo "✅ 视频生成完成！"
        echo "📥 $VIDEO_URL"

        if [ -n "$OUTPUT" ]; then
          echo "💾 下载到: $OUTPUT"
          curl -sL -o "$OUTPUT" "$VIDEO_URL"
          echo "✅ 下载完成: $OUTPUT"
        fi
      else
        echo "⚠️ 任务完成但未找到视频 URL"
        echo "$STATUS_RESPONSE"
      fi
      exit 0
      ;;
    failed)
      ERROR_MSG=$(echo "$STATUS_RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('error',{}).get('message',d.get('message','生成失败')))
" 2>/dev/null)
      echo "❌ 视频生成失败: $ERROR_MSG"
      exit 1
      ;;
    processing|pending)
      echo "   [$ELAPSED s] 状态: $STATUS | 进度: ${PROGRESS}%"
      ;;
    *)
      echo "   [$ELAPSED s] 未知状态: $STATUS"
      ;;
  esac
done

echo "❌ 超时（${TIMEOUT}s），任务仍在处理中"
echo "手动查询: curl ${BASE_URL}/tasks/${TASK_ID} -H 'Authorization: Bearer ${API_KEY}'"
exit 1
