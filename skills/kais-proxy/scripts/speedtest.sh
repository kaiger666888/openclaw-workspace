#!/usr/bin/env bash
# kais-proxy: 批量延迟测试 + 排序
# 用法: bash speedtest.sh [group]

set -euo pipefail
API="http://127.0.0.1:9090"
SECRET="${MIHOMO_SECRET:-}"
if [ -z "$SECRET" ]; then
  SECRET=$(grep '^secret:' /home/kai/clashctl/resources/runtime.yaml | awk '{print $2}')
fi

GROUP="${1:-}"

if [ -n "$GROUP" ]; then
  # 对指定 URLTest 组触发全部测速
  curl -s -X GET -H "Authorization: Bearer $SECRET" \
    "$API/group/$GROUP/delay?url=http://www.gstatic.com/generate_204&timeout=5000"
  echo ""
  exit 0
fi

# 全部节点测速 + 排序
curl -s -H "Authorization: Bearer $SECRET" "$API/proxies" | python3 - "$SECRET" "$API" << 'PYEOF'
import sys, json, subprocess

SECRET, BASE = sys.argv[1], sys.argv[2]
d = json.load(sys.stdin)
results = []

VALID_TYPES = ("Shadowsocks","Vmess","Vless","Trojan","Hysteria","Hysteria2","TUIC","WireGuard","Relay")

for name, p in d["proxies"].items():
    if p.get("type") not in VALID_TYPES:
        continue
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "5", "-H", f"Authorization: Bearer {SECRET}",
             f"{BASE}/proxies/{name}/delay?timeout=5000&url=http://www.gstatic.com/generate_204"],
            capture_output=True, text=True
        )
        data = json.loads(r.stdout)
        delay = data.get("delay", 0)
        if delay > 0:
            results.append((delay, name))
    except Exception:
        pass

results.sort()
for delay, name in results:
    print(f"{delay:>5d}ms  {name}")
print(f"\n共 {len(results)} 个可用节点")
PYEOF
