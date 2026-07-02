# Harness Engineering 学习与实践项目

[English](./README.md)

一个面向中文开发者的 **Harness Engineering 学习与实践项目**，同时附带一个可运行的轻量 **Agent Harness MVP**。

## 项目定位

这个仓库不是单纯的学习笔记，也不是一套追求大而全的平台产品。它更像一个三合一项目：

- **研究资料库**：系统整理 Harness Engineering 的核心概念、设计模式和开源实践
- **方法论样板**：把 `Plan -> Work -> Review` 这类工作流拆成可理解、可复用的结构
- **轻量 MVP**：提供一个可以本地运行的 Python 原型，帮助你从概念走到实践

## 这个仓库适合谁

- 想系统理解 Harness Engineering 的开发者
- 想研究 AI 编程工作流的人
- 想做自己的 Agent Harness / AI 开发规范的团队
- 更习惯用中文阅读深度材料的工程实践者

## 仓库里有什么

### 1. 研究文档

重点包括：

- Harness Engineering 核心概念
- 设计模式提炼
- `claude-code-harness`、`refact`、`agent-os` 等项目对比
- 从理论到实现的关键洞察

推荐从这里开始：

- [research/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.md)
- [research/core-concepts.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/core-concepts.md)
- [research/key-insights.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/key-insights.md)
- [research/comparison.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/comparison.md)

### 2. 可运行的 MVP

MVP 聚焦最核心的闭环：

- `plan`：任务规划与管理
- `work`：任务执行
- `review`：代码审查

相关入口：

- [harness-mvp/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/harness-mvp/README.md)
- [design/mvp-architecture.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/mvp-architecture.md)

### 3. 文档化实践

这个项目也在尝试回答一个更实际的问题：

**如果我们不只是“用 AI 写代码”，而是把 AI 纳入一个可约束、可审查、可迭代的工程流程，应该怎么设计？**

## 快速开始

### 读研究资料

建议顺序：

1. [research/core-concepts.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/core-concepts.md)
2. [research/key-insights.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/key-insights.md)
3. [research/comparison.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/comparison.md)

### 跑 MVP

```bash
cd harness-mvp
pip install -e ".[dev]"
harness --help
```

一个最小示例：

```bash
harness plan add --title "实现登录功能" --priority REQUIRED
harness work solo 1
harness review code src/auth.py
```

详细上手说明见：

- [docs/quick-start.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.zh-CN.md)

## 仓库结构

```text
harness-engineering-study/
├── docs/          # 使用说明、阶段总结、项目文档
├── design/        # 架构设计与 MVP 设计说明
├── research/      # 研究资料、对比分析、关键洞察
├── harness-mvp/   # 可运行的轻量 Agent Harness MVP
└── examples/      # 示例项目
```

## 当前策略

这个仓库现在采用的是一套分层国际化方案：

- **英文入口负责吸引 stars**：让 GitHub 路人和海外用户快速看懂项目价值
- **中文深内容负责保留差异化优势**：保留系统化、深度化、工程化的中文研究沉淀

这意味着：

- 首页、快速开始、导航页优先补英文
- 研究文档和架构文档继续以中文深内容为主

## 文档导航

- 英文入口：
  - [README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/README.md)
  - [docs/quick-start.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.md)
  - [docs/api-reference.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.md)
  - [docs/roadmap.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/roadmap.md)
  - [research/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.md)
  - [design/README.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.md)
- 中文入口：
  - [README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/README.zh-CN.md)
  - [docs/quick-start.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.zh-CN.md)
  - [docs/api-reference.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/api-reference.zh-CN.md)
  - [docs/roadmap.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/roadmap.zh-CN.md)

## 下一步

短期会优先继续优化这些方面：

- GitHub 首页展示与英文入口体验
- 文档导航和首次上手路径
- Demo、示例和可视化展示
- 更清晰的 roadmap 与 release 叙事

## License

MIT
