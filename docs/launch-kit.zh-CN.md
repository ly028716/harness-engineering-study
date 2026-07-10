# 传播素材包

这个文档把仓库对外传播时最常用的文案整理成一个固定入口，避免每次发帖、更新仓库动态、写社区介绍时都重新组织。

核心目标不是把项目包装成“产品发布”，而是更高效地把这个仓库的价值讲清楚：

- 这是一个 Harness Engineering 学习与实践仓库
- 它不只有研究笔记，也有可运行的 Python MVP
- 它的核心叙事是 `Plan -> Work -> Review`
- 英文入口负责吸引 GitHub 流量，中文深内容负责承接真正想继续读的人

## 统一定位

对外介绍时，尽量保持这几个关键词稳定：

- **项目类型**：Harness Engineering study + runnable MVP
- **核心循环**：`Plan -> Work -> Review`
- **差异化**：英文入口友好，中文内容更深
- **适合谁**：想研究 AI 辅助工程工作流、又不想一上来就看重框架的人

## GitHub 更新文案

适合发 GitHub Discussion、Release 说明、README 改版说明，或者作为长一点的英文介绍底稿。

```text
I have been turning this repository into a more usable public learning resource for Harness Engineering.

What is inside:
- research notes across OpenAI, Anthropic, claude-code-harness, refact, and agent-os
- a runnable Python MVP built around Plan -> Work -> Review
- example scenarios that show how a harness can structure real engineering tasks

Recent improvements:
- a stronger English GitHub entry layer
- a cleaner documentation gateway
- a featured auth-flow showcase for first-time visitors

If you are exploring AI-assisted engineering workflows and want something smaller and more inspectable than a heavy framework, this repo may be useful:
https://github.com/ly028716/harness-engineering-study
```

## X / Twitter 短帖文案

适合直接发一条短帖：

```text
I have been building a public study repo around Harness Engineering:

- research across OpenAI / Anthropic / claude-code-harness / refact / agent-os
- a runnable Python MVP
- a visible Plan -> Work -> Review loop

I recently cleaned up the GitHub surface and added a stronger showcase example for first-time visitors.

If you want a small, inspectable harness-style repo instead of a heavy framework:
https://github.com/ly028716/harness-engineering-study
```

## X / Twitter 线程开头

如果你想发成 thread，可以从这段起：

```text
I have been studying Harness Engineering in public and turning the notes into a runnable repo.

What I wanted was not another abstract "AI agent" demo, but something easier to inspect:
- explicit tasks
- visible execution flow
- reviewable outputs

The repo currently includes:
1. research across OpenAI, Anthropic, claude-code-harness, refact, and agent-os
2. a lightweight Python MVP
3. example workflows like auth-flow and API refactor

The core loop is simple:
Plan -> Work -> Review

Recent work focused on making the repo easier for GitHub visitors to understand quickly, while keeping deeper Chinese content for serious learners.

Repo:
https://github.com/ly028716/harness-engineering-study
```

## 中文社区介绍文案

适合发掘金、CSDN、知乎想法、V2EX、公众号草稿，或者作为中文长帖开头。

```text
最近我在持续整理一个 Harness Engineering 学习与实践仓库：

https://github.com/ly028716/harness-engineering-study

它不是单纯的“AI 自动编程演示”，而是想把 Harness Engineering 这件事拆开来看清楚：

1. 理论层
- 对 OpenAI、Anthropic、claude-code-harness、refact、agent-os 做了研究和对比

2. 实践层
- 做了一个可运行的 Python MVP
- 核心工作流是 Plan -> Work -> Review

3. 示例层
- 不只是放概念说明，还补了更贴近真实工程任务的 example
- 比如 auth-flow、api-refactor 这样的案例

最近这轮主要做的是仓库表面优化：
- 英文入口更清楚，方便 GitHub 海外用户快速理解
- 文档入口更集中
- 示例入口更像项目官网，而不是零散笔记

如果你也在关注 AI coding agent、工程化工作流、Harness / workflow orchestration，欢迎看看，也欢迎 star / issue / discussion。
```

## 发布前小检查

- 挑一个主打案例，默认优先 `auth-flow`
- 只强调最近 1 到 2 个改动，不要一口气罗列所有历史优化
- 贴一个最合适的入口链接，不必每次都只贴仓库首页
- CTA 保持简单：`欢迎 star / issue / feedback`

## 推荐链接选择

不同对象可以配不同链接：

- 想先看仓库定位：`README.md`
- 想先看案例：`examples/auth-flow/README.md`
- 想先看实现：`harness-mvp/README.md`
- 想先看文档地图：`docs/README.md`
