#!/bin/bash
# Notion 格式工具库
# 确保所有向 Notion 输出的内容符合标准格式

set -e

# 配置
NOTION_CLI="/home/kai/.local/bin/notion-cli"
TEMPLATES_DIR="/home/kai/.openclaw/workspace/scripts/lib"

# 颜色定义（用于日志）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================
# 核心函数：创建并填充页面（原子操作）
# ============================================
create_page_with_json() {
    local parent_id="$1"
    local title="$2"
    local json_file="$3"
    
    log_info "创建页面: $title"
    
    # 1. 创建页面
    local page_id
    page_id=$($NOTION_CLI page create --parent "$parent_id" --title "$title" 2>&1 | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")
    
    if [ -z "$page_id" ]; then
        log_error "页面创建失败"
        return 1
    fi
    
    log_info "页面创建成功: $page_id"
    
    # 2. 验证 JSON 格式
    if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
        log_error "JSON 格式验证失败: $json_file"
        return 1
    fi
    
    # 3. 追加 JSON 块
    log_info "追加内容..."
    if $NOTION_CLI block append --children-file "$json_file" "$page_id" 2>&1 | grep -q "successfully"; then
        log_info "内容追加成功"
        echo "$page_id"
        return 0
    else
        log_error "内容追加失败"
        return 1
    fi
}

# ============================================
# 验证函数：检查页面格式是否符合标准
# ============================================
validate_page_format() {
    local page_id="$1"
    local expected_blocks="$2"  # 期望的块类型，如 "callout,heading_2,divider"
    
    log_info "验证页面格式: $page_id"
    
    # 获取页面块列表
    local blocks
    blocks=$($NOTION_CLI block list "$page_id" 2>&1)
    
    # 检查是否有内容
    if echo "$blocks" | grep -q "No blocks found"; then
        log_error "页面为空"
        return 1
    fi
    
    # 检查是否有 Markdown 语法残留（格式错误的标志）
    if echo "$blocks" | grep -qE '^\[paragraph\].*\#\#|^\[paragraph\].*\-\-\-|^\[paragraph\].*\*\*'; then
        log_warn "检测到 Markdown 语法残留，格式可能不正确"
        return 2
    fi
    
    # 检查是否以 callout 开头（标准格式）- 跳过 "Blocks (n):" 前缀
    if ! echo "$blocks" | grep -v "^Blocks" | grep -v "^$" | head -1 | grep -q "callout"; then
        log_warn "页面未以 callout 摘要开头"
        return 2
    fi
    
    # 检查必需的块类型
    if [ -n "$expected_blocks" ]; then
        IFS=',' read -ra EXPECTED <<< "$expected_blocks"
        for block_type in "${EXPECTED[@]}"; do
            if ! echo "$blocks" | grep -q "\[$block_type\]"; then
                log_warn "缺少必需的块类型: $block_type"
                return 2
            fi
        done
    fi
    
    log_info "格式验证通过"
    return 0
}

# ============================================
# 修复函数：删除并重建页面
# ============================================
repair_page() {
    local page_id="$1"
    local parent_id="$2"
    local title="$3"
    local json_file="$4"
    
    log_warn "尝试修复页面: $page_id"
    
    # 1. 归档旧页面
    log_info "归档旧页面..."
    $NOTION_CLI page delete "$page_id" --force 2>/dev/null || true
    
    # 2. 创建新页面
    create_page_with_json "$parent_id" "$title" "$json_file"
}

# ============================================
# 智能追加：先验证再追加
# ============================================
smart_append() {
    local page_id="$1"
    local json_file="$2"
    local check_duplicate="$3"  # 可选：检查重复内容
    
    if [ "$check_duplicate" = "true" ]; then
        # 获取现有内容摘要
        local existing
        existing=$($NOTION_CLI block list "$page_id" 2>&1 | head -5)
        
        # 如果已有内容，警告
        if ! echo "$existing" | grep -q "No blocks found"; then
            log_warn "页面已有内容，追加可能导致重复"
        fi
    fi
    
    # 追加内容
    $NOTION_CLI block append --children-file "$json_file" "$page_id"
}

# ============================================
# 使用示例
# ============================================
# 
# # 创建新页面（推荐方式）
# page_id=$(create_page_with_json "parent-id" "标题" "/path/to/content.json")
#
# # 验证页面格式
# validate_page_format "$page_id" "callout,heading_2,divider"
#
# # 修复格式问题
# repair_page "$page_id" "parent-id" "标题" "/path/to/content.json"
#
