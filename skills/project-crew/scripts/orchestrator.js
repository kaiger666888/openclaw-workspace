#!/usr/bin/env node
// project-crew orchestrator — reads crew.js, builds DAG, outputs execution plan
// Usage: node orchestrator.js [--execute] <crew.js path>

const fs = require('fs');
const path = require('path');

// ── CLI args ──

const args = process.argv.slice(2);
const executeMode = args.includes('--execute');
const crewPath = args.find(a => !a.startsWith('--'));

// ── Parameter Validation ──

function parseSkillRegistry(registryPath) {
  const regDir = path.dirname(registryPath);
  const content = fs.readFileSync(registryPath, 'utf8');
  const skills = {};
  let currentSkill = null;
  for (const line of content.split('\n')) {
    const heading = line.match(/^## (.+)$/);
    if (heading) {
      currentSkill = heading[1].trim();
      skills[currentSkill] = { required: [], optional: [] };
      continue;
    }
    if (!currentSkill) continue;
    const match = line.match(/^\| (\w+) \|/);
    if (!match) continue;
    const field = match[1];
    const isRequired = line.includes('✅');
    if (isRequired) skills[currentSkill].required.push(field);
    else skills[currentSkill].optional.push(field);
  }
  return skills;
}

// Step-level fields that are NOT skill params
const STEP_LEVEL_FIELDS = new Set(['id', 'skill', 'input', 'output', 'mode', 'await', 'loop', 'timeout', 'retry', 'fallback', 'parallel', 'crew', 'workdir', 'awaitPrompt', 'awaitTimeout', 'cronAwait', 'evolve']);

// Skills that default to evolutionary development (user can add others via evolve: true)
const EVOLVE_ELIGIBLE_SKILLS = new Set(['coding-agent', 'deep-research']);

// ── Evolve: evolutionary development ──
// Determine if a step should use evolutionary development.
// Default ON for creative skills that produce output, unless explicitly disabled.
function shouldEvolve(step) {
  // Explicit opt-out
  if (step.evolve === false) return { enabled: false, reason: 'user-disabled' };
  // Explicit opt-in with config
  if (step.evolve && typeof step.evolve === 'object') return { enabled: true, reason: 'user-configured', ...step.evolve };
  // Creative skills with output → default ON
  // But only if the step has no explicit evolve: null (undefined means not set)
  if (step.evolve === undefined && EVOLVE_ELIGIBLE_SKILLS.has(step.skill || '') && step.output) {
    return { enabled: true, reason: 'default (creative skill)', rounds: 1, variants: 2, survive: 1, mutate: '', criteria: '' };
  }
  return null; // no evolve
}

function validateParams(steps, registryPath) {
  const warnings = [];
  try {
    const reg = parseSkillRegistry(registryPath);
    for (const step of steps) {
      if (!step.skill) continue;
      const skillDef = reg[step.skill];
      if (!skillDef) {
        warnings.push(`⚠️  Step "${step.id}": skill "${step.skill}" not found in registry`);
        continue;
      }
      // Check params for required skill fields, but skip step-level fields
      for (const field of skillDef.required) {
        if (STEP_LEVEL_FIELDS.has(field)) continue; // skip step-level fields like 'output'
        if (!step.params || !(field in step.params)) {
          warnings.push(`⚠️  Step "${step.id}": missing required param "${field}" for skill "${step.skill}"`);
        }
      }
    }
  } catch (e) {
    warnings.push(`⚠️  Could not read skill registry: ${e.message}`);
  }
  return warnings;
}

// ── DAG Core ──

function buildDAG(steps) {
  const nodes = new Map();
  const edges = [];
  // outputMap: filename → [stepId, ...] (multiple steps can output same file in loops)
  const outputMap = new Map();

  for (const step of steps) {
    nodes.set(step.id, step);
    if (step.output) {
      const outputs = Array.isArray(step.output) ? step.output : [step.output];
      for (const f of outputs) {
        if (!outputMap.has(f)) outputMap.set(f, []);
        outputMap.get(f).push(step.id);
      }
    }
  }

  for (const step of steps) {
    if (!step.input) continue;
    const inputs = Array.isArray(step.input) ? step.input : [step.input];
    for (const f of inputs) {
      const producers = outputMap.get(f);
      if (!producers) continue;
      for (const from of producers) {
        // Skip self-loop edges (handled by loop logic)
        if (from === step.id) continue;
        // Avoid duplicate edges
        if (!edges.some(([a, b]) => a === from && b === step.id)) {
          edges.push([from, step.id]);
        }
      }
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
  return layers;
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

function inferMode(steps, edges, explicitMode) {
  if (explicitMode) return [explicitMode];
  const { nodes } = buildDAG(steps);
  const tags = [];

  // Structural tags
  if (detectCycle(nodes, edges)) tags.push('event-loop');
  else if (steps.some(s => s.loop)) tags.push('event-loop');

  const layers = topologicalSort(nodes, edges);
  const inDeg = countInDegree(nodes, edges);
  const outDeg = countOutDegree(nodes, edges);
  const startNodes = [...inDeg.entries()].filter(([, d]) => d === 0).length;
  const mergeNodes = [...inDeg.entries()].filter(([, d]) => d > 1).length;
  const forkNodes = [...outDeg.entries()].filter(([, d]) => d > 1).length;

  if (steps.length === layers.length && steps.length > 1) tags.push('pipeline');
  else if ((startNodes === 1 && forkNodes > 0 && mergeNodes === 0) ||
           (startNodes > 1 && mergeNodes === 0 && forkNodes === 0)) tags.push('fan-out');
  else if (mergeNodes > 0 && forkNodes === 0) tags.push('map-reduce');
  else tags.push('dag');

  // Feature tags
  if (steps.some(s => s.await === 'human')) tags.push('approval');
  if (steps.some(s => s.crew)) tags.push('nested');

  return tags;
}

// ── Retry / Fallback / Log ──

function parseRetry(step) {
  if (!step.retry) return { max: 0, delay: 0 };
  if (typeof step.retry === 'number') return { max: step.retry, delay: 3000 };
  return { max: step.retry.max || 3, delay: step.retry.delay || 5000 };
}

function parseFallback(step) {
  return step.fallback || null;
}

// ── Execution Plan Generator ──

function generatePlan(crewPath) {
  const crewDef = require(path.resolve(crewPath));
  const steps = crewDef.steps || [];
  if (!steps.length) {
    return { project: crewDef.name, error: "No steps defined" };
  }

  const { nodes, edges } = buildDAG(steps);
  const mode = inferMode(steps, edges, crewDef.mode);
  const layers = topologicalSort(nodes, edges);

  // Build dependency map
  const deps = {};
  for (const step of steps) deps[step.id] = [];
  for (const [from, to] of edges) deps[to].push(from);

  // Build execution plan
  const executionPlan = layers.map((layer, i) => ({
    layer: i,
    steps: layer.map(id => {
      const step = nodes.get(id);
      const stepInfo = { id };
      if (step.skill) stepInfo.skill = step.skill;
      if (step.await) stepInfo.await = step.await;
      const retry = parseRetry(step);
      if (retry.max > 0) stepInfo.retry = retry;
      const fallback = parseFallback(step);
      if (fallback) stepInfo.fallback = fallback;
      return stepInfo;
    }),
    mode: i === 0 ? 'start' : (Array.isArray(mode) ? mode.join('+') : mode),
  }));

  // Build step configs for each step (retry, fallback)
  const stepConfigs = {};
  for (const step of steps) {
    const retry = parseRetry(step);
    const fallback = parseFallback(step);
    if (retry.max > 0 || fallback) {
      stepConfigs[step.id] = {};
      if (retry.max > 0) stepConfigs[step.id].retry = retry;
      if (fallback) stepConfigs[step.id].fallback = fallback;
    }
  }

  return {
    project: crewDef.name,
    workdir: crewDef.workdir || `/tmp/crew-${crewDef.name}`,
    inferredMode: Array.isArray(mode) ? mode : [mode],
    executionPlan,
    dependencies: deps,
    stepConfigs: Object.keys(stepConfigs).length > 0 ? stepConfigs : undefined,
    logFormat: {
      description: "Per-step execution log entry",
      schema: {
        timestamp: "ISO8601",
        project: "string",
        step: "string",
        status: "success|failed|retrying|fallback",
        duration: "ms",
        tokens: "number (estimated)",
        output: "string (file path or null)",
      },
    },
  };
}

// ── Nested DAG Support ──

function resolveNestedCrew(crewPath) {
  const crewDef = require(path.resolve(crewPath));
  const steps = [];
  const nestedWarnings = [];

  for (const step of (crewDef.steps || [])) {
    if (step.crew) {
      // Nested DAG: load child crew and prefix all step ids
      const childCrewPath = path.resolve(path.dirname(crewPath), step.crew);
      try {
        const childDef = require(childCrewPath);
        const childSteps = childDef.steps || [];
        if (!childSteps.length) {
          nestedWarnings.push(`⚠️  Nested crew "${step.crew}" has no steps, skipping`);
          continue;
        }
        const prefix = step.id + '.';
        const inputMapping = step.input ? (Array.isArray(step.input) ? step.input : [step.input]) : [];
        const childWorkdir = step.workdir || (crewDef.workdir || `/tmp/crew-${crewDef.name}`) + '/' + step.id;

        for (const cs of childSteps) {
          const nestedStep = { ...cs, id: prefix + cs.id };
          // Map external inputs to child's first steps
          if (inputMapping.length > 0 && !cs.input) {
            nestedStep.input = inputMapping;
          }
          // Map child outputs back through parent output
          if (step.output && cs.output === childSteps[childSteps.length - 1]?.output) {
            nestedStep.output = step.output;
          }
          nestedStep._nestedWorkdir = childWorkdir;
          nestedStep._parentId = step.id;
          steps.push(nestedStep);
        }
        nestedWarnings.push(`📦 Expanded nested crew "${step.crew}" → ${childSteps.length} steps (prefix: ${prefix})`);
      } catch (e) {
        nestedWarnings.push(`⚠️  Failed to load nested crew "${step.crew}": ${e.message}`);
        // Fallback: keep as-is
        steps.push(step);
      }
    } else {
      steps.push(step);
    }
  }

  return { ...crewDef, steps, _nestedWarnings: nestedWarnings };
}

// ── Loop Analysis ──

function analyzeLoops(steps) {
  const loopSteps = [];
  for (const step of steps) {
    if (!step.loop) continue;
    const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];
    const inputs = step.input ? (Array.isArray(step.input) ? step.input : [step.input]) : [];
    // Detect self-loop: output file == input file
    const selfLoop = outputs.some(o => inputs.includes(o));
    loopSteps.push({
      id: step.id,
      max: step.loop.max || 5,
      until: step.loop.until || 'quality acceptable',
      selfLoop,
      condition: step.loop.condition || null, // JS expression for programmatic check
    });
  }
  return loopSteps;
}

// ── Approval Gate Analysis ──

function analyzeApprovals(steps) {
  return steps
    .filter(s => s.await === 'human')
    .map(s => ({
      id: s.id,
      cronAwait: s.cronAwait || false,
      prompt: s.awaitPrompt || `审批请求：step "${s.id}" 已完成前置任务，是否继续？`,
      timeout: s.awaitTimeout || null, // minutes, null = no timeout
      inputs: s.input ? (Array.isArray(s.input) ? s.input : [s.input]) : [],
    }));
}

// ── Execute Mode: Generate structured commands ──

function generateCommands(crewPath) {
  // Resolve nested DAGs first
  const resolved = resolveNestedCrew(crewPath);
  const steps = resolved.steps || [];
  if (!steps.length) {
    return { project: resolved.name, error: "No steps defined" };
  }

  const { nodes, edges } = buildDAG(steps);
  const layers = topologicalSort(nodes, edges);
  const mode = inferMode(steps, edges, resolved.mode);
  const workdir = resolved.workdir || `/tmp/crew-${resolved.name}`;

  // Advanced analysis
  const loopAnalysis = analyzeLoops(steps);
  const approvalAnalysis = analyzeApprovals(steps);

  // Parameter validation
  const registryPath = path.resolve(__dirname, '..', 'references', 'skill-registry.md');
  const warnings = validateParams(steps, registryPath);
  if (resolved._nestedWarnings) warnings.push(...resolved._nestedWarnings);

  // Approval gate: steps with await:"human" must block subsequent steps in same layer
  // Re-layer: if a step with await:"human" is in layer N, move all other steps in that
  // layer (that don't have await) to layer N+1, adding dependency on the approval step
  const approvalStepIds = new Set(steps.filter(s => s.await === 'human').map(s => s.id));
  if (approvalStepIds.size > 0) {
    const newLayers = [];
    for (const layer of layers) {
      const approvalInLayer = layer.filter(id => approvalStepIds.has(id));
      const otherInLayer = layer.filter(id => !approvalStepIds.has(id));
      if (approvalInLayer.length > 0 && otherInLayer.length > 0) {
        // Approval steps go in current layer, others deferred
        newLayers.push(approvalInLayer);
        // Add synthetic edges: other steps depend on approval steps
        for (const apId of approvalInLayer) {
          for (const oId of otherInLayer) {
            if (!edges.some(([a, b]) => a === apId && b === oId)) {
              edges.push([apId, oId]);
            }
          }
        }
        newLayers.push(otherInLayer);
      } else {
        newLayers.push(layer);
      }
    }
    // Re-topological-sort after adding edges
    const reLayers = topologicalSort(nodes, edges);
    layers.length = 0;
    layers.push(...reLayers);
  }

  const commands = [];
  for (let i = 0; i < layers.length; i++) {
    for (const id of layers[i]) {
      const step = nodes.get(id);
      const inputs = step.input ? (Array.isArray(step.input) ? step.input : [step.input]) : [];
      const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];

      // Build human-readable instruction
      const paramStr = step.params ? ' ' + Object.entries(step.params).map(([k, v]) => `${k}='${v}'`).join(', ') : '';
      const inputStr = inputs.length > 0 ? `，读取 ${inputs.join(', ')}` : '';
      const outputStr = outputs.length > 0 ? `，输出到 ${outputs.join(', ')}` : '';
      const instruction = step.crew
        ? `展开嵌套 DAG: ${step.crew}${paramStr}${inputStr}${outputStr}`
        : step.skill
        ? `使用 ${step.skill} skill${paramStr}${inputStr}${outputStr}`
        : `${inputStr ? '读取 ' + inputs.join(', ') + '，' : ''}执行 ${id}${paramStr}${outputStr}`;

      // Build validation hint
      let validation = null;
      if (outputs.length > 0) {
        validation = `检查 ${outputs.join(', ')} 存在且非空`;
      } else if (step.await === 'human') {
        validation = '等待人工确认后继续';
      }

      const cmd = {
        step: id,
        layer: i,
        instruction,
        skillRef: step.skill || null,
        params: step.params || {},
        input: inputs.length > 0 ? inputs : null,
        output: outputs.length > 0 ? outputs : null,
        validation,
      };

      const retry = parseRetry(step);
      if (retry.max > 0) cmd.retry = retry;
      const fallback = parseFallback(step);
      if (fallback) cmd.fallback = fallback;

      // Approval gate metadata
      if (step.await) {
        const approval = approvalAnalysis.find(a => a.id === id);
        // reviewFiles: the step's own output (what was just produced) + any inputs for context
        const reviewFiles = [...outputs];
        for (const inp of approval?.inputs || []) {
          if (!reviewFiles.includes(inp)) reviewFiles.push(inp);
        }
        cmd.await = {
          type: 'human',
          prompt: approval?.prompt,
          cronSkip: !approval?.cronAwait,
          timeout: approval?.timeout,
          reviewFiles,
        };
      }

      // Event loop metadata
      const loopInfo = loopAnalysis.find(l => l.id === id);
      if (loopInfo) {
        cmd.loop = {
          max: loopInfo.max,
          until: loopInfo.until,
          selfLoop: loopInfo.selfLoop,
          condition: loopInfo.condition,
        };
        // For self-loop, update instruction to mention loop
        if (loopInfo.selfLoop) {
          cmd.instruction += `（循环执行，最多 ${loopInfo.max} 次，直到: ${loopInfo.until}）`;
        }
      }

      // ── Evolve: evolutionary development ──
      const evolveResult = shouldEvolve(step);
      if (evolveResult && evolveResult.enabled) {
        cmd.evolve = {
          enabled: true,
          rounds: evolveResult.rounds || 1,
          variants: evolveResult.variants || 2,
          survive: evolveResult.survive || 1,
          mutate: evolveResult.mutate || '',
          criteria: evolveResult.criteria || '',
          reason: evolveResult.reason || 'default',
        };
      } else if (evolveResult && !evolveResult.enabled) {
        cmd.evolve = { enabled: false, reason: evolveResult.reason };
      }

      if (step.timeout) cmd.timeout = step.timeout;
      if (step._nestedWorkdir) cmd.nestedWorkdir = step._nestedWorkdir;
      if (step._parentId) cmd.parentStep = step._parentId;

      commands.push(cmd);
    }
  }

  return {
    project: resolved.name,
    workdir,
    inferredMode: Array.isArray(mode) ? mode : [mode],
    totalSteps: commands.length,
    totalLayers: layers.length,
    commands,
    warnings: warnings.length > 0 ? warnings : undefined,
    // Layer-level parallel limits
    layerLimits: layers.map(layer => {
      const minParallel = Math.min(...layer.map(id => {
        const step = nodes.get(id);
        return step.parallel || Infinity;
      }));
      return { layer: null, steps: layer, maxParallel: minParallel === Infinity ? null : minParallel };
    }).map((l, i) => ({ ...l, layer: i })),
    // Advanced features summary
    features: {
      hasApproval: approvalAnalysis.length > 0,
      hasLoop: loopAnalysis.length > 0,
      hasNested: steps.some(s => s._parentId),
      hasEvolve: commands.some(c => c.evolve?.enabled),
      approvalGates: approvalAnalysis.length > 0 ? approvalAnalysis : undefined,
      loopSteps: loopAnalysis.length > 0 ? loopAnalysis : undefined,
      evolveSteps: commands.filter(c => c.evolve?.enabled).map(c => ({
        step: c.step,
        skill: c.skillRef,
        variants: c.evolve.variants,
        rounds: c.evolve.rounds,
        reason: c.evolve.reason,
      })),
    },
    logTemplate: {
      format: "[CREW] {{step}} | {{status}} | {{duration}}ms",
      fields: ["step", "status", "duration"],
      statuses: ["running", "success", "failed", "retrying", "fallback", "skipped", "awaiting_approval", "loop_iteration", "evolve_round"],
      example: "[CREW] search | success | 42000ms",
    },
  };
}

// ── CLI ──

if (!crewPath) {
  console.error("Usage: node orchestrator.js [--execute] <crew.js path>");
  process.exit(1);
}

try {
  if (executeMode) {
    const result = generateCommands(crewPath);
    console.log(JSON.stringify(result, null, 2));
  } else {
    const plan = generatePlan(crewPath);
    console.log(JSON.stringify(plan, null, 2));
  }
} catch (e) {
  console.error(`Error: ${e.message}`);
  process.exit(1);
}
