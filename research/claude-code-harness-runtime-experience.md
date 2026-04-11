# Claude Code Harness 运行体验记录

> 基于 claude-code-harness v3.0.0 的实际运行尝试和技能系统分析

## 运行环境准备

### 尝试时间
2026-04-08

### 环境信息
- **项目路径**: E:\IDEWorkplaces\GitHub\Harness\claude-code-harness
- **Node.js**: v25.2.1
- **操作系统**: Windows 11 Pro 10.0.26200

### 遇到的问题

#### 1. better-sqlite3 编译失败

**问题描述**:
```bash
npm install 失败
错误: better-sqlite3 需要编译原生模块
需要: Visual Studio with "Desktop development with C++" workload
```

**根本原因**:
- better-sqlite3 是原生 Node.js 模块，需要 node-gyp 编译
- Windows 环境需要 Visual Studio 构建工具
- 当前环境缺少 C++ 编译工具链

**影响**:
- 无法运行 TypeScript 核心引擎
- 无法测试守护规则系统
- 无法体验完整的 Harness 工作流

**解决方案**（未实施）:
1. 安装 Visual Studio 2022 with C++ workload
2. 或使用 windows-build-tools: `npm install --global windows-build-tools`
3. 或使用预编译的 better-sqlite3 二进制包

## 技能系统分析（基于代码阅读）

虽然无法运行，但通过阅读 skills-v3/ 目录下的 SKILL.md 文件，深入理解了 Harness v3 的技能系统设计。

### 1. harness-plan（计划技能）

**核心功能**:
- 统合了 3 个旧技能：planning, plans-management, sync-status
- 对话式需求收集 → Plans.md 生成
- 任务状态管理（cc:TODO, cc:WIP, cc:完了）
- 实现进度同步和回顾

**子命令**:

| 子命令 | 功能 | 触发方式 |
|--------|------|---------|
| `create` | 创建计划 | "计划を作って" / "create a plan" |
| `add` | 添加任务 | "タスクを追加して" / "add a task" |
| `update` | 更新状态 | "完了にして" / "mark complete" |
| `sync` | 进度同期 | "今どこ？" / "check progress" |

**工作流程**（create 模式）:
1. 确认会话上下文（从对话中提取 or 新询问）
2. 询问要构建什么（最多 3 个问题）
3. 技术调研（WebSearch）
4. 提取功能列表
5. 优先级矩阵（Required / Recommended / Optional）
6. TDD 采用判断（测试设计）
7. 生成 Plans.md（带 cc:TODO 标记）
8. 引导下一步行动

**进度同步流程**（sync 模式）:
1. 获取 Plans.md 当前状态
2. 检测 Plans.md 格式（v1: 3列 / v2: 5列）
3. 从 git status / git log 获取实现状态
4. 检查 Agent 追踪（.claude/state/agent-trace.jsonl）
5. 检测 Plans.md 与实现的差异
6. 自动修正未更新的标记
7. 提示下一步行动

**回顾机制**（默认开启）:
- 当有 1 个以上 cc:完了 任务时自动执行
- 分析估算精度、阻塞原因模式、范围变动
- 记录学习经验
- 可用 `sync --no-retro` 跳过

**关键洞察**:
- **对话式规划**: 不是一次性输入所有需求，而是通过最多 3 个问题逐步明确
- **优先级矩阵**: Required / Recommended / Optional 三级分类
- **状态标记系统**: cc:TODO, cc:WIP, cc:完了, blocked
- **自动同步**: 从 git 和 agent-trace 自动检测实现进度
- **持续回顾**: 完成任务后自动分析，积累经验

### 2. harness-work（执行技能）

**核心功能**:
- 统合了 5 个旧技能：work, impl, breezing, parallel-workflows, ci
- 从单任务到全并行团队执行
- 自动模式选择（基于任务数量）
- 支持多种执行模式

**执行模式自动选择**:

| 任务数量 | 自动选择模式 | 理由 |
|---------|-------------|------|
| **1 件** | Solo | 开销最小，直接实现最快 |
| **2-3 件** | Parallel（Task tool） | Worker 分离的优势开始显现 |
| **4 件以上** | Breezing | Lead 协调 + Worker 并行 + Reviewer 独立的三方分离最有效 |

**命令示例**:

```bash
# 自动模式（根据任务数量自动选择）
harness-work

# 全部任务，自动模式
harness-work all

# 指定任务
harness-work 3

# 强制并行模式（5 个 worker）
harness-work --parallel 5

# 强制团队模式
harness-work --breezing

# Codex CLI 委托（需明确指定）
harness-work --codex
```

**选项说明**:

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `all` | 全部未完成任务 | - |
| `N` or `N-M` | 任务编号/范围 | - |
| `--parallel N` | 并行 worker 数 | auto |
| `--sequential` | 强制串行执行 | - |
| `--codex` | Codex CLI 委托（仅明确指定时） | false |
| `--no-commit` | 禁止自动提交 | false |
| `--resume <id\|latest>` | 恢复前次会话 | - |
| `--breezing` | Lead/Worker/Reviewer 团队执行 | false |
| `--no-tdd` | 跳过 TDD 阶段 | false |
| `--no-simplify` | 跳过自动精简 | false |
| `--auto-mode` | 明确启用 Auto Mode | false |

**Effort 级别控制**（v2.1.68+）:
- Claude Code v2.1.68 起，Opus 4.6 默认 **medium effort** (◐)
- v2.1.72 简化为 3 级：low(○) / medium(◐) / high(●)
- 复杂任务使用 `ultrathink` 关键字启用 high effort (●)

**多要素评分**（决定是否使用 ultrathink）:

| 要素 | 条件 | 分数 |
|------|------|------|
| 文件数 | 变更对象 4 个文件以上 | +1 |
| 代码行数 | 变更 200 行以上 | +1 |
| 依赖关系 | 跨模块依赖 | +1 |
| 测试复杂度 | 需要集成测试 | +1 |

**阈值**: 总分 ≥ 3 时自动注入 ultrathink

**关键洞察**:
- **智能模式选择**: 根据任务数量自动选择最优执行模式
- **明确的阈值**: 1 件 Solo, 2-3 件 Parallel, 4+ 件 Breezing
- **Codex 不自动**: 避免依赖外部工具，需明确指定
- **Effort 自适应**: 根据任务复杂度自动调整思考深度
- **可恢复性**: 支持会话恢复（--resume）

### 3. harness-review（审查技能）

**核心功能**:
- 统合了 4 个旧技能：harness-review, codex-review, verify, troubleshoot
- 多角度代码/计划/范围审查
- 支持双重审查（Claude + Codex）
- 专门的安全审查模式

**审查类型自动判定**:

| 前置活动 | 审查类型 | 观点 |
|---------|---------|------|
| `harness-work` 后 | **Code Review** | Security, Performance, Quality, Accessibility, AI Residuals |
| `harness-plan` 后 | **Plan Review** | Clarity, Feasibility, Dependencies, Acceptance |
| 任务添加后 | **Scope Review** | Scope-creep, Priority, Feasibility, Impact |

**命令示例**:

```bash
# 自动判定审查类型
harness-review

# 强制代码审查
harness-review code

# 强制计划审查
harness-review plan

# 强制范围分析
harness-review scope

# 双重审查（Claude + Codex）
harness-review --dual

# 安全专项审查（只读模式）
harness-review --security
```

**Code Review 流程**:

**Step 1**: 收集变更差分
```bash
git diff --name-only --diff-filter=ACMR "${BASE_REF:-HEAD~1}"
git diff ${BASE_REF:-HEAD~1} --stat
git diff ${BASE_REF:-HEAD~1} -- ${CHANGED_FILES}
```

**Step 1.5**: AI Residuals 静态扫描
```bash
# 使用 scripts/review-ai-residuals.sh 返回稳定的 JSON
AI_RESIDUALS_JSON="$(bash scripts/review-ai-residuals.sh --base-ref "${BASE_REF:-HEAD~1}")"
```

**Step 2**: 5 个观点审查

| 观点 | 检查内容 |
|------|---------|
| **Security** | SQL 注入, XSS, 机密信息泄露, 输入验证 |
| **Performance** | N+1 查询, 不必要的重渲染, 内存泄漏 |
| **Quality** | 命名, 单一职责, 测试覆盖率, 错误处理 |
| **Accessibility** | ARIA 属性, 键盘导航, 颜色对比度 |
| **AI Residuals** | mockData, dummy, fake, localhost, TODO, FIXME, it.skip, 硬编码秘密/环境依赖 URL |

**AI Residuals 严重性判定**:

| 重要度 | 代表例 | 判定思路 |
|--------|--------|---------|
| **major** | localhost/127.0.0.1/0.0.0.0 连接, it.skip/describe.skip/test.skip, 硬编码秘密, dev/staging 固定 URL | 直接导致生产事故、误配置、验证遗漏。1 件即 REQUEST_CHANGES |
| **minor** | mockData, dummy, fakeData, TODO, FIXME | 可能是残留，但不一定立即事故。建议修复但不改变 verdict |
| **recommendation** | temporary implementation, replace later, placeholder implementation 等临时实现注释 | 注释本身不能断定为 bug，但需要追踪和明确化 |

**Verdict 判定阈值**:

| 重要度 | 定义 | 对 verdict 的影响 |
|--------|------|------------------|
| **critical** | 安全漏洞、数据丢失风险、生产故障可能性 | 1 件即 → REQUEST_CHANGES |
| **major** | 功能缺陷、性能问题、可维护性严重下降 | 2 件以上 → REQUEST_CHANGES |
| **minor** | 代码风格、命名、注释不足 | 不影响 verdict，但记录建议 |

**关键洞察**:
- **自动类型判定**: 根据前置活动自动选择审查类型
- **5 观点审查**: Security, Performance, Quality, Accessibility, AI Residuals
- **AI Residuals 专项**: 静态扫描工具 + 严重性分级
- **明确的阈值**: critical 1 件或 major 2 件以上 → REQUEST_CHANGES
- **双重审查**: Claude + Codex 并行，verdict 合并
- **安全专项**: OWASP Top 10 基础，只读模式

## 核心设计模式总结

### 1. 技能统合模式

**问题**: v2 版本有 41 个 legacy skills，功能重叠，难以维护

**解决**: v3 统合为 5 个核心技能
- harness-plan（统合 3 个）
- harness-work（统合 5 个）
- harness-review（统合 4 个）
- harness-release
- harness-setup

**优势**:
- 减少认知负担
- 统一工作流
- 易于维护和扩展

### 2. 自动模式选择

**问题**: 用户不知道何时用 Solo、Parallel 还是 Breezing

**解决**: 基于任务数量自动选择
- 1 件 → Solo（最快）
- 2-3 件 → Parallel（平衡）
- 4+ 件 → Breezing（最强）

**优势**:
- 降低使用门槛
- 自动优化性能
- 保留手动覆盖能力

### 3. 多要素评分系统

**问题**: 如何判断任务是否需要深度思考（ultrathink）

**解决**: 多维度评分
- 文件数（4+ 文件 = +1）
- 代码行数（200+ 行 = +1）
- 依赖关系（跨模块 = +1）
- 测试复杂度（集成测试 = +1）
- 总分 ≥ 3 → 启用 ultrathink

**优势**:
- 客观量化
- 自动适应
- 避免过度或不足

### 4. 阈值驱动的 Verdict

**问题**: 审查结果主观性强，难以一致

**解决**: 明确的阈值规则
- critical 1 件 → REQUEST_CHANGES
- major 2 件以上 → REQUEST_CHANGES
- minor 不影响 verdict

**优势**:
- 决策一致性
- 可预测性
- 易于解释

### 5. 静态扫描 + LLM 判断

**问题**: 纯 LLM 判断不稳定，难以复现

**解决**: 两阶段方法
1. 静态扫描工具（scripts/review-ai-residuals.sh）返回稳定 JSON
2. LLM 基于 JSON + diff 上下文做最终判断

**优势**:
- 可复现性
- 稳定性
- 审计追踪

### 6. 对话式规划

**问题**: 一次性输入所有需求困难

**解决**: 最多 3 个问题逐步明确
1. 确认上下文
2. 询问核心需求
3. 技术调研
4. 生成计划

**优势**:
- 降低认知负担
- 渐进式明确
- 自然交互

### 7. 自动进度同步

**问题**: Plans.md 与实际实现不同步

**解决**: 多源同步
- git status / git log
- .claude/state/agent-trace.jsonl
- 自动检测差异
- 自动更新标记

**优势**:
- 减少手动维护
- 实时反映状态
- 防止遗漏

## 与理论分析的对照

### 验证的设计原则

1. **角色分离** ✅
   - Lead（协调）、Worker（执行）、Reviewer（审查）
   - Breezing 模式完整实现三方分离

2. **约束驱动** ✅
   - 13 条守护规则（虽未能运行，但代码中可见）
   - 明确的 verdict 阈值
   - AI Residuals 静态扫描

3. **声明式规则** ✅
   - SKILL.md 文件定义技能
   - allowed-tools 声明工具权限
   - argument-hint 声明参数格式

4. **自动化决策** ✅
   - 自动模式选择（Solo/Parallel/Breezing）
   - 自动审查类型判定
   - 自动 ultrathink 启用

5. **可观测性** ✅
   - agent-trace.jsonl 追踪
   - Plans.md 状态管理
   - 回顾机制（retrospective）

### 新发现的模式

1. **技能统合模式**
   - v2 的 41 个技能 → v3 的 5 个核心技能
   - 减少认知负担，统一工作流

2. **多要素评分系统**
   - 客观量化任务复杂度
   - 自动调整 effort 级别

3. **静态扫描 + LLM 判断**
   - 提高可复现性和稳定性
   - 审计追踪

4. **对话式规划**
   - 最多 3 个问题逐步明确
   - 降低一次性输入负担

## 未能验证的部分

由于编译问题，以下部分未能实际运行验证：

1. **TypeScript 核心引擎**
   - 守护规则的实际执行效果
   - SQLite 状态管理
   - Hook 系统的实际表现

2. **Worktree 隔离**
   - 并行执行的实际效果
   - 文件冲突处理
   - Git 历史管理

3. **Breezing 模式**
   - Lead/Worker/Reviewer 协作
   - 并行任务调度
   - 结果合并

4. **Plans.md 同步**
   - 自动状态更新的准确性
   - agent-trace.jsonl 的实际内容
   - 回顾机制的实际输出

5. **Dual Review**
   - Claude + Codex 并行审查
   - Verdict 合并逻辑
   - 冲突处理

## 对 MVP 设计的启示

### 1. 优先级排序

**必须实现**（核心价值）:
- 计划管理（Plans.md）
- 任务状态跟踪
- 基础代码审查
- 自动模式选择

**可以延后**（增强功能）:
- Worktree 隔离（实现复杂）
- Dual Review（依赖外部工具）
- 回顾机制（需要数据积累）
- Codex 集成（外部依赖）

**可以简化**（降低复杂度）:
- 5 个技能 → 3 个核心功能（计划、执行、审查）
- SQLite → 文件系统（降低依赖）
- 多要素评分 → 简单规则（降低复杂度）

### 2. 技术选型建议

**避免原生模块**:
- better-sqlite3 → 纯 JS 实现或文件系统
- 减少编译依赖
- 提高跨平台兼容性

**优先轻量级**:
- 文件系统 > 数据库
- Markdown > 复杂格式
- Bash 脚本 > 复杂工具链

**保持可扩展性**:
- 插件式架构
- 声明式配置
- 清晰的接口

### 3. 工作流设计

**借鉴 harness-plan**:
- 对话式需求收集（最多 3 个问题）
- 优先级矩阵（Required/Recommended/Optional）
- 状态标记系统（TODO/WIP/完了）

**借鉴 harness-work**:
- 自动模式选择（基于任务数量）
- 明确的阈值（1/2-3/4+）
- 可恢复性（会话管理）

**借鉴 harness-review**:
- 5 观点审查框架
- 明确的 verdict 阈值
- 静态扫描 + LLM 判断

### 4. 简化策略

**从 5 技能简化为 3 核心**:
1. **plan**: 计划管理 + 进度同步
2. **work**: 任务执行（Solo/Parallel）
3. **review**: 代码审查（基础版）

**从复杂状态管理简化为文件系统**:
- Plans.md（任务列表）
- .harness/state.json（简单状态）
- .harness/history/（历史记录）

**从多模式简化为两模式**:
- Solo（1-2 个任务）
- Parallel（3+ 个任务）
- 暂不实现 Breezing（复杂度高）

## 总结

虽然因为 better-sqlite3 编译问题无法实际运行 claude-code-harness，但通过深入阅读 skills-v3/ 的 SKILL.md 文件，获得了以下关键洞察：

### 核心价值

1. **技能统合**: 从 41 个技能简化为 5 个核心技能
2. **自动决策**: 基于任务数量、复杂度自动选择模式
3. **明确阈值**: 客观的 verdict 判定规则
4. **对话式交互**: 降低一次性输入负担
5. **可观测性**: 完整的状态追踪和回顾机制

### 设计模式

1. **技能统合模式**: 减少认知负担
2. **自动模式选择**: 降低使用门槛
3. **多要素评分**: 客观量化复杂度
4. **阈值驱动 Verdict**: 决策一致性
5. **静态扫描 + LLM**: 提高可复现性
6. **对话式规划**: 渐进式明确需求
7. **自动进度同步**: 减少手动维护

### 对 MVP 的指导

1. **优先轻量级**: 避免原生模块，使用文件系统
2. **简化技能数**: 5 → 3（plan/work/review）
3. **简化模式数**: 3 → 2（Solo/Parallel）
4. **保留核心价值**: 自动决策、明确阈值、对话式交互
5. **延后复杂功能**: Worktree、Dual Review、回顾机制

---

**记录时间**: 2026-04-08
**分析基于**: claude-code-harness v3.0.0 源代码
**下一步**: 基于这些洞察设计 MVP 架构
