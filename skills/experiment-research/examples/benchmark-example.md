# 示例实验：简单性能测试

这是一个简单的示例，展示如何使用 experiment-research skill。

## 实验主题
测试 `echo` 命令的执行性能

## 实验类型
benchmark

## 实验命令
```bash
echo "Hello, World!"
```

## 预期结果
- 执行时间 < 0.1s
- 成功率 100%

## 如何运行

```bash
cd /home/kai/.openclaw/workspace/skills/experiment-research

# 运行实验
./scripts/run-benchmark.sh \
  -n "echo-performance" \
  -t benchmark \
  -r 5 \
  -c 'echo "Hello, World!"'

# 分析结果
python scripts/analyze-results.py results/echo-performance-*
```

## 这是干什么的？

这个示例展示了：
1. 如何使用 `run-benchmark.sh` 脚本
2. 实验结果保存在哪里
3. 如何使用 `analyze-results.py` 分析结果

对于真实的实验，你需要：
1. 编写自己的基准测试脚本
2. 定义有意义的指标
3. 设置合适的对照组
4. 多轮测试取平均
