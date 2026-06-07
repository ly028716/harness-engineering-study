# Harness MVP

轻量级 Agent Harness MVP，使用 Python 3.11+ 和 TDD 方法开发。实现了完整的 Plan→Work→Review 循环。

## 项目概述

这是一个从零开始构建的 Agent Harness，展示了如何通过约束设计和工具编排来引导 AI 自主完成软件开发任务。

**核心理念**：
- **Plan**：智能任务规划和分解（含依赖可视化和关键路径分析）
- **Work**：自动化任务执行（Solo/Parallel 模式，按角色选择 AI 模型）
- **Review**：5 观点代码审查（安全、性能、质量、可访问性、AI 残留，支持增量审查和自定义规则）

## 快速开始

### 安装

```bash
cd harness-mvp
pip install -e ".[dev]"
```

### 基本使用

```bash
# 1. 创建计划
harness plan add --title "实现登录功能" --priority REQUIRED

# 2. 执行任务
harness work solo 1

# 3. 审查代码
harness review code src/auth.py
```

## 已实现功能

### Phase 1: 核心框架
- ✅ CLI 框架（Click）
- ✅ 状态管理（StateManager）
- ✅ Markdown 解析器（MarkdownParser）

### Phase 2: Plan 功能
- ✅ 数据模型（Task, TaskStatus, Priority）
- ✅ 任务存储（TaskStore）
- ✅ 历史记录（HistoryManager）
- ✅ Planner Agent（PlanGenerator, PlannerAgent）

### Phase 3: Work 功能
- ✅ 执行引擎（ExecutionEngine）
- ✅ Worker Agent（按角色选择 AI 模型）
- ✅ Solo/Parallel 执行模式
- ✅ Git 工作区集成
- ✅ 依赖关系处理（拓扑排序）

### Phase 4: Review 功能
- ✅ Reviewer Agent（支持 AI 辅助审查）
- ✅ 5 观点审查（安全、性能、质量、可访问性、AI 残留）
- ✅ Verdict 判定（Critical ≥ 1 或 Major ≥ 2 → REQUEST_CHANGES）
- ✅ 审查报告生成
- ✅ 增量代码审查（基于 Git 变更）
- ✅ 自定义审查规则（正则表达式模式匹配）

### Phase 5: 配置系统和 AI 集成
- ✅ 配置系统（ConfigManager, Settings）
- ✅ 环境变量覆盖（ANTHROPIC_API_KEY, HARNESS_AI_MODEL）
- ✅ 配置 CLI 命令（show/set/init）
- ✅ AIClient 从配置读取 AI 模型

### Phase 6: 任务模板系统
- ✅ 模板数据模型（TaskTemplate, TemplatePrompt）
- ✅ 内置模板（feature, bugfix, refactor）
- ✅ 模板存储和加载（TemplateStore）
- ✅ 模板引擎（TemplateEngine）
- ✅ 自定义模板支持（.harness/templates/）
- ✅ CLI 命令集成（plan add --template, template list/show）

### Phase 7: 高级功能
- ✅ 任务依赖可视化（Mermaid 图、关键路径分析、循环检测）
- ✅ 多 AI 模型配置（按角色分配 Worker/Reviewer/Planner 模型）
- ✅ ModelName 枚举（含成本信息和模型验证）
- ✅ 模型管理 CLI 命令（config model list/show/set）
- ✅ 性能监控（PerformanceMonitor 聚合分析）
- ✅ 模型使用统计（每模型任务数、成功率、平均耗时）
- ✅ 瓶颈任务识别（最长耗时 TOP N）
- ✅ 工作量偏差分析（估算 vs 实际）

## CLI 命令

### Plan 命令

| 命令 | 描述 |
|------|------|
| `harness plan list` | 列出所有任务 |
| `harness plan show <id>` | 显示任务详情 |
| `harness plan add` | 添加新任务（交互式或参数式） |
| `harness plan add --template <name>` | 从模板创建任务 |
| `harness plan update <id> --status <status>` | 更新任务状态 |
| `harness plan sync` | 同步到 Plans.md |
| `harness plan stats` | 显示统计信息 |
| `harness plan graph` | 显示任务依赖图（Mermaid/文本报告） |

### Template 命令

| 命令 | 描述 |
|------|------|
| `harness template list` | 列出所有可用模板 |
| `harness template show <name>` | 显示模板详细信息 |

### Work 命令

| 命令 | 描述 |
|------|------|
| `harness work solo <id>` | Solo 模式执行单个任务 |
| `harness work parallel` | Parallel 模式执行所有 TODO 任务 |
| `harness work all [N\|M-K]` | 执行所有/指定范围任务 |
| `harness work status` | 显示执行状态 |

### Config 命令

| 命令 | 描述 |
|------|------|
| `harness config show` | 显示当前配置 |
| `harness config set <key> <value>` | 更新配置项 |
| `harness config init` | 重置为默认配置 |
| `harness config model list` | 列出可用 AI 模型及成本 |
| `harness config model show` | 显示各角色模型配置 |
| `harness config model set <role> <model>` | 设置角色模型 |

### Review 命令

| 命令 | 描述 |
|------|------|
| `harness review code <file>` | 审查代码文件 |
| `harness review code --all` | 审查所有变更文件 |
| `harness review incremental` | 增量审查 Git 变更 |
| `harness review plan` | 审查计划合理性 |
| `harness review last` | 显示最近审查结果 |
| `harness review rule add <name>` | 添加自定义审查规则 |
| `harness review rule list` | 列出自定义审查规则 |
| `harness review rule remove <name>` | 删除自定义审查规则 |
| `harness review rule toggle <name>` | 启用/禁用自定义规则 |

### Performance 命令

| 命令 | 描述 |
|------|------|
| `harness performance summary` | 显示性能摘要（总耗时/成功率/瓶颈） |
| `harness performance model-usage` | 显示模型使用统计 |
| `harness performance task <id>` | 显示任务时序信息 |
| `harness performance bottlenecks` | 显示瓶颈任务（最长耗时） |
| `harness performance effort` | 显示工作量分析（估算 vs 实际） |

## 使用示例

### 完整工作流

```bash
# 1. 添加任务
harness plan add \
  --title "实现用户登录" \
  --description "支持邮箱和密码验证" \
  --priority REQUIRED \
  --estimate 3

# 2. 查看任务列表
harness plan list

# 3. 执行任务（自动选择 Solo/Parallel 模式）
harness work all

# 4. 审查代码
harness review code src/auth.py

# 5. 查看统计
harness plan stats
```

### Plan 管理

```bash
# 交互式添加任务
harness plan add

# 从模板创建任务（交互式）
harness plan add --template feature

# 从模板创建任务（非交互式）
harness plan add --template feature \
  --var feature_name="用户认证" \
  --var description="实现JWT认证"

# 列出所有模板
harness template list

# 查看模板详情
harness template show feature

# 更新任务状态
harness plan update 1 --status WIP
harness plan update 1 --status DONE
harness plan update 1 --status BLOCKED --reason "等待 API 文档"

# 同步到 Plans.md
harness plan sync
```

### Work 执行

```bash
# Solo 模式（1-2 个任务）
harness work solo 1

# Parallel 模式（3+ 个任务）
harness work parallel

# 执行指定范围
harness work all 1-5

# 查看执行状态
harness work status
```

### Config 配置

```bash
# 显示当前配置
harness config show

# 更新 AI 模型
harness config set ai_model claude-opus-4-20250514

# 更新执行模式
harness config set execution_mode PARALLEL

# 更新最大 Worker 数
harness config set max_workers 8

# 重置为默认配置
harness config init

# AI 模型管理
harness config model list          # 列出可用模型及成本
harness config model show          # 显示各角色模型配置
harness config model set worker claude-haiku-4-20250514    # Worker 用轻量模型
harness config model set reviewer claude-opus-4-20250514   # Reviewer 用最强模型
```

### Review 审查

```bash
# 审查单个文件
harness review code src/auth.py

# 审查多个文件
harness review code src/auth.py src/user.py

# 审查所有 Python 文件
harness review code --all

# 审查计划
harness review plan

# 增量审查（Git 变更）
harness review incremental              # 最近一次提交
harness review incremental --base main  # 与 main 分支对比

# 自定义审查规则
harness review rule add check-debug \
  --pattern "print\(.*\)" \
  --message "检测到调试输出" \
  --severity MAJOR

# 查看最近审查
harness review last
```

### Performance 性能监控

```bash
# 性能摘要
harness performance summary

# 模型使用统计
harness performance model-usage

# 查看单个任务时序
harness performance task 1

# 瓶颈分析
harness performance bottlenecks --top 10

# 工作量偏差分析
harness performance effort
```

## 项目结构

```
harness-mvp/
├── harness/              # 核心包
│   ├── __init__.py      # 版本：0.7.0
│   ├── cli.py           # CLI 入口点
│   ├── ai_client.py     # AI 客户端
│   ├── config.py        # 配置管理（含 ModelName 枚举）
│   ├── models.py        # 数据模型
│   ├── store.py         # 任务存储
│   ├── history.py       # 历史记录
│   ├── planner.py       # Planner Agent
│   ├── executor.py      # 执行引擎
│   ├── git.py           # Git 集成
│   ├── reviewer.py      # Reviewer Agent
│   ├── parser.py        # Markdown 解析器
│   ├── state.py         # 状态管理器
│   ├── prompts.py       # 提示词模板
│   ├── code_extractor.py # 代码块提取器
│   ├── dependency_graph.py # 依赖可视化
│   ├── custom_rules.py  # 自定义审查规则
│   ├── templates.py     # 模板引擎
│   ├── template_loader.py # 模板加载
│   └── performance.py   # 性能监控
├── tests/               # 测试套件（514 个测试）
│   ├── test_cli.py
│   ├── test_cli_phase2.py
│   ├── test_cli_phase4.py
│   ├── test_cli_config.py
│   ├── test_cli_templates.py
│   ├── test_cli_performance.py
│   ├── test_ai_integration.py
│   ├── test_models.py
│   ├── test_store.py
│   ├── test_history.py
│   ├── test_planner.py
│   ├── test_executor.py
│   ├── test_reviewer.py
│   ├── test_parser.py
│   ├── test_state.py
│   ├── test_config.py
│   ├── test_model_config.py
│   ├── test_git.py
│   ├── test_dependency_graph.py
│   ├── test_custom_rules.py
│   ├── test_incremental_review.py
│   ├── test_performance.py
│   ├── test_integration.py
│   └── test_templates.py
├── .harness/            # 数据目录
│   ├── state.json       # 当前状态
│   ├── tasks.json       # 任务数据
│   └── history/         # 历史记录
├── pyproject.toml       # 项目配置
├── Plans.md             # 计划文件
└── README.md            # 本文件
```

## 数据模型

### Task（任务）

```python
from harness.models import Task, TaskStatus, Priority

task = Task(
    id=1,
    title="实现登录功能",
    description="支持邮箱和密码验证",
    status=TaskStatus.TODO,
    priority=Priority.REQUIRED,
    acceptance_criteria=["返回 200", "返回 JWT token"],
    estimated_effort=3
)

# 状态转换
task.start()      # TODO -> WIP
task.complete()   # WIP -> DONE
task.block("等待 API 文档")  # WIP -> BLOCKED
```

### Issue（审查问题）

```python
from harness.models import Issue, Severity, Category

issue = Issue(
    severity=Severity.CRITICAL,
    category=Category.SECURITY,
    message="发现 SQL 注入风险",
    file="src/auth.py",
    line=42,
    suggestion="使用参数化查询"
)
```

### ReviewResult（审查结果）

```python
from harness.models import ReviewResult, Verdict

result = ReviewResult(
    verdict=Verdict.REQUEST_CHANGES,
    issues=[issue1, issue2],
    summary="需要修改：2 个严重问题"
)
```

## 核心 API

### 任务模板系统

#### 使用内置模板

系统提供 3 种内置模板：

1. **feature** - 功能开发任务
2. **bugfix** - Bug修复任务
3. **refactor** - 代码重构任务

```bash
# 列出所有模板
harness template list

# 查看模板详情
harness template show feature

# 使用模板创建任务（交互式）
harness plan add --template feature
```

#### 创建自定义模板

自定义模板文件存放在 `.harness/templates/` 目录，使用 JSON 格式。

**模板 JSON 格式**：

```json
{
  "name": "template-name",
  "title": "任务标题 {variable_name}",
  "description": "任务描述\n可以包含多个 {variables}",
  "priority": "REQUIRED|RECOMMENDED|OPTIONAL",
  "estimated_effort": 1-5,
  "acceptance_criteria": [
    "验收标准 1",
    "验收标准 2"
  ],
  "prompts": [
    {
      "key": "variable_name",
      "question": "提示用户的问题",
      "required": true,
      "multiline": false,
      "default": "默认值（可选）"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 模板唯一标识符，仅包含字母、数字、下划线、连字符 |
| `title` | string | 是 | 任务标题，可包含 `{variable}` 占位符 |
| `description` | string | 是 | 任务描述，可包含 `{variable}` 占位符和 Markdown 格式 |
| `priority` | string | 是 | 优先级：REQUIRED / RECOMMENDED / OPTIONAL |
| `estimated_effort` | number | 是 | 估算工作量，范围 1-5 |
| `acceptance_criteria` | array | 否 | 验收标准列表 |
| `prompts` | array | 是 | 变量提示配置，至少包含一个 |

**Prompt 字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `key` | string | 是 | 变量名，必须是有效的标识符（字母、数字、下划线） |
| `question` | string | 是 | 提示用户的问题文本 |
| `required` | boolean | 否 | 是否必填，默认 true |
| `multiline` | boolean | 否 | 是否支持多行输入，默认 false |
| `default` | string | 否 | 默认值，仅对非必填字段有效 |

**自定义模板示例**：

`.harness/templates/documentation.json`:

```json
{
  "name": "documentation",
  "title": "编写 {document_name} 文档",
  "description": "### 文档内容\n{content}\n\n### 目标读者\n{audience}\n\n### 验收标准\n- [ ] 文档结构清晰\n- [ ] 示例代码完整\n- [ ] 经过审校",
  "priority": "OPTIONAL",
  "estimated_effort": 1,
  "acceptance_criteria": [
    "文档结构清晰",
    "示例代码完整",
    "经过审校"
  ],
  "prompts": [
    {
      "key": "document_name",
      "question": "请输入文档名称",
      "required": true
    },
    {
      "key": "content",
      "question": "请输入文档内容大纲",
      "required": true,
      "multiline": true
    },
    {
      "key": "audience",
      "question": "请输入目标读者",
      "required": false,
      "default": "开发者"
    }
  ]
}
```

**使用自定义模板**：

```bash
# 创建模板目录
mkdir -p .harness/templates

# 创建模板文件
# 编辑 .harness/templates/documentation.json

# 验证模板已加载
harness template list
# 输出应包含：
#   documentation - 编写文档任务 (自定义)

# 使用自定义模板
harness plan add --template documentation
```

**模板验证规则**：

1. **必填字段**：name, title, description, prompts
2. **name 格式**：仅包含字母、数字、下划线、连字符
3. **priority 值**：必须是 REQUIRED、RECOMMENDED 或 OPTIONAL
4. **estimated_effort 范围**：1-5 之间的整数
5. **变量一致性**：description 中的所有 `{variable}` 必须在 prompts 中定义
6. **prompt key 格式**：必须是有效的 Python 标识符（字母开头，仅包含字母、数字、下划线）

**模板加载优先级**：

1. 自定义模板（.harness/templates/*.json）
2. 内置模板（harness/template_loader.py）

如果自定义模板与内置模板同名，自定义模板会覆盖内置模板。

**错误处理**：

```bash
# 模板不存在
$ harness plan add --template nonexistent
❌ 错误: 模板 'nonexistent' 不存在
可用模板: feature, bugfix, refactor

# 模板验证失败
$ harness plan add --template invalid
❌ 错误: 模板验证失败
- 变量 {unknown_var} 未在 prompts 中定义
- estimated_effort 必须在 1-5 范围内

# 缺少必填变量（非交互式模式）
$ harness plan add --template feature --var feature_name="用户认证"
❌ 错误: 缺少必填变量: {description}
```

### TaskStore（任务存储）

```python
from harness.store import TaskStore
from pathlib import Path

store = TaskStore(Path(".harness"))

# 基本操作
store.add_task(task)
store.update_task(task)
store.delete_task(1)

# 查询
task = store.get_task(1)
tasks = store.load_tasks()
wip_tasks = store.get_tasks_by_status(TaskStatus.WIP)
required_tasks = store.get_tasks_by_priority(Priority.REQUIRED)

# 统计
stats = store.get_statistics()
# {'total': 10, 'todo': 3, 'wip': 2, 'done': 5, 'blocked': 0, 'progress_percent': 50}
```

### HistoryManager（历史记录）

```python
from harness.history import HistoryManager

history = HistoryManager(Path(".harness"))

# 记录事件
history.log_task_created(task)
history.log_task_updated(task, ["status"])
history.log_task_completed(task, duration_minutes=30)
history.log_task_blocked(task, "等待 API 文档")

# 查询事件
all_events = history.get_all_events()
task_events = history.get_events_by_task(1)
recent_events = history.get_recent_events(limit=5)
```

### ReviewerAgent（代码审查）

```python
from harness.reviewer import ReviewerAgent

reviewer = ReviewerAgent()

# 审查代码
code = open("src/auth.py").read()
result = reviewer.review_code(code, "src/auth.py")

print(f"判定：{result.verdict.value}")
print(f"问题数：{len(result.issues)}")

for issue in result.issues:
    print(f"[{issue.severity.value}] {issue.category.value}")
    print(f"  {issue.message}")
    print(f"  {issue.file}:{issue.line}")
    if issue.suggestion:
        print(f"  建议：{issue.suggestion}")
```

### 多 AI 模型配置

系统支持按角色（Worker/Reviewer/Planner）分配不同的 AI 模型，实现成本优化和任务适配。

#### 配置方式（优先级从低到高）

1. **代码默认值**：`claude-sonnet-4-20250514`
2. **config.json 文件**：`.harness/config.json`
3. **环境变量**：`HARNESS_WORKER_MODEL` 等
4. **显式参数**：`AIClient(model="...")`

#### 配置文件示例

```json
{
  "ai_model": "claude-sonnet-4-20250514",
  "worker_model": "claude-haiku-4-20250514",
  "reviewer_model": "claude-opus-4-20250514",
  "planner_model": "claude-opus-4-20250514"
}
```

#### 环境变量

```bash
export HARNESS_WORKER_MODEL=claude-haiku-4-20250514
export HARNESS_REVIEWER_MODEL=claude-opus-4-20250514
export HARNESS_PLANNER_MODEL=claude-opus-4-20250514
```

#### Python API

```python
from harness.config import ModelName, get_model_for_role, Settings

# 枚举信息
for m in ModelName.list_all():
    print(f"{m.display_name}: 输入 ${m.cost_per_1k_input}/1K, 输出 ${m.cost_per_1k_output}/1K")

# 按角色解析模型
settings = Settings(
    ai_model="claude-sonnet-4-20250514",
    worker_model="claude-haiku-4-20250514",
)
model = get_model_for_role(settings, "worker")  # → "claude-haiku-4-20250514"
model = get_model_for_role(settings, "reviewer")  # → "claude-sonnet-4-20250514"（回退到全局）
```

### PerformanceMonitor（性能监控）

```python
from harness.performance import PerformanceMonitor

monitor = PerformanceMonitor(Path(".harness"))

# 性能摘要
metrics = monitor.get_summary()
print(f"总耗时：{metrics.total_duration_minutes:.0f} 分钟")
print(f"成功率：{metrics.success_rate}%")
print(f"瓶颈任务：{len(metrics.bottleneck_tasks)} 个")

# 模型使用统计
for stat in monitor.get_model_usage():
    print(f"{stat.model_name}: {stat.task_count} 次, {stat.success_rate}% 成功率")

# 单个任务时序
timing = monitor.get_task_timing(1)
print(f"耗时：{timing['duration_minutes']} 分钟")

# 工作量分析
analysis = monitor.get_effort_analysis()
print(f"准确度：{analysis['accuracy_percent']}%")
```

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 查看覆盖率

```bash
pytest tests/ --cov=harness --cov-report=term-missing
```

### 测试结果

- ✅ 514 个测试全部通过
- ✅ 核心模块覆盖率：config.py 89%, executor.py 84%, models.py 83%, git.py 92%
- ✅ dependency_graph.py 覆盖率：97%
- ✅ reviewer.py 覆盖率：100%
- ✅ history.py 覆盖率：95%
- ✅ 涵盖：单元测试、集成测试、CLI 测试、AI 集成测试

## 技术栈

- **Python 3.11+**
- **Click 8.1.0+** - CLI 框架
- **pytest 7.4.0+** - 测试框架
- **pytest-cov 4.1.0+** - 覆盖率工具
- **Anthropic SDK** - AI 集成（可选）

## 设计原则

1. **轻量级**：零编译依赖，纯 Python 实现
2. **TDD 驱动**：测试先行，确保代码质量
3. **模块化**：清晰的职责分离
4. **可观测性**：完整的历史记录和状态追踪
5. **自动化**：智能模式选择，减少手动决策

## 核心特性

### 自动模式选择

```python
# 1-2 个任务 → Solo 模式（最小开销）
# 3+ 个任务 → Parallel 模式（Worker 分离）
mode = select_execution_mode(tasks)
```

### 依赖关系处理

```python
# 使用拓扑排序处理任务依赖
# 无依赖的任务在同一批次并行执行
batches = engine.prepare_batches(tasks)
```

### 依赖可视化

```bash
# 生成 Mermaid 依赖图
harness plan graph

# 文本分析报告（含关键路径和循环检测）
harness plan graph --output report
```

### 多 AI 模型路由

```python
# Worker → Haiku（轻量、低成本）
# Reviewer → Opus（最强推理）
# Planner → Opus（复杂规划）
# 未配置的角色自动回退到全局默认模型
model = get_model_for_role(settings, "worker")
```

### 性能监控

```bash
# 性能摘要
harness performance summary

# 模型使用统计
harness performance model-usage

# 瓶颈任务 TOP 5
harness performance bottlenecks --top 5

# 工作量偏差分析
harness performance effort
```

```python
from harness.performance import PerformanceMonitor

monitor = PerformanceMonitor(Path(".harness"))

# 聚合分析（只读，不修改任何数据）
metrics = monitor.get_summary()
model_stats = monitor.get_model_usage()
effort_analysis = monitor.get_effort_analysis()
```

### Verdict 判定

```python
# Critical >= 1 → REQUEST_CHANGES
# Major >= 2 → REQUEST_CHANGES
# 其他 → APPROVE
verdict = determine_verdict(issues)
```

## 5 观点审查

### 1. 安全检查（Security）
- SQL 注入风险
- XSS 漏洞
- 硬编码密钥
- eval() 使用

### 2. 性能检查（Performance）
- N+1 查询问题
- 低效算法

### 3. 质量检查（Quality）
- 过长函数（>50 行）
- 缺失文档字符串
- 裸 except
- 魔法数字

### 4. 可访问性检查（Accessibility）
- 图片缺少 alt 属性
- div 作为按钮缺少 role
- 表单输入缺少 label

### 5. AI 残留检查（AI Residuals）
- TODO/FIXME 注释
- mock 数据
- localhost 硬编码
- 跳过的测试

## Plans.md 格式

```markdown
# 计划

## Tasks

### Required（必需）

- [ ] **Task 1**: TODO 任务
  任务描述
  - ✅ 验收标准 1
  - ✅ 验收标准 2
  - 估算：2
  - 依赖：无

### Recommended（推荐）

- [~] **Task 2**: 进行中的任务
  - 估算：3

### Optional（可选）

- [x] **Task 3**: 已完成的任务 ✅

- [!] **Task 4**: 被阻塞的任务
  - 阻塞原因
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
# 所有测试
pytest tests/ -v

# 特定模块
pytest tests/test_reviewer.py -v

# 覆盖率
pytest tests/ --cov=harness --cov-report=html
```

### 代码风格

项目遵循 PEP 8 规范，使用 TDD 方法开发。

## 许可

MIT License

## 相关文档

- [完整学习计划](../docs/learning-plan.md)
- [快速开始指南](../docs/quick-start.md)
- [API 参考文档](../docs/api-reference.md)
- [任务状态跟踪](../docs/TASK-STATUS.md)
- [Phase 1 完成报告](../docs/phase1-completion.md)
- [Phase 2 完成报告](../docs/phase2-completion.md)
- [Phase 3 完成报告](../docs/phase3-completion.md)
- [Phase 4 完成报告](../docs/phase4-completion.md)
- [Phase 5 完成报告](../docs/phase5-completion.md)
- [MVP 架构设计](../design/mvp-architecture.md)

---

**版本**: 0.7.0
**状态**: Phase 1-7 全部完成 ✅
**测试**: 514 个测试
