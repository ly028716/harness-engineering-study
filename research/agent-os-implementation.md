# Agent OS 实现分析

> 基于标准驱动的 AI 开发工作流系统

## 项目概览

**Agent OS** 是一个轻量级的标准驱动开发系统，帮助塑造更好的规范，保持 Agent 在轻量级系统中对齐。

### 核心特点

1. **标准驱动开发**：从代码库中提取模式和约定，形成文档化标准
2. **命令式工作流**：5 个核心命令覆盖完整开发流程
3. **配置文件系统**：YAML 配置 + Markdown 文档
4. **Profile 继承**：支持多 Profile 和继承关系
5. **与 AI 工具集成**：配合 Claude Code、Cursor、Antigravity 等工具使用
6. **语言无关**：任何语言、任何框架

## 架构分析

### 1. 目录结构

```
agent-os/
├── config.yml                    # 全局配置（版本、默认 Profile）
├── commands/                     # 命令定义
│   └── agent-os/
│       ├── discover-standards.md    # 发现标准
│       ├── inject-standards.md      # 注入标准
│       ├── index-standards.md       # 索引标准
│       ├── shape-spec.md            # 塑造规范
│       └── plan-product.md          # 产品规划
├── profiles/                     # Profile 配置
│   └── default/
│       └── global/
│           └── tech-stack.md     # 技术栈标准
└── scripts/                      # 安装脚本
    ├── common-functions.sh
    ├── project-install.sh        # 项目安装
    └── sync-to-profile.sh        # 同步到 Profile
```

### 2. 项目内结构（安装后）

```
your-project/
├── agent-os/
│   ├── product/                  # 产品文档
│   │   ├── mission.md            # 产品使命
│   │   ├── roadmap.md            # 产品路线图
│   │   └── tech-stack.md         # 技术栈
│   ├── standards/                # 标准文档
│   │   ├── index.yml             # 标准索引
│   │   ├── root/                 # 根级标准
│   │   ├── api/                  # API 标准
│   │   ├── database/             # 数据库标准
│   │   └── frontend/             # 前端标准
│   └── specs/                    # 规范文档
│       └── YYYY-MM-DD-HHMM-feature-slug/
│           ├── plan.md           # 完整计划
│           ├── shape.md          # 塑造笔记
│           ├── standards.md      # 应用的标准
│           ├── references.md     # 参考实现
│           └── visuals/          # 视觉稿
└── .claude/
    └── commands/                 # Claude 命令（符号链接）
        └── agent-os/
```

## 核心设计模式

### 1. 标准驱动开发

**理念**：从代码库中提取隐性知识，形成显性标准

**流程**：

```
代码库 → 发现模式 → 文档化标准 → 注入上下文 → 指导开发
```

**标准文件结构**：

```markdown
# {标准名称}

## 概述

[简要说明这个标准是什么]

## 为什么

[解释为什么采用这个模式]

## 如何应用

[具体的应用指南]

## 示例

[代码示例]

## 反模式

[不应该做什么]
```

### 2. 命令式工作流

**5 个核心命令**：

| 命令 | 用途 | 输入 | 输出 |
|------|------|------|------|
| discover-standards | 发现标准 | 代码库 + 用户确认 | standards/*.md |
| index-standards | 索引标准 | standards/*.md | standards/index.yml |
| inject-standards | 注入标准 | 上下文 + 标准索引 | 上下文增强 |
| shape-spec | 塑造规范 | 功能描述 + 标准 | specs/{timestamp-slug}/ |
| plan-product | 产品规划 | 用户回答 | product/*.md |

**命令定义格式**：

```markdown
# {命令名称}

{简要描述}

## Important Guidelines

- 使用 AskUserQuestion 工具
- 提供建议选项
- 保持轻量级

## Process

### Step 1: {步骤名称}

{详细说明}

### Step 2: {步骤名称}

...
```

### 3. 标准索引系统

**index.yml 结构**：

```yaml
folder-name:
  file-name:
    description: Brief description here
```

**示例**：

```yaml
root:
  coding-style:
    description: General coding style, formatting, linting rules
  naming:
    description: File naming, variable naming, class naming conventions

api:
  error-handling:
    description: Error codes, exception handling, error response format
  response-format:
    description: API response envelope structure, status codes, pagination

database:
  migrations:
    description: Migration file structure, naming conventions, rollback patterns
```

**索引用途**：
- 快速匹配相关标准
- 避免读取所有标准文件
- 支持自动建议

### 4. Profile 继承系统

**config.yml 配置**：

```yaml
version: 3.0
default_profile: default

profiles:
  profile-a:
    inherits_from: default
  profile-b:
    inherits_from: profile-a
```

**继承规则**：
- 子 Profile 继承父 Profile 的标准
- 子 Profile 可以覆盖父 Profile 的标准
- 支持多层继承

### 5. 规范塑造流程

**shape-spec 工作流**：

```
1. 明确构建内容
   ↓
2. 收集视觉稿
   ↓
3. 识别参考实现
   ↓
4. 检查产品上下文
   ↓
5. 浮现相关标准
   ↓
6. 生成规范文件夹名
   ↓
7. 结构化计划
   ↓
8. 完成计划
   ↓
9. 准备执行
```

**Task 1 始终是保存规范文档**：

```markdown
## Task 1: Save Spec Documentation

Create `agent-os/specs/{folder-name}/` with:

- **plan.md** — This full plan
- **shape.md** — Shaping notes
- **standards.md** — Relevant standards
- **references.md** — Reference implementations
- **visuals/** — Mockups or screenshots
```

### 6. 标准发现流程

**discover-standards 工作流**：

```
1. 确定焦点区域
   - 分析代码库结构
   - 识别 3-5 个主要区域
   - 用户选择区域
   ↓
2. 分析并呈现发现
   - 读取关键文件（5-10 个）
   - 查找模式（不寻常、有主见、部落知识、一致）
   - 用户选择要文档化的模式
   ↓
3. 询问为什么，然后起草标准
   - 对每个标准询问 1-2 个澄清问题
   - 等待用户回答
   - 起草标准
   - 用户确认
   - 创建文件
   ↓
4. 自动运行 index-standards
```

**关键原则**：
- 一次一个标准（完整循环）
- 询问"为什么"而非"是什么"
- 保持简洁（AI 可扫描）
- 提供建议选项

### 7. 标准注入机制

**三种场景**：

1. **Conversation**（对话）：
   ```
   Reading these standards into our context:
   
   ---
   
   [Full content of standard 1]
   
   ---
   
   [Full content of standard 2]
   ```

2. **Skill**（技能）：
   ```
   Include these file references in your skill:
   
   - agent-os/standards/api/response-format.md
   - agent-os/standards/api/error-handling.md
   ```

3. **Plan**（计划）：
   ```
   Include these standards in your plan's context section:
   
   - agent-os/standards/api/response-format.md
   - agent-os/standards/api/error-handling.md
   ```

**自动建议模式**：
- 读取 index.yml
- 分析工作上下文
- 匹配并建议相关标准
- 用户确认后注入

**显式模式**：
```bash
/inject-standards api                           # api/ 下所有标准
/inject-standards api/response-format           # 单个文件
/inject-standards api/response-format api/auth  # 多个文件
/inject-standards root                          # 根目录所有标准
/inject-standards root/naming                   # 根目录单个文件
```

### 8. 产品规划流程

**plan-product 工作流**：

```
1. 检查现有产品文档
   ↓
2. 收集产品愿景（mission.md）
   - 解决什么问题？
   - 为谁服务？
   - 独特之处是什么？
   ↓
3. 收集路线图（roadmap.md）
   - MVP 必备功能？
   - 发布后计划功能？
   ↓
4. 确定技术栈（tech-stack.md）
   - 检查是否有 global/tech-stack.md 标准
   - 使用标准或自定义
   ↓
5. 生成文件
```

**产品文档结构**：

```
agent-os/product/
├── mission.md      # 问题、目标用户、解决方案
├── roadmap.md      # Phase 1 MVP、Phase 2 Post-Launch
└── tech-stack.md   # Frontend、Backend、Database、Other
```

## 关键洞察

### 1. 标准即知识库

**核心理念**：将隐性的部落知识显性化

**好处**：
- 新成员快速上手
- AI Agent 理解项目约定
- 减少重复解释
- 保持一致性

**标准类型**：
- **根级标准**：通用约定（命名、代码风格）
- **领域标准**：特定领域（API、数据库、前端）
- **全局标准**：跨项目标准（技术栈）

### 2. 轻量级优于重量级

**设计原则**：
- 简洁的标准文档（AI 可扫描）
- 最小化配置
- 快速的工作流
- 渐进式采用

**避免**：
- 过度文档化
- 复杂的配置
- 强制性流程
- 一次性完成所有标准

### 3. 交互式工作流

**AskUserQuestion 工具**：
- 始终使用工具询问用户
- 提供建议选项
- 一次一个问题
- 等待用户回答

**好处**：
- 减少用户思考负担
- 提高准确性
- 保持对话流畅
- 避免假设

### 4. 规范先于实现

**shape-spec 理念**：
- 在实现前塑造规范
- 收集上下文和约束
- 识别相关标准
- 生成结构化计划

**Task 1 保存规范**：
- 确保规范被持久化
- 便于后续查找
- 支持知识积累
- 可追溯决策

### 5. 标准的可发现性

**index.yml 的价值**：
- 快速匹配（无需读取所有文件）
- 自动建议
- 保持同步
- 易于维护

**索引维护**：
- discover-standards 自动运行
- 手动运行 index-standards
- 自动清理过期条目
- 用户确认新条目描述

### 6. Profile 灵活性

**多 Profile 支持**：
- 不同项目不同标准
- 继承减少重复
- 全局标准共享
- 项目特定覆盖

**使用场景**：
- 团队级 Profile（default）
- 项目类型 Profile（rails、react）
- 客户级 Profile（client-a）

### 7. 与 AI 工具集成

**设计目标**：
- 配合 Claude Code 使用
- 支持 Cursor、Antigravity
- 语言无关
- 框架无关

**集成方式**：
- 命令符号链接到 .claude/commands/
- 标准注入到上下文
- 规范指导实现
- 产品文档提供背景

## 对比其他 Harness

### vs claude-code-harness

| 维度 | agent-os | claude-code-harness |
|------|----------|---------------------|
| 核心理念 | 标准驱动 | Plan→Work→Review 循环 |
| 架构 | 命令式工作流 | 三智能体协作 |
| 状态管理 | 文件系统（Markdown） | Plans.md + SQLite + Memory |
| 质量保证 | 标准约束 | Preflight + 独立审查 |
| 并行执行 | 不支持 | Worktree 隔离 |
| 学习曲线 | 平缓 | 中等 |
| 适用场景 | 标准化、团队协作 | 高质量要求 |

### vs refact

| 维度 | agent-os | refact |
|------|----------|--------|
| 核心理念 | 标准驱动 | 编排优于执行 |
| 架构 | 命令式工作流 | 中心化 GlobalContext |
| 语言 | Bash + Markdown | Rust |
| 工具系统 | 5 个命令 | 50+ 工具 |
| 配置方式 | YAML + Markdown | YAML 配置 |
| 性能 | 轻量级 | 高性能 |
| 适用场景 | 标准化、文档驱动 | IDE 集成、端到端任务 |

## 可借鉴的设计

### 1. 标准驱动开发

**适用场景**：需要团队协作和知识传承的项目

**实现要点**：
- 从代码库中提取模式
- 文档化为标准
- 索引系统支持快速匹配
- 注入机制增强上下文

### 2. 命令式工作流

**适用场景**：需要清晰流程的开发工作流

**实现要点**：
- 每个命令一个 Markdown 文件
- 详细的步骤说明
- 交互式用户确认
- 符号链接到 .claude/commands/

### 3. 交互式确认

**适用场景**：需要用户参与决策的场景

**实现要点**：
- 始终使用 AskUserQuestion 工具
- 提供建议选项
- 一次一个问题
- 等待用户回答

### 4. 规范塑造流程

**适用场景**：需要在实现前明确需求和约束

**实现要点**：
- 收集上下文（视觉稿、参考实现、产品文档）
- 识别相关标准
- 生成结构化计划
- Task 1 保存规范文档

### 5. Profile 继承系统

**适用场景**：多项目、多团队环境

**实现要点**：
- YAML 配置继承关系
- 子 Profile 覆盖父 Profile
- 全局标准共享
- 项目特定定制

### 6. 轻量级设计

**适用场景**：需要快速采用和低学习曲线

**实现要点**：
- 最小化配置
- 简洁的文档
- 渐进式采用
- 避免过度工程

## 总结

### 核心价值

1. **标准驱动**：从代码库中提取隐性知识，形成显性标准
2. **命令式工作流**：5 个核心命令覆盖完整开发流程
3. **交互式确认**：始终使用 AskUserQuestion 工具
4. **规范先于实现**：shape-spec 在实现前塑造规范
5. **轻量级设计**：最小化配置，快速采用
6. **Profile 灵活性**：支持多 Profile 和继承
7. **与 AI 工具集成**：配合 Claude Code 等工具使用

### 设计精髓

1. **标准即知识库**：将部落知识显性化
2. **索引系统**：快速匹配相关标准
3. **注入机制**：三种场景（对话、技能、计划）
4. **规范塑造**：Task 1 始终保存规范文档
5. **交互式工作流**：提供建议选项，减少用户负担
6. **轻量级优于重量级**：简洁、快速、渐进式

### 适用场景

**最适合**：
- 需要标准化的团队协作
- 知识传承和新成员培训
- 文档驱动的开发流程
- 多项目环境（Profile 继承）

**不太适合**：
- 需要高度自动化的场景
- 需要并行执行的复杂任务
- 需要深度 IDE 集成
- 单人快速原型开发

### 学习要点

1. **理解标准驱动**：如何从代码库中提取标准
2. **掌握命令工作流**：5 个核心命令的使用
3. **学习交互式确认**：AskUserQuestion 工具的使用
4. **实践规范塑造**：shape-spec 的完整流程
5. **配置 Profile 继承**：多项目环境的标准管理

---

**分析完成时间**：2026-04-08
**基于版本**：agent-os latest
**下一步**：综合三个项目的分析，设计 MVP 架构
