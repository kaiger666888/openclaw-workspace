# 代理服务故障临时解决方案

**时间**: 2026-03-17 07:25  
**问题**: 星云代理所有节点拒绝连接 (connection refused)  
**影响**: 无法访问外网 API（Brave Search、Google、OpenAI 等）

---

## 问题确认

### 日志证据
```
dial tcp 14.17.92.71:1101: connect: connection refused
dial tcp 14.17.92.71:1111: connect: connection refused
dial tcp 14.17.92.71:1121: connect: connection refused
```

### 节点状态
```bash
curl http://127.0.0.1:9090/proxies/VIP香港-2A｜原生解锁🇭🇰 | jq '.alive'
# 输出: false（所有节点都是 false）
```

### 流量状态
- 剩余流量：194.38 GB ✅
- 套餐到期：2026-11-27 ✅
- 下次重置：25 天后 ✅

**结论**: 非流量/过期问题，是服务器故障或被封禁

---

## 临时解决方案（按优先级）

### 方案1：更新订阅链接（推荐）

**步骤：**

1. 访问星云官网获取最新订阅
   ```
   https://cdn.xxxlsop3.com
   或
   https://cdn.xxxlsop3.xyz
   ```

2. 下载最新配置文件（Clash/Mihomo 格式）

3. 替换配置文件
   ```bash
   # 备份当前配置
   cp /home/kai/clashctl/resources/profiles/1.yaml \
      /home/kai/clashctl/resources/profiles/1.yaml.bak-$(date +%Y%m%d)
   
   # 替换为新配置
   mv 新配置.yaml /home/kai/clashctl/resources/profiles/1.yaml
   
   # 重启 mihomo
   killall -HUP mihomo
   ```

4. 验证连接
   ```bash
   curl -I https://www.google.com
   ```

### 方案2：临时禁用代理（应急方案）

**适用场景**: 临时需要访问国内可访问的资源

```bash
# 临时禁用代理
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy

# 或仅对当前 shell 禁用
export no_proxy="*"
```

**注意**: 
- 禁用后无法访问被墙资源（Google、OpenAI 等）
- Brave Search API 可能也无法访问

### 方案3：使用备用代理服务（中期方案）

**推荐服务商：**

1. **Clash for Windows 订阅**
   - 支持多协议
   - 节点丰富

2. **V2Ray 订阅**
   - 稳定性好
   - 支持多平台

3. **Shadowsocks**
   - 轻量级
   - 配置简单

**配置方法：**
```bash
# 下载配置文件后
cp 新订阅.yaml /home/kai/clashctl/resources/profiles/2.yaml

# 修改启动命令使用新配置
/home/kai/clashctl/bin/mihomo -d /home/kai/clashctl/resources -f /home/kai/clashctl/resources/profiles/2.yaml
```

### 方案4：使用代理池（长期方案）

**优点：**
- 自动切换故障节点
- 提高可用性
- 分散风险

**实现：**
1. 配置多个代理服务
2. 使用脚本定期检测可用性
3. 自动切换到可用节点

---

## 针对 Brave API 的特殊方案

### 方案A：使用备用搜索服务

**1. Google Custom Search API**
```bash
# 需要 Google Cloud API Key
curl "https://www.googleapis.com/customsearch/v1?key=API_KEY&cx=SEARCH_ENGINE_ID&q=test"
```

**2. Bing Search API**
```bash
# 需要 Azure API Key
curl "https://api.bing.microsoft.com/v7.0/search?q=test" -H "Ocp-Apim-Subscription-Key: API_KEY"
```

**3. DuckDuckGo Instant Answer API（免费）**
```bash
curl "https://api.duckduckgo.com/?q=test&format=json"
```

### 方案B：部署海外 VPS

**推荐服务商：**
- Vultr
- DigitalOcean
- AWS Lightsail

**配置步骤：**
1. 购买海外 VPS（$5/月起）
2. 安装 OpenClaw
3. 配置代理服务
4. 通过 VPS 访问外部 API

---

## 立即行动建议

### 优先级 P0（现在执行）
1. ✅ 访问 https://cdn.xxxlsop3.com 更新订阅
2. ✅ 测试新配置是否可用
3. ✅ 如果仍失败，联系星云客服

### 优先级 P1（今天完成）
1. 配置备用代理服务
2. 实现 Brave API 降级方案（Google/Bing）
3. 添加代理健康监控

### 优先级 P2（本周完成）
1. 部署海外 VPS（如果代理服务持续不稳定）
2. 实现代理池自动切换
3. 建立本地搜索缓存机制

---

## 相关文件

- 代理配置：`/home/kai/clashctl/resources/profiles/1.yaml`
- 备份配置：`/home/kai/clashctl/resources/profiles/1.yaml.backup-*`
- mihomo 日志：`/tmp/mihomo.log`
- 问题排查：`memory/brave-api-fix.md`

---

**创建时间**: 2026-03-17 07:25  
**状态**: 待更新订阅或配置备用代理
