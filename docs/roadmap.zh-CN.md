# 路线图

[English](./roadmap.md)

这份路线图是面向 GitHub 公开访客写的，重点是让别人快速理解项目接下来会往哪里走，而不是只看内部阶段记录。

## 项目方向

这个项目会继续沿着两条主线演进：

1. **研究与文档主线**
   - 让 Harness Engineering 更容易被系统学习和理解
2. **可运行 MVP 主线**
   - 提供一个轻量、实用、可参考的 Agent Harness 原型

## 已完成

### 研究基础

- 核心概念整理
- 设计模式提炼
- `claude-code-harness`、`refact`、`agent-os` 等项目对比
- 理论文档翻译与方法论总结

### MVP 核心闭环

- `plan` 任务规划与管理
- `work` 的 solo / parallel 执行模式
- `review` 多视角代码审查
- 基于文件的轻量状态管理

### 质量与可用性增强

- 核心模块测试覆盖增强
- 自定义审查规则
- 任务依赖图生成与可视化
- 基于 Git 变更的增量审查
- 任务模板与复用式工作流

## 进行中

### GitHub 展示层优化

- 更清晰的英文首页入口
- 英中分层的仓库结构
- research / design / usage 文档导航补齐
- 更适合公开访客理解的路线图与说明文案

### 上手体验优化

- 更短的首次运行路径
- 更清晰的快速开始文档
- 英文入口与中文深内容分层整理

## 计划中

### 短期

- 继续优化仓库展示面，提升 discoverability 和 stars 转化
- 增加更直观的 demo 与使用展示
- 继续梳理公开文档层级与项目叙事
- 增强示例驱动的上手体验

### 中期

- 完善按角色分配模型的配置能力
- 补强性能跟踪与瓶颈分析
- 增强执行过程可观测性
- 优化 MVP 的 CLI 体验与工程易用性

### 长期

- 在真实项目中进一步验证使用价值
- 提炼更适合团队采用的 harness 工作模式
- 增加公开案例与实战样例

## 当前不优先做的事

为了保持项目聚焦，以下方向暂时不是当前优先级：

- 把 MVP 直接做成大型生产平台
- 构建复杂的分布式执行系统
- 提前投入企业级重基础设施能力
- 直接与成熟 AI IDE 产品正面竞争

## 成功信号

如果项目在这些方面持续变好，就说明方向是对的：

- GitHub 首页更容易让人看懂
- 新用户能在 10 分钟内完成首次试用
- 作为学习资料的价值更强
- 作为轻量 harness 参考实现的复用性更高

## 相关文档

- [README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/README.zh-CN.md)
- [quick-start.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/docs/quick-start.zh-CN.md)
- [research/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/research/README.zh-CN.md)
- [design/README.zh-CN.md](/E:/IDEWorkplaces/VS/harness-engineering-study/design/README.zh-CN.md)
