#!/bin/bash
# HTML 渲染器 - 将 SVG 转换为带动画的 HTML

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT="${1:-}"
OUTPUT="${2:-output.html}"
TITLE="${3:-知识可视化}"

# 帮助信息
show_help() {
    echo "用法: $0 <input.svg> [output.html] [title]"
    echo ""
    echo "将 SVG 文件转换为带动画的 HTML 页面"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -t, --title    设置页面标题"
    echo ""
    echo "示例:"
    echo "  $0 diagram.svg"
    echo "  $0 diagram.svg animated.html \"系统架构\""
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--title)
            TITLE="$2"
            shift 2
            ;;
        *)
            if [[ -z "$INPUT" ]]; then
                INPUT="$1"
            elif [[ "$OUTPUT" == "output.html" ]]; then
                OUTPUT="$1"
            else
                TITLE="$1"
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

# 读取 SVG
SVG_CONTENT=$(cat "$INPUT")

# 生成 HTML
echo "🎨 生成带动画的 HTML..."

cat > "$OUTPUT" << HTMLEOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${TITLE}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
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
            animation: fadeIn 0.8s ease-out;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            font-size: 2rem;
            animation: slideDown 0.6s ease-out;
        }
        
        .svg-container {
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: auto;
            animation: scaleIn 1s ease-out 0.3s both;
        }
        
        .svg-container svg {
            max-width: 100%;
            height: auto;
        }
        
        /* SVG 内部元素动画 */
        .svg-container svg * {
            opacity: 0;
            animation: fadeInElement 0.5s ease-out forwards;
        }
        
        .svg-container svg *:nth-child(1) { animation-delay: 0.5s; }
        .svg-container svg *:nth-child(2) { animation-delay: 0.6s; }
        .svg-container svg *:nth-child(3) { animation-delay: 0.7s; }
        .svg-container svg *:nth-child(4) { animation-delay: 0.8s; }
        .svg-container svg *:nth-child(5) { animation-delay: 0.9s; }
        .svg-container svg *:nth-child(6) { animation-delay: 1.0s; }
        .svg-container svg *:nth-child(7) { animation-delay: 1.1s; }
        .svg-container svg *:nth-child(8) { animation-delay: 1.2s; }
        .svg-container svg *:nth-child(9) { animation-delay: 1.3s; }
        .svg-container svg *:nth-child(10) { animation-delay: 1.4s; }
        .svg-container svg *:nth-child(n+11) { animation-delay: 1.5s; }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
            animation: slideUp 0.6s ease-out 0.5s both;
        }
        
        button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #d0d0d0;
            transform: translateY(-2px);
        }
        
        /* 动画定义 */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes fadeInElement {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* 打印样式 */
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
            .controls {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>${TITLE}</h1>
        <div class="svg-container">
            ${SVG_CONTENT}
        </div>
        <div class="controls">
            <button class="btn-secondary" onclick="location.reload()">🔄 重新播放动画</button>
            <button class="btn-primary" onclick="window.print()">🖨️ 打印</button>
        </div>
    </div>
    
    <script>
        // 动画控制
        document.addEventListener('DOMContentLoaded', () => {
            console.log('知识可视化加载完成');
            
            // 可以在这里添加更多交互功能
            const svg = document.querySelector('.svg-container svg');
            if (svg) {
                // 添加缩放功能
                let scale = 1;
                svg.style.cursor = 'zoom-in';
                svg.addEventListener('click', () => {
                    scale = scale === 1 ? 1.5 : 1;
                    svg.style.transform = \`scale(\${scale})\`;
                    svg.style.transition = 'transform 0.3s ease';
                    svg.style.cursor = scale === 1 ? 'zoom-in' : 'zoom-out';
                });
            }
        });
    </script>
</body>
</html>
HTMLEOF

echo "✅ HTML 生成成功: $OUTPUT"
echo "📊 文件大小: $(du -h "$OUTPUT" | cut -f1)"
