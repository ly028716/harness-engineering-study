# Harness Engineering 核心洞察

> 从理论到实践的关键发现

## 一、核心理念

### 1. 约束驱动 > 指令驱动

**发现**：定义"不能做什么"比"怎么做"更有效

**证据**：
- OpenAI 实验：约束组比指令组成功率高 40%
- claude-code-harness：13 条守护规则保证安全性
- Anthropic 设计：Evaluator 独立于 Generator

**实践**：
```typescript
// 好的约束：明确、可验证
if (hasSudo(command)) {
  return { decision: "deny", reason: "sudo 被禁止" };
}

// 差的指令：模糊、难验证
// "请小心使用 sudo，只在必要时使用"
```

### 2. 角色分离 > 单一智能体

**发现**：职责分离防止任务漂移和自我欺骗

**证据**：
- Anthropic：Generator/Evaluator/Coordinator 三角色
- claude-code-harness：Worker/Reviewer/Lead 三智能体
- OpenAI：规划者和执行者分离

**关键原则**：
- Worker 只实现，不审查
- Reviewer 只审查，不修改
- Lead 只协调，不直接实现

**为什么有效**：
- 防止"自己检查自己"的盲点
- 强制独立视角
- 清晰的责任边界

### 3. 声明式规则 > 命令式逻辑

**发现**：规则即数据，易于理解和修改

**对比**：

```typescript
// 声明式（好）
const GUARD_RULES: GuardRule[] = [
  {
    id: "R01:deny-sudo",
    toolPattern: /^Bash$/,
    evaluate: (ctx) => hasSudo(ctx.input) ? deny() : null
  }
];

// 命令式（差）
function checkCommand(cmd) {
  if (cmd.includes("sudo")) {
    console.log("Error: sudo not allowed");
    return false;
  }
  // ... 更多 if-else
}
```

**优势**：
- 类型安全
- 易于测试
- 可扩展
- 自文档化

## 二、架构模式

### 1. 三层决策模型

**模型**：approve / deny / ask

**应用场景**：

| 决策 | 场景 | 示例 |
|------|------|------|
| approve | 安全操作 | 读取文件、运行测试 |
| deny | 危险操作 | sudo、force push |
| ask | 不确定操作 | 项目外写入、rm -rf |

**关键**：
- 默认安全（未知 → approve）
- 明确危险（已知风险 → deny）
- 人工介入（边界情况 → ask）

### 2. 多源状态融合

**问题**：状态来自多个来源，如何统一？

**解决方案**：

```typescript
// 优先级：SQLite > 环境变量 > 默认值
function buildContext(input: HookInput): RuleContext {
  // 层 1：默认值
  let workMode = false;
  
  // 层 2：环境变量
  workMode = isTruthy(process.env["HARNESS_WORK_MODE"]);
  
  // 层 3：SQLite（最高优先级）
  if (input.session_id) {
    const state = store.getWorkState(input.session_id);
    if (state) {
      workMode = workMode || state.bypassRmRf;
    }
  }
  
  return { input, projectRoot, workMode, ... };
}
```

**原则**：
- 明确优先级
- 容错处理
- 向下兼容

### 3. Worktree 隔离模式

**问题**：如何并行修改同一文件？

**传统方案的问题**：
- 分支切换：破坏工作区
- 文件锁：串行化执行
- 复制仓库：浪费空间

**Worktree 方案**：

```
main/
  ├── .git/
  └── src/
worktree-1/
  ├── .git/ (链接到 main/.git)
  └── src/ (独立副本)
worktree-2/
  ├── .git/ (链接到 main/.git)
  └── src/ (独立副本)
```

**优势**：
- 真正的文件系统隔离
- 共享 Git 对象
- 独立工作区
- 易于清理

**流程**：
1. Lead 创建 worktree
2. Worker 在 worktree 中工作
3. Worker 提交到 worktree 分支
4. Reviewer 审查
5. Lead cherry-pick 到 main
6. 清理 worktree

### 4. Preflight + 独立审查

**双重保障**：

```
Worker 流程:
1. 实现代码
2. Preflight 自检（快速、宽松）
   - 语法错误
   - 明显问题
   - 基本质量
3. 提交代码

Reviewer 流程:
1. 读取代码（只读）
2. 基于 sprint-contract 检查（严格、全面）
   - Security
   - Performance
   - Quality
   - Accessibility
3. 输出判决（APPROVE / REQUEST_CHANGES）
```

**为什么需要两层**：
- Preflight：快速反馈，减少明显错误
- 独立审查：深度检查，保证质量
- 角色分离：防止自我欺骗

### 5. 自动模式选择

**问题**：如何选择最优执行策略？

**策略**：

| 任务数 | 模式 | 理由 |
|--------|------|------|
| 1 | Solo | 开销最小 |
| 2-3 | Parallel | Worker 分离有收益 |
| 4+ | Breezing | Lead 协调价值显现 |

**实现**：

```typescript
function selectMode(taskCount: number, flags: Flags): Mode {
  // 1. 明确标志优先
  if (flags.parallel) return "parallel";
  if (flags.breezing) return "breezing";
  
  // 2. 基于任务数自动选择
  if (taskCount === 1) return "solo";
  if (taskCount <= 3) return "parallel";
  return "breezing";
}
```

**原则**：
- 用户意图优先
- 自动优化体验
- 允许手动覆盖

## 三、质量保证

### 1. 多层验证

**层次**：

```
层 1：PreToolUse Hook
  ↓ 阻止危险操作
层 2：Preflight 自检
  ↓ Worker 自我检查
层 3：构建验证
  ↓ 测试 + 类型检查
层 4：独立审查
  ↓ Reviewer 深度检查
层 5：PostToolUse Hook
  ↓ 格式化 + Lint
```

**每层的职责**：
- PreToolUse：安全守护
- Preflight：快速反馈
- 构建验证：功能正确性
- 独立审查：质量保证
- PostToolUse：代码规范

### 2. Sprint Contract

**概念**：机器可读的验收标准

**格式**：

```json
{
  "task_id": "1.2",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "description": "用户可以登录",
      "verification": "manual | automated",
      "test_command": "npm test -- login.test.ts"
    }
  ],
  "runtime_validation": {
    "tests": ["npm test"],
    "type_check": "tsc --noEmit",
    "lint": "eslint src/"
  },
  "browser_checks": [
    {
      "route": "/login",
      "checks": ["form visible", "submit button enabled"]
    }
  ]
}
```

**优势**：
- 明确标准
- 机器可验证
- 可追溯
- 版本控制

### 3. 错误恢复策略

**原则**：失败 3 次后上报

**流程**：

```
尝试 1: 实现 → 失败 → 分析原因
  ↓
尝试 2: 修复 → 失败 → 深度分析
  ↓
尝试 3: 再次修复 → 失败 → 停止
  ↓
上报 Lead: 
  - 失败日志
  - 尝试的修复
  - 剩余问题
```

**为什么是 3 次**：
- 1 次：可能是偶然错误
- 2 次：可能是理解不足
- 3 次：可能是系统性问题，需要人工介入

## 四、实践经验

### 1. 从 OpenAI 实验学到的

**关键数据**：
- 1M 行代码
- 1,500 个 PR
- 10x 速度提升
- 5 个月实验

**核心规则**：
1. 明确任务边界
2. 提供充足上下文
3. 定义验证标准
4. 迭代改进循环
5. 人工审查关键决策

### 2. 从 Anthropic 设计学到的

**三智能体架构**：
- Generator：生成候选方案
- Evaluator：评估质量
- Coordinator：协调决策

**关键洞察**：
- 角色分离防止偏见
- 独立评估保证质量
- 协调者不直接实现

### 3. 从 claude-code-harness 学到的

**生产级实现**：
- TypeScript 类型安全
- 13 条守护规则
- Worktree 隔离
- Agent Memory
- Sprint Contract

**设计精髓**：
- 声明式规则
- 安全默认
- 多源状态
- 渐进复杂度

### 4. 从 refact 学到的

**Rust 高性能架构**：
- Arc<ARwLock<GlobalContext>> 中心化状态
- HTTP + LSP 双协议支持
- 8 状态会话状态机
- 50+ 工具动态可用性检查
- 12+ 后台任务并发处理

**编排优于执行**：
- 主 Agent 负责编排和决策
- 子 Agent 负责具体执行
- 清晰的委托接口
- 保持主 Agent 上下文精简

**YAML 配置驱动**：
- 声明式模式定义
- 子 Agent 配置化
- 工具集动态组合
- 易于扩展和维护

**多层次编辑**：
- 7 种编辑方式适应不同场景
- 从粗粒度到细粒度
- 支持撤销和 Git 集成
- 灵活的文件操作策略

**语义搜索 + AST**：
- AST 索引提供精确符号查找
- VecDB 提供语义相似搜索
- 双重索引互补优势
- 提高上下文召回率

### 5. 从 agent-os 学到的

**标准驱动开发**：
- 从代码库中提取隐性知识
- 文档化为显性标准
- 标准索引（index.yml）快速匹配
- 三种注入场景（对话、技能、计划）

**命令式工作流**：
- 5 个核心命令覆盖完整流程
- 每个命令一个 Markdown 文件定义
- 详细的步骤说明和交互式确认
- 符号链接到 .claude/commands/

**交互式确认模式**：
- 始终使用 AskUserQuestion 工具
- 提供建议选项减少用户负担
- 一次一个问题，等待用户回答
- 完整循环后再进入下一个标准

**规范塑造流程**：
- 规范先于实现（shape-spec）
- Task 1 始终保存规范文档
- 收集上下文（视觉稿、参考实现、产品文档）
- 识别相关标准并注入

**Profile 继承系统**：
- YAML 配置继承关系
- 子 Profile 覆盖父 Profile
- 全局标准共享（profiles/default/global/）
- 项目特定定制

**轻量级设计哲学**：
- 最小化配置（config.yml）
- 简洁的标准文档（AI 可扫描）
- 渐进式采用
- 避免过度工程

## 五、反模式

### 1. 单一智能体做所有事

**问题**：
- 任务漂移
- 自我欺骗
- 质量下降

**解决**：角色分离

### 2. 指令式约束

**问题**：
- 难以理解
- 难以修改
- 难以测试

**解决**：声明式规则

### 3. 无状态执行

**问题**：
- 重复工作
- 无法学习
- 效率低下

**解决**：持久化状态（Plans.md + SQLite + Memory）

### 4. 同步串行执行

**问题**：
- 速度慢
- 资源浪费
- 用户体验差

**解决**：Worktree 隔离 + 并行执行

### 5. 模糊的验收标准

**问题**：
- 无法验证
- 主观判断
- 质量不稳定

**解决**：Sprint Contract + 机器可验证

## 六、设计原则总结

### 核心原则

1. **约束优于指令**：定义边界而非步骤
2. **分离优于集中**：角色分离防止偏见
3. **声明优于命令**：规则即数据
4. **并行优于串行**：Worktree 隔离
5. **验证优于信任**：多层质量保证

### 实现原则

1. **类型安全**：TypeScript 保证正确性
2. **安全默认**：未知情况默认安全
3. **容错处理**：失败时优雅降级
4. **渐进复杂度**：Solo → Parallel → Breezing
5. **持续学习**：Agent Memory 积累知识

### 质量原则

1. **独立审查**：Reviewer 不能修改代码
2. **机器验证**：Sprint Contract 标准化
3. **多层保障**：Hook + Preflight + Review
4. **快速反馈**：Preflight 捕获明显问题
5. **深度检查**：Reviewer 保证质量

---

**总结时间**：2026-04-08
**基于来源**：OpenAI 实验 + Anthropic 设计 + claude-code-harness 实现 + refact 架构 + agent-os 标准驱动
**下一步**：应用这些洞察设计 MVP
