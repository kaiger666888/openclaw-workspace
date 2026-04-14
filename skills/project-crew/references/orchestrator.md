# 编排器算法详解

## DAG 构建

### 依赖解析

```js
function buildDAG(steps) {
  const nodes = new Map(); // id -> step
  const edges = [];        // [from, to]
  
  // 收集 output 文件 → step id 的映射
  const outputMap = new Map(); // filename -> stepId
  for (const step of steps) {
    nodes.set(step.id, step);
    if (step.output) {
      const outputs = Array.isArray(step.output) ? step.output : [step.output];
      for (const f of outputs) outputMap.set(f, step.id);
    }
  }
  
  // 解析 input → 建边
  for (const step of steps) {
    if (!step.input) continue;
    const inputs = Array.isArray(step.input) ? step.input : [step.input];
    for (const f of inputs) {
      const from = outputMap.get(f);
      if (from && from !== step.id) edges.push([from, step.id]);
    }
  }
  
  return { nodes, edges };
}
```

### 环检测

```js
function detectCycle(nodes, edges) {
  const WHITE = 0, GRAY = 1, BLACK = 2;
  const color = new Map([...nodes.keys()].map(k => [k, WHITE]));
  
  function dfs(node) {
    color.set(node, GRAY);
    for (const [from, to] of edges) {
      if (from !== node) continue;
      if (color.get(to) === GRAY) return true; // back edge = cycle
      if (color.get(to) === WHITE && dfs(to)) return true;
    }
    color.set(node, BLACK);
    return false;
  }
  
  return [...nodes.keys()].some(id => color.get(id) === WHITE && dfs(id));
}
```

### 拓扑排序（Kahn's algorithm）

```js
function topologicalSort(nodes, edges) {
  const inDegree = new Map([...nodes.keys()].map(k => [k, 0]));
  for (const [, to] of edges) inDegree.set(to, inDegree.get(to) + 1);
  
  const queue = [...inDegree.entries()].filter(([, d]) => d === 0).map(([id]) => id);
  const layers = [];
  
  while (queue.length) {
    layers.push([...queue]);
    const next = [];
    for (const id of queue) {
      for (const [from, to] of edges) {
        if (from !== id) continue;
        inDegree.set(to, inDegree.get(to) - 1);
        if (inDegree.get(to) === 0) next.push(to);
      }
    }
    queue.length = 0;
    queue.push(...next);
  }
  
  return layers; // 每层可并行执行
}
```

## 模式推断

```js
function inferMode(steps, edges) {
  const { nodes } = buildDAG(steps);
  
  // 1. 检查 approval
  if (steps.some(s => s.await === 'human')) return 'approval';
  
  // 2. 检查 cycle
  if (detectCycle(nodes, edges)) return 'event-loop';
  
  // 3. 检查图结构
  const layers = topologicalSort(nodes, edges);
  const inDegree = countInDegree(nodes, edges);
  const outDegree = countOutDegree(nodes, edges);
  
  const startNodes = [...inDegree.entries()].filter(([,d]) => d === 0).length;
  const endNodes = [...outDegree.entries()].filter(([,d]) => d === 0).length;
  const mergeNodes = [...inDegree.entries()].filter(([,d]) => d > 1).length;
  
  if (steps.length === layers.length && steps.length > 1) return 'pipeline';
  if (startNodes > 1 || mergeNodes > 0) {
    if (mergeNodes > 0) return 'map-reduce';
    return 'fan-out';
  }
  if (steps.some(s => s.loop)) return 'event-loop';
  
  return 'dag';
}
```

## 执行引擎

### 伪代码

```
async function execute(crewDef) {
  createWorkdir(crewDef.workdir)
  const { nodes, edges } = buildDAG(crewDef.steps)
  const mode = crewDef.mode || inferMode(crewDef.steps, edges)
  const layers = topologicalSort(nodes, edges)
  
  for (const layer of layers) {
    if (mode === 'approval') {
      const step = layer[0]
      if (step.await === 'human') {
        report(`⏸️ 等待人工审批: ${step.id}`)
        const approved = await waitForHumanApproval()
        if (!approved) { report('❌ 已拒绝'); return }
      }
    }
    
    const promises = layer.map(id => spawnSubAgent(nodes.get(id)))
    const results = await Promise.allSettled(promises)
    
    for (const [i, r] of results.entries()) {
      if (r.status === 'rejected') {
        report(`⚠️ Step ${layer[i]} 失败: ${r.reason}`)
      }
    }
  }
  
  report('✅ 编排完成')
}
```

### Sub-Agent Spawn

每个 step spawn 为独立 sub-agent，注入以下上下文：

```
你是 <skill> skill 的执行器。

工作目录: <workdir>
输入文件: <input files with paths>
输出文件: <output files with paths>
参数: <params>

请先读取 skill SKILL.md 获取执行指导，然后完成任务。
产出文件写入工作目录。
```
