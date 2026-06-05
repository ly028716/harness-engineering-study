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
│   ├── stage1-tasks.md           # 阶段任务清单
│   ├── quick-start.md            # 快速开始指南
│   ├── api-reference.md          # API 参考文档
│   └── phase*-completion.md      # 各阶段完成报告
├── design/                        # 设计文档
│   └── mvp-architecture.md       # MVP 架构设计
├── research/                      # 研究资料
│   ├── core-concepts.md          # 核心概念
│   ├── design-patterns.md        # 设计模式
│   ├── comparison.md             # 项目对比
│   └── *-analysis.md             # 深度分析文档
├── harness-mvp/                   # MVP 实现（核心）
│   ├── harness/                  # 核心包（14 个模块）
│   ├── tests/                    # 测试套件（272 个测试，86% 覆盖率）
│   └── README.md                 # 详细文档
└── examples/                     # 使用示例
    └── todo-app/                 # Todo App 示例项目
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

### 3. 运行 MVP

```bash
cd harness-mvp
pip install -e ".[dev]"

# 查看命令帮助
harness --help

# 创建任务并执行
harness plan add --title "Hello World" --priority REQUIRED
harness work solo 1
harness review code hello.py
```

详细说明请查看 [harness-mvp/README.md](harness-mvp/README.md) 或 [docs/quick-start.md](docs/quick-start.md)。

## 核心资源

### 理论文档
- [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
- [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
- [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

### 开源项目
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) - Plan→Work→Review 循环
- [refact](https://github.com/smallcloudai/refact) - 端到端工程任务处理
- [agent-os](https://github.com/buildermethods/agent-os) - 规划和执行系统

## 关键概念

- **Harness**：控制和引导 AI 行为的框架/工具链
- **Autonomous Loop**：自主循环，AI 自主规划、执行、验证的过程
- **Plan→Work→Review**：规划→工作→审查的开发循环
- **Constraint Design**：约束设计，定义 AI 的行为边界
- **Tool Orchestration**：工具编排，协调多个工具的使用
- **Context Management**：上下文管理，维护 AI 的工作记忆

## 当前进度

**阶段一：理解核心概念** ✅ 100%
- 核心理论文档阅读完成
- 核心概念文档编写完成
- 关键问题提炼完成

**阶段二：研究现有实践** ✅ 95%
- claude-code-harness 深度分析完成
- refact 深度分析完成
- agent-os 深度分析完成
- 对比分析文档完成
- 设计模式提炼完成

**阶段三：构建 MVP** ✅ 100%
- **Phase 1** 核心框架 ✅ — CLI、状态管理、Markdown 解析
- **Phase 2** Plan 功能 ✅ — 数据模型、任务存储、Planner Agent
- **Phase 3** Work 功能 ✅ — Solo/Parallel 执行引擎、Git 集成
- **Phase 4** Review 功能 ✅ — 5 观点审查、Verdict 判定
- **Phase 5** 文档和配置 ✅ — 中英文文档、配置系统、AI 集成

**阶段四：迭代增强** ⏳ 未开始
**阶段五：实战应用** ⏳ 未开始

### MVP 质量指标

| 指标 | 数值 |
|------|------|
| 测试数量 | 272 ✅ |
| 测试覆盖率 | 86% ✅ |
| 模块数量 | 14 |
| reviewer.py 覆盖率 | 100% ✅ |
| CLI 命令 | 18+ |
| 文档 | 中英文双版 |

## 贡献

这是一个个人学习项目，欢迎交流和讨论。

## 许可

MIT License

## 联系

如有问题或建议，欢迎提 Issue。

---

**开始日期**：2026-04-08
**最后更新**：2026-06-05
**当前阶段**：阶段三完成 ✅
**状态**：MVP 构建完成，迭代增强待开始
