#!/bin/bash
# PlantUML Server 渲染脚本
# 将 .puml 文件渲染为 .svg

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT="${1:-}"
OUTPUT="${2:-output.svg}"

# 帮助信息
show_help() {
    echo "用法: $0 <input.puml> [output.svg]"
    echo ""
    echo "将 PlantUML 文件渲染为 SVG 图片"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -s, --server   指定 PlantUML 服务器地址"
    echo ""
    echo "示例:"
    echo "  $0 diagram.puml"
    echo "  $0 diagram.puml output.svg"
}

# 解析参数
SERVER="${PLANTUML_SERVER:-https://www.plantuml.com/plantuml}"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--server)
            SERVER="$2"
            shift 2
            ;;
        *)
            if [[ -z "$INPUT" ]]; then
                INPUT="$1"
            elif [[ "$OUTPUT" == "output.svg" ]]; then
                OUTPUT="$1"
            fi
            shift
            ;;
    esac
done

# 检查输入
if [[ -z "$INPUT" ]]; then
    echo "错误: 请指定输入文件"
    show_help
    exit 1
fi

if [[ ! -f "$INPUT" ]]; then
    echo "错误: 文件不存在: $INPUT"
    exit 1
fi

# 临时文件
ENCODED_FILE=$(mktemp)
trap "rm -f $ENCODED_FILE" EXIT

# 编码 PlantUML 为 URL 安全格式
encode_plantuml() {
    python3 << 'PYEOF'
import sys
import zlib

def encode_plantuml(text):
    """PlantUML 特殊编码"""
    # 压缩
    compressed = zlib.compress(text.encode('utf-8'), 9)
    
    # 自定义 base64 编码
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    result = []
    
    # 每次处理 3 字节
    for i in range(0, len(compressed), 3):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0
        
        result.append(chars[b1 >> 2])
        result.append(chars[((b1 & 0x3) << 4) | (b2 >> 4)])
        result.append(chars[((b2 & 0xF) << 2) | (b3 >> 6)])
        result.append(chars[b3 & 0x3F])
    
    return ''.join(result)

# 读取输入
text = sys.stdin.read()
encoded = encode_plantuml(text)
print(encoded)
PYEOF
}

# 读取并编码
echo "📄 读取 PlantUML 文件: $INPUT"
PLANTUML_CODE=$(cat "$INPUT")

# 使用 Python 编码
echo "🔄 编码 PlantUML..."
ENCODED=$(echo "$PLANTUML_CODE" | encode_plantuml)

if [[ -z "$ENCODED" ]]; then
    echo "错误: PlantUML 编码失败"
    exit 1
fi

# 构建 URL
URL="${SERVER}/svg/~1${ENCODED}"

# 下载 SVG
echo "⬇️  从服务器获取 SVG: $SERVER"
if curl -f -s "$URL" -o "$OUTPUT"; then
    # 验证 SVG
    if grep -q '<svg' "$OUTPUT" 2>/dev/null; then
        echo "✅ SVG 渲染成功: $OUTPUT"
        echo "📊 文件大小: $(du -h "$OUTPUT" | cut -f1)"
    else
        echo "⚠️  警告: 输出可能不是有效的 SVG"
        echo "前 200 字符:"
        head -c 200 "$OUTPUT"
        exit 1
    fi
else
    echo "❌ 从服务器获取 SVG 失败"
    exit 1
fi
