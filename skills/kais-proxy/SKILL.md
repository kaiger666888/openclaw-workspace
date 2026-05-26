---
name: kais-proxy
version: 1.0.0
description: "Mihomo 代理配置管理工具。管理订阅刷新、可用节点选择、延迟测试、代理组切换。触发词：代理管理、proxy、节点选择、切换节点、测速、刷新订阅、mihomo、clash、proxy manager、节点测试、选个节点、换个节点、代理测速、哪个节点快、代理状态"
---

# kais-proxy

Mihomo (Clash Meta) 代理管理工具。通过 RESTful API 管理代理节点。

<!-- FREEDOM:low -->

## 环境配置

- **API 地址**：`http://127.0.0.1:9090`
- **Secret**：运行时从 `MIHOMO_SECRET` 环境变量读取，或自动从 `/home/kai/clashctl/resources/runtime.yaml` 提取
- **配置目录**：`/home/kai/clashctl/resources/`
- **订阅来源**：wudixingxing（proxy-provider）
- **进程**：`/home/kai/clashctl/bin/mihomo`

## 核心操作

所有操作通过 `scripts/` 目录下的脚本执行，无需手动构造 API 请求。

### 1. 查看代理状态

```bash
bash ~/.openclaw/workspace/skills/kais-proxy/scripts/status.sh
```

输出代理组名称、当前节点、节点总数。

### 2. 刷新订阅

```bash
bash ~/.openclaw/workspace/skills/kais-proxy/scripts/refresh.sh
```

触发 provider 刷新，更新节点列表，显示可用节点数。

### 3. 延迟测试

全部节点测速 + 排序：
```bash
bash ~/.openclaw/workspace/skills/kais-proxy/scripts/speedtest.sh
```

对指定 URLTest 组触发测速：
```bash
bash ~/.openclaw/workspace/skills/kais-proxy/scripts/speedtest.sh "♻️ 自动选择"
```

### 4. 切换节点

```bash
bash ~/.openclaw/workspace/skills/kais-proxy/scripts/switch.sh "🔰 节点选择" "IEPL 日本 1"
```

参数：`<组名> <节点名>`。

### 5. 获取所有节点列表

```bash
curl -s -H "Authorization: Bearer $SECRET" http://127.0.0.1:9090/proxies | python3 -c "
import sys,json
d=json.load(sys.stdin)
[print(n) for n,p in sorted(d['proxies'].items()) if p.get('type') in ('Shadowsocks','Vmess','Vless','Trojan','Hysteria','Hysteria2','TUIC','WireGuard','Relay')]
"
```

## 代理组说明

| 组名 | 类型 | 用途 |
|------|------|------|
| 🔰 节点选择 | Selector | 主代理选择入口 |
| ♻️ 自动选择 | URLTest | 自动测速选最优 |
| 📲 电报信息 | Selector | Telegram 流量 |
| 🌍 国外媒体 | Selector | YouTube/Twitter 等 |
| Ⓜ️ 微软服务 | Selector | 微软相关 |
| 🍎 苹果服务 | Selector | Apple 相关 |
| 🌏 国内媒体 | Selector | 国内直连 |
| 🐟 漏网之鱼 | Selector | 兜底规则 |

## 使用场景

### 用户说"帮我选个快的节点"
1. 运行 `refresh.sh` 刷新订阅
2. 运行 `speedtest.sh` 批量测速
3. 推荐前 3 个最快节点
4. 询问是否切换，确认后运行 `switch.sh`

### 用户说"刷新订阅"或"更新节点"
1. 运行 `refresh.sh`
2. 显示结果

### 用户说"切换到日本节点"
1. 运行 `speedtest.sh` 获取所有节点延迟
2. 筛选名称含"日本"的节点
3. 切换到最快的，运行 `switch.sh`
4. 确认结果

### 用户说"当前代理状态"
1. 运行 `status.sh`
2. 展示结果

## 故障排查

- **API 返回 Unauthorized**：检查 runtime.yaml 中的 secret
- **节点全部超时**：检查网络连通性，尝试 `refresh.sh`
- **刷新订阅失败**：检查 `/home/kai/clashctl/resources/providers/wudixingxing.yaml`
- **进程未运行**：`/home/kai/clashctl/bin/mihomo -d /home/kai/clashctl/resources -f /home/kai/clashctl/resources/runtime.yaml`

<!-- /FREEDOM:low -->
