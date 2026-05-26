#!/usr/bin/env bash
# kais-proxy: 切换节点
# 用法: bash switch.sh <组名> <节点名>
set -euo pipefail
API="http://127.0.0.1:9090"
SECRET="${MIHOMO_SECRET:-}"
if [ -z "$SECRET" ]; then
  SECRET=$(grep '^secret:' /home/kai/clashctl/resources/runtime.yaml | awk '{print $2}')
fi

GROUP="$1"
NODE="$2"

echo "🔄 切换 [$GROUP] → [$NODE]..."
RESULT=$(curl -s -X PUT -H "Authorization: Bearer $SECRET" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$NODE\"}" \
  "$API/proxies/$GROUP")

echo "$RESULT"
echo "✅ 切换完成"
