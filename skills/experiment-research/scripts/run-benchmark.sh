#!/bin/bash
# 基准测试执行脚本
# 用于运行实验并记录结果

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$SKILL_DIR/results"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EXPERIMENT_ID=$(uuidgen | cut -d'-' -f1)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 用法说明
usage() {
    cat << EOF
用法: $0 [选项]

基准测试执行脚本

选项:
  -n, --name       实验名称 (必需)
  -t, --type       实验类型: benchmark|comparison|usability|hybrid (默认: benchmark)
  -r, --rounds     实验轮次 (默认: 5)
  -c, --command    实验命令 (必需)
  -o, --output     输出目录 (默认: results/)
  -h, --help       显示帮助信息

示例:
  $0 -n "rust-vs-go" -t benchmark -r 5 -c "./benchmark.sh"
  $0 --name "react-vs-vue" --type comparison --rounds 3 --command "npm test"

EOF
    exit 1
}

# 解析参数
EXPERIMENT_NAME=""
EXPERIMENT_TYPE="benchmark"
ROUNDS=5
COMMAND=""
OUTPUT_DIR="$RESULTS_DIR"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            EXPERIMENT_NAME="$2"
            shift 2
            ;;
        -t|--type)
            EXPERIMENT_TYPE="$2"
            shift 2
            ;;
        -r|--rounds)
            ROUNDS="$2"
            shift 2
            ;;
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "未知参数: $1"
            usage
            ;;
    esac
done

# 验证必需参数
if [ -z "$EXPERIMENT_NAME" ]; then
    log_error "缺少实验名称 (-n, --name)"
    usage
fi

if [ -z "$COMMAND" ]; then
    log_error "缺少实验命令 (-c, --command)"
    usage
fi

# 创建输出目录
EXPERIMENT_DIR="$OUTPUT_DIR/$EXPERIMENT_NAME-$EXPERIMENT_ID"
mkdir -p "$EXPERIMENT_DIR"

log_info "实验配置:"
echo "  名称: $EXPERIMENT_NAME"
echo "  类型: $EXPERIMENT_TYPE"
echo "  轮次: $ROUNDS"
echo "  命令: $COMMAND"
echo "  输出: $EXPERIMENT_DIR"
echo ""

# 收集环境信息
collect_env_info() {
    cat << EOF > "$EXPERIMENT_DIR/environment.json"
{
  "timestamp": "$TIMESTAMP",
  "experiment_id": "$EXPERIMENT_ID",
  "hostname": "$(hostname)",
  "os": "$(uname -s)",
  "os_version": "$(uname -r)",
  "cpu": "$(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)",
  "cpu_cores": $(nproc),
  "memory_total": $(free -m | awk '/^Mem:/{print $2}'),
  "disk_total": $(df -BG / | awk 'NR==2{print $2}' | sed 's/G//')
}
EOF
}

# 运行单轮实验
run_single_round() {
    local round=$1
    local result_file="$EXPERIMENT_DIR/round-$round.json"

    log_info "运行第 $round/$ROUNDS 轮..."

    # 记录开始时间
    local start_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local start_epoch=$(date +%s.%N)

    # 运行命令并捕获输出
    set +e
    local output
    output=$(eval "$COMMAND" 2>&1)
    local exit_code=$?
    set -e

    # 记录结束时间
    local end_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local end_epoch=$(date +%s.%N)
    local duration=$(echo "$end_epoch - $start_epoch" | bc)

    # 保存结果
    cat << EOF > "$result_file"
{
  "round": $round,
  "start_time": "$start_time",
  "end_time": "$end_time",
  "duration_seconds": $duration,
  "exit_code": $exit_code,
  "output": $(echo "$output" | jq -Rs .)
}
EOF

    if [ $exit_code -eq 0 ]; then
        log_info "第 $round 轮完成 (耗时: ${duration}s)"
    else
        log_warn "第 $round 轮失败 (exit code: $exit_code)"
    fi

    echo "$result_file"
}

# 主执行流程
main() {
    log_info "开始实验: $EXPERIMENT_NAME"

    # 收集环境信息
    collect_env_info
    log_info "环境信息已收集"

    # 运行所有轮次
    for round in $(seq 1 $ROUNDS); do
        run_single_round $round
        echo ""
    done

    # 生成汇总报告
    log_info "生成汇总报告..."

    cat << EOF > "$EXPERIMENT_DIR/summary.json"
{
  "experiment_name": "$EXPERIMENT_NAME",
  "experiment_type": "$EXPERIMENT_TYPE",
  "experiment_id": "$EXPERIMENT_ID",
  "timestamp": "$TIMESTAMP",
  "total_rounds": $ROUNDS,
  "command": "$COMMAND",
  "results": [
$(ls -1 "$EXPERIMENT_DIR"/round-*.json | while read file; do
    cat "$file"
    echo ","
done | sed '$ s/,$//')
  ]
}
EOF

    # 显示结果摘要
    log_info "实验完成!"
    echo ""
    echo "结果目录: $EXPERIMENT_DIR"
    echo "汇总文件: $EXPERIMENT_DIR/summary.json"
    echo ""

    # 计算统计数据
    log_info "性能统计:"
    jq -r '.results[] | .duration_seconds' "$EXPERIMENT_DIR/summary.json" | \
        awk '{sum+=$1; sumsq+=$1*$1; if(NR==1||$1<min)min=$1; if($1>max)max=$1} END {
            avg=sum/NR;
            if(NR>1) std=sqrt(sumsq/NR - avg*avg);
            printf "  平均: %.3fs\n  最小: %.3fs\n  最大: %.3fs\n  标准差: %.3fs\n", avg, min, max, std
        }'
}

# 执行主流程
main

exit 0
