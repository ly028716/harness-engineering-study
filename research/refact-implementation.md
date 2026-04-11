# Refact 实现分析

> 基于 Rust 实现的端到端 AI 软件开发 Agent

## 项目概览

**Refact** 是一个开源的 AI 软件开发 Agent，在 SWE-bench verified 中排名第一，能够端到端处理工程任务。

### 核心特点

1. **Rust 2021 实现**：高性能、类型安全的核心引擎
2. **HTTP + LSP 双协议**：支持 Web API 和 IDE 集成
3. **50+ 工具集成**：文件编辑、搜索、Web、Shell、数据库、浏览器等
4. **会话状态机**：8 种状态管理复杂的异步工作流
5. **多模式支持**：NO_TOOLS、EXPLORE、AGENT、TASK_PLANNER、TASK_AGENT
6. **15+ LLM 提供商**：Anthropic、OpenAI、DeepSeek、Gemini、Groq 等
7. **AST 索引**：7 种语言的语法树解析和跨引用链接
8. **VecDB 语义搜索**：SQLite + vec0 扩展实现 RAG
9. **Git 集成**：Shadow repos、Checkpoints、自动提交消息生成
10. **任务看板**：Kanban 风格的任务管理系统

## 架构分析

### 1. 核心架构（GlobalContext）

**中心化共享状态**：

```rust
// GlobalContext 是整个系统的中心
Arc<ARwLock<GlobalContext>>

// HTTP 服务器（Axum）和 LSP 服务器（tower-lsp）共享同一个 GlobalContext
// 12+ 后台任务通过 start_background_tasks() 启动
```

**后台任务**：
- AST 索引器
- VecDB 嵌入生成
- Git shadow 清理
- 遥测上报
- 知识图谱维护
- Trajectory 备忘录
- Agent 监控
- OAuth 令牌刷新

### 2. 源码布局

```
src/
  main.rs              — CLI 入口（--http-port, --lsp-stdin-stdout, --ast, --vecdb）
  global_context.rs    — SharedGlobalContext
  lsp.rs               — tower-lsp LanguageServer 实现
  
  http/routers/v1/     — 27+ HTTP 端点
  
  chat/                — 22+ 文件，~15K LOC
    session.rs         — 会话管理
    queue.rs           — 命令队列处理
    generation.rs      — LLM 生成流程
    tools.rs           — 工具调用执行
    trajectories.rs    — 对话历史持久化
    linearize.rs       — 消息线性化
    stream_core.rs     — SSE 流式输出
    types.rs           — 核心类型定义
  
  llm/                 — LLM 适配器（OpenAI、Anthropic 协议）
  
  tools/               — 50+ 工具实现
    file_edit/         — 文件编辑工具（7 种编辑方式）
    tool_search.rs     — 语义搜索
    tool_shell.rs      — Shell 命令执行
    tool_subagent.rs   — 子 Agent 委托
    tool_web.rs        — Web 抓取
    tool_tasks.rs      — 任务管理
  
  ast/                 — 语法树索引
    ast_indexer_thread.rs  — 后台索引线程
    ast_db.rs              — LMDB 存储
    treesitter/            — 7 种语言解析器
  
  vecdb/               — 语义搜索
    vecdb_search.rs    — SQLite vec0 查询
  
  providers/           — 15+ LLM 提供商适配
  
  integrations/        — 外部集成
    github.rs          — GitHub API
    gitlab.rs          — GitLab API
    chrome.rs          — Headless Chrome
    postgresql.rs      — PostgreSQL 连接
    mysql.rs           — MySQL 连接
    docker.rs          — Docker 操作
    pdb.rs             — Python 调试器
    mcp.rs             — MCP 协议（stdio + SSE）
  
  knowledge_graph/     — 知识图谱（petgraph DiGraph）
  
  tasks/               — Kanban 任务看板
  
  git/                 — Git 操作
    shadow.rs          — Shadow repos
    checkpoints.rs     — 检查点管理
  
  yaml_configs/        — YAML 配置系统
    defaults/modes/    — 模式定义（agent、explore、task_planner 等）
    defaults/subagents/  — 子 Agent 定义
```

## 核心设计模式

### 1. 会话状态机

**8 种状态**：

```rust
pub enum SessionState {
    Idle,                // 空闲，等待用户输入
    Generating,          // LLM 生成中
    ExecutingTools,      // 工具执行中
    Paused,              // 暂停，等待工具确认
    WaitingIde,          // 等待 IDE 响应
    WaitingUserInput,    // 等待用户输入
    Completed,           // 完成
    Error,               // 错误
}
```

**状态转换**：

```
Idle → Generating → ExecutingTools → Generating → ...
                  ↓
                Paused (需要确认)
                  ↓
                ExecutingTools → Generating
                  ↓
                Completed
```

### 2. 命令队列模式

**异步命令处理**：

```rust
pub struct ChatSession {
    command_queue: VecDeque<CommandRequest>,
    queue_processor_running: Arc<AtomicBool>,
    queue_notify: Arc<Notify>,
    // ...
}

// 命令类型
pub enum ChatCommand {
    UserMessage { content, attachments },
    SetParams { patch },
    UpdateMessage { message_id, content },
    RemoveMessage { message_id },
    TruncateMessages { keep_count },
    RetryFromIndex { index },
    Abort,
    ApproveTools { tool_call_ids },
    RejectTools { tool_call_ids },
    BranchFromChat { branch_chat_id },
    RestoreFromTrajectory { trajectory_id },
    ClearDraft,
    SetDraft { content },
    Regenerate,
}
```

**优先级处理**：
- Priority messages（优先用户消息）
- Tool decisions（工具决策）
- IDE tool results（IDE 工具结果）
- Regular commands（常规命令）

### 3. SSE 事件流模式

**实时事件推送**：

```rust
// 订阅：GET /v1/chats/subscribe?chat_id={id}
// 事件有单调递增的 seq: u64

pub enum ChatEvent {
    Snapshot { thread, runtime, messages },
    StreamStarted { message_id },
    StreamDelta { message_id, delta },
    StreamFinished { message_id },
    MessageAdded { message },
    MessageUpdated { message },
    MessageRemoved { message_id },
    MessagesTruncated { keep_count },
    ThreadUpdated { thread },
    QueueUpdated { queue_size, queued_items },
    RuntimeUpdated { runtime },
    PauseRequired { tool_calls },
}
```

**Delta 操作**：
- AppendContent
- AppendReasoning
- SetToolCalls
- SetThinkingBlocks
- AddCitation
- AddServerContentBlock
- SetUsage
- MergeExtra

### 4. 模式系统（Modes）

**5 种核心模式**：

| 模式 | 用途 | 工具集 |
|------|------|--------|
| NO_TOOLS | 纯聊天 | 无 |
| EXPLORE | 上下文收集 | 快速工具（cat、search） |
| AGENT | 自主任务执行 | 完整工具集（50+ 工具） |
| TASK_PLANNER | 任务规划 | Kanban 管理 |
| TASK_AGENT | 任务执行 | 任务卡片执行 |

**模式配置（YAML）**：

```yaml
# agent.yaml
schema_version: 8
id: agent
title: Agent
description: Full multi-step workflow with tools and editing capabilities

thread_defaults:
  include_project_info: true
  checkpoints_enabled: true
  auto_approve_editing_tools: true
  auto_approve_dangerous_commands: false

prompt: |
  You are Refact Agent, an orchestrating software engineer.
  Your primary role is to coordinate and delegate work to subagents.
  
  ## Core Philosophy: Orchestrate
  - Understand the user's request and break it into subtasks
  - Delegate subtasks to subagent() calls
  - Synthesize results, make decisions, make changes
  - Communicate progress and results to the user

tools:
  - tree
  - cat
  - search_pattern
  - search_symbol_definition
  - search_semantic
  - knowledge
  - web
  - web_search
  - shell
  - create_textdoc
  - update_textdoc
  - rm
  - mv
  - subagent
  - strategic_planning
  - code_review
  # ... 更多工具

tool_confirm:
  rules:
    - match: "tree"
      action: auto
    - match: "cat"
      action: auto
    - match: "search_*"
      action: auto
    # ... 更多规则
```

### 5. 子 Agent 委托模式

**Subagent 工具**：

```yaml
# subagent.yaml
schema_version: 2
id: subagent
title: Subagent
description: General-purpose focused subagent for delegated tasks
expose_as_tool: true

tool:
  description: Delegate a specific task to a sub-agent
  agentic: true
  allow_parallel: true
  parameters:
    - name: task
      type: string
      description: Clear description of what the subagent should do
    - name: expected_result
      type: string
      description: Description of what the successful result should look like
    - name: tools
      type: string
      description: Comma-separated list of tool names
    - name: max_steps
      type: string
      description: Maximum number of steps (default 10)

subchat:
  context_mode: bare
  stateful: true
  max_steps: 10
  model_type: light
  n_ctx: 200000
  max_new_tokens: 16000
  temperature: 0.2

messages:
  system_prompt: |
    You are a focused sub-agent executing a specific task.
    
    Guidelines:
    - Stay focused on the assigned task only
    - Use the provided tools to accomplish the task
    - Be thorough but efficient - you have a limited step budget
    - Report progress and findings clearly
    - When you achieve the expected result, summarize what you found/did
    - If you cannot complete the task, explain why and what you tried

tools:
  - tree
  - cat
  - search_pattern
  - search_symbol_definition
  - search_semantic
  - knowledge
  - web
  - web_search
```

**Strategic Planning 子 Agent**：

```yaml
# strategic_planning.yaml
schema_version: 2
id: strategic_planning
title: Strategic Planning
description: Strategic planning with file gathering phase
expose_as_tool: true

tool:
  description: Strategically plan a solution for a complex problem
  agentic: true

subchat:
  context_mode: fork
  stateful: false
  model_type: thinking
  n_ctx: 400000
  max_new_tokens: 128000
  tokens_for_rag: 200000
  reasoning_effort: high

gather_files:
  subagent: strategic_planning_gather_files
  max_files: 30

prompts:
  solver: |
    Your task is to identify and solve the problem stated in the conversation.
    
    You are an expert strategic planner. Analyze the problem comprehensively.
    Consider:
    - Technical feasibility
    - Edge cases and potential issues
    - Implementation approach
    - Testing strategy
  
  guardrails: "💿 Now confirm the plan with the user"

tools: []
```

### 6. 工具系统

**工具分类**：

```rust
// 代码库搜索工具
let codebase_search_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolAstDefinition),
    Box::new(ToolTree),
    Box::new(ToolCat),
    Box::new(ToolRegexSearch),
    Box::new(ToolSearch),
];

// 代码库修改工具
let codebase_change_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolCreateTextDoc),
    Box::new(ToolUpdateTextDoc),
    Box::new(ToolUpdateTextDocByLines),
    Box::new(ToolUpdateTextDocRegex),
    Box::new(ToolUpdateTextDocAnchored),
    Box::new(ToolApplyPatch),
    Box::new(ToolUndoTextDoc),
    Box::new(ToolRm),
    Box::new(ToolMv),
];

// Web 工具
let web_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolWeb),
    Box::new(ToolWebSearch),
];

// 系统工具
let system_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolShell),
    Box::new(ToolShellService),
    Box::new(ToolAddWorkspaceFolder),
];

// 深度分析工具
let deep_analysis_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolStrategicPlanning),
    Box::new(ToolCodeReview),
    Box::new(ToolDeepResearch),
    Box::new(ToolSubagent),
    Box::new(ToolTasksSet),
];

// 知识工具
let knowledge_tools: Vec<Box<dyn Tool + Send>> = vec![
    Box::new(ToolGetKnowledge),
    Box::new(ToolCreateKnowledge),
];
```

**工具可用性检查**：

```rust
fn tool_available(
    tool: &Box<dyn Tool + Send>,
    ast_on: bool,
    vecdb_on: bool,
    is_there_a_thinking_model: bool,
    allow_knowledge: bool,
    allow_experimental: bool,
) -> bool {
    let dependencies = tool.tool_depends_on();
    if dependencies.contains(&"ast".to_string()) && !ast_on {
        return false;
    }
    if dependencies.contains(&"vecdb".to_string()) && !vecdb_on {
        return false;
    }
    if dependencies.contains(&"thinking".to_string()) && !is_there_a_thinking_model {
        return false;
    }
    if dependencies.contains(&"knowledge".to_string()) && !allow_knowledge {
        return false;
    }
    if tool.tool_description().experimental && !allow_experimental {
        return false;
    }
    true
}
```

### 7. 文件编辑工具

**7 种编辑方式**：

1. **create_textdoc**：创建新文件
2. **update_textdoc**：完整替换文件内容
3. **update_textdoc_by_lines**：按行号编辑
4. **update_textdoc_regex**：正则表达式替换
5. **update_textdoc_anchored**：基于锚点的编辑
6. **apply_patch**：应用 unified diff patch
7. **undo_textdoc**：撤销编辑

**Undo 历史**：
- 每个文件维护编辑历史
- 支持多级撤销
- 与 Git checkpoints 集成

### 8. AST 索引系统

**支持的语言**：
- C / C++（共享解析器）
- Python
- Java
- Kotlin
- JavaScript
- Rust
- TypeScript

**两阶段索引**：

```
Phase 1: Parse + Store
  - 解析源文件生成 AST
  - 提取定义（函数、类、变量）
  - 存储到 LMDB

Phase 2: Link Cross-References
  - 链接符号引用
  - 构建调用图
  - 生成继承关系
```

**LMDB 存储结构**：

```
Key Prefixes:
  d| — 定义（definitions）
  c| — 模糊查找（fuzzy lookup）
  u| — 反向链接（back-links）
  classes| — 继承关系
```

**Skeletonizer**：
- 生成代码骨架（去除实现细节）
- 用于嵌入生成
- 减少 token 消耗

### 9. VecDB 语义搜索

**技术栈**：
- SQLite + vec0 扩展
- 余弦相似度 KNN 搜索
- 批量嵌入生成

**文件分割器**：

```rust
// Trajectory JSON：4 条消息/块
// Markdown：基于标题的分割
// 代码：基于 AST 的 token 窗口
```

**搜索流程**：

```
1. 嵌入查询文本
2. KNN 搜索（余弦相似度）
3. 拒绝低于阈值的结果
4. 归一化有用性分数
5. 返回排序结果
```

**后台线程**：
- 入队 → 分割 → 缓存检查 → 嵌入 → 存储
- 清理：保留 10 个最新表，删除 >7 天的表

### 10. Git 集成

**Shadow Repos**：
- 为每个工作区创建 shadow repo
- 自动跟踪文件变更
- 支持 diff 和 blame

**Checkpoints**：
- 自动创建检查点
- 支持恢复到任意检查点
- 与会话历史关联

**自动提交消息**：
- 基于 diff 生成提交消息
- 使用 LLM 生成描述性消息
- 支持自定义模板

### 11. 任务看板系统

**Kanban 风格**：

```
Planning → Active → Paused → Completed
                  ↓
                Abandoned
```

**任务卡片**：

```rust
pub struct TaskCard {
    pub id: String,
    pub title: String,
    pub description: String,
    pub status: TaskStatus,
    pub agent_id: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}
```

**任务工具**：
- `tasks_set`：创建/更新任务
- `task_done`：标记任务完成
- `task_spawn_agent`：为任务启动 Agent
- `task_wait_for_agents`：等待 Agent 完成
- `task_merge_agent`：合并 Agent 结果

### 12. 知识图谱

**技术栈**：
- petgraph DiGraph（有向图）
- 节点：概念、文件、符号
- 边：关系（调用、继承、引用）

**操作**：
- Builder：构建图
- Cleanup：清理过期节点
- Staleness：标记陈旧数据
- Query：查询关系

## 关键洞察

### 1. 编排优于执行

**核心理念**：主 Agent 负责编排，子 Agent 负责执行

```
Main Agent:
  - 理解用户请求
  - 分解任务
  - 委托给 subagent()
  - 综合结果
  - 做出决策
  - 执行编辑

Subagent:
  - 专注单一任务
  - 使用有限工具集
  - 有步数限制
  - 报告结果
```

**好处**：
- 主 Agent 上下文保持精简
- 子 Agent 可以并行执行
- 清晰的职责边界
- 易于调试和监控

### 2. 状态机驱动

**会话状态机**：
- 明确的状态定义
- 清晰的状态转换规则
- 异步事件驱动
- 支持暂停和恢复

**命令队列**：
- 异步命令处理
- 优先级队列
- 原子操作
- 幂等性保证

### 3. YAML 配置驱动

**模式定义**：
- 声明式配置
- 易于扩展
- 版本控制
- 热重载支持

**子 Agent 定义**：
- 工具集配置
- 系统提示
- 参数定义
- 上下文模式

### 4. 工具依赖管理

**动态工具可用性**：
- 基于依赖检查
- 运行时验证
- 优雅降级
- 实验性标志

### 5. 多层次编辑

**7 种编辑方式**：
- 适应不同场景
- 从粗粒度到细粒度
- 支持撤销
- 与 Git 集成

### 6. 语义搜索 + AST

**双重索引**：
- AST：精确的符号查找
- VecDB：语义相似搜索
- 互补优势
- 提高召回率

### 7. 实时协作

**SSE 事件流**：
- 实时状态同步
- 增量更新
- 低延迟
- 支持多客户端

### 8. 检查点系统

**时间旅行**：
- 自动检查点
- 任意恢复
- 与会话关联
- 支持分支

## 对比 claude-code-harness

| 维度 | Refact | claude-code-harness |
|------|--------|---------------------|
| 语言 | Rust | TypeScript |
| 架构 | 中心化 GlobalContext | 分布式 Hook 系统 |
| 状态管理 | 8 状态状态机 | 3 智能体角色分离 |
| 工具系统 | 50+ 工具，动态可用性 | 13 条守护规则 |
| 编辑方式 | 7 种编辑工具 | Write/Edit/Bash |
| 并行执行 | Subagent 并行 | Worktree 隔离 |
| 质量保证 | Code Review 子 Agent | Preflight + Reviewer |
| 任务管理 | Kanban 看板 | Plans.md 表格 |
| 上下文管理 | Trajectory + Knowledge Graph | Plans.md + SQLite + Memory |
| 模式系统 | 5 种模式（YAML 配置） | 3 种模式（Solo/Parallel/Breezing） |

## 可借鉴的设计

### 1. 编排模式

**适用场景**：需要分解复杂任务的 Harness

**实现要点**：
- 主 Agent 负责编排
- 子 Agent 负责执行
- 清晰的委托接口
- 结果综合机制

### 2. 状态机模式

**适用场景**：需要管理复杂异步流程

**实现要点**：
- 明确的状态定义
- 清晰的转换规则
- 事件驱动
- 支持暂停/恢复

### 3. YAML 配置系统

**适用场景**：需要灵活配置的 Harness

**实现要点**：
- 声明式配置
- 模式定义
- 工具集配置
- 系统提示模板

### 4. 工具依赖管理

**适用场景**：工具集动态变化的环境

**实现要点**：
- 依赖声明
- 运行时检查
- 优雅降级
- 实验性标志

### 5. 多层次编辑

**适用场景**：需要精细控制文件编辑

**实现要点**：
- 多种编辑粒度
- 撤销支持
- Git 集成
- 冲突处理

### 6. SSE 事件流

**适用场景**：需要实时反馈的 UI

**实现要点**：
- 增量更新
- 单调序列号
- 心跳机制
- 重连支持

### 7. 检查点系统

**适用场景**：需要支持回滚的 Harness

**实现要点**：
- 自动检查点
- 快照存储
- 恢复机制
- 分支支持

## 总结

### 核心价值

1. **编排优于执行**：主 Agent 编排，子 Agent 执行
2. **状态机驱动**：清晰的状态管理和转换
3. **YAML 配置**：声明式、易扩展的配置系统
4. **工具丰富**：50+ 工具覆盖各种场景
5. **实时协作**：SSE 事件流实现实时反馈
6. **语义搜索**：AST + VecDB 双重索引
7. **检查点系统**：支持时间旅行和回滚

### 设计精髓

1. **中心化状态**：GlobalContext 统一管理
2. **异步命令队列**：解耦命令提交和执行
3. **子 Agent 委托**：保持主 Agent 上下文精简
4. **多层次编辑**：7 种编辑方式适应不同场景
5. **动态工具可用性**：基于依赖的运行时检查
6. **模式系统**：YAML 配置驱动的行为定义
7. **实时事件流**：SSE 推送增量更新

### 适用场景

**最适合**：
- 需要编排多个子任务的复杂工作流
- 需要实时反馈的交互式应用
- 需要灵活配置的多模式系统
- 需要丰富工具集的端到端任务

**不太适合**：
- 简单的单任务执行
- 不需要实时反馈的批处理
- 工具集固定的场景

### 学习要点

1. **理解编排模式**：主 Agent 如何委托子 Agent
2. **掌握状态机**：8 种状态和转换规则
3. **学习 YAML 配置**：模式和子 Agent 定义
4. **研究工具系统**：50+ 工具的分类和依赖
5. **实践 SSE 事件流**：实时状态同步机制

---

**分析完成时间**：2026-04-08
**基于版本**：refact latest
**下一步**：分析 agent-os 项目架构
