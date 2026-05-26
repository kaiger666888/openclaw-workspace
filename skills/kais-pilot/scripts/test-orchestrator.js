#!/usr/bin/env node
// project-crew orchestrator logic tests
// Implements: DAG build, cycle detection, mode inference, topological sort, error handling

// ── Orchestrator core (from references/orchestrator.md) ──

function buildDAG(steps) {
  const nodes = new Map();
  const edges = [];
  const outputMap = new Map();

  for (const step of steps) {
    nodes.set(step.id, step);
    if (step.output) {
      const outputs = Array.isArray(step.output) ? step.output : [step.output];
      for (const f of outputs) outputMap.set(f, step.id);
    }
  }

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

function detectCycle(nodes, edges) {
  const WHITE = 0, GRAY = 1, BLACK = 2;
  const color = new Map([...nodes.keys()].map(k => [k, WHITE]));

  function dfs(node) {
    color.set(node, GRAY);
    for (const [from, to] of edges) {
      if (from !== node) continue;
      if (color.get(to) === GRAY) return true;
      if (color.get(to) === WHITE && dfs(to)) return true;
    }
    color.set(node, BLACK);
    return false;
  }

  return [...nodes.keys()].some(id => color.get(id) === WHITE && dfs(id));
}

function countInDegree(nodes, edges) {
  const deg = new Map([...nodes.keys()].map(k => [k, 0]));
  for (const [, to] of edges) deg.set(to, deg.get(to) + 1);
  return deg;
}

function countOutDegree(nodes, edges) {
  const deg = new Map([...nodes.keys()].map(k => [k, 0]));
  for (const [from] of edges) deg.set(from, deg.get(from) + 1);
  return deg;
}

function topologicalSort(nodes, edges) {
  const inDegree = countInDegree(nodes, edges);
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

  return layers;
}

function inferMode(steps, edges, explicitMode) {
  if (explicitMode) return explicitMode;

  const { nodes } = buildDAG(steps);

  if (steps.some(s => s.await === 'human')) return 'approval';
  if (detectCycle(nodes, edges)) return 'event-loop';
  if (steps.some(s => s.loop)) return 'event-loop';

  const layers = topologicalSort(nodes, edges);
  const inDeg = countInDegree(nodes, edges);
  const outDeg = countOutDegree(nodes, edges);

  const startNodes = [...inDeg.entries()].filter(([, d]) => d === 0).length;
  const endNodes = [...outDeg.entries()].filter(([, d]) => d === 0).length;
  const mergeNodes = [...inDeg.entries()].filter(([, d]) => d > 1).length;
  const forkNodes = [...outDeg.entries()].filter(([, d]) => d > 1).length;

  // pipeline: fully serial chain
  if (steps.length === layers.length && steps.length > 1) return 'pipeline';

  // fan-out: single start fans to multiple, or any node has outDegree > 1
  // but only if it's a simple fan structure (no merge + fork mixing)
  if ((startNodes === 1 && forkNodes > 0 && mergeNodes === 0) ||
      (startNodes > 1 && mergeNodes === 0 && forkNodes === 0)) {
    return 'fan-out';
  }

  // map-reduce: multiple sources converge to one point
  if (mergeNodes > 0 && forkNodes === 0) {
    return 'map-reduce';
  }

  // dag: complex graph with mixed patterns
  return 'dag';
}

// ── Test harness ──

let passed = 0, failed = 0;
function assert(label, condition, detail) {
  if (condition) {
    passed++;
    console.log(`✅ ${label}`);
  } else {
    failed++;
    console.log(`❌ ${label}${detail ? ' — ' + detail : ''}`);
  }
}

// ── Retry / Fallback helpers (shared with orchestrator.js) ──

function parseRetry(step) {
  if (!step.retry) return { max: 0, delay: 0 };
  if (typeof step.retry === 'number') return { max: step.retry, delay: 3000 };
  return { max: step.retry.max || 3, delay: step.retry.delay || 5000 };
}

function parseFallback(step) {
  return step.fallback || null;
}

// ── T01: Pipeline ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md" },
    { id: "b", skill: "s2", input: "a.md", output: "b.md" },
    { id: "c", skill: "s3", input: "b.md" },
  ];
  const { nodes, edges } = buildDAG(steps);
  const mode = inferMode(steps, edges);
  const layers = topologicalSort(nodes, edges);

  assert("T01: pipeline — DAG edges", edges.length === 2 && edges[0][1] === "b" && edges[1][1] === "c");
  assert("T01: pipeline — mode", mode === "pipeline", `got ${mode}`);
  assert("T01: pipeline — layers sequential", layers.length === 3 && layers.every(l => l.length === 1));
}

// ── T02: Fan-out ──

{
  const steps = [
    { id: "a", skill: "s1", output: "brief.md" },
    { id: "b", skill: "s2", input: "brief.md" },
    { id: "c", skill: "s3", input: "brief.md" },
    { id: "d", skill: "s4", input: "brief.md" },
  ];
  const { nodes, edges } = buildDAG(steps);
  const mode = inferMode(steps, edges);
  const layers = topologicalSort(nodes, edges);

  assert("T02: fan-out — edges", edges.length === 3, `got ${edges.length}`);
  assert("T02: fan-out — mode", mode === "fan-out", `got ${mode}`);
  assert("T02: fan-out — parallel layer", layers[1].length === 3, `got ${layers[1]?.length}`);
}

// ── T03: Map-reduce ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md" },
    { id: "b", skill: "s2", output: "b.md" },
    { id: "c", skill: "s3", output: "c.md" },
    { id: "d", skill: "s4", input: ["a.md", "b.md", "c.md"] },
  ];
  const { nodes, edges } = buildDAG(steps);
  const mode = inferMode(steps, edges);
  const layers = topologicalSort(nodes, edges);

  assert("T03: map-reduce — edges", edges.length === 3, `got ${edges.length}`);
  assert("T03: map-reduce — mode", mode === "map-reduce", `got ${mode}`);
  assert("T03: map-reduce — merge in layer 2", layers[1].length === 1, `got ${layers[1]?.length}`);
}

// ── T04: Approval ──

{
  const steps = [
    { id: "draft", skill: "s1", output: "draft.md" },
    { id: "review", input: "draft.md", await: "human" },
    { id: "publish", skill: "s3", input: "draft.md" },
  ];
  const { edges } = buildDAG(steps);
  const mode = inferMode(steps, edges);
  const hasApproval = steps.some(s => s.await === "human");

  assert("T04: approval — has await human", hasApproval);
  assert("T04: approval — mode", mode === "approval", `got ${mode}`);
}

// ── T05: Event-loop ──

{
  const steps = [
    { id: "draft", skill: "s1", output: "v1.md" },
    { id: "review", input: "v1.md", output: "v1.md", loop: { max: 5, until: "quality >= 8" } },
  ];
  const { nodes, edges } = buildDAG(steps);
  const hasLoop = steps.some(s => s.loop);
  const mode = inferMode(steps, edges);

  assert("T05: event-loop — has loop config", hasLoop);
  // Self-loop (same file as input+output) is implicit cycle; detected via loop flag
  assert("T05: event-loop — mode", mode === "event-loop", `got ${mode}`);
}

// ── T06: Complex DAG (nested patterns) ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md" },
    { id: "b", skill: "s2", input: "a.md", output: "b.md" },
    { id: "c", skill: "s3", input: "a.md", output: "c.png" },
    { id: "d", skill: "s4", output: "d.md" },
    { id: "e", skill: "s5", input: ["b.md", "c.png"], output: "e.md" },
    { id: "f", skill: "s6", input: ["e.md", "d.md"] },
  ];
  const { nodes, edges } = buildDAG(steps);
  const layers = topologicalSort(nodes, edges);
  const mode = inferMode(steps, edges);

  const expectedLayers = [["a", "d"], ["b", "c"], ["e"], ["f"]];
  const layersMatch = layers.length === 4 &&
    layers[0].sort().join() === expectedLayers[0].sort().join() &&
    layers[1].sort().join() === expectedLayers[1].sort().join() &&
    layers[2].join() === expectedLayers[2].join() &&
    layers[3].join() === expectedLayers[3].join();

  assert("T06: DAG — mode", mode === "dag", `got ${mode}`);
  assert("T06: DAG — topological layers correct", layersMatch,
    `got ${JSON.stringify(layers)}`);
}

// ── T07: Empty steps ──

{
  let error = null;
  try {
    const steps = [];
    const { nodes, edges } = buildDAG(steps);
    const mode = inferMode(steps, edges);
    // Should not crash; mode for empty graph is undefined/edge case
    assert("T07: empty steps — no crash", true);
  } catch (e) {
    assert("T07: empty steps — no crash", false, e.message);
  }
}

// ── T08: Cycle without loop marker ──

{
  const steps = [
    { id: "a", skill: "s1", output: "x.md", input: "z.md" },
    { id: "b", skill: "s2", output: "z.md", input: "x.md" },
  ];
  const { nodes, edges } = buildDAG(steps);
  const cycleDetected = detectCycle(nodes, edges);
  const mode = inferMode(steps, edges);

  assert("T08: cycle detection — detected", cycleDetected);
  assert("T08: cycle detection — mode event-loop", mode === "event-loop", `got ${mode}`);
}

// ── T09: Input references non-existent output ──

{
  let error = null;
  try {
    const steps = [
      { id: "a", skill: "s1", output: "a.md" },
      { id: "b", skill: "s2", input: "nonexistent.md" },
    ];
    const { nodes, edges } = buildDAG(steps);
    // Should not crash; nonexistent input simply doesn't create an edge
    assert("T09: invalid ref — no crash", true);
    assert("T09: invalid ref — no edge created", edges.length === 0, `got ${edges.length}`);
  } catch (e) {
    assert("T09: invalid ref — no crash", false, e.message);
  }
}

// ── T10: Explicit mode override ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md" },
    { id: "b", skill: "s2", input: "a.md" },
    { id: "c", skill: "s3", input: "a.md" },
  ];
  const { edges } = buildDAG(steps);
  const autoMode = inferMode(steps, edges, null);
  const overrideMode = inferMode(steps, edges, "pipeline");

  assert("T10: auto mode is fan-out", autoMode === "fan-out", `got ${autoMode}`);
  assert("T10: explicit override wins", overrideMode === "pipeline", `got ${overrideMode}`);
}

// ── T11: Retry config parsing ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md", retry: { max: 3, delay: 5000 } },
    { id: "b", skill: "s2", input: "a.md", retry: 2 },
    { id: "c", skill: "s3", input: "a.md" },
  ];
  const { nodes, edges } = buildDAG(steps);

  assert("T11: retry — object config", parseRetry(steps[0]).max === 3 && parseRetry(steps[0]).delay === 5000);
  assert("T11: retry — number shorthand", parseRetry(steps[1]).max === 2 && parseRetry(steps[1]).delay === 3000);
  assert("T11: retry — no retry defaults zero", parseRetry(steps[2]).max === 0);
}

// ── T12: Fallback config parsing ──

{
  const steps = [
    { id: "a", skill: "s1", output: "a.md" },
    { id: "b", skill: "s2", input: "a.md", fallback: "deep-research" },
    { id: "c", skill: "s3", input: "a.md" },
  ];

  assert("T12: fallback — has fallback", parseFallback(steps[1]) === "deep-research");
  assert("T12: fallback — no fallback returns null", parseFallback(steps[0]) === null);
  assert("T12: fallback — no fallback returns null (c)", parseFallback(steps[2]) === null);
}

// ── T13: Execution log format ──

{
  const logEntry = {
    timestamp: "2026-04-03T18:55:00Z",
    project: "tech-research-test",
    step: "search",
    status: "success",
    duration: 42000,
    tokens: 8000,
    output: "/tmp/crew-xxx/research.md",
  };
  const validStatuses = ["success", "failed", "retrying", "fallback"];

  assert("T13: log — has required fields",
    logEntry.timestamp && logEntry.project && logEntry.step && logEntry.status && logEntry.duration != null);
  assert("T13: log — valid status", validStatuses.includes(logEntry.status));
  assert("T13: log — duration is number", typeof logEntry.duration === "number" && logEntry.duration > 0);
}

// ── T14: --execute mode command structure ──

{
  const steps = [
    { id: "search", skill: "deep-research", params: { topic: "AI 2026", depth: "quick" }, output: "research.md" },
    { id: "notion", skill: "notion", input: "research.md", params: { pageId: "xxx" }, retry: { max: 3, delay: 5000 }, fallback: "deep-research" },
  ];
  const { nodes, edges } = buildDAG(steps);
  const layers = topologicalSort(nodes, edges);
  const workdir = "/tmp/crew-test";

  // Simulate generateCommands output
  const commands = [];
  for (let i = 0; i < layers.length; i++) {
    for (const id of layers[i]) {
      const step = nodes.get(id);
      const inputs = step.input ? (Array.isArray(step.input) ? step.input : [step.input]) : [];
      const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];
      const paramStr = step.params ? ' ' + Object.entries(step.params).map(([k, v]) => `${k}='${v}'`).join(', ') : '';
      const inputStr = inputs.length > 0 ? `，读取 ${inputs.join(', ')}` : '';
      const outputStr = outputs.length > 0 ? `，输出到 ${outputs.join(', ')}` : '';
      const instruction = `使用 ${step.skill} skill${paramStr}${inputStr}${outputStr}`;
      let validation = null;
      if (outputs.length > 0) validation = `检查 ${outputs.join(', ')} 存在且非空`;
      const cmd = { step: id, layer: i, instruction, skillRef: step.skill, params: step.params || {}, input: inputs.length > 0 ? inputs : null, output: outputs.length > 0 ? outputs : null, validation };
      const retry = parseRetry(step);
      if (retry.max > 0) cmd.retry = retry;
      const fallback = parseFallback(step);
      if (fallback) cmd.fallback = fallback;
      commands.push(cmd);
    }
  }

  assert("T14: execute — has commands array", Array.isArray(commands) && commands.length === 2);
  assert("T14: execute — first command structure",
    commands[0].step === "search" && commands[0].layer === 0 && commands[0].skillRef === "deep-research" && Array.isArray(commands[0].output));
  assert("T14: execute — second command has retry/fallback",
    commands[1].retry && commands[1].retry.max === 3 && commands[1].fallback === "deep-research");
  assert("T14: execute — instruction is human-readable", commands[0].instruction.includes("deep-research") && commands[0].instruction.includes("topic"));
  assert("T14: execute — validation field present for output steps", commands[0].validation !== null);
}

// ── T15: Parameter validation ──

{
  // Test the validation logic inline (same as orchestrator.js parseSkillRegistry + validateParams)
  const mockRegistry = `## deep-research
| field | type | required | desc |
| topic | string | ✅ | topic |
| depth | string | ❌ | depth |
| output | string | ✅ | output path |

## notion
| pageId | string | ✅ | page id |
| title | string | ❌ | title |`;

  function parseReg(content) {
    const skills = {};
    let current = null;
    for (const line of content.split('\n')) {
      const h = line.match(/^## (.+)$/);
      if (h) { current = h[1].trim(); skills[current] = { required: [], optional: [] }; continue; }
      if (!current) continue;
      const m = line.match(/^\| (\w+) \|/);
      if (!m) continue;
      if (line.includes('✅')) skills[current].required.push(m[1]);
      else skills[current].optional.push(m[1]);
    }
    return skills;
  }

  const reg = parseReg(mockRegistry);
  assert("T15: validate — registry parsed", reg["deep-research"] && reg["deep-research"].required.includes("topic"));

  const warnings = [];
  const steps = [
    { id: "s1", skill: "deep-research", params: { depth: "quick" } }, // missing topic, output
    { id: "s2", skill: "deep-research", params: { topic: "AI" } },     // missing output
    { id: "s3", skill: "notion", params: { pageId: "xxx" } },         // all required present
    { id: "s4", skill: "unknown-skill", params: {} },                  // not in registry
  ];
  for (const step of steps) {
    if (!step.skill) continue;
    const def = reg[step.skill];
    if (!def) { warnings.push(`not found: ${step.skill}`); continue; }
    for (const f of def.required) {
      if (!step.params || !(f in step.params)) warnings.push(`missing ${f}`);
    }
  }

  assert("T15: validate — warns on missing required params", warnings.length === 4); // topic, output for s1; output for s2; not found for s4
  assert("T15: validate — warns on unknown skill", warnings.some(w => w.includes("not found")));
  assert("T15: validate — no warning for complete params", !warnings.some(w => w.includes("s3")));
}

// ── T16: Log template ──

{
  const logTemplate = {
    format: "[CREW] {{step}} | {{status}} | {{duration}}ms",
    fields: ["step", "status", "duration"],
    statuses: ["running", "success", "failed", "retrying", "fallback", "skipped"],
    example: "[CREW] search | success | 42000ms",
  };

  assert("T16: log — has format template", typeof logTemplate.format === "string" && logTemplate.format.includes("{{step}}"));
  assert("T16: log — has fields array", Array.isArray(logTemplate.fields) && logTemplate.fields.length === 3);
  assert("T16: log — has valid statuses", logTemplate.statuses.includes("success") && logTemplate.statuses.includes("failed"));
  assert("T16: log — example matches template", logTemplate.example.match(/\[CREW\] \w+ \| \w+ \| \d+ms/));

  // Test template interpolation
  const entry = { step: "notion", status: "retrying", duration: 15000 };
  const logLine = logTemplate.format
    .replace('{{step}}', entry.step)
    .replace('{{status}}', entry.status)
    .replace('{{duration}}', entry.duration);
  assert("T16: log — interpolation works", logLine === "[CREW] notion | retrying | 15000ms");
}

// ── Report ──

console.log(`\n总计: ${passed}/${passed + failed} 通过`);
if (failed > 0) process.exit(1);
