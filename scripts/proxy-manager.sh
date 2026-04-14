#!/bin/bash
# 代理服务管理工具

PROXY_CONF="/home/kai/clashctl/resources/profiles/1.yaml"
MIHOMO_PID=$(pgrep mihomo)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

case "$1" in
    status)
        echo -e "${YELLOW}代理服务状态${NC}"
        echo "PID: $MIHOMO_PID"
        
        if [ -n "$MIHOMO_PID" ]; then
            echo -e "mihomo: ${GREEN}运行中${NC}"
        else
            echo -e "mihomo: ${RED}未运行${NC}"
        fi
        
        echo ""
        echo -e "${YELLOW}环境变量${NC}"
        echo "HTTP_PROXY: ${HTTP_PROXY:-未设置}"
        echo "HTTPS_PROXY: ${HTTPS_PROXY:-未设置}"
        echo ""
        
        echo -e "${YELLOW}节点状态${NC}"
        curl -s http://127.0.0.1:9090/proxies/星云 2>/dev/null | \
            jq -r '"当前节点: \(.now)\n节点状态: \(.all[:3] | .[])"' 2>/dev/null || \
            echo "无法获取节点状态"
        ;;
    
    test)
        echo -e "${YELLOW}测试代理连接${NC}"
        
        echo "测试 Google..."
        if curl -I --connect-timeout 5 --silent https://www.google.com | grep -q "HTTP"; then
            echo -e "Google: ${GREEN}✓ 可用${NC}"
        else
            echo -e "Google: ${RED}✗ 不可用${NC}"
        fi
        
        echo "测试 Brave API..."
        if curl -I --connect-timeout 5 --silent https://api.search.brave.com | grep -q "HTTP"; then
            echo -e "Brave API: ${GREEN}✓ 可用${NC}"
        else
            echo -e "Brave API: ${RED}✗ 不可用${NC}"
        fi
        
        echo "测试国内网站..."
        if curl -I --connect-timeout 5 --silent https://www.baidu.com | grep -q "HTTP"; then
            echo -e "百度: ${GREEN}✓ 可用${NC}"
        else
            echo -e "百度: ${RED}✗ 不可用${NC}"
        fi
        ;;
    
    disable)
        echo -e "${YELLOW}临时禁用代理${NC}"
        echo "请在当前 shell 执行以下命令："
        echo ""
        echo "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy"
        echo ""
        echo "或添加到 ~/.bashrc 永久禁用："
        echo "export no_proxy='*'"
        ;;
    
    enable)
        echo -e "${YELLOW}启用代理${NC}"
        echo "请在当前 shell 执行以下命令："
        echo ""
        echo "export http_proxy=http://127.0.0.1:7890"
        echo "export https_proxy=http://127.0.0.1:7890"
        echo "export HTTP_PROXY=http://127.0.0.1:7890"
        echo "export HTTPS_PROXY=http://127.0.0.1:7890"
        ;;
    
    restart)
        echo -e "${YELLOW}重启 mihomo 服务${NC}"
        if [ -n "$MIHOMO_PID" ]; then
            killall -HUP mihomo
            echo -e "${GREEN}✓ 配置已重新加载${NC}"
        else
            nohup /home/kai/clashctl/bin/mihomo -d /home/kai/clashctl/resources \
                -f /home/kai/clashctl/resources/profiles/1.yaml > /tmp/mihomo.log 2>&1 &
            echo -e "${GREEN}✓ mihomo 已启动${NC}"
        fi
        sleep 2
        $0 test
        ;;
    
    switch)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}可用节点列表${NC}"
            curl -s http://127.0.0.1:9090/proxies/星云 2>/dev/null | \
                jq -r '.all[]' | head -20
            echo ""
            echo "使用方法: $0 switch '节点名称'"
        else
            NODE_NAME="$2"
            echo -e "${YELLOW}切换到节点: $NODE_NAME${NC}"
            curl -X PUT "http://127.0.0.1:9090/proxies/星云" \
                -H "Content-Type: application/json" \
                -d "{\"name\":\"$NODE_NAME\"}" > /dev/null 2>&1
            
            sleep 2
            $0 test
        fi
        ;;
    
    update)
        echo -e "${YELLOW}更新订阅步骤${NC}"
        echo ""
        echo "1. 访问官网获取订阅链接："
        echo "   https://cdn.xxxlsop3.com"
        echo "   或 https://cdn.xxxlsop3.xyz"
        echo ""
        echo "2. 下载 Clash/Mihomo 格式配置文件"
        echo ""
        echo "3. 备份当前配置："
        echo "   cp $PROXY_CONF ${PROXY_CONF}.bak-\$(date +%Y%m%d)"
        echo ""
        echo "4. 替换配置文件："
        echo "   mv 新配置.yaml $PROXY_CONF"
        echo ""
        echo "5. 重启 mihomo："
        echo "   $0 restart"
        ;;
    
    *)
        echo "代理服务管理工具"
        echo ""
        echo "用法: $0 {status|test|disable|enable|restart|switch|update}"
        echo ""
        echo "命令说明："
        echo "  status   - 查看代理服务状态"
        echo "  test     - 测试代理连接"
        echo "  disable  - 临时禁用代理"
        echo "  enable   - 启用代理"
        echo "  restart  - 重启 mihomo 服务"
        echo "  switch   - 切换代理节点"
        echo "  update   - 更新订阅指南"
        echo ""
        echo "示例："
        echo "  $0 status"
        echo "  $0 test"
        echo "  $0 switch 'VIP香港-1A｜原生解锁🇭🇰'"
        ;;
esac
