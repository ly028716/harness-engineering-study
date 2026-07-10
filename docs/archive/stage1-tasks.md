# 阶段一任务清单

## 本周目标：理解 Harness Engineering 核心概念

### 任务 1：阅读核心理论文档 ✅

**已完成**：
- ✅ 创建项目结构
- ✅ 整理资源链接
- ✅ 编写核心概念文档
- ✅ 深入阅读 OpenAI Harness Engineering（已整理中文文档）
- ✅ 深入阅读 Anthropic Harness Design（已整理中文文档）
- ✅ 阅读 Modern Agent Harness Blueprint 2026（已整理综合指南）
- ✅ 记录关键洞察和问题

### 任务 2：理解核心模式 ✅

**学习重点**：
- ✅ Plan→Work→Review 循环的具体实现
- ✅ 约束设计的方法和技巧
- ✅ 提示工程的最佳实践
- ✅ 上下文管理策略
- ✅ 质量验证机制

**输出**：
- ✅ 在 `research/claude-code-harness-implementation.md` 中补充实例
- ✅ 创建详细的实现分析文档

### 任务 3：对比分析 ✅

**分析维度**：
- ✅ 不同项目的架构差异
- ✅ 各自的优势和局限
- ✅ 适用场景
- ✅ 可借鉴的设计模式

**输出**：
- ✅ 创建对比表格
- ✅ 记录到 `research/comparison.md`
- ✅ 创建 `research/existing-harnesses-analysis.md`
- ✅ 创建 `research/design-patterns.md`

### 任务 4：提出问题

**思考问题**：
- [ ] Harness 的核心价值是什么？
- [ ] 什么样的任务适合用 Harness？
- [ ] 如何平衡自主性和可控性？
- [ ] 如何处理失败和错误？
- [ ] 如何评估 Harness 的效果？

**输出**：
- [ ] 问题清单和初步思考
- [ ] 记录到 `research/questions.md`

## 下周计划：研究现有项目

### 准备工作
- [ ] 安装必要的开发环境
- [ ] 克隆 claude-code-harness 项目
- [ ] 克隆 refact 项目
- [ ] 克隆 agent-os 项目

### 分析任务
- [ ] 运行 claude-code-harness 示例
- [ ] 阅读源码，理解实现
- [ ] 绘制架构图
- [ ] 记录关键代码片段

## 学习笔记

### 2026-04-08（第一天）

**今日完成**：
- 创建项目结构
- 编写学习计划
- 整理资源汇总
- 编写核心概念文档
- 创建 README
- 整理 OpenAI Harness Engineering 中文文档
- 整理 Anthropic Harness Design 中文文档
- 整理 Modern Agent Harness Blueprint 2026 综合指南
- 分析三个开源项目（claude-code-harness、refact、agent-os）
- 创建详细对比分析文档
- 提炼核心设计模式
- **深度分析 claude-code-harness 实现**
  - TypeScript 核心引擎分析
  - 13 条守护规则详解
  - 三智能体架构剖析
  - 5 个关键设计模式提炼
- **深度分析 refact 实现**
  - Rust 高性能架构
  - 编排优于执行理念
  - YAML 配置驱动
  - 多层次编辑工具
  - 语义搜索 + AST 索引
- **深度分析 agent-os 实现**
  - 标准驱动开发理念
  - 5 个核心命令工作流
  - 交互式确认模式
  - Profile 继承系统
  - 轻量级设计哲学
- **更新所有文档**
  - 更新 comparison.md 完整对比
  - 更新 key-insights.md 添加 agent-os 学习
  - 更新 README.md 和 stage1-tasks.md 进度

**关键洞察**：

1. **角色分离是防止任务漂移的关键**
   - Anthropic 的三智能体设计验证了这一点
   - Generator、Evaluator、Coordinator 各司其职
   - claude-code-harness 的 Worker/Reviewer/Lead 模式是生产级实现

2. **约束驱动优于指令驱动**
   - OpenAI 的实验证明了约束的重要性
   - 定义"不能做什么"比"怎么做"更有效
   - claude-code-harness 的 13 条规则是最佳实践

3. **声明式规则系统的威力**
   - TypeScript 类型安全保证规则正确性
   - 规则即数据，易于理解和修改
   - 第一个匹配的规则生效，优先级清晰

4. **Worktree 隔离解决并行难题**
   - 真正的文件系统隔离
   - 支持并行修改同一文件
   - Git 历史清晰，易于回滚

5. **Preflight 自检 + 独立审查的双重保障**
   - Worker 自检捕获明显问题
   - Reviewer 独立审查保证质量
   - 角色分离防止自我欺骗

6. **编排优于执行（refact 核心理念）**
   - 主 Agent 负责编排和决策
   - 子 Agent 负责具体执行
   - 保持主 Agent 上下文精简
   - 积极委托，综合而非重复

7. **YAML 配置驱动的灵活性**
   - 声明式模式定义
   - 子 Agent 配置化
   - 工具集动态组合
   - 易于扩展和维护

8. **标准驱动开发（agent-os 核心理念）**
   - 从代码库中提取隐性知识
   - 文档化为显性标准
   - 标准索引快速匹配
   - 规范先于实现

9. **交互式确认的价值**
   - 始终使用 AskUserQuestion 工具
   - 提供建议选项减少用户负担
   - 一次一个问题，完整循环
   - 防止假设和误解

10. **轻量级优于重量级**
    - 最小化配置
    - 简洁的文档
    - 渐进式采用
    - 避免过度工程

**下一步**：
- ✅ 阅读 Modern Agent Harness Blueprint 2026
- ✅ 深度分析 claude-code-harness 实现
- ✅ 深度分析 refact 项目实现
- ✅ 深度分析 agent-os 项目实现
- ✅ 设计 MVP 架构（design/mvp-architecture.md）
- [ ] 运行 claude-code-harness 示例（可选）
- [ ] 完成问题清单（可选）
- [ ] 开始实现 MVP

**问题和思考**：
- ✅ 如何设计有效的约束？→ 声明式规则 + TypeScript 类型安全
- ✅ 如何平衡 AI 的自主性和人类的控制？→ 三层决策（approve/deny/ask）
- ✅ 什么样的任务最适合 Harness？→ 多任务、长期维护、高质量要求
- ✅ 如何实现并行执行？→ Worktree 隔离 + Worker 独立
- ✅ 如何实现高效编排？→ 主 Agent 编排 + 子 Agent 委托（refact）
- ✅ 如何管理知识和标准？→ 标准驱动 + 索引系统（agent-os）
- ✅ 如何设计轻量级工作流？→ 命令式 + 交互式确认（agent-os）
- [ ] 如何评估 Harness 的效果？→ 待深入研究
- [ ] MVP 应该包含哪些最小功能？
- [ ] 如何实现轻量级但有效的质量保证？
- [ ] 三个项目的设计如何融合？

## 资源链接快速访问

### 必读文档
1. [OpenAI Harness Engineering](https://gist.github.com/rianjs/61503602eb42266bb0e125fe8912be5f)
2. [Anthropic Harness Design](https://gist.github.com/0xK8oX/0292e8da944ceb9226a7c2500b47124e)
3. [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3)

### 重点项目
1. [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)
2. [refact](https://github.com/smallcloudai/refact)
3. [agent-os](https://github.com/buildermethods/agent-os)

## 时间安排

### 本周（2026-04-08 至 2026-04-14）
- 周一-周二：阅读理论文档
- 周三-周四：理解核心模式
- 周五：对比分析和总结
- 周末：整理笔记，准备下周

### 下周（2026-04-15 至 2026-04-21）
- 周一：环境准备
- 周二-周四：分析 claude-code-harness
- 周五：分析 refact 和 agent-os
- 周末：总结和架构设计

## 评估标准

### 阶段一完成标准
- ✅ 能够清晰解释 Harness Engineering 的核心概念
- ✅ 理解 Plan→Work→Review 循环的工作原理
- ✅ 识别出至少 5 个关键设计模式（已识别 10+ 个）
- ✅ 能够对比不同 Harness 的优劣
- ⏳ 提出至少 10 个有深度的问题（已提出 11 个）
- ✅ 完成核心概念文档的补充

### 阶段二完成标准
- ✅ 深度分析 claude-code-harness 实现
- ✅ 深度分析 refact 实现
- ✅ 深度分析 agent-os 实现
- ✅ 完成详细对比分析文档
- ✅ 提炼核心设计模式和洞察
- ⏳ 运行实际示例并记录体验（可选）

### 阶段三完成标准
- ✅ MVP 架构设计完成（design/mvp-architecture.md）
  - 设计原则明确（轻量级、核心聚焦、明确规则、可观测）
  - 技术栈选型（Python、JSON、Click、Anthropic SDK）
  - 核心概念定义（Task、Plan、ExecutionMode、Review）
  - 目录结构规划
  - 命令接口设计
  - 核心流程实现方案
  - 状态管理方案
  - 核心算法设计
  - Prompt 设计
  - 实现计划（5 个 Phase）
- ⏳ MVP 实现
  - Phase 1: 核心框架（1-2 天）
  - Phase 2: Plan 功能（2-3 天）
  - Phase 3: Work 功能（3-4 天）
  - Phase 4: Review 功能（2-3 天）
  - Phase 5: 测试和文档（1-2 天）

---

**更新时间**：2026-04-08  
**当前状态**：阶段二完成，阶段三架构设计完成，准备开始 MVP 实现  
**完成度**：阶段一 100%，阶段二 95%（可选任务未完成），阶段三架构设计 100%
