# claude-code-harness 实现分析

> 基于实际代码的深度分析

## 项目概览

**claude-code-harness** 是一个自引用项目（使用 Harness 改进 Harness 本身），为 Claude Code 提供完整的 Plan→Work→Review 工作流。

### 核心特点

1. **TypeScript 核心引擎**：类型安全的守护规则系统
2. **5 动词技能**：setup, plan, work, review, release
3. **三智能体架构**：Worker, Reviewer, Lead
4. **13 条安全规则**：R01-R13 声明式守护
5. **并行执行**：支持多 Worker 并发
6. **自我改进**：使用自身工具链开发

## 架构分析

### 1. 核心引擎（core/）

#### 类型系统（types.ts）

```typescript
// Hook I/O 协议
interface HookInput {
  tool_name: string;           // 工具名称
  tool_input: Record<string, unknown>;  // 工具参数
  session_id?: string;         // 会话 ID
  cwd?: string;                // 工作目录
  plugin_root?: string;        // 插件根目录
}

// Hook 决策
type HookDecision = "approve" | "deny" | "ask";

interface HookResult {
  decision: HookDecision;
  reason?: string;             // 用户说明
  systemMessage?: string;      // Claude 上下文
}

// 规则评估上下文
interface RuleContext {
  input: HookInput;
  projectRoot: string;
  workMode: boolean;           // work 模式
  codexMode: boolean;          // codex 模式
  breezingRole: string | null; // breezing 角色
}

// 守护规则定义
interface GuardRule {
  id: string;                  // 规则标识
  toolPattern: RegExp;         // 工具匹配模式
  evaluate: (ctx: RuleContext) => HookResult | null;
}
```

**设计亮点**：
- 清晰的类型边界
- 协议驱动的设计
- 可扩展的规则系统

#### 主入口（index.ts）

```typescript
// 执行流程
async function main(): Promise<void> {
  const hookType = process.argv[2] as HookType;
  
  // 1. 读取 stdin
  const raw = await readStdin();
  
  // 2. 解析输入
  const input = parseInput(raw);
  
  // 3. 路由到处理器
  const result = await route(hookType, input);
  
  // 4. 输出结果
  process.stdout.write(JSON.stringify(result) + "\n");
}

// 路由逻辑
async function route(hookType: HookType, input: HookInput): Promise<HookResult> {
  switch (hookType) {
    case "pre-tool":
      return evaluatePreTool(input);
    case "post-tool":
      return evaluatePostTool(input);
    case "permission":
      return evaluatePermission(input);
    default:
      return { decision: "approve" };  // 安全默认
  }
}
```

**设计模式**：
- **管道模式**：stdin → parse → route → stdout
- **安全默认**：未知情况默认 approve
- **错误容错**：异常时返回安全结果

#### 守护规则（rules.ts）

**13 条核心规则**：

| 规则 | 保护对象 | 动作 | 说明 |
|------|---------|------|------|
| R01 | sudo 命令 | deny | 禁止提权操作 |
| R02 | .git/, .env, 密钥 | deny | 禁止写入敏感文件 |
| R03 | Shell 重定向到保护文件 | deny | 禁止绕过写入保护 |
| R04 | 项目外文件 | ask | 需要确认 |
| R05 | rm -rf | ask | 危险删除需确认（work 模式除外）|
| R06 | git push --force | deny | 禁止强制推送 |
| R07-R09 | 模式特定守护 | 上下文相关 | work/codex 模式调整 |
| R10 | --no-verify, --no-gpg-sign | deny | 禁止绕过 git hooks |
| R11 | git reset --hard main/master | deny | 禁止重置主分支 |
| R12 | 直接推送到 main/master | warn | 警告但允许 |
| R13 | 重要文件编辑 | warn | 警告但允许 |

**规则评估引擎**：

```typescript
export function evaluateRules(ctx: RuleContext): HookResult {
  for (const rule of GUARD_RULES) {
    // 1. 检查工具是否匹配
    if (!rule.toolPattern.test(ctx.input.tool_name)) continue;
    
    // 2. 评估规则
    const result = rule.evaluate(ctx);
    
    // 3. 第一个匹配的规则生效
    if (result !== null) return result;
  }
  
  // 4. 默认批准
  return { decision: "approve" };
}
```

**规则设计原则**：
1. **声明式**：规则即数据
2. **可组合**：规则独立评估
3. **优先级**：第一个匹配的规则生效
4. **安全默认**：无匹配时批准
5. **上下文感知**：work/codex 模式调整行为

#### PreToolUse 评估（pre-tool.ts）

```typescript
export function evaluatePreTool(input: HookInput): HookResult {
  // 1. 构建上下文
  const ctx = buildContext(input);
  
  // 2. 评估规则
  return evaluateRules(ctx);
}

function buildContext(input: HookInput): RuleContext {
  const projectRoot = input.cwd ?? process.cwd();
  
  // 环境变量初始值
  let workMode = isTruthy(process.env["HARNESS_WORK_MODE"]);
  let codexMode = isTruthy(process.env["HARNESS_CODEX_MODE"]);
  
  // SQLite 状态补充（优先级更高）
  if (input.session_id) {
    const dbPath = resolveDbPath(projectRoot);
    if (dbPath) {
      const store = new HarnessStore(dbPath);
      const state = store.getWorkState(input.session_id);
      if (state) {
        workMode = workMode || state.bypassRmRf;
        codexMode = codexMode || state.codexMode;
      }
    }
  }
  
  return { input, projectRoot, workMode, codexMode, breezingRole: null };
}
```

**上下文构建策略**：
- **多源融合**：环境变量 + SQLite 状态
- **优先级**：SQLite > 环境变量
- **容错**：DB 失败时回退到环境变量

### 2. 技能系统（skills/）

#### harness-plan（计划技能）

**职责**：
- 创建 Plans.md
- 管理任务状态
- 同步实现进度

**核心流程**：

```
create 子命令:
1. 上下文确认（对话历史提取）
2. 需求收集（最多 3 问）
3. 技术调查（WebSearch）
4. 功能列表提取
5. 优先级矩阵（Required/Recommended/Optional）
6. TDD 判断
7. Plans.md 生成（cc:TODO 标记）
8. 下一步指引

sync 子命令:
1. 读取 Plans.md
2. 检测格式（v1: 3列 / v2: 5列）
3. git status/log 获取实现状态
4. 检查 agent-trace.jsonl
5. 差异检测
6. 自动修正建议
7. 回顾分析（默认开启）
```

**Plans.md 格式**：

```markdown
# [项目名] Plans.md

创建日期: YYYY-MM-DD

---

## Phase N: 阶段名

| Task | 内容 | DoD | Depends | Status |
|------|------|-----|---------|--------|
| N.1  | 说明 | 测试通过 | - | cc:TODO |
| N.2  | 说明 | lint 0 错误 | N.1 | cc:WIP |
| N.3  | 说明 | 迁移可执行 | N.1, N.2 | cc:完了 |
```

**状态标记**：

| 标记 | 含义 |
|------|------|
| pm:依頼中 | PM 已委托 |
| cc:TODO | 未开始 |
| cc:WIP | 进行中 |
| cc:完了 | Worker 完成 |
| pm:確認済 | PM 审查完成 |
| blocked | 阻塞（必须说明原因）|

#### harness-work（执行技能）

**职责**：
- 实现 Plans.md 任务
- 自动选择执行模式
- 并行/串行执行
- Codex 委托

**模式自动选择**：

| 任务数 | 自动模式 | 理由 |
|--------|---------|------|
| 1 件 | Solo | 开销最小，直接实现最快 |
| 2-3 件 | Parallel | Worker 分离开始有收益 |
| 4+ 件 | Breezing | Lead 协调 + Worker 并行 + Reviewer 独立 |

**执行流程**：

```
Solo 模式（1 任务）:
1. 读取 Plans.md
2. 标记 cc:WIP
3. TDD（可选）
4. 实现
5. Preflight 自检
6. 构建验证
7. 错误恢复（最多 3 次）
8. 提交
9. 独立审查
10. 标记 cc:完了

Parallel 模式（2-3 任务）:
1. 读取 Plans.md
2. 为每个任务启动 Worker（Task tool）
3. Worker 并行执行
4. 收集结果
5. 汇总报告

Breezing 模式（4+ 任务）:
1. Lead 读取 Plans.md
2. 任务分配给 Worker（worktree 隔离）
3. Worker 在 worktree 中实现并提交
4. Worker 返回 commit hash
5. Reviewer 独立审查
6. Lead cherry-pick 到 main
7. Lead 更新 Plans.md
```

**关键特性**：
- **自动模式选择**：基于任务数量
- **Worktree 隔离**：并行写入同一文件
- **Preflight 自检**：Worker 自我检查
- **独立审查**：Reviewer 不能修改代码
- **错误恢复**：最多 3 次自动修复

### 3. 智能体系统（agents-v3/）

#### Worker（工作智能体）

**配置**：

```yaml
name: worker
tools: [Read, Write, Edit, Bash, Grep, Glob]
disallowedTools: [Agent]
model: sonnet
effort: medium
maxTurns: 100
permissionMode: bypassPermissions
memory: project
isolation: worktree
```

**职责**：
1. 实现单个任务
2. Preflight 自检
3. 构建验证
4. 错误恢复
5. 提交准备

**执行流程**：

```
1. 输入解析
2. 内存确认（过去模式）
3. Plans.md 更新（solo 模式）
4. TDD 判断
5. TDD 阶段（Red）
6. 实现（Green）
   - solo: 直接 Write/Edit/Bash
   - codex: 委托给 Codex CLI
   - breezing: 在 worktree 中实现
7. Preflight 自检
8. 构建验证
9. 错误恢复（最多 3 次）
10. 提交
    - solo: git commit 到 main
    - breezing: git commit 到 worktree
11. 返回结果给 Lead
12. 接收审查反馈（breezing）
13. 修正（最多 3 次）
14. 等待独立审查
15. Plans.md 更新（solo 模式）
16. 完成报告
17. 内存更新
```

**输出格式**：

```json
{
  "status": "completed | failed | escalated",
  "task": "完成的任务",
  "files_changed": ["变更文件列表"],
  "commit": "提交哈希",
  "worktreePath": "worktree 路径（breezing）",
  "summary": "变更摘要（breezing）",
  "memory_updates": ["内存更新"],
  "escalation_reason": "升级原因（失败时）"
}
```

**关键设计**：
- **Worktree 隔离**：并行安全
- **禁用 Agent 工具**：防止无限递归
- **Preflight 自检**：减少审查负担
- **内存学习**：持续改进
- **错误恢复**：自动修复

#### Reviewer（审查智能体）

**配置**：

```yaml
name: reviewer
tools: [Read, Grep, Glob]
disallowedTools: [Write, Edit, Bash, Agent]
model: sonnet
effort: medium
maxTurns: 50
permissionMode: bypassPermissions
memory: project
```

**职责**：
1. 静态代码审查
2. 基于 sprint-contract 验证
3. 多角度检查
4. 输出结构化结果

**审查角度**：

| 角度 | 检查内容 |
|------|---------|
| Security | SQL 注入, XSS, 密钥泄露 |
| Performance | N+1 查询, 内存泄漏, 不必要计算 |
| Quality | 命名, 单一职责, 测试覆盖 |
| Accessibility | ARIA 属性, 键盘导航 |

**审查流程**：

```
1. 读取 sprint-contract.json
2. 读取 reviewer profile（static/runtime/browser）
3. 确认审查对象
4. 执行检查
   - contract 验证
   - 代码质量
   - 安全性
   - 性能
   - 可访问性
5. 生成 gaps 列表
6. 判定 verdict
   - APPROVE: 无 critical/major 问题
   - REQUEST_CHANGES: 有 critical/major 问题
7. 输出结构化结果
8. 内存更新建议
```

**输出格式**：

```json
{
  "schema_version": "review-result.v1",
  "verdict": "APPROVE | REQUEST_CHANGES",
  "type": "code | plan | scope",
  "reviewer_profile": "static | runtime | browser",
  "checks": [
    {
      "id": "contract-check-1",
      "status": "passed | failed | skipped",
      "source": "sprint-contract"
    }
  ],
  "gaps": [
    {
      "severity": "critical | major | minor",
      "location": "文件名:行号",
      "issue": "问题描述",
      "suggestion": "修复建议"
    }
  ],
  "followups": ["下次审查项"],
  "memory_updates": ["内存更新"]
}
```

**关键设计**：
- **只读权限**：不能修改代码
- **禁用 Agent**：防止递归
- **Contract 驱动**：基于约定验证
- **结构化输出**：机器可读
- **内存学习**：记录模式

### 4. 工作流程

#### Solo 工作流（1 任务）

```
用户: "实现任务 1"
  ↓
harness-work
  ↓
读取 Plans.md
  ↓
标记 cc:WIP
  ↓
Worker 实现
  ├─ TDD（可选）
  ├─ 实现
  ├─ Preflight 自检
  ├─ 构建验证
  └─ 错误恢复
  ↓
git commit
  ↓
Reviewer 审查
  ├─ 读取代码
  ├─ 检查质量
  └─ 输出 verdict
  ↓
[APPROVE] 标记 cc:完了
[REQUEST_CHANGES] Worker 修正
```

#### Breezing 工作流（4+ 任务）

```
用户: "实现所有任务"
  ↓
harness-work --breezing
  ↓
Lead 读取 Plans.md
  ↓
Lead 分配任务
  ├─ Worker 1 (worktree-1)
  ├─ Worker 2 (worktree-2)
  └─ Worker 3 (worktree-3)
  ↓
Worker 并行执行
  ├─ 在 worktree 中实现
  ├─ Preflight 自检
  ├─ 构建验证
  └─ git commit（worktree）
  ↓
Worker 返回结果
  ├─ commit hash
  ├─ worktreePath
  └─ summary
  ↓
Reviewer 独立审查
  ├─ 读取 worktree 代码
  ├─ 基于 contract 验证
  └─ 输出 verdict
  ↓
[APPROVE]
  Lead cherry-pick 到 main
  Lead 更新 Plans.md
[REQUEST_CHANGES]
  Lead 发送反馈给 Worker
  Worker 在 worktree 修正
  Worker git commit --amend
  重新审查
```

## 核心设计模式

### 1. 角色分离模式

**实现**：
- **Worker**：只负责实现，不能审查
- **Reviewer**：只负责审查，不能修改
- **Lead**：协调和决策，不直接实现

**好处**：
- 防止任务漂移
- 清晰的职责边界
- 独立的质量把关

### 2. 约束驱动模式

**实现**：
- 13 条守护规则（R01-R13）
- sprint-contract.json 约定
- DoD（Definition of Done）

**好处**：
- 明确的质量标准
- 自动化验证
- 可追溯的决策

### 3. 迭代验证模式

**实现**：
- Preflight 自检（Worker）
- 独立审查（Reviewer）
- 错误恢复（最多 3 次）
- 内存学习

**好处**：
- 持续改进
- 减少返工
- 知识积累

### 4. 工具编排模式

**实现**：
- Hook 系统（PreToolUse/PostToolUse）
- 工具权限控制
- 模式切换（solo/parallel/breezing）

**好处**：
- 灵活的执行策略
- 安全的工具使用
- 可扩展的架构

### 5. 上下文管理模式

**实现**：
- Plans.md（任务上下文）
- agent-trace.jsonl（执行历史）
- SQLite 状态（会话状态）
- Agent Memory（学习记忆）

**好处**：
- 状态持久化
- 可恢复的会话
- 知识传承

## 技术亮点

### 1. TypeScript 核心引擎

**优势**：
- 类型安全
- 编译时检查
- 易于维护
- 性能优秀

**实现**：
```typescript
// 声明式规则
const GUARD_RULES: GuardRule[] = [
  { id: "R01", toolPattern: /^Bash$/, evaluate: ... },
  { id: "R02", toolPattern: /^Write|Edit$/, evaluate: ... },
  // ...
];

// 类型安全的评估
export function evaluateRules(ctx: RuleContext): HookResult {
  for (const rule of GUARD_RULES) {
    if (!rule.toolPattern.test(ctx.input.tool_name)) continue;
    const result = rule.evaluate(ctx);
    if (result !== null) return result;
  }
  return { decision: "approve" };
}
```

### 2. Worktree 隔离

**优势**：
- 并行写入同一文件
- 独立的工作空间
- 安全的实验环境

**实现**：
```yaml
# Worker frontmatter
isolation: worktree
```

### 3. Sprint Contract

**优势**：
- 明确的验证标准
- 机器可读的约定
- 可追溯的决策

**格式**：
```json
{
  "task_id": "1.1",
  "acceptance_criteria": [...],
  "runtime_validation": {
    "tests": ["npm test"],
    "type_check": "tsc --noEmit"
  },
  "browser_checks": [...]
}
```

### 4. Agent Memory

**优势**：
- 持续学习
- 知识积累
- 模式识别

**使用**：
```yaml
# Agent frontmatter
memory: project
```

### 5. 自动模式选择

**优势**：
- 智能决策
- 最优性能
- 用户友好

**逻辑**：
```
1 任务 → Solo（最快）
2-3 任务 → Parallel（平衡）
4+ 任务 → Breezing（最强）
```

## 关键洞察

### 1. 自引用设计

**观察**：项目使用自身工具链开发

**价值**：
- 吃自己的狗粮
- 真实场景验证
- 持续改进循环

### 2. 声明式规则

**观察**：守护规则是数据而非代码

**价值**：
- 易于理解
- 易于修改
- 易于测试
- 易于扩展

### 3. 独立审查

**观察**：Reviewer 不能修改代码

**价值**：
- 防止审查者越权
- 保持审查客观性
- 清晰的职责边界

### 4. 多源状态

**观察**：环境变量 + SQLite + Plans.md

**价值**：
- 灵活的配置
- 可靠的持久化
- 容错的回退

### 5. 渐进式复杂度

**观察**：Solo → Parallel → Breezing

**价值**：
- 简单任务不过度设计
- 复杂任务充分支持
- 用户体验优化

## 对比其他 Harness

### vs OpenAI 实验

| 维度 | claude-code-harness | OpenAI 实验 |
|------|-------------------|------------|
| 规则系统 | 13 条声明式规则 | 5 条核心规则 |
| 智能体 | 3 个（Worker/Reviewer/Lead）| 3 个（Generator/Evaluator/Coordinator）|
| 并行执行 | Worktree 隔离 | 未提及 |
| 质量保证 | 4 角度审查 | 多层验证 |
| 工具集成 | Claude Code 原生 | 自定义工具 |

### vs Anthropic 设计

| 维度 | claude-code-harness | Anthropic 设计 |
|------|-------------------|---------------|
| 架构 | Worker/Reviewer/Lead | Generator/Evaluator/Coordinator |
| 实现 | 生产级代码 | 概念验证 |
| 规则 | TypeScript 类型安全 | 概念描述 |
| 状态 | SQLite + Plans.md | 未详细说明 |
| 扩展性 | 插件系统 | 理论框架 |

## 可借鉴的设计

### 1. TypeScript 核心引擎

**适用场景**：需要类型安全和高性能的 Harness

**实现要点**：
- 定义清晰的类型系统
- 声明式规则表
- 管道式处理流程
- 安全默认策略

### 2. 三智能体架构

**适用场景**：复杂的多任务并行执行

**实现要点**：
- Worker：只实现，不审查
- Reviewer：只审查，不修改
- Lead：协调和决策

### 3. Worktree 隔离

**适用场景**：需要并行修改同一文件

**实现要点**：
- 为每个 Worker 创建 worktree
- 在 worktree 中独立工作
- Lead cherry-pick 到 main

### 4. Sprint Contract

**适用场景**：需要明确的验证标准

**实现要点**：
- 定义 JSON Schema
- 包含验收标准
- 包含验证方法
- 机器可读

### 5. 自动模式选择

**适用场景**：需要优化用户体验

**实现要点**：
- 基于任务数量
- 基于任务复杂度
- 基于资源可用性
- 允许手动覆盖

## 总结

### 核心价值

1. **生产级实现**：不是概念验证，是真实可用的工具
2. **类型安全**：TypeScript 核心引擎保证质量
3. **角色分离**：Worker/Reviewer/Lead 清晰职责
4. **并行执行**：Worktree 隔离支持真正的并行
5. **持续学习**：Agent Memory 积累知识

### 设计精髓

1. **声明式规则**：规则即数据，易于理解和修改
2. **安全默认**：未知情况默认安全行为
3. **独立审查**：Reviewer 不能修改代码
4. **多源状态**：环境变量 + SQLite + Plans.md
5. **渐进复杂度**：Solo → Parallel → Breezing

### 适用场景

**最适合**：
- 需要高质量保证的项目
- 多任务并行执行
- 长期维护的代码库
- 团队协作开发

**不太适合**：
- 简单的一次性脚本
- 探索性编程
- 快速原型验证

### 学习要点

1. **从简单开始**：先理解 Solo 模式
2. **理解角色分离**：Worker/Reviewer/Lead 的职责
3. **掌握规则系统**：13 条守护规则的设计
4. **学习状态管理**：Plans.md + SQLite + Memory
5. **实践并行执行**：Worktree 隔离的使用

---

**分析完成时间**：2026-04-08
**基于版本**：claude-code-harness v3
**下一步**：分析 refact 和 agent-os 项目
