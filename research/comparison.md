# Harness 项目对比分析

> 三个开源 Harness 项目的深度对比

## 快速对比表

| 维度 | claude-code-harness | refact | agent-os |
|------|-------------------|--------|----------|
| **语言** | TypeScript | Rust | Bash + Markdown |
| **核心理念** | Plan→Work→Review 循环 | 编排优于执行 | 标准驱动开发 |
| **架构模式** | 三智能体协作 | 中心化 GlobalContext | 命令式工作流 |
| **状态管理** | Plans.md + SQLite + Memory | 8 状态状态机 | 文件系统（Markdown） |
| **工具系统** | 13 条守护规则 | 50+ 工具动态可用性 | 5 个核心命令 |
| **并行执行** | Worktree 隔离 | Subagent 并行 | 不支持 |
| **配置方式** | TypeScript 代码 | YAML 配置 | YAML + Markdown |
| **主要优势** | 质量保证强 | 工具集成深、性能高 | 标准化程度高 |
| **适用场景** | 高质量要求项目 | IDE 深度集成、端到端任务 | 团队协作开发 |
| **学习曲线** | 中等 | 较陡 | 较平缓 |
| **扩展性** | 中等 | 高 | 很高 |
| **自动化程度** | 高 | 很高 | 中等 |
| **人工介入** | 阶段性审查 | 异常时介入 | 持续参与 |

## 详细对比

### 1. 架构设计

#### claude-code-harness

**模式**：三智能体协作
```
Lead (协调) ←→ Worker (执行) ←→ Reviewer (审查)
```

**特点**：
- 角色分离清晰
- Lead 负责协调和决策
- Worker 专注执行
- Reviewer 独立审查
- 通过计划文档通信

**优势**：
- 职责明确，不易混淆
- 质量控制严格
- 防止自我欺骗
- 适合需要审查的场景

**劣势**：
- 需要三个 Agent 实例
- 通信开销
- 可能存在理解偏差

#### refact

**模式**：中心化编排 + 子 Agent 委托
```
Main Agent (编排) → Subagent 1 (执行任务 A)
                   → Subagent 2 (执行任务 B)
                   → Subagent 3 (执行任务 C)
```

**特点**：
- GlobalContext 中心化状态管理
- 主 Agent 负责编排和决策
- 子 Agent 负责具体执行
- 8 状态会话状态机
- 50+ 工具动态可用性检查
- YAML 配置驱动

**优势**：
- 主 Agent 上下文保持精简
- 子 Agent 可并行执行
- 工具集成强大（HTTP + LSP）
- 执行效率高（Rust 性能）
- 配置灵活（YAML）
- 跨编辑器支持

**劣势**：
- 架构较复杂
- 学习成本高（Rust + 异步）
- 依赖特定工具链

#### agent-os

**模式**：命令式工作流
```
命令 → 交互式确认 → 文档生成 → 标准注入
```

**特点**：
- 5 个核心命令（discover-standards, inject-standards, index-standards, shape-spec, plan-product）
- 每个命令一个 Markdown 文件定义
- 交互式用户确认（AskUserQuestion）
- 标准驱动开发流程
- Profile 继承系统

**优势**：
- 轻量级设计
- 学习曲线平缓
- 标准化程度高
- 适合团队协作
- 易于扩展和定制

**劣势**：
- 不支持并行执行
- 需要持续人工参与
- 自动化程度较低
- 不适合快速原型

### 2. 工作流程

#### claude-code-harness

**流程**：
```
1. Plan 阶段
   - 创建计划
   - 自我评估 (100分制)
   - 识别缺陷
   - 改进计划
   
2. Work 阶段
   - 实现功能
   - 编写测试
   - 运行验证
   
3. Review 阶段
   - 质量检查
   - 决策：通过/返工
```

**特点**：
- 三阶段清晰分离
- 量化评估标准
- 缺陷驱动改进
- 迭代优化

#### refact

**流程**：
```
1. 理解任务
   - 读取用户请求
   - 检查自动注入的上下文（memories, trajectories）
   - 分解为独立子任务
   
2. 委托探索（Delegate exploration to subagent）
   - "查找符号 X 的所有用法" → subagent with search_symbol_usages, cat
   - "理解模块 Y 如何工作" → subagent with cat, tree, search_pattern
   - "查找匹配模式 Z 的文件" → subagent with search_pattern, tree
   
3. 规划（Plan when needed）
   - 简单修改：直接执行或委托单个 subagent
   - 明确修改：简要说明计划，然后委托实现
   - 重大修改：发布要点摘要，询问"看起来对吗？"
   - 多文件修改：并行生成 subagents 进行独立文件更新
   
4. 实现（Implement without Delegation）
   - 不要将文件修改委托给 subagents
   - 自己执行计划
   
5. 验证（Validate via Delegation）
   - 委托测试运行：subagent(task="运行测试并报告失败", tools="shell,cat")
   - 对于重大修改，运行 code_review() 检查 bug、缺失测试和代码质量
   - 审查结果并决定下一步
   - 迭代直到成功或向用户解释阻塞
```

**特点**：
- 编排优于执行（主 Agent 编排，子 Agent 执行）
- 积极委托（有疑问时使用 subagent）
- 综合而非重复（总结洞察，不要回显完整输出）
- 失败时适应（分析原因，尝试不同方法）
- 任务进度跟踪（tasks_set 显示进度）

#### agent-os

**流程**：
```
1. 发现标准（discover-standards）
   - 确定焦点区域
   - 分析并呈现发现
   - 询问为什么，然后起草标准
   - 自动运行 index-standards

2. 塑造规范（shape-spec）
   - 明确构建内容
   - 收集视觉稿
   - 识别参考实现
   - 检查产品上下文
   - 浮现相关标准
   - 生成规范文件夹名
   - 结构化计划
   - Task 1 保存规范文档

3. 注入标准（inject-standards）
   - 自动建议模式：分析上下文，匹配标准
   - 显式模式：指定标准路径
   - 三种场景：对话、技能、计划

4. 产品规划（plan-product）
   - 收集产品愿景（mission.md）
   - 收集路线图（roadmap.md）
   - 确定技术栈（tech-stack.md）
```

**特点**：
- 标准驱动开发
- 交互式确认（AskUserQuestion）
- 规范先于实现
- 文档即知识库
- 轻量级工作流

### 3. 质量保证机制

#### claude-code-harness

**机制**：
- **量化评估**：100分制评分系统
- **缺陷列表**：明确的问题清单
- **多轮改进**：迭代直到满意
- **人工审查**：关键节点人工确认

**强度**：★★★★★

**适用**：对质量要求极高的项目

#### refact

**机制**：
- **Code Review 子 Agent**：重大修改后运行，检查 bug、缺失测试、代码质量
- **Strategic Planning 子 Agent**：复杂问题的战略规划，使用 thinking 模型
- **自动文件收集**：strategic_planning 自动收集相关文件（max_files: 30）
- **测试执行工具**：委托 subagent 运行测试并报告失败
- **Git Checkpoints**：自动创建检查点，支持时间旅行和回滚
- **Knowledge 持久化**：task_done() 自动保存到知识库
- **Trajectory 搜索**：search_trajectories() 查找相关过去对话

**强度**：★★★★☆

**适用**：需要快速迭代和深度 IDE 集成的项目

#### agent-os

**机制**：
- **标准索引系统**：index.yml 快速匹配相关标准
- **标准注入**：三种场景（对话、技能、计划）增强上下文
- **规范文档**：specs/ 目录保存完整规范（plan.md, shape.md, standards.md, references.md）
- **交互式确认**：AskUserQuestion 工具持续验证
- **Profile 继承**：多层标准覆盖和继承

**强度**：★★★☆☆

**适用**：团队协作和标准化项目，重视文档和知识传承

### 4. 上下文管理

#### claude-code-harness

**策略**：
- 使用 `thoughts/` 目录
- 保存所有阶段产物
- 符号链接便于访问
- 阶段间明确传递

**优势**：
- 完整的历史记录
- 易于回溯
- 支持长期项目

#### refact

**策略**：
- LSP 提供代码上下文
- 工具集成获取项目信息
- 实时更新上下文
- 智能上下文选择

**优势**：
- 上下文丰富
- 实时性强
- 工具辅助

#### agent-os

**策略**：
- 标准文档作为上下文（standards/*.md）
- 标准索引（index.yml）快速匹配
- 规范文档持久化（specs/YYYY-MM-DD-HHMM-slug/）
- Profile 继承系统（config.yml）
- 产品文档（product/mission.md, roadmap.md, tech-stack.md）

**优势**：
- 结构化存储
- 易于共享和版本控制
- 知识积累和传承
- 标准化上下文格式
- 轻量级文件系统

### 5. 扩展性

#### claude-code-harness

**扩展点**：
- 可以添加更多评估维度
- 可以自定义工作流阶段
- 可以集成其他工具

**扩展难度**：中等

**适合扩展的方向**：
- 更复杂的评估系统
- 更多的质量检查
- 特定领域的规则

#### refact

**扩展点**：
- 插件式工具集成
- LSP 协议扩展
- 自定义命令
- 新语言支持

**扩展难度**：较高（需要理解 LSP）

**适合扩展的方向**：
- 新的编辑器支持
- 更多语言支持
- 自定义工具集成

#### agent-os

**扩展点**：
- 自定义命令（commands/agent-os/*.md）
- 新的标准类型（standards/*/）
- Profile 继承（config.yml）
- 标准模板
- 工作流组合

**扩展难度**：很低（Markdown + YAML）

**适合扩展的方向**：
- 特定领域标准（API、数据库、前端等）
- 团队特定工作流
- 新的命令定义
- 跨项目标准共享

### 6. 适用场景分析

#### claude-code-harness

**最适合**：
- ✅ 高质量要求的项目
- ✅ 需要严格审查的场景
- ✅ 复杂功能开发
- ✅ 关键业务系统

**不太适合**：
- ❌ 快速原型验证
- ❌ 探索性编程
- ❌ 简单脚本任务
- ❌ 时间紧迫的项目

**典型用例**：
- 金融系统开发
- 医疗软件开发
- 安全关键系统
- 企业级应用

#### refact

**最适合**：
- ✅ 需要深度 IDE 集成
- ✅ 多语言项目
- ✅ 快速迭代开发
- ✅ 个人开发者

**不太适合**：
- ❌ 需要严格流程控制
- ❌ 团队协作场景
- ❌ 高度定制化需求
- ❌ 特殊工具链

**典型用例**：
- 日常开发任务
- 代码重构
- Bug 修复
- 功能增强

#### agent-os

**最适合**：
- ✅ 团队协作开发
- ✅ 需要标准化的项目
- ✅ 知识传承和新成员培训
- ✅ 文档驱动的开发流程
- ✅ 多项目环境（Profile 继承）

**不太适合**：
- ❌ 个人快速原型开发
- ❌ 需要高度自动化的场景
- ❌ 需要并行执行的复杂任务
- ❌ 需要深度 IDE 集成

**典型用例**：
- 企业产品开发
- 开源项目维护
- 团队协作项目
- 标准化开发流程
- 知识库建设

### 7. 技术栈对比

#### claude-code-harness

**核心技术**：
- AI Agent 协作
- 文件系统存储
- Markdown 文档
- 评分系统

**依赖**：
- 最小依赖
- 易于部署
- 跨平台

#### refact

**核心技术**：
- Rust 2021 + Tokio 异步运行时
- HTTP (Axum) + LSP (tower-lsp) 双协议
- Tree-sitter AST 解析（7 种语言）
- SQLite + vec0 语义搜索
- LMDB/Heed 索引存储
- Git2 版本控制
- Headless Chrome 浏览器自动化
- YAML 配置系统

**依赖**：
- Rust 工具链
- LSP 客户端（IDE/编辑器）
- 可选：PostgreSQL/MySQL/Docker
- 15+ LLM 提供商之一

#### agent-os

**核心技术**：
- Bash + Markdown 命令定义
- YAML 配置系统（config.yml）
- 文件系统存储（standards/, specs/, product/）
- 标准索引（index.yml）
- Profile 继承系统

**依赖**：
- 最小依赖（Bash、文件系统）
- Claude Code 或其他 AI 工具
- Git（可选，用于版本控制）
- 易于部署和维护

### 8. 学习路径建议

#### 对于初学者

**推荐顺序**：
1. **claude-code-harness**（先学）
   - 概念清晰
   - 易于理解
   - 快速上手
   
2. **agent-os**（再学）
   - 系统化方法
   - 标准化思维
   - 团队协作
   
3. **refact**（深入）
   - 技术深度
   - 工具集成
   - 高级特性

#### 对于有经验的开发者

**推荐顺序**：
1. **refact**（先学）
   - 直接解决实际问题
   - 提升开发效率
   - 深度工具集成
   
2. **agent-os**（再学）
   - 标准化流程
   - 团队协作
   - 可扩展架构
   
3. **claude-code-harness**（参考）
   - 质量保证思路
   - 评估机制
   - 协作模式

### 9. 实践建议

#### 选择 claude-code-harness 如果：
- 你需要严格的质量控制
- 项目对可靠性要求高
- 愿意投入时间做规划和审查
- 团队规模小，沟通成本低

#### 选择 refact 如果：
- 你需要端到端的工程任务处理
- 需要深度 IDE 集成（LSP 协议）
- 项目需要多语言支持（25+ 语言）
- 需要语义搜索和 AST 索引
- 追求高性能（Rust 实现）
- 需要编排多个子任务
- 个人开发或小团队

#### 选择 agent-os 如果：
- 团队需要统一标准
- 项目长期维护
- 需要高度定制化
- 重视文档和规范

### 10. 混合使用策略

**可以组合使用**：

```
agent-os (标准和规范)
    ↓
claude-code-harness (质量保证)
    ↓
refact (日常开发)
```

**组合优势**：
- agent-os 提供标准和工作流
- claude-code-harness 保证质量
- refact 提升开发效率

**实施建议**：
1. 用 agent-os 建立项目标准
2. 用 claude-code-harness 处理关键功能
3. 用 refact 处理日常任务

## 核心设计模式提取

### 模式 1：角色分离

**来源**：claude-code-harness

**核心思想**：
- 规划和执行分离
- 评估独立于生成
- 清晰的职责边界

**应用**：
- 防止任务漂移
- 提高质量一致性
- 便于并行工作

### 模式 2：工具编排

**来源**：refact

**核心思想**：
- 深度集成开发工具
- 标准化工具接口
- 自动化工具调用

**应用**：
- 提升开发效率
- 减少手动操作
- 保证一致性

### 模式 3：规范驱动

**来源**：agent-os

**核心思想**：
- 规范先于实现
- 文档即代码
- 标准化流程

**应用**：
- 团队协作
- 知识传承
- 质量保证

### 模式 4：迭代验证

**来源**：所有项目

**核心思想**：
- 持续验证
- 快速反馈
- 自动重试

**应用**：
- 提高成功率
- 减少错误累积
- 自我修复

### 模式 5：上下文管理

**来源**：所有项目

**核心思想**：
- 结构化存储
- 分层管理
- 智能选择

**应用**：
- 长期项目支持
- 知识复用
- 决策追溯

## 总结

### 核心洞察

1. **没有银弹**
   - 每个项目都有其适用场景
   - 需要根据实际需求选择
   - 可以组合使用

2. **质量 vs 速度 vs 编排**
   - claude-code-harness 偏向质量（三智能体 + 独立审查）
   - refact 平衡速度和质量（编排 + 子 Agent 委托 + Rust 性能）
   - agent-os 偏向标准化（规范驱动）

3. **个人 vs 团队**
   - refact 适合个人和小团队（编排模式）
   - agent-os 适合团队（标准化）
   - claude-code-harness 两者皆可（灵活模式选择）

4. **简单 vs 复杂**
   - 简单任务用 refact（快速编排）
   - 复杂任务用 claude-code-harness（深度审查）或 refact（strategic_planning）
   - 长期项目用 agent-os（标准化）或 refact（knowledge + trajectory）

### 下一步行动

基于这些分析，我们的 MVP 应该：

1. **借鉴 claude-code-harness**
   - Plan→Work→Review 循环
   - 三智能体角色分离
   - 独立审查机制
   - Worktree 隔离
   - 守护规则系统

2. **借鉴 refact**
   - 编排优于执行的理念
   - 子 Agent 委托模式
   - YAML 配置驱动
   - 多层次编辑工具
   - 语义搜索 + AST 索引
   - Knowledge 持久化

3. **借鉴 agent-os**
   - 标准驱动开发理念
   - 命令式工作流设计
   - 交互式确认（AskUserQuestion）
   - 标准索引系统
   - Profile 继承机制
   - 轻量级文件系统存储

4. **创新点**
   - 更轻量级的实现（TypeScript，避免 Rust 复杂度）
   - 混合架构（三智能体 + 子 Agent 委托）
   - 更灵活的配置（YAML + TypeScript）
   - 更好的学习曲线（渐进式复杂度）

---

**参考资源**：
- [claude-code-harness](https://github.com/Chachamaru127/claude-code-harness)
- [refact](https://github.com/smallcloudai/refact)
- [agent-os](https://github.com/buildermethods/agent-os)
- [Building AI-Powered Development Harnesses](https://blakecrosley.com/guides/agent-architecture)
- [Research → Plan → Implement: The Claude Code Framework](https://www.alexkurkin.com/guides/claude-code-framework)

**文档创建时间**：2026-04-08
**状态**：完成
