# Harness Engineering 学习与实践计划

## 概述

本计划旨在帮助独立开发者系统学习和实践 Harness Engineering，从理论到实践，从简单到复杂。

## 什么是 Harness Engineering？

Harness Engineering 是一种新的软件开发范式：
- **从编写代码转向编写约束** - 定义 AI 应该如何工作
- **人机协作的新模式** - 人类负责架构设计和质量把控，AI 负责具体实现
- **可持续的 AI 开发** - 通过 harness（工具链/框架）让 AI 能够长期、稳定地参与开发

## 学习路径

### 阶段一：理解核心概念（1-2周）

**目标**：建立对 Harness Engineering 的基础理解

**学习资源**：
1. [OpenAI 的 Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f) - 0 行代码构建产品的实验
2. [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) - Plan→Work→Review 自主循环
3. [Anthropic 的 Harness 设计](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e) - 长期 AI 开发的 Harness 设计
4. [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

**任务清单**：
- [ ] 阅读 OpenAI Gist，理解 0 行代码实验的核心思想
- [ ] 研究 Plan→Work→Review 循环模式
- [ ] 学习 Anthropic 的 3 个 Harness 设计实例
- [ ] 记录核心概念和设计模式到 `research/core-concepts.md`
- [ ] 识别不同项目的共同点和差异

**关键概念**：
- 提示工程（Prompt Engineering）
- 约束设计（Constraint Design）
- 自主循环（Autonomous Loop）
- 质量把控（Quality Control）
- 上下文管理（Context Management）

### 阶段二：研究现有实践（2-3周）

**目标**：深入分析现有 Harness 项目的架构和实现

**重点项目**：
1. **claude-code-harness** - 自主开发循环
2. **refact** - 端到端工程任务处理
3. **agent-os** - 规划和执行系统

**任务清单**：
- [ ] 克隆并运行 claude-code-harness
- [ ] 分析 refact 的代码理解和生成机制
- [ ] 研究 agent-os 的规划系统设计
- [ ] 记录架构分析到 `research/existing-harnesses-analysis.md`
- [ ] 提取可复用的设计模式

**学习重点**：
- 任务分解策略
- 代码生成和验证
- 错误处理和重试机制
- 状态管理
- 工具调用和 API 集成

### 阶段三：构建 MVP Harness（3-4周）

**目标**：构建一个简单但完整的 Harness 系统

**MVP 功能**：
1. 任务接收 - 接受自然语言任务描述
2. 规划生成 - 将任务分解为可执行步骤
3. 代码生成 - 调用 Claude API 生成代码
4. 基础验证 - 语法检查、简单测试
5. 结果反馈 - 展示执行结果

**技术栈**：
- Python 3.10+
- Anthropic Claude API
- 文件系统存储
- 基础日志系统

**核心组件**：
```
mvp/
├── orchestrator/     # 主控制循环
├── planner/          # 任务规划器
├── executor/         # 代码执行器
├── validator/        # 质量验证器
└── memory/           # 上下文管理
```

**任务清单**：
- [ ] 设计架构图（`docs/architecture-design.md`）
- [ ] 实现 Orchestrator - 主控制循环
- [ ] 实现 Planner - 任务分解
- [ ] 实现 Executor - 代码生成和执行
- [ ] 实现 Validator - 基础验证
- [ ] 实现 Memory - 简单的上下文存储
- [ ] 编写使用示例
- [ ] 测试完整流程

### 阶段四：迭代增强（4-8周）

**目标**：增强 Harness 的智能性和可靠性

**增强方向**：

1. **智能规划**
   - 多步骤任务分解
   - 依赖关系识别
   - 并行执行优化

2. **高级验证**
   - 单元测试自动生成
   - 代码质量检查（linting）
   - 安全性扫描

3. **记忆系统**
   - 项目上下文管理
   - 历史决策记录
   - 模式学习和复用

4. **自我改进**
   - 错误分析和学习
   - 提示优化
   - 性能监控

5. **多智能体协作**
   - 专门化 agent（前端、后端、测试）
   - 协调机制
   - 冲突解决

### 阶段五：实战项目（持续）

**目标**：在真实项目中应用和验证 Harness

**应用场景**：
1. 个人工具开发
2. 开源项目贡献
3. 新技术学习和原型验证

**评估指标**：
- 开发速度提升
- 代码质量
- 维护成本
- 人工干预频率

## 关键成功因素

1. **渐进式学习** - 不要试图一次性理解所有概念
2. **动手实践** - 理论必须结合实践
3. **记录反思** - 记录每次实验的结果和思考
4. **社区交流** - 参与相关社区讨论
5. **持续迭代** - Harness 本身需要不断优化

## 推荐的第一步行动

- **本周内**：深入阅读 OpenAI Gist 和 Anthropic 的 Harness 设计文档
- **第二周**：克隆 claude-code-harness 项目，运行并理解其工作流程
- **第三周**：设计你自己的 MVP harness 架构图
- **第四周**：实现最简单的 Plan→Execute→Review 循环

## 学习资源

### 核心资源
- [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
- [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
- [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

### 实践项目
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)
- [refact](https://github.com/smallcloudai/refact)
- [agent-os](https://github.com/buildermethods/agent-os)
- [AgentGPT](https://github.com/reworkd/AgentGPT)
- [agno](https://github.com/agno-agi/agno)

### 技术基础
- Agent 架构设计
- 提示工程（Prompt Engineering）
- LLM 能力边界
- API 设计和集成
- 错误处理和重试策略
- 状态管理

## 进度跟踪

- 开始日期：2026-04-08
- 当前阶段：阶段一 - 理解核心概念
- 下一个里程碑：完成核心概念学习（预计 2026-04-22）

## 笔记和反思

（在学习过程中记录你的思考和发现）
