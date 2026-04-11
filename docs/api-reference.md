# Harness MVP API 参考文档

完整的 API 文档，涵盖所有核心类和方法。

## 目录

- [数据模型](#数据模型)
- [任务管理](#任务管理)
- [执行引擎](#执行引擎)
- [代码审查](#代码审查)
- [工具函数](#工具函数)

## 数据模型

### TaskStatus

任务状态枚举。

```python
from harness.models import TaskStatus

class TaskStatus(Enum):
    TODO = "TODO"        # 待办
    WIP = "WIP"          # 进行中
    DONE = "DONE"        # 已完成
    BLOCKED = "BLOCKED"  # 被阻塞
```

**方法**：
- `from_string(value: str) -> TaskStatus` - 从字符串创建（大小写不敏感）

### Priority

优先级枚举。

```python
from harness.models import Priority

class Priority(Enum):
    REQUIRED = "REQUIRED"          # 必需
    RECOMMENDED = "RECOMMENDED"    # 推荐
    OPTIONAL = "OPTIONAL"          # 可选
```

**方法**：
- `from_string(value: str) -> Priority` - 从字符串创建（大小写不敏感）

### Task

任务数据类。

```python
from harness.models import Task, TaskStatus, Priority
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.REQUIRED
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)
    estimated_effort: int = 1
    actual_effort: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    block_reason: Optional[str] = None
```

**方法**：

#### `start() -> None`
标记任务为进行中（TODO → WIP）。

```python
task.start()
```

#### `complete() -> None`
标记任务为完成（WIP → DONE）。

```python
task.complete()
```

#### `block(reason: str) -> None`
标记任务为被阻塞（WIP → BLOCKED）。

```python
task.block("等待 API 文档")
```

#### `add_acceptance_criterion(criterion: str) -> None`
添加验收标准。

```python
task.add_acceptance_criterion("返回 200")
```

#### `add_dependency(task_id: int) -> None`
添加依赖任务。

```python
task.add_dependency(2)
```

#### `to_dict() -> Dict[str, Any]`
序列化为字典。

```python
data = task.to_dict()
```

#### `from_dict(data: Dict[str, Any]) -> Task` (classmethod)
从字典创建任务。

```python
task = Task.from_dict(data)
```

### Severity

问题严重程度枚举。

```python
from harness.models import Severity

class Severity(Enum):
    CRITICAL = "CRITICAL"  # 严重
    MAJOR = "MAJOR"        # 主要
    MINOR = "MINOR"        # 次要
    INFO = "INFO"          # 提示
```

### Category

问题类别枚举。

```python
from harness.models import Category

class Category(Enum):
    SECURITY = "SECURITY"              # 安全
    PERFORMANCE = "PERFORMANCE"        # 性能
    QUALITY = "QUALITY"                # 质量
    ACCESSIBILITY = "ACCESSIBILITY"    # 可访问性
    AI_RESIDUALS = "AI_RESIDUALS"      # AI 残留
```

### Issue

代码审查问题数据类。

```python
from harness.models import Issue, Severity, Category

@dataclass
class Issue:
    severity: Severity
    category: Category
    message: str
    file: str
    line: int
    suggestion: Optional[str] = None
```

**方法**：
- `to_dict() -> Dict[str, Any]` - 序列化为字典
- `from_dict(data: Dict[str, Any]) -> Issue` (classmethod) - 从字典创建

### Verdict

审查判定结果枚举。

```python
from harness.models import Verdict

class Verdict(Enum):
    APPROVE = "APPROVE"                    # 批准
    REQUEST_CHANGES = "REQUEST_CHANGES"    # 需要修改
```

### ReviewResult

代码审查结果数据类。

```python
from harness.models import ReviewResult, Verdict, Issue

@dataclass
class ReviewResult:
    verdict: Verdict
    issues: List[Issue]
    summary: str = ""
```

**方法**：
- `to_dict() -> Dict[str, Any]` - 序列化为字典

## 任务管理

### TaskStore

任务存储管理器。

```python
from harness.store import TaskStore
from pathlib import Path

store = TaskStore(Path(".harness"))
```

**方法**：

#### `__init__(harness_dir: Path)`
初始化任务存储。

**参数**：
- `harness_dir` - .harness 目录路径

#### `save_tasks(tasks: List[Task]) -> None`
保存任务列表。

```python
store.save_tasks([task1, task2])
```

#### `load_tasks() -> List[Task]`
加载所有任务。

```python
tasks = store.load_tasks()
```

#### `get_task(task_id: int) -> Optional[Task]`
获取指定任务。

```python
task = store.get_task(1)
```

#### `add_task(task: Task) -> None`
添加新任务。

```python
store.add_task(task)
```

#### `update_task(task: Task) -> None`
更新任务。

```python
store.update_task(task)
```

#### `delete_task(task_id: int) -> None`
删除任务。

```python
store.delete_task(1)
```

#### `get_tasks_by_status(status: TaskStatus) -> List[Task]`
按状态查询任务。

```python
wip_tasks = store.get_tasks_by_status(TaskStatus.WIP)
```

#### `get_tasks_by_priority(priority: Priority) -> List[Task]`
按优先级查询任务。

```python
required_tasks = store.get_tasks_by_priority(Priority.REQUIRED)
```

#### `get_next_task_id() -> int`
获取下一个任务 ID。

```python
next_id = store.get_next_task_id()
```

#### `get_statistics() -> Dict[str, int]`
获取任务统计信息。

```python
stats = store.get_statistics()
# {'total': 10, 'todo': 3, 'wip': 2, 'done': 5, 'blocked': 0, 'progress_percent': 50}
```

### HistoryManager

历史记录管理器。

```python
from harness.history import HistoryManager
from pathlib import Path

history = HistoryManager(Path(".harness"))
```

**方法**：

#### `__init__(harness_dir: Path)`
初始化历史记录管理器。

#### `log_task_created(task: Task) -> None`
记录任务创建事件。

```python
history.log_task_created(task)
```

#### `log_task_updated(task: Task, fields: List[str]) -> None`
记录任务更新事件。

```python
history.log_task_updated(task, ["status", "description"])
```

#### `log_task_completed(task: Task, duration_minutes: int) -> None`
记录任务完成事件。

```python
history.log_task_completed(task, duration_minutes=30)
```

#### `log_task_blocked(task: Task, reason: str) -> None`
记录任务阻塞事件。

```python
history.log_task_blocked(task, "等待 API 文档")
```

#### `get_all_events() -> List[Dict[str, Any]]`
获取所有事件。

```python
events = history.get_all_events()
```

#### `get_events_by_task(task_id: int) -> List[Dict[str, Any]]`
获取指定任务的事件。

```python
events = history.get_events_by_task(1)
```

#### `get_recent_events(limit: int = 10) -> List[Dict[str, Any]]`
获取最近的事件。

```python
events = history.get_recent_events(limit=5)
```

#### `get_events_by_type(event_type: str) -> List[Dict[str, Any]]`
按类型获取事件。

```python
events = history.get_events_by_type("task_completed")
```

## 执行引擎

### ExecutionMode

执行模式枚举。

```python
from harness.executor import ExecutionMode

class ExecutionMode(Enum):
    SOLO = "SOLO"          # 1-2 个任务
    PARALLEL = "PARALLEL"  # 3+ 个任务
```

### ExecutionResult

执行结果数据类。

```python
from harness.executor import ExecutionResult

@dataclass
class ExecutionResult:
    task_id: int
    task_title: str
    success: bool
    output: str = ""
    error: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
```

**方法**：
- `to_dict() -> Dict[str, Any]` - 序列化为字典

### select_execution_mode

自动选择执行模式。

```python
from harness.executor import select_execution_mode

mode = select_execution_mode(tasks)
# 1-2 个任务 → ExecutionMode.SOLO
# 3+ 个任务 → ExecutionMode.PARALLEL
```

**参数**：
- `tasks: List[Task]` - 任务列表

**返回**：
- `ExecutionMode` - 执行模式

### TaskExecutionService

任务执行服务（高层 API）。

```python
from harness.executor import TaskExecutionService
from pathlib import Path

service = TaskExecutionService(Path(".harness"))
```

**方法**：

#### `__init__(harness_dir: Path)`
初始化任务执行服务。

#### `execute_tasks(task_ids: Optional[List[int]] = None) -> List[ExecutionResult]`
执行任务（自动选择模式）。

```python
# 执行所有 TODO 任务
results = service.execute_tasks()

# 执行指定任务
results = service.execute_tasks([1, 2, 3])
```

**参数**：
- `task_ids` - 任务 ID 列表，None 表示执行所有 TODO 任务

**返回**：
- `List[ExecutionResult]` - 执行结果列表

#### `execute_task_solo(task_id: int) -> ExecutionResult`
以 Solo 模式执行单个任务。

```python
result = service.execute_task_solo(1)
```

#### `execute_task_parallel(task_ids: List[int]) -> List[ExecutionResult]`
以 Parallel 模式执行多个任务。

```python
results = service.execute_task_parallel([1, 2, 3])
```

## 代码审查

### ReviewerAgent

代码审查 Agent。

```python
from harness.reviewer import ReviewerAgent

reviewer = ReviewerAgent()
```

**方法**：

#### `review_code(code: str, file_path: str) -> ReviewResult`
审查代码。

```python
code = open("src/auth.py").read()
result = reviewer.review_code(code, "src/auth.py")

print(f"判定：{result.verdict.value}")
print(f"问题数：{len(result.issues)}")
```

**参数**：
- `code` - 代码内容
- `file_path` - 文件路径

**返回**：
- `ReviewResult` - 审查结果

#### `check_security(code: str, file_path: str) -> List[Issue]`
安全检查。

检测：
- SQL 注入风险
- XSS 漏洞
- 硬编码密钥
- eval() 使用

```python
issues = reviewer.check_security(code, "src/auth.py")
```

#### `check_performance(code: str, file_path: str) -> List[Issue]`
性能检查。

检测：
- N+1 查询问题
- 低效算法

```python
issues = reviewer.check_performance(code, "src/repository.py")
```

#### `check_quality(code: str, file_path: str) -> List[Issue]`
质量检查。

检测：
- 过长函数（>50 行）
- 缺失文档字符串
- 裸 except
- 魔法数字

```python
issues = reviewer.check_quality(code, "src/utils.py")
```

#### `check_accessibility(code: str, file_path: str) -> List[Issue]`
可访问性检查（仅 HTML/JSX 文件）。

检测：
- 图片缺少 alt 属性
- div 作为按钮缺少 role
- 表单输入缺少 label

```python
issues = reviewer.check_accessibility(code, "src/component.html")
```

#### `check_ai_residuals(code: str, file_path: str) -> List[Issue]`
AI 残留检查。

检测：
- TODO/FIXME 注释
- mock 数据
- localhost 硬编码
- 跳过的测试

```python
issues = reviewer.check_ai_residuals(code, "src/config.py")
```

### determine_verdict

判定 Verdict。

```python
from harness.reviewer import determine_verdict

verdict = determine_verdict(issues)
# Critical >= 1 → REQUEST_CHANGES
# Major >= 2 → REQUEST_CHANGES
# 其他 → APPROVE
```

**参数**：
- `issues: List[Issue]` - 问题列表

**返回**：
- `Verdict` - 判定结果

## 工具函数

### StateManager

状态管理器。

```python
from harness.state import StateManager
from pathlib import Path

state = StateManager(Path(".harness"))
```

**方法**：
- `load() -> Dict[str, Any]` - 加载状态
- `save(state: Dict[str, Any]) -> None` - 保存状态
- `update(key: str, value: Any) -> None` - 更新状态

### MarkdownParser

Markdown 解析器。

```python
from harness.parser import MarkdownParser

parser = MarkdownParser()
tasks = parser.parse_file(Path("Plans.md"))
```

**方法**：
- `parse_file(file_path: Path) -> List[Task]` - 解析 Plans.md 文件

## 使用示例

### 完整工作流

```python
from pathlib import Path
from harness.models import Task, TaskStatus, Priority
from harness.store import TaskStore
from harness.history import HistoryManager
from harness.executor import TaskExecutionService
from harness.reviewer import ReviewerAgent

# 初始化
harness_dir = Path(".harness")
store = TaskStore(harness_dir)
history = HistoryManager(harness_dir)
executor = TaskExecutionService(harness_dir)
reviewer = ReviewerAgent()

# 1. 创建任务
task = Task(
    id=store.get_next_task_id(),
    title="实现登录功能",
    description="支持邮箱和密码验证",
    priority=Priority.REQUIRED,
    acceptance_criteria=["返回 200", "返回 JWT token"],
    estimated_effort=3
)
store.add_task(task)
history.log_task_created(task)

# 2. 执行任务
result = executor.execute_task_solo(task.id)
if result.success:
    print(f"✅ 任务执行成功")
else:
    print(f"❌ 任务执行失败：{result.error}")

# 3. 审查代码
code = open("src/auth.py").read()
review_result = reviewer.review_code(code, "src/auth.py")

print(f"判定：{review_result.verdict.value}")
for issue in review_result.issues:
    print(f"[{issue.severity.value}] {issue.message}")
```

## 错误处理

所有方法在遇到错误时会抛出异常：

```python
try:
    task = store.get_task(999)
    if task is None:
        print("任务不存在")
except Exception as e:
    print(f"错误：{e}")
```

## 类型提示

所有 API 都提供完整的类型提示，支持 IDE 自动补全和类型检查。

```python
from typing import List, Optional, Dict, Any
from harness.models import Task, TaskStatus
from harness.store import TaskStore

def process_tasks(store: TaskStore, status: TaskStatus) -> List[Task]:
    tasks: List[Task] = store.get_tasks_by_status(status)
    return tasks
```

---

**版本**: 0.4.0
**更新日期**: 2026-04-11
