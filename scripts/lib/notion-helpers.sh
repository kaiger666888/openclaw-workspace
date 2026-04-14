#!/bin/bash
# Notion API 辅助函数库
# 解决字符限制、引号转义、重试等问题

# 配置
NOTION_CLI="/home/kai/.local/bin/notion-cli"
MAX_CHARS=1900  # 留100字符余量
MAX_RETRIES=3
RETRY_DELAY=2

# 将内容分段（每段不超过 MAX_CHARS）
# 用法：split_content "长内容"
split_content() {
  local content="$1"
  local length=${#content}
  local start=0
  local part_num=1

  while [ $start -lt $length ]; do
    local end=$((start + MAX_CHARS))
    if [ $end -gt $length ]; then
      end=$length
    fi

    # 尝试在段落边界分割
    if [ $end -lt $length ]; then
      local substring="${content:$start:$((end - start))}"
      # 查找最后一个换行符
      local last_newline=$(echo "$substring" | grep -bo $'\n' | tail -1 | grep -o '[0-9]*' || echo "")
      if [ -n "$last_newline" ] && [ $last_newline -gt $((MAX_CHARS / 2)) ]; then
        end=$((start + last_newline + 1))
      fi
    fi

    echo "${content:$start:$((end - start))}"
    start=$end
    part_num=$((part_num + 1))
  done
}

# 安全地追加内容到 Notion 页面（带重试）
# 用法：safe_append "页面ID" "内容"
safe_append() {
  local page_id="$1"
  local content="$2"
  local retry=0

  # 将内容写入临时文件（避免引号问题）
  local temp_file=$(mktemp)
  echo "$content" > "$temp_file"

  while [ $retry -lt $MAX_RETRIES ]; do
    # 使用文件内容，避免 Shell 引号解析
    local result=$(unset NODE_OPTIONS && $NOTION_CLI page append --content "$(cat "$temp_file")" "$page_id" 2>&1)
    local exit_code=$?

    if [ $exit_code -eq 0 ] && ! echo "$result" | grep -q "request fail"; then
      rm -f "$temp_file"
      return 0
    fi

    retry=$((retry + 1))
    if [ $retry -lt $MAX_RETRIES ]; then
      echo "⚠️ 追加失败，${RETRY_DELAY}秒后重试 ($retry/$MAX_RETRIES)..."
      sleep $RETRY_DELAY
    fi
  done

  rm -f "$temp_file"
  echo "❌ 追加失败，已达最大重试次数"
  return 1
}

# 分段追加长内容到 Notion 页面
# 用法：append_long_content "页面ID" "长内容"
append_long_content() {
  local page_id="$1"
  local content="$2"
  local part_num=1
  local total_parts=0

  # 先计算总段数
  local length=${#content}
  local temp_start=0
  while [ $temp_start -lt $length ]; do
    total_parts=$((total_parts + 1))
    temp_start=$((temp_start + MAX_CHARS))
  done

  # 如果内容不长，直接追加
  if [ $length -le $MAX_CHARS ]; then
    echo "📝 追加内容 (${length}字符)..."
    safe_append "$page_id" "$content"
    return $?
  fi

  # 分段追加
  echo "📝 内容较长 (${length}字符)，将分${total_parts}段追加..."

  local start=0
  while [ $start -lt $length ]; do
    local end=$((start + MAX_CHARS))
    if [ $end -gt $length ]; then
      end=$length
    fi

    # 在段落边界分割
    if [ $end -lt $length ]; then
      local substring="${content:$start:$((end - start))}"
      local last_newline=$(echo "$substring" | grep -bo $'\n' | tail -1 | grep -o '[0-9]*' || echo "")
      if [ -n "$last_newline" ] && [ $last_newline -gt $((MAX_CHARS / 2)) ]; then
        end=$((start + last_newline + 1))
      fi
    fi

    local part="${content:$start:$((end - start))}"
    echo "  📄 第${part_num}/${total_parts}段 ($((end - start))字符)..."

    if ! safe_append "$page_id" "$part"; then
      echo "❌ 第${part_num}段追加失败"
      return 1
    fi

    start=$end
    part_num=$((part_num + 1))

    # 段间短暂延迟，避免 API 限流
    if [ $start -lt $length ]; then
      sleep 0.5
    fi
  done

  echo "✅ 所有内容追加完成"
  return 0
}

# 安全地创建页面（带重试）
# 用法：safe_create_page "父页面ID" "标题" "内容"
safe_create_page() {
  local parent_id="$1"
  local title="$2"
  local content="$3"
  local retry=0

  # 将内容写入临时文件
  local temp_file=$(mktemp)
  echo "$content" > "$temp_file"

  while [ $retry -lt $MAX_RETRIES ]; do
    local result=$(unset NODE_OPTIONS && $NOTION_CLI page create \
      --parent "$parent_id" \
      --title "$title" \
      --content "$(cat "$temp_file")" 2>&1)

    local page_id=$(echo "$result" | grep -oP '(?<=ID: )[0-9a-f-]+' || echo "")

    if [ -n "$page_id" ]; then
      rm -f "$temp_file"
      echo "$page_id"
      return 0
    fi

    retry=$((retry + 1))
    if [ $retry -lt $MAX_RETRIES ]; then
      echo "⚠️ 创建失败，${RETRY_DELAY}秒后重试 ($retry/$MAX_RETRIES)..."
      sleep $RETRY_DELAY
    fi
  done

  rm -f "$temp_file"
  echo "❌ 页面创建失败"
  return 1
}

# 转义 Markdown 特殊字符（用于 Shell 安全传递）
# 用法：escape_for_shell "内容"
escape_for_shell() {
  local content="$1"
  # 使用 base64 编码避免所有 Shell 解析问题
  echo "$content" | base64 -w 0
}

# 从 base64 解码
# 用法：unesless_from_shell "base64编码的内容"
unencode_from_shell() {
  local encoded="$1"
  echo "$encoded" | base64 -d
}
