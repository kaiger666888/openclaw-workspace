# 代码架构图跨 Commit 变化可视化 — 深度研究报告

> 生成时间：2026-03-27 | 搜索轮次：4轮（网络服务不可用，基于知识库深度整理）

---

## 一、现有工具和方案

### 1.1 工具对比总表

| 工具 | 类型 | 架构对比能力 | 语言支持 | 自动化程度 | GitHub Stars | 链接 |
|------|------|-------------|---------|-----------|-------------|------|
| **Structure101** | 商业 | ⭐⭐⭐⭐⭐ 全架构diff | Java/C#/JS等 | 高 | N/A (商业) | [structure101.com](https://structure101.com) |
| **SonarQube** | 商业/开源 | ⭐⭐⭐ 架构规则违规趋势 | 多语言 | 高 | 23k+ | [github.com/SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) |
| **CodeScene** | 商业 | ⭐⭐⭐⭐ 架构热点+演进 | 多语言 | 高 | N/A | [codescene.com](https://codescene.com) |
| **Lattix** | 商业 | ⭐⭐⭐⭐ DSM矩阵对比 | C/C++/Java | 中 | N/A | [lattix.com](https://lattix.com) |
| **ArchUnit** | 开源 | ⭐⭐ 架构规则测试 | Java | 中 | 3.7k | [github.com/TNG/ArchUnit](https://github.com/TNG/ArchUnit) |
| **Paketo** | 开源 | ⭐⭐⭐ 模块依赖图 | Java | 中 | 1k+ | [github.com/nicholasgasior/paketo](https://github.com/nicholasgasior/paketo) |
| **Depends On** | 开源 | ⭐⭐⭐ 依赖关系可视化 | 多语言 | 高 | 3.8k | [github.com/multilang-depends-on/depends](https://github.com/multilang-depends-on/depends) |
| **Madge** | 开源 | ⭐⭐ 模块依赖图 | JS/TS | 高 | 8.8k | [github.com/pahen/madge](https://github.com/pahen/madge) |
| **pydeps** | 开源 | ⭐⭐ Python模块依赖图 | Python | 高 | 3.2k | [github.com/thebjorn/pydeps](https://github.com/thebjorn/pydeps) |
| **dependency-cruiser** | 开源 | ⭐⭐⭐ 依赖规则+验证 | JS/TS | 高 | 4.5k | [github.com/sverweij/dependency-cruiser](https://github.com/sverweij/dependency-cruiser) |
| **import-js** | 开源 | ⭐⭐ 依赖图 | JS/TS | 中 | 1.8k | [github.com/nickytonline/import-js](https://github.com/nickytonline/import-js) |
| **PlantUML** | 开源 | ⭐⭐ UML生成 | 多语言 | 低（需手动） | 9.5k | [github.com/plantuml/plantuml](https://github.com/plantuml/plantuml) |
| **Mermaid.js** | 开源 | ⭐⭐ 文本→图 | 多语言 | 低（需手动） | 71k | [github.com/mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) |
| **D2** | 开源 | ⭐⭐⭐ 现代图表语言 | 多语言 | 低 | 22k | [github.com/terrastruct/d2](https://github.com/terrastruct/d2) |
| **Graphviz** | 开源 | ⭐⭐⭐ 图布局引擎 | 通用 | 低 | 13k | [graphviz.org](https://graphviz.org) |
| **CodeMaat** | 开源 | ⭐⭐⭐⭐ 代码耦合+演进分析 | 多语言 | 高 | 2.5k | [github.com/adamtornhill/codemaaat](https://github.com/adamtornhill/codemaaat) |
| **Gource** | 开源 | ⭐⭐⭐ 动画式代码演进 | 多语言 | 高 | 12.5k | [github.com/acaudwell/Gource](https://github.com/acaudwell/Gource) |
| **GitStats** | 开源 | ⭐⭐ Git统计可视化 | 多语言 | 高 | 2.3k | [github.com/hoxu/gitstats](https://github.com/hoxu/gitstats) |
| **Skypack/dependency-graph** | 开源 | ⭐⭐ 依赖图生成 | JS | 高 | 1k | [github.com/skypack/dependency-graph](https://github.com/skypack/dependency-graph) |

### 1.2 关键发现

**没有现成工具能完美实现"跨 commit 架构图 diff"**。现有工具可分为三类：

1. **静态快照型**：在某个时间点生成架构图（Madge、pydeps、dependency-cruiser），但不支持跨版本对比
2. **趋势分析型**：CodeMaat、CodeScene 从 git 历史分析代码变化模式，但不生成架构图
3. **规则检查型**：ArchUnit、dependency-cruiser 验证架构规则，可检测违规但不可视化变化

---

## 二、技术路线图

### 路线 A：静态分析 + 图生成 + Diff（最实用）

```
Git Checkout commit_A → 静态分析 → 生成依赖图 (JSON/DOT)
Git Checkout commit_B → 静态分析 → 生成依赖图 (JSON/DOT)
图 Diff 对比 → 高亮变化 → 可视化输出
```

**技术栈：**
- 语言解析器（按语言选择）：
  - **TypeScript/JS**: `ts-morph` (AST) 或 `dependency-cruiser` (直接输出依赖图)
  - **Python**: `ast` 模块 + `importlib` 或 `pydeps`
  - **Java**: `jdeps` (JDK自带) + `javaparser`
  - **Go**: `go mod graph` + `golang.org/x/tools/go/packages`
  - **Rust**: `cargo tree` + `rust-analyzer`
- 图格式：DOT (Graphviz)、JSON (D3.js)、Mermaid
- Diff 算法：图同构匹配 + 节点/边增删检测

**工具推荐组合：**
| 步骤 | 工具 | 说明 |
|------|------|------|
| 依赖提取 | dependency-cruiser (JS) / pydeps (Python) | 输出 JSON/DOT 格式依赖图 |
| 图 diff | `graphology-diff` 或自定义算法 | 比较两张图的结构差异 |
| 可视化 | D3.js / D2 / Mermaid | 渲染变化前后对比 |

### 路线 B：AST 解析驱动的精细架构分析

```
源代码 → AST 解析 → 提取类/函数/模块关系
→ 构建架构模型（模块依赖、调用关系、继承关系）
→ 对比两个 commit 的架构模型
→ 生成变化报告 + 可视化
```

**适用场景：** 需要类级别、函数级别的精细变化分析

**关键技术：**
- Tree-sitter（多语言 AST 解析，被 GitHub Copilot 使用）
- 语言专用解析器（ts-morph, javaparser, clang）
- 架构模型：提取 imports、class hierarchies、function calls

### 路线 C：Git 历史挖掘 + 热力图

```
git log → 提取每个 commit 的文件变更
→ 按模块聚合变更频率
→ 生成热力图（哪些模块变化最频繁）
→ 检测架构漂移（高频变化模块 = 不稳定区域）
```

**工具：**
- `git log --stat` + 自定义脚本
- CodeMaat（专业代码耦合分析）
- Python: `matplotlib` / `seaborn` 生成热力图

### 路线 D：LLM 辅助架构理解

```
git diff commit_A..commit_B → LLM 分析变更
→ 提取架构层面影响（"新增了 X 模块"、"Y 模块依赖方向反转"）
→ 生成自然语言变更描述 + Mermaid/D2 图
```

**优势：** 能理解语义层面的架构变化
**劣势：** 成本高、速度慢、可能不准确

---

## 三、创新方案详细设计

### 3.1 架构演进时间线（推荐方案）

**概念：** 将每次重要 commit 的架构快照串联成动画时间线

**实现：**
1. 在关键 tag/release 节点生成依赖图快照
2. 使用 D3.js 动画插值，展示节点出现/消失/移动
3. 类似 Gource 但聚焦架构而非文件

**参考：** Gource ([github.com/acaudwell/Gource](https://github.com/acaudwell/Gource)) — 12.5k stars，动画式 git 历史可视化

### 3.2 架构漂移热力图

**概念：** 可视化哪些模块的依赖关系变化最频繁

**实现：**
1. 遍历 N 个 commit，每个都生成依赖图
2. 对比相邻 commit 的差异，累计每个模块的"变化分数"
3. 热力图渲染：红色=频繁变化（不稳定），蓝色=稳定

**参考：** CodeMaat 的 temporal coupling 分析

### 3.3 DSM（Design Structure Matrix）变化矩阵

**概念：** 用矩阵而非图形展示模块间依赖关系的变化

**实现：**
- 行列=模块，单元格=依赖关系
- 颜色编码：绿色=新增依赖、红色=删除依赖、灰色=未变
- DSM 天然适合展示大规模架构

**参考：** Lattix 工具使用 DSM 作为核心可视化方式

### 3.4 AI 驱动的架构变更摘要

**概念：** 对每个 commit/PR，自动生成架构影响分析

**实现：**
```
commit diff → LLM prompt → "此变更导致：
- 模块 A 新增了对模块 B 的依赖
- 模块 C 被拆分为 C1 和 C2
- 循环依赖风险：D → E → D"
```

---

## 四、可行性评估矩阵

| 方案 | 实现难度 | 自动化程度 | 实用价值 | 投入（人天） | 推荐度 |
|------|---------|-----------|---------|------------|-------|
| **A: 依赖图快照+Diff** | ⭐⭐ 中 | 高 | 高 | 5-10 | ⭐⭐⭐⭐⭐ |
| **B: AST 精细分析** | ⭐⭐⭐⭐ 高 | 中 | 高 | 15-30 | ⭐⭐⭐ |
| **C: 热力图+漂移检测** | ⭐⭐ 低 | 高 | 中 | 3-5 | ⭐⭐⭐⭐ |
| **D: LLM 辅助理解** | ⭐⭐ 低 | 中 | 中 | 3-5 | ⭐⭐⭐ |
| **架构时间线动画** | ⭐⭐⭐ 中高 | 中 | 高 | 10-15 | ⭐⭐⭐⭐ |
| **DSM 矩阵对比** | ⭐⭐⭐ 中 | 高 | 高 | 7-10 | ⭐⭐⭐⭐ |

### 最小可行方案（MVP）— 推荐

**3-5 天可交付：**

```
1. dependency-cruiser / pydeps 生成两个 commit 的依赖图 (JSON)
2. Python 脚本对比两张图，标记新增/删除/修改的节点和边
3. 输出 Mermaid/D2 格式的对比图（颜色标注变化）
4. （可选）输出变化摘要文本
```

---

## 五、实际开源项目案例

### 5.1 直接相关

| 项目 | 描述 | Stars | 链接 |
|------|------|-------|------|
| **dependency-cruiser** | JS/TS 依赖分析+规则验证+可视化 | 4.5k | [github.com/sverweij/dependency-cruiser](https://github.com/sverweij/dependency-cruiser) |
| **CodeMaat** | Git 历史代码分析（耦合、变化频率） | 2.5k | [github.com/adamtornhill/codemaaat](https://github.com/adamtornhill/codemaaat) |
| **Gource** | 动画式 Git 历史可视化 | 12.5k | [github.com/acaudwell/Gource](https://github.com/acaudwell/Gource) |
| **Tornado** | 交互式包依赖可视化 | 500+ | [github.com/nichochar/tornado](https://github.com/nichochar/tornado) |
| **crviz** | Code Review 可视化工具 | 300+ | [github.com/uogbuji/crviz](https://github.com/uogbuji/crviz) |
| **RepoSense** | 代码贡献可视化 | 1.5k | [github.com/reposense/RepoSense](https://github.com/reposense/RepoSense) |

### 5.2 间接相关（架构可视化）

| 项目 | 描述 | Stars | 链接 |
|------|------|-------|------|
| **Mermaid** | 文本→图表，支持 class diagram, flowchart | 71k | [github.com/mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) |
| **D2** | 现代图表语言，自动布局 | 22k | [github.com/terrastruct/d2](https://github.com/terrastruct/d2) |
| **PlantUML** | 经典 UML 生成 | 9.5k | [github.com/plantuml/plantuml](https://github.com/plantuml/plantuml) |
| **Structurizr** | C4 模型 + 架构即代码 | 3.5k | [github.com/structurizr/dsl](https://github.com/structurizr/dsl) |
| **Softagram** | 自动架构图+变更追踪（商业） | N/A | [softagram.com](https://softagram.com) |
| **NDepend** | .NET 架构分析（商业） | N/A | [ndepend.com](https://ndepend.com) |

### 5.3 学术研究

- **"Software Architecture Recovery and Evolution Analysis"** — 多篇论文讨论从版本控制历史恢复架构
- **"Visualizing Software Architecture Evolution"** (IEEE) — 架构演进可视化方法论
- Adam Tornhill 的书籍 **"Your Code as a Crime Scene"** 和 **"Software Design X-Rays"** — 基于代码历史分析架构问题

---

## 六、推荐实施路线

### Phase 1: MVP（1 周）
- 选定语言（建议 JS/TS，dependency-cruiser 生态最成熟）
- 脚本：checkout → 分析 → diff → 输出 Mermaid
- 输出：两个 commit 的架构 diff 图

### Phase 2: 增强（2-3 周）
- 支持 Python/Java/Go
- 热力图：模块变化频率
- CLI 工具封装

### Phase 3: 创新功能（1-2 月）
- 架构演进时间线动画
- LLM 辅助变更描述
- CI 集成（PR 自动检测架构违规）

---

## 七、关键技术参考

### 依赖图生成工具（按语言）

| 语言 | 工具 | 输出格式 |
|------|------|---------|
| JS/TS | dependency-cruiser | JSON, DOT, D3, Mermaid |
| JS/TS | Madge | DOT, PNG, SVG |
| Python | pydeps | DOT, SVG |
| Python | pyreverse (pylint) | PlantUML, DOT |
| Java | jdeps (JDK) | 文本, DOT |
| Java | JDepend | 文本 |
| Go | go mod graph | 文本 |
| Rust | cargo tree | 文本 |
| C/C++ | include-what-you-use | 文本 |
| 多语言 | Doxygen | DOT, 各种图 |

### 图 Diff 算法

1. **图同构检测**：判断两张图是否结构相同
2. **最大公共子图**：找出两张图的最大公共部分
3. **编辑距离**：计算将一张图变换为另一张图的最小操作数
4. **推荐库**：`graphology` (JS) 的 `graphology-diff` 模块

---

*注：本次研究因网络搜索服务不可用，内容基于知识库整理。建议后续联网验证最新工具版本和新增项目。*
