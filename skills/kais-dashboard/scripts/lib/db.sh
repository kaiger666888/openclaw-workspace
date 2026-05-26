#!/bin/bash
# db.sh - 数据库操作封装
# Usage: source db.sh; db_init; db_insert_snapshot ...

DASHBOARD_DIR="$HOME/.openclaw/workspace/data/dashboard"
DB_PATH="$DASHBOARD_DIR/dashboard.db"
SKILL_DIR="$HOME/.openclaw/workspace/skills/kais-dashboard"

db_init() {
  mkdir -p "$DASHBOARD_DIR"
  if [ ! -f "$DB_PATH" ]; then
    sqlite3 "$DB_PATH" < "$SKILL_DIR/scripts/schema.sql"
  fi
}

db_insert_snapshot() {
  local platform="$1"
  local json="$2"
  local today="$(date +%Y-%m-%d)"

  # 从 JSON 提取字段（jq 可选，fallback 用 grep）
  local followers views likes comments favorites shares coins posts new_followers new_views rate

  if command -v jq &>/dev/null && echo "$json" | jq . &>/dev/null; then
    followers=$(echo "$json" | jq -r '.followers // 0')
    views=$(echo "$json" | jq -r '.total_views // 0')
    likes=$(echo "$json" | jq -r '.total_likes // 0')
    comments=$(echo "$json" | jq -r '.total_comments // 0')
    favorites=$(echo "$json" | jq -r '.total_favorites // 0')
    shares=$(echo "$json" | jq -r '.total_shares // 0')
    coins=$(echo "$json" | jq -r '.total_coins // 0')
    posts=$(echo "$json" | jq -r '.total_posts // 0')
    new_followers=$(echo "$json" | jq -r '.new_followers // 0')
    new_views=$(echo "$json" | jq -r '.new_views // 0')
    rate=$(echo "$json" | jq -r '.interaction_rate // 0')
  else
    followers=$(echo "$json" | grep -o '"followers":[0-9]*' | grep -o '[0-9]*' || echo 0)
    views=$(echo "$json" | grep -o '"total_views":[0-9]*' | grep -o '[0-9]*' || echo 0)
    likes=$(echo "$json" | grep -o '"total_likes":[0-9]*' | grep -o '[0-9]*' || echo 0)
    comments=$(echo "$json" | grep -o '"total_comments":[0-9]*' | grep -o '[0-9]*' || echo 0)
    favorites=$(echo "$json" | grep -o '"total_favorites":[0-9]*' | grep -o '[0-9]*' || echo 0)
    shares=$(echo "$json" | grep -o '"total_shares":[0-9]*' | grep -o '[0-9]*' || echo 0)
    coins=$(echo "$json" | grep -o '"total_coins":[0-9]*' | grep -o '[0-9]*' || echo 0)
    posts=$(echo "$json" | grep -o '"total_posts":[0-9]*' | grep -o '[0-9]*' || echo 0)
    new_followers=$(echo "$json" | grep -o '"new_followers":[0-9]*' | grep -o '[0-9]*' || echo 0)
    new_views=$(echo "$json" | grep -o '"new_views":[0-9]*' | grep -o '[0-9]*' || echo 0)
    rate=$(echo "$json" | grep -o '"interaction_rate":[0-9.]*' | grep -o '[0-9.]*' || echo 0)
  fi

  sqlite3 "$DB_PATH" "INSERT OR REPLACE INTO daily_snapshots 
    (platform, date, followers, total_views, total_likes, total_comments, 
     total_favorites, total_shares, total_coins, total_posts, 
     new_followers, new_views, interaction_rate, raw_json)
    VALUES ('$platform', '$today', ${followers:-0}, ${views:-0}, ${likes:-0}, 
            ${comments:-0}, ${favorites:-0}, ${shares:-0}, ${coins:-0}, ${posts:-0},
            ${new_followers:-0}, ${new_views:-0}, ${rate:-0}, '${json//\'/\'\'}');"
}

db_log() {
  local platform="$1" action="$2" message="$3"
  sqlite3 "$DB_PATH" "INSERT INTO collect_logs (platform, action, message) 
    VALUES ('$platform', '$action', '${message//\'/\'\'}');"
}

db_get_latest() {
  local platform="$1"
  sqlite3 -json "$DB_PATH" "SELECT * FROM daily_snapshots WHERE platform='$platform' ORDER BY date DESC LIMIT 1;"
}

db_get_trend() {
  local platform="$1" days="${2:-30}"
  sqlite3 -json "$DB_PATH" "SELECT date, followers, total_views, total_likes, interaction_rate 
    FROM daily_snapshots WHERE platform='$platform' ORDER BY date DESC LIMIT $days;"
}

db_export_json() {
  # 导出所有平台最新数据为 JSON
  sqlite3 -json "$DB_PATH" "
    SELECT s.*, a.account_name 
    FROM daily_snapshots s 
    LEFT JOIN accounts a ON s.platform = a.platform 
    WHERE s.date = (SELECT MAX(date) FROM daily_snapshots)
    ORDER BY s.platform;"
}
