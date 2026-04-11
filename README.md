# Harness Engineering 学习项目

一个系统学习和实践 Harness Engineering 的项目，从理论到实践，从简单到复杂。

## 什么是 Harness Engineering？

Harness Engineering 是一种新的软件开发范式：
- **从编写代码转向编写约束** - 定义 AI 应该如何工作
- **人机协作的新模式** - 人类负责架构设计和质量把控，AI 负责具体实现
- **可持续的 AI 开发** - 通过 harness（工具链/框架）让 AI 能够长期、稳定地参与开发

## 项目结构

```
harness-engineering-study/
├── docs/                          # 文档
│   ├── learning-plan.md          # 完整学习计划
│   └── stage1-tasks.md           # 阶段一任务清单
├── design/                        # 设计文档
│   └── mvp-architecture.md       # MVP 架构设计
├── research/                      # 研究资料
│   ├── resources.md              # 资源汇总
│   ├── core-concepts.md          # 核心概念
│   ├── openai-harness-engineering-cn.md  # OpenAI 实验中文文档
│   ├── anthropic-harness-design-cn.md    # Anthropic 设计中文文档
│   ├── modern-harness-2026-cn.md # 2026 年最新实践综合指南
│   ├── existing-harnesses-analysis.md    # 现有项目分析
│   ├── comparison.md             # 项目对比分析
│   └── design-patterns.md        # 核心设计模式
├── mvp/                          # MVP 实现
│   ├── orchestrator/             # 主控制循环
│   ├── planner/                  # 任务规划器
│   ├── executor/                 # 代码执行器
│   ├── validator/                # 质量验证器
│   └── memory/                   # 上下文管理
└── examples/                     # 使用示例
```

## 学习路径

### 阶段一：理解核心概念（1-2周）
- 阅读核心资源文档
- 理解 Plan→Work→Review 循环
- 学习约束设计和提示工程

### 阶段二：研究现有实践（2-3周）
- 分析 claude-code-harness
- 研究 refact 和 agent-os
- 提取设计模式

### 阶段三：构建 MVP（3-4周）
- 设计架构
- 实现核心组件
- 测试完整流程

### 阶段四：迭代增强（4-8周）
- 智能规划
- 高级验证
- 记忆系统
- 自我改进

### 阶段五：实战应用（持续）
- 真实项目实践
- 持续优化改进

## 快速开始

### 1. 阅读文档

```bash
# 查看完整学习计划
cat docs/learning-plan.md

# 了解核心概念
cat research/core-concepts.md

# 浏览资源汇总
cat research/resources.md
```

### 2. 研究现有项目

推荐按以下顺序学习：
1. [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f) - 理解核心理念
2. [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e) - 学习设计原则
3. [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) - 分析实现

### 3. 构建 MVP

（即将开始）

## 核心资源

### 理论文档
- [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
- [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
- [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

### 开源项目
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) - Plan→Work→Review 循环
- [refact](https://github.com/smallcloudai/refact) - 端到端工程任务处理
- [agent-os](https://github.com/buildermethods/agent-os) - 规划和执行系统
- [AgentGPT](https://github.com/reworkd/AgentGPT) - 浏览器端自主 Agent
- [agno](https://github.com/agno-agi/agno) - 多智能体系统

## 关键概念

- **Harness**：控制和引导 AI 行为的框架/工具链
- **Autonomous Loop**：自主循环，AI 自主规划、执行、验证的过程
- **Plan→Work→Review**：规划→工作→审查的开发循环
- **Constraint Design**：约束设计，定义 AI 的行为边界
- **Tool Orchestration**：工具编排，协调多个工具的使用
- **Context Management**：上下文管理，维护 AI 的工作记忆

## 当前进度

**阶段一：理解核心概念** ✅ 已完成
- ✅ 项目结构创建
- ✅ 学习计划制定
- ✅ 资源汇总完成
- ✅ 核心概念文档
- ✅ OpenAI Harness Engineering 中文文档
- ✅ Anthropic Harness Design 中文文档
- ✅ Modern Harness 2026 综合指南
- ✅ 现有项目分析（claude-code-harness、refact、agent-os）
- ✅ 对比分析文档
- ✅ 核心设计模式提炼
- ✅ claude-code-harness 深度实现分析
- ✅ refact 深度实现分析
- ✅ agent-os 深度实现分析

**阶段二：研究现有实践** ✅ 已完成
- ✅ 分析 claude-code-harness 代码结构
- ✅ 理解 TypeScript 核心引擎
- ✅ 掌握守护规则系统
- ✅ 学习三智能体架构
- ✅ 分析 refact 项目（Rust 架构、工具系统、会话状态机）
- ✅ 分析 agent-os 项目（标准驱动、命令系统、Profile 继承）
- ✅ claude-code-harness 运行体验记录

**阶段三：构建 MVP** 🚧 进行中
- ✅ MVP 架构设计（design/mvp-architecture.md）
  - 设计原则：轻量级、核心功能聚焦、明确决策规则、可观测性
  - 技术栈：Python 3.11+、JSON 文件、Click CLI、Anthropic SDK
  - 3 个核心技能：plan（计划管理）、work（任务执行）、review（代码审查）
  - 自动模式选择：1-2 任务 Solo、3+ 任务 Parallel
  - 明确的 Verdict 阈值：Critical 1 或 Major 2+ → REQUEST_CHANGES
- ✅ MVP 实现 - Phase 1: 核心框架（harness-mvp/）
  - ✅ 项目结构和配置（pyproject.toml）
  - ✅ CLI 框架（Click）- `harness --version`, `harness plan create`
  - ✅ 状态管理（StateManager）- JSON 持久化到 .harness/state.json
  - ✅ Markdown 解析器（MarkdownParser）- 解析 Plans.md 格式
  - ✅ 测试覆盖率 98%（19 个测试全部通过）
  - ✅ 核心代码 98 行，零编译依赖
- ✅ MVP 实现 - Phase 2: Plan 功能（harness-mvp/）
  - ✅ 数据模型（Task, TaskStatus, Priority - dataclass + Enum）
  - ✅ 任务存储（TaskStore - JSON 持久化）
  - ✅ 历史记录（HistoryManager - 变更历史追踪）
  - ✅ Planner Agent（PlanGenerator - 任务生成）
  - ✅ CLI 命令扩展：
    - `harness plan list` - 列出所有任务
    - `harness plan show <id>` - 显示任务详情
    - `harness plan update <id> --status <status>` - 更新状态
    - `harness plan sync` - 同步 Plans.md 和状态
    - `harness plan add` - 交互式添加任务
    - `harness plan stats` - 进度统计
  - ✅ 测试覆盖率 92%（81 个测试全部通过）
- ✅ MVP 实现 - Phase 3: Work 功能（harness-mvp/）
  - ✅ 执行引擎（ExecutionEngine - 172 行）
    - Worker Agent 实现
  - ✅ 执行模式（ExecutionMode 枚举）
    - Solo 模式（1-2 任务）
    - Parallel 模式（3+ 任务）
  - ✅ 自动模式选择（select_execution_mode）
  - ✅ Git 集成（GitWorktreeManager - 131 行）
    - 工作区隔离
    - 模拟模式支持
  - ✅ CLI 命令扩展：
    - `harness work solo <id>` - 单任务执行
    - `harness work parallel` - 并行执行
    - `harness work all [N|M-K]` - 执行所有/指定任务
    - `harness work status` - 执行状态
  - ✅ 依赖关系处理（拓扑排序分批次）
  - ✅ 执行结果记录（ExecutionResult）
  - ✅ 测试覆盖率 80%（123 个测试全部通过）
- ✅ MVP 实现 - Phase 4: Review 功能（harness-mvp/）
  - ✅ Reviewer Agent（ReviewerAgent - 498 行）
    - 5 观点审查实现
  - ✅ 安全检查（Security）
    - SQL 注入、XSS、硬编码密钥、eval 使用
  - ✅ 性能检查（Performance）
    - N+1 查询、低效算法
  - ✅ 质量检查（Quality）
    - 过长函数、缺失文档、裸 except、魔法数字
  - ✅ 可访问性检查（Accessibility）
    - 缺少 alt、role、label 属性
  - ✅ AI 残留检查（AI Residuals）
    - TODO/FIXME、mock 数据、localhost、跳过的测试
  - ✅ Verdict 判定（determine_verdict）
    - Critical ≥ 1 或 Major ≥ 2 → REQUEST_CHANGES
  - ✅ CLI 命令扩展：
    - `harness review code <file>` - 审查代码文件
    - `harness review code --all` - 审查所有变更
    - `harness review plan` - 审查计划合理性
    - `harness review last` - 显示最近审查结果
  - ✅ 测试覆盖率 84%（190 个测试全部通过）
  - ✅ reviewer.py 覆盖率 100%
- ⏳ MVP 实现 - Phase 5: 测试和文档

## 贡献

这是一个个人学习项目，欢迎交流和讨论。

## 许可

MIT License

## 联系

如有问题或建议，欢迎提 Issue。

---

**开始日期**：2026-04-08
**当前阶段**：阶段三 - 构建 MVP（Phase 4 已完成）
**Phase 1 成果**：核心框架实现完成，98% 测试覆盖率，19 个测试全部通过
**Phase 2 成果**：Plan 功能实现完成，92% 测试覆盖率，81 个测试全部通过
**Phase 3 成果**：Work 功能实现完成，80% 测试覆盖率，123 个测试全部通过
**Phase 4 成果**：Review 功能实现完成，84% 测试覆盖率，190 个测试全部通过
**下一步**：实现 Phase 5 - 测试和文档（完善文档、使用指南、示例项目）
