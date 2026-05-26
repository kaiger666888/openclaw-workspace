#!/usr/bin/env bash
# kais-proxy: 刷新订阅
set -euo pipefail
API="http://127.0.0.1:9090"
SECRET="${MIHOMO_SECRET:-}"
if [ -z "$SECRET" ]; then
  SECRET=$(grep '^secret:' /home/kai/clashctl/resources/runtime.yaml | awk '{print $2}')
fi

echo "🔄 正在刷新订阅..."
RESULT=$(curl -s -X PUT -H "Authorization: Bearer $SECRET" "$API/providers/proxies/wudixingxing")
echo "$RESULT"

if echo "$RESULT" | grep -q '"status":"success"'; then
  echo "✅ 订阅刷新成功"
  # 等待节点加载
  sleep 3
  # 显示节点总数
  COUNT=$(curl -s -H "Authorization: Bearer $SECRET" "$API/proxies" | python3 -c "
import sys,json
d=json.load(sys.stdin)
nodes=[n for n,p in d['proxies'].items() if p.get('type') in ('Shadowsocks','Vmess','Vless','Trojan','Hysteria','Hysteria2','TUIC','WireGuard','Relay')]
print(len(nodes))
" 2>/dev/null)
  echo "📊 当前可用节点: ${COUNT:-?} 个"
else
  echo "❌ 刷新失败，请检查订阅链接"
fi
