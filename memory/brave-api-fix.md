# Brave API 网络访问问题解决方案

## 问题诊断 (2026-03-17 07:15)

### 根本原因
**非 API 限流，而是网络访问问题**

1. **直连测试失败**
   - `ping api.search.brave.com` → 100% 丢包
   - `curl --noproxy "*"` → 连接超时

2. **代理测试失败**
   - `curl` 通过代理 → SSL 握手错误
   - 代理服务运行正常（mihomo 7890/7891）

3. **结论**
   - `api.search.brave.com` 在中国大陆可能被限制访问
   - mihomo 代理规则未包含该域名

## 解决方案

### 方案1：配置 mihomo 代理规则（推荐）

**步骤：**

1. 找到 mihomo 配置文件
```bash
# 常见位置
~/.config/mihomo/config.yaml
/etc/mihomo/config.yaml
```

2. 添加域名规则（在 `rules:` 部分）
```yaml
rules:
  # Brave Search API
  - DOMAIN-SUFFIX,brave.com,PROXY
  - DOMAIN-SUFFIX,search.brave.com,PROXY
  - DOMAIN,api.search.brave.com,PROXY
```

3. 重启 mihomo 服务
```bash
systemctl restart mihomo
# 或
killall -HUP mihomo
```

4. 测试连接
```bash
curl -I https://api.search.brave.com
```

### 方案2：使用备用搜索服务

**选项：**

1. **Google Custom Search API**
   - 需要 Google Cloud 账号
   - 免费额度：100 次/天
   - 文档：https://developers.google.com/custom-search/v1/overview

2. **Bing Search API**
   - 需要 Azure 账号
   - 免费层级：3 次/秒，1000 次/月
   - 文档：https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

3. **DuckDuckGo Instant Answer API**
   - 免费，无需 API Key
   - 功能有限（无完整搜索结果）
   - 文档：https://duckduckgo.com/api

**实施：**
- 修改 OpenClaw 配置，添加备用搜索服务
- 实现搜索服务降级逻辑

### 方案3：环境变量配置（临时）

**设置代理绕过：**
```bash
# 添加到 ~/.bashrc 或 /etc/environment
export no_proxy="localhost,127.0.0.1,api.search.brave.com"
export NO_PROXY="localhost,127.0.0.1,api.search.brave.com"
```

**注意：** 此方案无效，因为直连也失败

## 推荐行动

### 立即执行（优先级 P0）
1. **配置 mihomo 规则** - 最快解决当前问题
2. **测试连接** - 确认问题解决
3. **重试失败任务** - AIGC 前沿总结、每日新闻等

### 中期改进（优先级 P1）
1. **添加备用搜索服务** - 提高系统可靠性
2. **实现降级逻辑** - Brave 失败时自动切换
3. **监控搜索服务** - 添加可用性检测

### 长期优化（优先级 P2）
1. **本地搜索缓存** - 减少外部依赖
2. **多源聚合搜索** - 提高结果质量
3. **离线模式支持** - 网络故障时的备选方案

## 相关信息

- **mihomo 配置位置**: 未知（需查找）
- **Brave API 限流规则**: 2000 次/月（免费）
- **当前使用情况**: 多个任务失败，未消耗额度

## 参考链接

- Brave Search API 文档：https://brave.com/search/api/
- mihomo 配置指南：https://wiki.metacubex.one/
- OpenClaw web_search 工具：~/.nvm/.../openclaw/tools/web-search.ts

---

**创建时间**: 2026-03-17 07:15  
**最后更新**: 2026-03-17 07:25  
**状态**: ❌ 代理服务完全不可用 - 所有节点拒绝连接

## 执行记录 (2026-03-17 07:15-07:25)

### 已完成
1. ✅ 诊断问题：非 API 限流，而是网络访问问题
2. ✅ 定位 mihomo 配置文件：`/home/kai/clashctl/resources/profiles/1.yaml`
3. ✅ 添加 Brave API 代理规则
4. ✅ 重新加载 mihomo 配置

### 发现的新问题
1. **代理服务故障** - 所有 HTTPS 连接 SSL 握手失败
   - 测试：`curl https://www.google.com` → SSL_ERROR_SYSCALL
   - 测试：`curl https://api.openai.com` → SSL_ERROR_SYSCALL
   - 测试：`curl https://api.search.brave.com` → SSL_ERROR_SYSCALL

2. **切换节点无效** - 尝试切换到美国节点，问题依旧

3. **直连也失败** - `curl --noproxy "*"` 超时

### 根本原因
**mihomo 代理服务本身存在 SSL 连接问题，可能原因：**
- 代理服务器故障或维护
- SSL 证书问题
- 代理配置损坏
- 网络运营商干扰

### 推荐解决方案（优先级排序）

#### P0 - 立即执行
1. **检查代理服务状态**
   ```bash
   # 查看 mihomo 日志
   tail -100 /tmp/mihomo.log
   
   # 检查代理订阅是否过期
   # 访问代理服务提供商网站
   ```

2. **更新代理订阅**
   - 访问星云官网：https://cdn.xxxlsop3.com
   - 下载最新订阅链接
   - 更新 mihomo 配置

3. **临时禁用代理，使用备用方案**
   ```bash
   # 临时禁用代理
   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
   
   # 使用 web_fetch 直接访问（如果网络允许）
   # 或使用备用搜索服务
   ```

#### P1 - 中期改进
1. **配置备用代理**
   - 添加第二个代理服务
   - 实现自动切换逻辑

2. **实现搜索服务降级**
   - Brave API → Google Custom Search → Bing Search
   - 本地缓存机制

#### P2 - 长期优化
1. **监控代理健康状态**
   - 定期检测代理可用性
   - 自动切换故障节点

2. **多云部署**
   - VPS 部署（不受国内网络限制）
   - 边缘节点加速
