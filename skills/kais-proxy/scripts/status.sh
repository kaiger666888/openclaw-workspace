#!/usr/bin/env bash
# kais-proxy: 代理状态概览
set -euo pipefail
API="http://127.0.0.1:9090"
SECRET="${MIHOMO_SECRET:-}"
if [ -z "$SECRET" ]; then
  SECRET=$(grep '^secret:' /home/kai/clashctl/resources/runtime.yaml | awk '{print $2}')
fi

curl -s -H "Authorization: Bearer $SECRET" "$API/proxies" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('📋 代理组状态')
print('─' * 55)
for name,p in d['proxies'].items():
    t=p.get('type','')
    if t in ('Selector','URLTest','Fallback'):
        now=p.get('now','')
        allc=len(p.get('all',[]))
        tag = '🌐' if t=='URLTest' else '🔧'
        print(f'{tag} {name:14s} → {now:18s} ({allc}个节点)')
"
