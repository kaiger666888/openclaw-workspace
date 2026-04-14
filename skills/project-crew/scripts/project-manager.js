#!/usr/bin/env node
// project-crew project manager — bootstrap repos, manage git worktrees, checkpoint/resume
// Usage:
//   node project-manager.js --bootstrap <crew.js>    Create repo with .gitignore, LFS, structure
//   node project-manager.js --worktrees <crew.js>    Create parallel worktrees
//   node project-manager.js --checkpoint <crew.js>   Commit current state as checkpoint
//   node project-manager.js --status <crew.js>       Show project status
//   node project-manager.js --rollback <crew.js> --to <commit>  Rollback to commit
//   node project-manager.js --evolve <crew.js>       Compare worktrees, keep best
//   node project-manager.js --merge <crew.js>        Merge best worktree to main

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);
// crewPath is declared below (after command parsing, for --template support)

function getCrewDef(p) {
  return require(path.resolve(p));
}

function getProjectRoot(crewDef) {
  return crewDef.workdir || crewDef.repoPath || `/tmp/crew-${crewDef.name}`;
}

function run(cmd, cwd, { silent = false } = {}) {
  try {
    return execSync(cmd, { cwd, encoding: 'utf8', timeout: 30000, stdio: ['pipe','pipe','pipe'] }).trim();
  } catch (e) {
    return null;
  }
}

// ── .gitignore Templates ──

const GITIGNORE_TEMPLATES = {
  node: `node_modules/
dist/
.env
.env.local
*.log
.DS_Store
coverage/
.nyc_output/
.cache/
.parcel-cache/
.vercel/
.netlify/`,

  python: `__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/
*.egg
.env
.venv/
venv/
.ipynb_checkpoints/
.mypy_cache/
.ruff_cache/`,

  rust: `/target/
**/*.rs.bk
Cargo.lock
*.swp
*.swo
*~
.env`,

  go: `/vendor/
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
.env
go.work.sum`,

  general: `.DS_Store
Thumbs.db
*.log
.env
.env.local
tmp/
*.tmp
*.bak
*.swp
*.swo
*~`
};

// ── Project Templates ──

const PROJECT_TEMPLATES = {
  'node-lib': {
    name: 'Node.js Library',
    lang: 'node',
    steps: [
      { id: 'research', skill: 'deep-research', params: { topic: 'REPLACE_TOPIC', depth: 'medium' }, output: 'docs/research.md' },
      { id: 'design', skill: 'general', input: 'docs/research.md', output: 'docs/design.md' },
      { id: 'implement', skill: 'coding-agent', input: 'docs/design.md', output: 'src/index.js' },
      { id: 'test', skill: 'coding-agent', input: 'src/index.js', output: 'test-results.md', loop: { max: 3, until: '所有测试通过' } },
      { id: 'docs', skill: 'general', input: ['docs/design.md', 'test-results.md'], output: 'docs/api.md' },
    ],
    files: {
      'src/package.json': JSON.stringify({ name: '', version: '0.1.0', type: 'module', main: 'src/index.js', scripts: { test: 'node --test', lint: 'eslint src/', build: 'esbuild src/index.js --bundle --outfile=dist/index.js --format=esm' } }, null, 2),
      '.env.example': '# API keys\n# API_KEY=your_key_here\n',
    },
  },
  'python-api': {
    name: 'Python API Service',
    lang: 'python',
    steps: [
      { id: 'research', skill: 'deep-research', params: { topic: 'REPLACE_TOPIC', depth: 'medium' }, output: 'docs/research.md' },
      { id: 'implement', skill: 'coding-agent', input: 'docs/research.md', output: 'app/main.py' },
      { id: 'test', skill: 'coding-agent', input: 'app/main.py', output: 'test-results.md', loop: { max: 3, until: '所有测试通过' } },
      { id: 'docs', skill: 'general', input: ['docs/research.md', 'test-results.md'], output: 'docs/api.md' },
    ],
    files: {
      'requirements.txt': 'fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0\n',
      'Dockerfile': 'FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n',
      '.env.example': '# Database\n# DATABASE_URL=postgresql://...\n# API_KEY=your_key\n',
    },
  },
  'fullstack': {
    name: 'Full-Stack Web App',
    lang: 'node',
    steps: [
      { id: 'research', skill: 'deep-research', params: { topic: 'REPLACE_TOPIC', depth: 'medium' }, output: 'docs/research.md' },
      { id: 'design', skill: 'general', input: 'docs/research.md', output: 'docs/design.md' },
      { id: 'frontend', skill: 'coding-agent', input: 'docs/design.md', output: 'src/app/index.html' },
      { id: 'backend', skill: 'coding-agent', input: 'docs/design.md', output: 'src/api/server.js' },
      { id: 'test', skill: 'coding-agent', input: ['src/app/index.html', 'src/api/server.js'], output: 'test-results.md', loop: { max: 3, until: '测试通过' } },
      { id: 'docs', skill: 'general', input: ['docs/design.md', 'test-results.md'], output: 'docs/guide.md' },
    ],
    files: {
      'src/package.json': JSON.stringify({ name: '', version: '0.1.0', type: 'module', scripts: { dev: 'node src/api/server.js', build: 'esbuild src/app/index.html --bundle --outfile=dist/index.html', test: 'node --test' } }, null, 2),
      'docker-compose.yml': 'services:\n  app:\n    build: .\n    ports:\n      - "3000:3000"\n    env_file: .env\n  db:\n    image: postgres:16-alpine\n    environment:\n      POSTGRES_DB: app\n      POSTGRES_PASSWORD: dev\n    ports:\n      - "5432:5432"\n',
      '.env.example': '# App\n# PORT=3000\n# DATABASE_URL=postgresql://app:dev@localhost:5432/app\n',
    },
  },
  'cli-tool': {
    name: 'CLI Tool',
    lang: 'node',
    steps: [
      { id: 'research', skill: 'deep-research', params: { topic: 'REPLACE_TOPIC', depth: 'quick' }, output: 'docs/research.md' },
      { id: 'implement', skill: 'coding-agent', input: 'docs/research.md', output: 'src/cli.js' },
      { id: 'test', skill: 'coding-agent', input: 'src/cli.js', output: 'test-results.md', loop: { max: 3, until: '测试通过' } },
      { id: 'docs', skill: 'general', input: ['docs/research.md', 'test-results.md'], output: 'docs/usage.md' },
    ],
    files: {
      'src/package.json': JSON.stringify({ name: '', version: '0.1.0', type: 'module', bin: { cli: 'src/cli.js' }, scripts: { start: 'node src/cli.js', test: 'node --test' } }, null, 2),
      '.env.example': '# Config\n# CONFIG_PATH=./config.json\n',
    },
  },
  'rust-lib': {
    name: 'Rust Library',
    lang: 'rust',
    steps: [
      { id: 'research', skill: 'deep-research', params: { topic: 'REPLACE_TOPIC', depth: 'medium' }, output: 'docs/research.md' },
      { id: 'implement', skill: 'coding-agent', input: 'docs/research.md', output: 'src/lib.rs' },
      { id: 'test', skill: 'coding-agent', input: 'src/lib.rs', output: 'test-results.md', loop: { max: 3, until: 'cargo test 通过' } },
      { id: 'docs', skill: 'general', input: ['docs/research.md', 'test-results.md'], output: 'docs/api.md' },
    ],
    files: {
      'Cargo.toml': '[package]\nname = ""\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n\n[dev-dependencies]\n',
    },
  },
};

// ── LFS Patterns ──

const LFS_PATTERNS = {
  'ml-model': ['*.onnx', '*.gguf', '*.safetensors', '*.bin', '*.pt', '*.pth'],
  'media': ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.mp4', '*.mp3', '*.wav', '*.webp'],
  'dataset': ['*.csv', '*.parquet', '*.arrow', '*.feather', '*.jsonl'],
  'binary': ['*.wasm', '*.so', '*.dylib', '*.dll'],
};

// ── Project Bootstrap ──

function bootstrap(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const project = typeof crewDef.project === 'object' ? crewDef.name : (crewDef.project || crewDef.name);

  if (!fs.existsSync(root)) fs.mkdirSync(root, { recursive: true });

  // Init git repo
  if (!fs.existsSync(path.join(root, '.git'))) {
    run('git init', root);
    run('git checkout -b main', root);
  }

  // Detect language from project definition
  const lang = detectLanguage(crewDef);
  const gitignore = GITIGNORE_TEMPLATES[lang] || GITIGNORE_TEMPLATES.general;
  fs.writeFileSync(path.join(root, '.gitignore'), gitignore);

  // LFS setup
  const lfs = crewDef.lfs || [];
  if (lfs.length > 0) {
    run('git lfs install', root);
    for (const pattern of lfs) {
      run(`git lfs track "${pattern}"`, root);
    }
    // Add .gitattributes
    const attrs = lfs.map(p => `${p} filter=lfs diff=lfs merge=lfs -text`).join('\n');
    fs.appendFileSync(path.join(root, '.gitattributes'), attrs + '\n');
  }

  // README
  const readme = `# ${project}

> Generated by project-crew

## Project Goal
${crewDef.goal || 'N/A'}

## Structure
${describeStructure(crewDef)}

## Worktrees
\`\`\`
git worktree list
\`\`\`

## Checkpoints
Each development step creates a git checkpoint. Use:
- \`git log --oneline\` to view checkpoints
- \`git checkout <commit>\` to rollback
\`\`\`
`;
  fs.writeFileSync(path.join(root, 'README.md'), readme);

  // Create directory structure from steps
  createProjectStructure(crewDef, root);

  // Create template files if any
  const templateFiles = crewDef.files || {};
  for (const [filePath, content] of Object.entries(templateFiles)) {
    const fullPath = path.join(root, filePath);
    fs.mkdirSync(path.dirname(fullPath), { recursive: true });
    fs.writeFileSync(fullPath, content);
  }

  // Initial commit
  run('git add -A', root);
  run('git commit -m "init: project bootstrap by project-crew"', root) ||
    console.log('(No changes to commit)');

  // Branch: dev
  const devExists = run('git rev-parse --verify dev', root);
  if (!devExists) run('git checkout -b dev', root);
  else run('git checkout dev', root);

  // ── GitHub Remote Integration ──
  let github = null;
  const githubConfig = crewDef.github || crewDef.project?.github;
  if (githubConfig) {
    const repoName = typeof githubConfig === 'string' ? githubConfig : crewDef.name;
    const isPrivate = githubConfig.private !== false;
    const description = crewDef.goal || `Project: ${crewDef.name}`;

    // Check gh auth
    const ghAuth = run('gh auth status 2>&1', root);
    if (ghAuth && !ghAuth.includes('not logged in')) {
      // Create repo
      const visibility = isPrivate ? '--private' : '--public';
      const repoUrl = run(`gh repo create ${repoName} ${visibility} --description "${description}" --source=. --push 2>&1`, root);
      github = { repo: repoName, private: isPrivate, created: !!repoUrl };

      // Push dev branch
      run('git push -u origin dev', root);
      github.pushed = true;
    } else {
      github = { error: 'gh CLI not authenticated. Run `gh auth login` first.' };
    }
  }

  return {
    project,
    root,
    lang,
    lfs: lfs.length > 0,
    gitInitialized: true,
    branch: 'dev',
    structure: describeStructure(crewDef),
    github,
  };
}

function detectLanguage(crewDef) {
  const allSteps = crewDef.steps || [];
  for (const step of allSteps) {
    const s = JSON.stringify(step).toLowerCase();
    if (s.includes('node') || s.includes('npm') || s.includes('typescript')) return 'node';
    if (s.includes('python') || s.includes('pip') || s.includes('pytorch')) return 'python';
    if (s.includes('rust') || s.includes('cargo')) return 'rust';
    if (s.includes('go') || s.includes('golang')) return 'go';
  }
  // Check project.lang hint
  if (crewDef.project?.lang) return crewDef.project.lang;
  return 'general';
}

function describeStructure(crewDef) {
  const lines = [];
  for (const step of (crewDef.steps || [])) {
    const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];
    for (const f of outputs) {
      const dir = path.dirname(f);
      if (dir && dir !== '.') lines.push(`- \`${dir}/\` — ${step.id} output`);
    }
  }
  return lines.join('\n') || '- (flat structure, all files in root)';
}

function createProjectStructure(crewDef, root) {
  for (const step of (crewDef.steps || [])) {
    const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];
    for (const f of outputs) {
      const dir = path.dirname(f);
      if (dir && dir !== '.' && !fs.existsSync(path.join(root, dir))) {
        fs.mkdirSync(path.join(root, dir), { recursive: true });
      }
    }
  }
}

// ── Git Worktree Parallel Development ──

function createWorktrees(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const count = crewDef.worktrees || 2;
  const strategy = crewDef.evolveStrategy || 'best-output';

  // Ensure we're on main and it has at least one commit
  run('git checkout main', root);

  const worktrees = [];
  for (let i = 0; i < count; i++) {
    const branchName = `wt-${String(i + 1).padStart(2, '0')}`;
    const wtPath = path.resolve(root, `../${crewDef.name}-wt${i + 1}`);

    // Clean up if exists
    if (fs.existsSync(wtPath)) fs.rmSync(wtPath, { recursive: true });

    // Create branch from current HEAD
    run(`git branch ${branchName} 2>/dev/null || true`, root);

    // Create worktree
    const wtResult = run(`git worktree add "${wtPath}" "${branchName}" 2>&1`, root);
    if (!wtResult || wtResult.includes('fatal')) {
      // Branch might already exist, try force
      run(`git worktree add -f "${wtPath}" "${branchName}" 2>&1`, root);
    }

    // Copy crew.js to worktree
    fs.mkdirSync(wtPath, { recursive: true });
    fs.copyFileSync(path.resolve(crewPath), path.join(wtPath, 'crew.js'));

    worktrees.push({
      id: i + 1,
      branch: branchName,
      path: wtPath,
      status: 'ready',
    });
  }

  // Save worktree metadata
  const meta = {
    project: crewDef.name,
    count,
    strategy,
    worktrees,
    createdAt: new Date().toISOString(),
  };
  fs.writeFileSync(path.join(root, '.crew-meta.json'), JSON.stringify(meta, null, 2));

  return {
    count,
    strategy,
    worktrees,
    instruction: `Parallel development initialized. Each worktree has its own branch. Execute the crew DAG independently in each worktree, then run --evolve to compare.`,
  };
}

// ── Checkpoint ──

function checkpoint(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const stepId = args[args.indexOf('--step') + 1] || 'manual';
  const msg = args[args.indexOf('--message') + 1] || `checkpoint: ${stepId} completed`;

  run('git add -A', root);
  const commitOutput = run(`git commit -m "${msg}"`, root);
  const hash = commitOutput ? commitOutput.match(/\[.+\s([a-f0-9]+)\]/)?.[1] : null;

  return {
    step: stepId,
    commit: hash || commitOutput,
    message: msg,
    timestamp: new Date().toISOString(),
  };
}

// ── Status ──

function status(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);

  const currentBranch = run('git branch --show-current', root) || 'unknown';
  const log = run('git log --oneline -20', root) || '(no commits)';
  const worktrees = run('git worktree list', root) || '(no worktrees)';

  let meta = null;
  const metaPath = path.join(root, '.crew-meta.json');
  if (fs.existsSync(metaPath)) {
    meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  }

  return {
    project: crewDef.name,
    root,
    branch: currentBranch,
    recentCheckpoints: log.split('\n').filter(Boolean),
    worktrees: worktrees.split('\n').filter(Boolean),
    parallelConfig: meta,
  };
}

// ── Rollback ──

function rollback(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const targetCommit = args[args.indexOf('--to') + 1];

  if (!targetCommit || targetCommit.startsWith('--')) {
    return { error: 'Missing --to <commit>. Use --status to see available checkpoints.' };
  }

  // Check if commit exists
  const valid = run(`git cat-file -t ${targetCommit}`, root);
  if (!valid) {
    return { error: `Commit "${targetCommit}" not found in this repository. Use --status to see available checkpoints.` };
  }

  // Create recovery branch before rollback
  const recoveryBranch = `recovery-${Date.now()}`;
  run(`git branch ${recoveryBranch}`, root);

  // Reset to target
  run(`git reset --hard ${targetCommit}`, root);

  return {
    rollbackTo: targetCommit,
    recoveryBranch,
    message: `Rolled back to ${targetCommit}. Recovery branch: ${recoveryBranch}`,
    instruction: `To resume from this point, execute the crew DAG starting from the current state.`,
  };
}

// ── Evolve (Compare & Select Best) ──

function evolve(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const metaPath = path.join(root, '.crew-meta.json');

  if (!fs.existsSync(metaPath)) {
    return { error: 'No parallel worktree config found. Run --worktrees first.' };
  }

  const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  const results = [];

  for (const wt of meta.worktrees) {
    const wtPath = wt.path;
    if (!fs.existsSync(wtPath)) {
      results.push({ id: wt.id, branch: wt.branch, status: 'missing' });
      continue;
    }

    // Evaluate worktree: count commits, check output files
    const commitCount = (run('git log --oneline', wtPath) || '').split('\n').filter(Boolean).length;
    const lastCommit = run('git log --oneline -1', wtPath) || '(none)';
    const outputFiles = evaluateOutputs(crewDef, wtPath);
    const score = outputFiles.totalScore;

    results.push({
      id: wt.id,
      branch: wt.branch,
      path: wtPath,
      commits: commitCount,
      lastCommit,
      outputs: outputFiles,
      score,
    });
  }

  // Rank by score
  results.sort((a, b) => (b.score || 0) - (a.score || 0));

  // Mark survivors and pruned
  const survivors = [];
  const pruned = [];
  for (let i = 0; i < results.length; i++) {
    if (i === 0 || (results[i].score || 0) >= (results[0].score || 0) * 0.8) {
      results[i].decision = 'survive';
      survivors.push(results[i]);
    } else {
      results[i].decision = 'prune';
      pruned.push(results[i]);
    }
  }

  return {
    strategy: meta.strategy,
    results,
    best: results[0],
    survivors,
    pruned,
    instruction: pruned.length > 0
      ? `Best worktree: ${results[0].branch} (score: ${results[0].score}). Pruned ${pruned.length} underperformer(s). To merge best: run --merge`
      : `All worktrees performing well. Best: ${results[0].branch}`,
  };
}

function evaluateOutputs(crewDef, wtPath) {
  const checks = [];
  let totalScore = 0;
  let maxScore = 0;

  for (const step of (crewDef.steps || [])) {
    const outputs = step.output ? (Array.isArray(step.output) ? step.output : [step.output]) : [];
    for (const f of outputs) {
      maxScore += 10;
      const filePath = path.join(wtPath, f);
      if (!fs.existsSync(filePath)) {
        checks.push({ file: f, exists: false, score: 0 });
        continue;
      }
      const stat = fs.statSync(filePath);
      const size = stat.size;
      let score = 5; // exists = 5 points
      if (size > 100) score = 7;
      if (size > 500) score = 8;
      if (size > 2000) score = 9;
      if (size > 5000) score = 10;
      totalScore += score;
      checks.push({ file: f, exists: true, size, score });
    }
  }

  return { checks, totalScore, maxScore };
}

// ── Merge Best ──

function mergeBest(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const metaPath = path.join(root, '.crew-meta.json');

  if (!fs.existsSync(metaPath)) {
    return { error: 'No parallel worktree config found.' };
  }

  // Run evolve to find best
  const evolveResult = evolve(crewPath);
  if (!evolveResult.best) {
    return { error: 'No worktrees to merge.' };
  }

  const best = evolveResult.best;
  run('git checkout main', root);

  // Merge best branch into main
  const mergeResult = run(`git merge ${best.branch} --no-edit`, root);

  return {
    mergedFrom: best.branch,
    score: best.score,
    mergeResult: mergeResult || 'already up to date',
    message: `Merged best worktree (${best.branch}) into main.`,
  };
}

// ── Cleanup ──

function cleanup(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const metaPath = path.join(root, '.crew-meta.json');

  const removed = [];

  // Remove pruned worktrees if metadata exists
  if (fs.existsSync(metaPath)) {
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));

    // Run evolve to get current pruned list
    const evolveResult = evolve(crewPath);
    if (evolveResult.pruned) {
      for (const wt of evolveResult.pruned) {
        if (wt.path && fs.existsSync(wt.path)) {
          fs.rmSync(wt.path, { recursive: true, force: true });
          removed.push({ branch: wt.branch, path: wt.path, reason: 'pruned' });
        }
        // Remove git worktree tracking
        run(`git worktree remove "${wt.path}" --force 2>/dev/null`, root);
        // Delete branch
        run(`git branch -D ${wt.branch} 2>/dev/null`, root);
      }
    }

    // Update metadata to only include survivors
    meta.worktrees = evolveResult.survivors || meta.worktrees;
    meta.lastCleanup = new Date().toISOString();
    fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
  }

  // Clean orphan worktree references
  const wtList = run('git worktree list --porcelain', root) || '';
  const wtDirs = [];
  for (const line of wtList.split('\n')) {
    if (line.startsWith('worktree ')) wtDirs.push(line.slice(9));
  }
  for (const wtDir of wtDirs) {
    if (wtDir === root) continue; // skip main repo
    if (!fs.existsSync(wtDir)) {
      run(`git worktree prune`, root);
      removed.push({ path: wtDir, reason: 'orphan (directory missing)' });
    }
  }

  // Optional: git gc
  const gcFlag = args.includes('--gc');
  if (gcFlag) {
    run('git reflog expire --expire=now --all', root);
    run('git gc --prune=now --aggressive', root);
    removed.push({ action: 'git gc --aggressive' });
  }

  return {
    removed,
    message: removed.length > 0
      ? `Cleaned up ${removed.length} item(s).`
      : 'Nothing to clean up.',
  };
}

// ── Template ──

function template(crewPath) {
  const tmplIdx = args.indexOf('--template');
  const nameIdx = args.indexOf('--name');
  const templateName = (tmplIdx >= 0 ? args[tmplIdx + 1] : null) || (nameIdx >= 0 ? args[nameIdx + 1] : null);

  if (!templateName) {
    return {
      available: Object.keys(PROJECT_TEMPLATES),
      usage: 'node project-manager.js --template <name> crew.js',
      templates: Object.fromEntries(
        Object.entries(PROJECT_TEMPLATES).map(([k, v]) => [k, { name: v.name, lang: v.lang, steps: v.steps.length }])
      ),
    };
  }

  const tmpl = PROJECT_TEMPLATES[templateName];
  if (!tmpl) {
    return { error: `Unknown template "${templateName}". Available: ${Object.keys(PROJECT_TEMPLATES).join(', ')}` };
  }

  // Generate crew.js from template
  const topicIdx = args.indexOf('--topic');
  const topic = (topicIdx >= 0 ? args[topicIdx + 1] : null) || 'your topic here';
  const crewDef = {
    name: templateName,
    goal: `${tmpl.name} — ${topic}`,
    project: { lang: tmpl.lang },
    workdir: crewPath ? path.dirname(path.resolve(crewPath)) : `/tmp/crew-${templateName}`,
    steps: tmpl.steps.map(s => ({
      ...s,
      params: s.params ? Object.fromEntries(
        Object.entries(s.params).map(([k, v]) => [k, v === 'REPLACE_TOPIC' ? topic : v])
      ) : undefined,
    })),
    files: tmpl.files,
  };

  const outputPath = crewPath || path.join(crewDef.workdir, 'crew.js');
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `module.exports = ${JSON.stringify(crewDef, null, 2)};\n`);

  return {
    template: templateName,
    name: tmpl.name,
    lang: tmpl.lang,
    steps: tmpl.steps.length,
    topic,
    output: outputPath,
    nextStep: `Run: node project-manager.js --bootstrap ${outputPath}`,
  };
}

// ── Push ──

function pushToRemote(crewPath) {
  const crewDef = getCrewDef(crewPath);
  const root = getProjectRoot(crewDef);
  const branch = args[args.indexOf('--branch') + 1] || run('git branch --show-current', root) || 'dev';

  const remote = run('git remote get-url origin', root);
  if (!remote) {
    return { error: 'No remote configured. Use `github: true` in crew.js bootstrap.' };
  }

  const pushResult = run(`git push -u origin ${branch}`, root);

  return {
    branch,
    remote,
    result: pushResult || 'already up to date',
  };
}

// ── CLI ──

let crewPath = args.find(a => !a.startsWith('--'));
const command = args.find(a => a.startsWith('--'))?.replace('--', '');
// For --template, crewPath is optional (it's the output path)
if (command === 'template') {
  crewPath = args.find(a => !a.startsWith('--') && a.endsWith('.js'));
}

if (!command || (command !== 'template' && !crewPath)) {
  console.error(`Usage: node project-manager.js --<command> <crew.js>
Commands:
  --bootstrap      Create repo with .gitignore, LFS, directory structure, GitHub remote
  --template NAME  Generate crew.js from template (node-lib/python-api/fullstack/cli-tool/rust-lib)
  --worktrees      Create N parallel git worktrees (N = crew.worktrees or 2)
  --checkpoint     Commit current state (--step <id> --message <msg>)
  --status         Show project status, checkpoints, worktrees
  --rollback       Rollback to a commit (--to <commit>)
  --evolve         Compare worktrees, keep best, prune underperformers
  --merge          Merge best worktree into main
  --cleanup        Remove pruned worktrees and orphan references (--gc for aggressive cleanup)
  --push           Push current branch to remote (--branch <name>)`);
  process.exit(1);
}

try {
  let result;
  switch (command) {
    case 'bootstrap': result = bootstrap(crewPath); break;
    case 'template': result = template(crewPath); break;  // crewPath optional for template
    case 'worktrees': result = createWorktrees(crewPath); break;
    case 'checkpoint': result = checkpoint(crewPath); break;
    case 'status': result = status(crewPath); break;
    case 'rollback': result = rollback(crewPath); break;
    case 'evolve': result = evolve(crewPath); break;
    case 'merge': result = mergeBest(crewPath); break;
    case 'cleanup': result = cleanup(crewPath); break;
    case 'push': result = pushToRemote(crewPath); break;
    default: console.error(`Unknown command: --${command}`); process.exit(1);
  }
  console.log(JSON.stringify(result, null, 2));
} catch (e) {
  console.error(`Error: ${e.message}`);
  process.exit(1);
}
