# Harness MVP

轻量级 Agent Harness MVP，使用 Python 3.11+ 和 TDD 方法开发。实现了完整的 Plan→Work→Review 循环。

## 项目概述

这是一个从零开始构建的 Agent Harness，展示了如何通过约束设计和工具编排来引导 AI 自主完成软件开发任务。

**核心理念**：
- **Plan**：智能任务规划和分解
- **Work**：自动化任务执行（Solo/Parallel 模式）
- **Review**：5 观点代码审查（安全、性能、质量、可访问性、AI 残留）

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
- ✅ Worker Agent
- ✅ Solo/Parallel 执行模式
- ✅ Git 工作区集成
- ✅ 依赖关系处理（拓扑排序）

### Phase 4: Review 功能
- ✅ Reviewer Agent
- ✅ 5 观点审查（安全、性能、质量、可访问性、AI 残留）
- ✅ Verdict 判定（Critical ≥ 1 或 Major ≥ 2 → REQUEST_CHANGES）
- ✅ 审查报告生成

## CLI 命令

### Plan 命令

| 命令 | 描述 |
|------|------|
| `harness plan list` | 列出所有任务 |
| `harness plan show <id>` | 显示任务详情 |
| `harness plan add` | 添加新任务（交互式或参数式） |
| `harness plan update <id> --status <status>` | 更新任务状态 |
| `harness plan sync` | 同步到 Plans.md |
| `harness plan stats` | 显示统计信息 |

### Work 命令

| 命令 | 描述 |
|------|------|
| `harness work solo <id>` | Solo 模式执行单个任务 |
| `harness work parallel` | Parallel 模式执行所有 TODO 任务 |
| `harness work all [N\|M-K]` | 执行所有/指定范围任务 |
| `harness work status` | 显示执行状态 |

### Review 命令

| 命令 | 描述 |
|------|------|
| `harness review code <file>` | 审查代码文件 |
| `harness review code --all` | 审查所有变更文件 |
| `harness review plan` | 审查计划合理性 |
| `harness review last` | 显示最近审查结果 |

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

# 查看最近审查
harness review last
```

## 项目结构

```
harness-mvp/
├── harness/              # 核心包
│   ├── __init__.py      # 版本：0.4.0
│   ├── cli.py           # CLI 入口点
│   ├── models.py        # 数据模型
│   ├── store.py         # 任务存储
│   ├── history.py       # 历史记录
│   ├── planner.py       # Planner Agent
│   ├── executor.py      # 执行引擎
│   ├── git.py           # Git 集成
│   ├── reviewer.py      # Reviewer Agent
│   ├── parser.py        # Markdown 解析器
│   └── state.py         # 状态管理器
├── tests/               # 测试套件（190 个测试）
│   ├── test_cli.py
│   ├── test_cli_phase2.py
│   ├── test_cli_phase4.py
│   ├── test_models.py
│   ├── test_store.py
│   ├── test_history.py
│   ├── test_planner.py
│   ├── test_executor.py
│   ├── test_reviewer.py
│   ├── test_parser.py
│   ├── test_state.py
│   └── test_integration.py
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

- ✅ 190 个测试全部通过
- ✅ 测试覆盖率：84%（超过 80% 要求）
- ✅ reviewer.py 覆盖率：100%

## 技术栈

- **Python 3.11+**
- **Click 8.1.0+** - CLI 框架
- **pytest 7.4.0+** - 测试框架
- **pytest-cov 4.1.0+** - 覆盖率工具

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
- [Phase 1 完成报告](../docs/phase1-completion.md)
- [Phase 2 完成报告](../docs/phase2-completion.md)
- [Phase 3 完成报告](../docs/phase3-completion.md)
- [Phase 4 完成报告](../docs/phase4-completion.md)
- [MVP 架构设计](../design/mvp-architecture.md)

---

**版本**: 0.4.0
**状态**: Phase 1-4 完成 ✅
**测试**: 190 个测试，84% 覆盖率
**下一步**: Phase 5 - 文档和示例
