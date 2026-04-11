# Harness Engineering 资源汇总

## 核心概念文档

### 1. OpenAI 的 Harness Engineering 实验
- **链接**：https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f
- **核心思想**：0 行手写代码构建产品
- **关键点**：
  - 5 个月实验，构建内部 beta 产品
  - 完全依赖 AI 生成代码
  - 人类负责架构设计和质量把控
  - 证明了 AI 辅助开发的可行性

### 2. Anthropic 的 Harness 设计
- **链接**：https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e
- **标题**：Beyond Single Agents: Anthropic's Harness Design for Long-Running AI Development
- **核心思想**：长期 AI 开发的 Harness 设计
- **包含**：3 个实际工作示例
- **关键点**：
  - 超越单一 Agent 的设计
  - 长期运行的 AI 开发系统
  - 工具编排和自主能力

### 3. Modern Agent Harness Blueprint 2026
- **链接**：https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3
- **核心思想**：2026 年现代 Agent Harness 蓝图
- **关键点**：
  - 最新的 Harness 设计模式
  - 现代化的架构方法

## 开源项目

### 1. claude-code-harness
- **链接**：https://github.com/Chachamaru127/claude-code-harness
- **描述**：通过自主的 Plan→Work→Review 循环实现高质量开发
- **核心特性**：
  - 自主开发循环
  - 任务规划和分解
  - 代码生成和审查
  - 质量保证机制
- **适合学习**：理解完整的自主开发流程

### 2. refact (smallcloudai)
- **链接**：https://github.com/smallcloudai/refact
- **描述**：端到端处理工程任务的 AI Agent
- **核心特性**：
  - 集成开发者工具
  - 规划、执行、迭代
  - 直到成功完成任务
- **适合学习**：工具集成和任务执行

### 3. agent-os (buildermethods)
- **链接**：https://github.com/buildermethods/agent-os
- **描述**：用于更好地规划和执行软件开发任务的系统
- **核心特性**：
  - 规划系统设计
  - 执行引擎架构
  - 状态管理
- **适合学习**：系统架构和规划机制

### 4. AgentGPT (reworkd)
- **链接**：https://github.com/reworkd/AgentGPT
- **描述**：在浏览器中组装、配置和部署自主 AI Agents
- **核心特性**：
  - 浏览器端运行
  - 可视化配置
  - 自主 Agent 部署
- **适合学习**：用户界面和交互设计

### 5. agno (agno-agi)
- **链接**：https://github.com/agno-agi/agno
- **描述**：构建能够学习和改进的多智能体系统
- **核心特性**：
  - 多智能体协作
  - 学习和改进机制
  - 交互式系统
- **适合学习**：多 Agent 协作和学习机制

### 6. awesome-harness-engineering (walkinglabs)
- **链接**：https://github.com/walkinglabs/awesome-harness-engineering
- **描述**：Harness Engineering 的工具和指南集合
- **适合学习**：发现更多相关资源

## 技术调查

### Manus AI Agent 技术调查
- **链接**：https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f
- **描述**：深入技术调查 Manus AI agent
- **关键点**：
  - 架构分析
  - 工具编排
  - 自主能力

## 相关技术

### LLM 评估框架
- **EleutherAI/lm-evaluation-harness**
- **链接**：https://github.com/EleutherAI/lm-evaluation-harness
- **描述**：语言模型的少样本评估框架
- **用途**：评估和测试 LLM 能力

### CI/CD 平台
- **harness/harness**
- **链接**：https://github.com/harness/harness
- **描述**：端到端开发平台（注意：这是 CI/CD 工具，不是 AI Harness）

## 学习顺序建议

### 第一周：理论基础
1. 阅读 OpenAI Gist - 理解核心理念
2. 阅读 Anthropic Harness 设计 - 学习设计原则
3. 阅读 Modern Agent Harness Blueprint - 了解最新趋势

### 第二周：项目分析
1. 克隆 claude-code-harness，运行示例
2. 研究 refact 的代码结构
3. 分析 agent-os 的架构设计

### 第三周：动手实践
1. 设计自己的 MVP 架构
2. 实现基础的 Plan→Execute→Review 循环
3. 测试和迭代

## 关键概念索引

- **Harness**：控制和引导 AI 行为的框架/工具链
- **Autonomous Loop**：自主循环，AI 自主规划、执行、验证的过程
- **Plan→Work→Review**：规划→工作→审查的开发循环
- **Constraint Design**：约束设计，定义 AI 的行为边界
- **Tool Orchestration**：工具编排，协调多个工具的使用
- **Context Management**：上下文管理，维护 AI 的工作记忆
- **Quality Gate**：质量门禁，确保输出质量的检查点

## 社区和讨论

- GitHub Topics: https://github.com/topics/harness
- 相关 Gists 和讨论
- AI Agent 开发社区

## 更新日志

- 2026-04-08：初始资源汇总
