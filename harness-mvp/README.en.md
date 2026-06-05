# Harness MVP

A lightweight Agent Harness MVP built with Python 3.11+ using TDD methodology. Implements the complete Plan → Work → Review loop.

## Overview

This project demonstrates how to build an Agent Harness from scratch, showcasing constraint-driven design and tool orchestration to guide AI through autonomous software development tasks.

**Core Concepts**:
- **Plan**: Intelligent task planning and decomposition
- **Work**: Automated task execution (Solo/Parallel modes)
- **Review**: 5-perspective code review (Security, Performance, Quality, Accessibility, AI Residuals)

## Quick Start

### Installation

```bash
cd harness-mvp
pip install -e ".[dev]"
```

### Basic Usage

```bash
# 1. Create a plan
harness plan add --title "Implement login" --priority REQUIRED

# 2. Execute a task
harness work solo 1

# 3. Review code
harness review code src/auth.py
```

## Features

### Phase 1: Core Framework
- ✅ CLI framework (Click)
- ✅ State management (StateManager)
- ✅ Markdown parser (MarkdownParser)

### Phase 2: Plan
- ✅ Data models (Task, TaskStatus, Priority)
- ✅ Task storage (TaskStore)
- ✅ History tracking (HistoryManager)
- ✅ Planner Agent (PlanGenerator, PlannerAgent)

### Phase 3: Work
- ✅ Execution engine (ExecutionEngine)
- ✅ Worker Agent
- ✅ Solo/Parallel execution modes
- ✅ Git workspace integration
- ✅ Dependency resolution (topological sort)

### Phase 4: Review
- ✅ Reviewer Agent
- ✅ 5-perspective review (Security, Performance, Quality, Accessibility, AI Residuals)
- ✅ Verdict determination (Critical ≥ 1 or Major ≥ 2 → REQUEST_CHANGES)
- ✅ Review report generation

### Phase 5: Configuration & AI Integration
- ✅ Configuration system (ConfigManager, Settings)
- ✅ Environment variable overrides (ANTHROPIC_API_KEY, HARNESS_AI_MODEL)
- ✅ Config CLI commands (show/set/init)
- ✅ AIClient reads AI model from config

## CLI Commands

### Plan Commands

| Command | Description |
|---------|-------------|
| `harness plan list` | List all tasks |
| `harness plan show <id>` | Show task details |
| `harness plan add` | Add a new task (interactive or parametric) |
| `harness plan update <id> --status <status>` | Update task status |
| `harness plan sync` | Sync to Plans.md |
| `harness plan stats` | Show statistics |

### Work Commands

| Command | Description |
|---------|-------------|
| `harness work solo <id>` | Execute single task in Solo mode |
| `harness work parallel` | Execute all TODO tasks in Parallel mode |
| `harness work all [N\|M-K]` | Execute tasks (all, range, or specific) |
| `harness work status` | Show execution status |

### Config Commands

| Command | Description |
|---------|-------------|
| `harness config show` | Show current configuration |
| `harness config set <key> <value>` | Update a configuration value |
| `harness config init` | Reset to default configuration |

### Review Commands

| Command | Description |
|---------|-------------|
| `harness review code <file>` | Review a code file |
| `harness review code --all` | Review all changed files |
| `harness review plan` | Review plan quality |
| `harness review last` | Show most recent review results |

## Usage Examples

### Complete Workflow

```bash
# 1. Add a task
harness plan add \
  --title "Implement user login" \
  --description "Support email and password authentication" \
  --priority REQUIRED \
  --estimate 3

# 2. List tasks
harness plan list

# 3. Execute tasks (auto-selects Solo/Parallel mode)
harness work all

# 4. Review code
harness review code src/auth.py

# 5. View statistics
harness plan stats
```

### Plan Management

```bash
# Interactive task creation
harness plan add

# Update task status
harness plan update 1 --status WIP
harness plan update 1 --status DONE
harness plan update 1 --status BLOCKED --reason "Waiting for API docs"

# Sync to Plans.md
harness plan sync
```

### Work Execution

```bash
# Solo mode (1-2 tasks)
harness work solo 1

# Parallel mode (3+ tasks)
harness work parallel

# Execute a range
harness work all 1-5

# Check execution status
harness work status
```

### Config Management

```bash
# Show current configuration
harness config show

# Change AI model
harness config set ai_model claude-opus-4-20250514

# Change execution mode
harness config set execution_mode PARALLEL

# Change max workers
harness config set max_workers 8

# Reset to defaults
harness config init
```

### Code Review

```bash
# Review a single file
harness review code src/auth.py

# Review multiple files
harness review code src/auth.py src/user.py

# Review all Python files
harness review code --all

# Review the plan
harness review plan

# View latest review
harness review last
```

## Project Structure

```
harness-mvp/
├── harness/              # Core package
│   ├── __init__.py      # Version: 0.6.0
│   ├── cli.py           # CLI entry point
│   ├── ai_client.py     # AI client
│   ├── config.py        # Configuration management
│   ├── models.py        # Data models
│   ├── store.py         # Task storage
│   ├── history.py       # History tracking
│   ├── planner.py       # Planner Agent
│   ├── executor.py      # Execution engine
│   ├── git.py           # Git integration
│   ├── reviewer.py      # Reviewer Agent
│   ├── parser.py        # Markdown parser
│   └── state.py         # State manager
├── tests/               # Test suite (272 tests, 86% coverage)
│   ├── test_cli.py
│   ├── test_cli_phase2.py
│   ├── test_cli_phase4.py
│   ├── test_cli_config.py
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
│   └── test_integration.py
├── .harness/            # Data directory
│   ├── state.json       # Current state
│   ├── tasks.json       # Task data
│   └── history/         # Event history
├── pyproject.toml       # Project configuration
├── Plans.md             # Plan file
├── README.md            # Chinese documentation
└── README.en.md         # English documentation (this file)
```

## Data Models

### Task

```python
from harness.models import Task, TaskStatus, Priority

task = Task(
    id=1,
    title="Implement login",
    description="Support email and password auth",
    status=TaskStatus.TODO,
    priority=Priority.REQUIRED,
    acceptance_criteria=["Return 200", "Return JWT token"],
    estimated_effort=3
)

# State transitions
task.start()      # TODO -> WIP
task.complete()   # WIP -> DONE
task.block("Waiting for API docs")  # WIP -> BLOCKED
```

### Issue (Review Finding)

```python
from harness.models import Issue, Severity, Category

issue = Issue(
    severity=Severity.CRITICAL,
    category=Category.SECURITY,
    message="SQL injection risk detected",
    file="src/auth.py",
    line=42,
    suggestion="Use parameterized queries"
)
```

### ReviewResult

```python
from harness.models import ReviewResult, Verdict

result = ReviewResult(
    verdict=Verdict.REQUEST_CHANGES,
    issues=[issue1, issue2],
    summary="2 critical issues need fixing"
)
```

## Core API

### TaskStore

```python
from harness.store import TaskStore
from pathlib import Path

store = TaskStore(Path(".harness"))

# CRUD operations
store.add_task(task)
store.update_task(task)
store.delete_task(1)

# Queries
task = store.get_task(1)
tasks = store.load_tasks()
wip_tasks = store.get_tasks_by_status(TaskStatus.WIP)
required_tasks = store.get_tasks_by_priority(Priority.REQUIRED)

# Statistics
stats = store.get_statistics()
# {'total': 10, 'todo': 3, 'wip': 2, 'done': 5, 'blocked': 0, 'progress_percent': 50}
```

### HistoryManager

```python
from harness.history import HistoryManager

history = HistoryManager(Path(".harness"))

# Log events
history.log_task_created(task)
history.log_task_updated(task, ["status"])
history.log_task_completed(task, duration_minutes=30)
history.log_task_blocked(task, "Waiting for API docs")

# Query events
all_events = history.get_all_events()
task_events = history.get_events_by_task(1)
recent_events = history.get_recent_events(limit=5)
```

### ReviewerAgent

```python
from harness.reviewer import ReviewerAgent

reviewer = ReviewerAgent()

# Review code
code = open("src/auth.py").read()
result = reviewer.review_code(code, "src/auth.py")

print(f"Verdict: {result.verdict.value}")
print(f"Issues: {len(result.issues)}")

for issue in result.issues:
    print(f"[{issue.severity.value}] {issue.category.value}")
    print(f"  {issue.message}")
    print(f"  {issue.file}:{issue.line}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

### ConfigManager

```python
from harness.config import ConfigManager
from pathlib import Path

manager = ConfigManager(Path(".harness"))

# Load with environment variable overrides
settings = manager.load_with_env_overrides()
print(f"AI Model: {settings.ai_model}")
print(f"Execution Mode: {settings.execution_mode.value}")
print(f"Max Workers: {settings.max_workers}")

# Update settings
manager.update(ai_model="claude-opus-4-20250514")
manager.update(max_workers=8)

# Reset to defaults
manager.reset()
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### View Coverage

```bash
pytest tests/ --cov=harness --cov-report=term-missing
```

### Test Results

- ✅ 272 tests passing
- ✅ Coverage: 86% (exceeds 80% requirement)
- ✅ reviewer.py coverage: 100%

## Tech Stack

- **Python 3.11+**
- **Click 8.1.0+** - CLI framework
- **pytest 7.4.0+** - Testing framework
- **pytest-cov 4.1.0+** - Coverage tool
- **Anthropic SDK** - AI integration (optional)

## Design Principles

1. **Lightweight**: Zero compilation dependencies, pure Python
2. **TDD-Driven**: Tests first, ensuring code quality
3. **Modular**: Clean separation of concerns
4. **Observable**: Complete history and state tracking
5. **Automated**: Smart mode selection reduces manual decisions

## Key Features

### Auto Mode Selection

```python
# 1-2 tasks → Solo mode (minimal overhead)
# 3+ tasks → Parallel mode (worker separation)
mode = select_execution_mode(tasks)
```

### Dependency Resolution

```python
# Uses topological sort for task dependencies
# Independent tasks execute in parallel batches
batches = engine.prepare_batches(tasks)
```

### Verdict Rules

```python
# Critical >= 1 → REQUEST_CHANGES
# Major >= 2 → REQUEST_CHANGES
# Otherwise → APPROVE
verdict = determine_verdict(issues)
```

## 5-Perspective Review

### 1. Security
- SQL injection risks
- XSS vulnerabilities
- Hardcoded secrets
- eval() usage

### 2. Performance
- N+1 query problems
- Inefficient algorithms

### 3. Quality
- Overly long functions (>50 lines)
- Missing docstrings
- Bare except clauses
- Magic numbers

### 4. Accessibility
- Images missing alt attributes
- div as button without role
- Form inputs without labels

### 5. AI Residuals
- TODO/FIXME comments
- Mock data
- Hardcoded localhost
- Skipped tests

## Plans.md Format

```markdown
# Plan

## Tasks

### Required

- [ ] **Task 1**: TODO task
  Task description
  - ✅ Acceptance criterion 1
  - ✅ Acceptance criterion 2
  - Estimate: 2
  - Dependencies: none

### Recommended

- [~] **Task 2**: In-progress task
  - Estimate: 3

### Optional

- [x] **Task 3**: Completed task ✅

- [!] **Task 4**: Blocked task
  - Block reason
```

## Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_reviewer.py -v

# Coverage report
pytest tests/ --cov=harness --cov-report=html
```

### Code Style

The project follows PEP 8 conventions and is developed using TDD methodology.

## License

MIT License

## Related Documentation

- [Full Learning Plan](../docs/learning-plan.md)
- [Quick Start Guide (Chinese)](../docs/quick-start.md)
- [API Reference (Chinese)](../docs/api-reference.md)
- [Phase 1 Completion Report](../docs/phase1-completion.md)
- [Phase 2 Completion Report](../docs/phase2-completion.md)
- [Phase 3 Completion Report](../docs/phase3-completion.md)
- [Phase 4 Completion Report](../docs/phase4-completion.md)
- [Phase 5 Completion Report](../docs/phase5-completion.md)
- [MVP Architecture](../design/mvp-architecture.md)

---

**Version**: 0.6.0
**Status**: All phases complete ✅
**Tests**: 272 tests, 86% coverage
