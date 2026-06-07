# Harness MVP API 参考文档

完整的 API 文档，涵盖所有核心类和方法。

## 目录

- [数据模型](#数据模型)
- [任务管理](#任务管理)
- [模板系统](#模板系统)
- [配置管理](#配置管理)
- [执行引擎](#执行引擎)
- [代码审查](#代码审查)
- [CLI 命令](#cli-命令)
- [工具函数](#工具函数)
- [故障排查](#故障排查)

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

## 配置管理

### Settings

配置设置数据类。

```python
from harness.config import Settings, ExecutionModePreference

@dataclass
class Settings:
    ai_model: str = "claude-sonnet-4-20250514"
    execution_mode: ExecutionModePreference = ExecutionModePreference.AUTO
    max_workers: int = 4
    api_key: str = ""  # 仅内存持有，不写入文件
```

**方法**：

#### `to_dict() -> Dict[str, Any]`
序列化为字典（排除敏感字段）。

```python
data = settings.to_dict()
# {"ai_model": "...", "execution_mode": "AUTO", "max_workers": 4}
```

#### `from_dict(data: Dict[str, Any]) -> Settings` (classmethod)
从字典创建设置。

```python
settings = Settings.from_dict({"ai_model": "claude-opus-4-20250514"})
```

#### `merge(other: Settings) -> Settings`
合并两个设置对象（other 的非默认值覆盖当前值）。

```python
merged = settings.merge(other_settings)
```

### ExecutionModePreference

执行模式偏好枚举。

```python
from harness.config import ExecutionModePreference

class ExecutionModePreference(Enum):
    AUTO = "AUTO"        # 自动选择
    SOLO = "SOLO"        # 始终 Solo
    PARALLEL = "PARALLEL"  # 始终 Parallel
```

### ConfigManager

配置管理器。

```python
from harness.config import ConfigManager
from pathlib import Path

manager = ConfigManager(Path(".harness"))
```

**方法**：

#### `__init__(harness_dir: Path)`
初始化配置管理器。如果配置文件不存在，自动创建默认配置。

#### `load() -> Settings`
从文件加载配置。

```python
settings = manager.load()
```

#### `save(settings: Settings) -> None`
保存配置到文件。

```python
manager.save(settings)
```

#### `update(**kwargs) -> Settings`
更新部分配置。

```python
settings = manager.update(ai_model="claude-opus-4-20250514")
settings = manager.update(max_workers=8)
```

#### `reset() -> None`
重置为默认配置。

```python
manager.reset()
```

#### `load_with_env_overrides() -> Settings`
加载配置并应用环境变量覆盖。

```python
# ANTHROPIC_API_KEY 覆盖 api_key
# HARNESS_AI_MODEL 覆盖 ai_model
settings = manager.load_with_env_overrides()
```

### load_config

便捷函数。

```python
from harness.config import load_config

config = load_config(Path(".harness"))
# 等同于 ConfigManager(harness_dir).load_with_env_overrides()
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

## 模板系统

### TaskTemplate

任务模板数据模型。

```python
from harness.templates import TaskTemplate, TemplatePrompt
from harness.models import Priority

template = TaskTemplate(
    name="feature",
    title="实现 {feature_name} 功能",
    description="### 功能描述\n{description}",
    priority=Priority.REQUIRED,
    estimated_effort=3,
    prompts=[
        TemplatePrompt("feature_name", "请输入功能名称", required=True),
        TemplatePrompt("description", "请输入功能描述", required=True, multiline=True)
    ]
)
```

**属性**：
- `name: str` - 模板唯一标识符
- `title: str` - 任务标题（可包含变量占位符）
- `description: str` - 任务描述（可包含变量占位符）
- `priority: Priority` - 默认优先级
- `estimated_effort: int` - 默认工作量（1-5）
- `prompts: List[TemplatePrompt]` - 变量提示配置
- `acceptance_criteria: List[str]` - 验收标准

**方法**：
- `get_variables() -> Set[str]` - 提取所有 `{variable}` 占位符
- `validate() -> List[str]` - 验证模板结构，返回错误列表
- `to_dict() -> Dict[str, Any]` - 序列化为字典
- `from_dict(data: Dict[str, Any]) -> TaskTemplate` - 从字典反序列化（类方法）

**示例**：

```python
# 提取变量
variables = template.get_variables()
# {'feature_name', 'description'}

# 验证模板
errors = template.validate()
if errors:
    print(f"验证失败: {errors}")
else:
    print("验证通过")

# 序列化
data = template.to_dict()

# 反序列化
template = TaskTemplate.from_dict(data)
```

### TemplatePrompt

模板变量提示配置。

```python
from harness.templates import TemplatePrompt

prompt = TemplatePrompt(
    key="feature_name",
    question="请输入功能名称",
    required=True,
    multiline=False,
    default=None
)
```

**属性**：
- `key: str` - 变量名（必须是有效标识符）
- `question: str` - 提示用户的问题
- `required: bool` - 是否必填（默认 True）
- `multiline: bool` - 是否多行输入（默认 False）
- `default: Optional[str]` - 默认值（可选）

**方法**：
- `validate() -> List[str]` - 验证提示配置，返回错误列表

### TemplateStore

模板存储和加载管理器。

```python
from harness.template_loader import TemplateStore
from pathlib import Path

store = TemplateStore(Path(".harness"))
```

**属性**：
- `harness_dir: Path` - .harness 目录路径
- `custom_template_dir: Path` - 自定义模板目录（.harness/templates/）

**方法**：
- `get_all_templates() -> Dict[str, TaskTemplate]` - 获取所有模板（自定义覆盖内置）
- `get_template(name: str) -> Optional[TaskTemplate]` - 获取指定模板
- `list_templates() -> List[Tuple[str, TaskTemplate, bool]]` - 列出所有模板（name, template, is_custom）
- `load_custom_templates() -> Dict[str, TaskTemplate]` - 加载自定义模板

**示例**：

```python
# 获取所有模板
templates = store.get_all_templates()
for name, template in templates.items():
    print(f"{name}: {template.title}")

# 获取特定模板
feature_template = store.get_template("feature")
if feature_template:
    print(f"找到模板: {feature_template.title}")

# 列出模板（带自定义标记）
for name, template, is_custom in store.list_templates():
    suffix = " (自定义)" if is_custom else ""
    print(f"{name}{suffix}: {template.title}")
```

### TemplateEngine

模板引擎，负责从模板创建任务。

```python
from harness.templates import TemplateEngine
from harness.template_loader import TemplateStore
from harness.store import TaskStore
from pathlib import Path

template_store = TemplateStore(Path(".harness"))
task_store = TaskStore(Path(".harness"))
engine = TemplateEngine(template_store, task_store)
```

**方法**：

#### create_task_from_template

从模板创建任务。

```python
task = engine.create_task_from_template(
    template_name="feature",
    variables={"feature_name": "用户认证", "description": "实现JWT认证"},
    interactive=False
)
```

**参数**：
- `template_name: str` - 模板名称
- `variables: Optional[Dict[str, str]]` - 变量值（非交互式模式）
- `interactive: bool` - 是否交互式提示用户输入（默认 True）

**返回**：
- `Task` - 创建的任务对象

**异常**：
- `TemplateNotFoundError` - 模板不存在
- `TemplateValidationError` - 模板验证失败
- `MissingVariableError` - 缺少必填变量（非交互式模式）

**示例**：

```python
# 交互式模式
task = engine.create_task_from_template("feature", interactive=True)

# 非交互式模式
variables = {
    "feature_name": "用户认证",
    "description": "实现基于JWT的用户登录认证"
}
task = engine.create_task_from_template("feature", variables=variables, interactive=False)

# 错误处理
from harness.templates import TemplateNotFoundError, TemplateValidationError, MissingVariableError

try:
    task = engine.create_task_from_template("nonexistent")
except TemplateNotFoundError as e:
    print(f"模板不存在: {e}")
except TemplateValidationError as e:
    print(f"验证失败: {e}")
except MissingVariableError as e:
    print(f"缺少变量: {e}")
```

### 自定义模板格式

自定义模板文件存放在 `.harness/templates/` 目录，使用 JSON 格式。

**JSON 模板格式**：

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

**完整示例** (`.harness/templates/documentation.json`):

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

**验证规则**：
- `name` 必须是有效标识符（字母、数字、下划线、连字符）
- `priority` 必须是 REQUIRED、RECOMMENDED 或 OPTIONAL
- `estimated_effort` 必须是 1-5 之间的整数
- `prompts` 至少包含一个元素
- 所有 `{variable}` 必须在 `prompts` 中定义
- `prompt.key` 必须是有效的 Python 标识符

## CLI 命令

Harness MVP 提供了完整的命令行界面，支持任务管理、模板操作、代码审查等功能。

### 任务管理命令

#### harness plan add

创建新任务。支持两种模式：

**模式1: 从模板创建（推荐）**

```bash
# 交互式模式（系统会提示输入变量）
harness plan add --template feature

# 非交互式模式（适合脚本/自动化）
harness plan add --template feature \
  --var feature_name="用户认证" \
  --var description="实现基于JWT的用户登录认证"
```

**模式2: 手动创建**

```bash
# 交互式输入
harness plan add

# 命令行参数
harness plan add \
  --title "实现登录功能" \
  --description "支持邮箱和密码验证" \
  --priority REQUIRED \
  --estimate 3
```

**选项说明**：
- `--template, -t <name>` - 使用指定模板（feature, bugfix, refactor 或自定义模板）
- `--var <key=value>` - 设置模板变量（可多次使用，仅在 --template 模式下有效）
- `--title <text>` - 任务标题（手动模式）
- `--description, -d <text>` - 任务描述（手动模式）
- `--priority, -p <level>` - 优先级：REQUIRED, RECOMMENDED, OPTIONAL（手动模式）
- `--estimate, -e <1-5>` - 工作量估算（手动模式）

**示例**：

```bash
# 使用内置 feature 模板
$ harness plan add --template feature

✨ 使用模板: feature

请输入功能名称: 任务模板系统
请输入功能描述（多行输入，按 Ctrl+D 或 Ctrl+Z 结束）:
> 实现任务模板系统，支持快速创建标准化任务
> 包含内置模板和自定义模板能力
>

✅ 任务创建成功! (ID: 10)
   标题: 实现 任务模板系统 功能
   优先级: REQUIRED
   工作量: 3

# 使用 bugfix 模板（非交互式）
$ harness plan add --template bugfix \
  --var bug_description="登录500错误" \
  --var description="服务器在用户登录时返回500错误" \
  --var reproduction_steps="1. 访问/login 2. 输入凭据 3. 点击登录" \
  --var fix_plan="检查数据库连接配置"

✅ 任务创建成功! (ID: 11)

# 使用 refactor 模板
$ harness plan add --template refactor \
  --var module_name="executor模块" \
  --var goal="降低圈复杂度，提升可维护性" \
  --var scope="ExecutionEngine类和相关测试"

✅ 任务创建成功! (ID: 12)

# 手动创建任务
$ harness plan add \
  --title "编写API文档" \
  --description "为所有公共API编写文档字符串" \
  --priority OPTIONAL \
  --estimate 2

已添加任务 #13: 编写API文档
```

#### harness plan list

列出所有任务。

```bash
harness plan list
```

**输出示例**：

```
任务列表:

#1  [TODO]     实现用户认证功能        (REQUIRED, 估算: 3)
#2  [WIP]      修复登录500错误         (REQUIRED, 估算: 2)
#3  [DONE]     重构executor模块        (RECOMMENDED, 估算: 3)
#10 [BLOCKED]  实现支付集成            (REQUIRED, 估算: 5)
                被阻塞: 等待API密钥

统计:
  总数: 10  |  待办: 3  |  进行中: 2  |  完成: 4  |  阻塞: 1
  完成率: 40%
```

#### harness plan show

显示任务详情。

```bash
harness plan show <task_id>
```

**示例**：

```bash
$ harness plan show 1

=== 任务 #1 ===

标题: 实现 任务模板系统 功能
状态: TODO
优先级: REQUIRED
工作量: 3 (实际: -)

描述:
### 功能描述
实现任务模板系统，支持快速创建标准化任务
包含内置模板和自定义模板能力

### 实现要点
- 设计数据模型
- 实现核心逻辑
- 编写单元测试
- 更新文档

### 验收标准
- [ ] 功能正常工作
- [ ] 测试覆盖率 >= 80%
- [ ] 代码审查通过

创建时间: 2026-06-05 10:30:00
更新时间: 2026-06-05 10:30:00
```

#### 其他任务命令

```bash
# 开始执行任务
harness work solo <task_id>
harness work parallel <task_id1> <task_id2> ...

# 更新任务状态
harness plan update <task_id> --status DONE
harness plan block <task_id> --reason "等待API密钥"

# 删除任务
harness plan delete <task_id>
```

### 模板管理命令

#### harness template list

列出所有可用模板（内置 + 自定义）。

```bash
harness template list
```

**输出示例**：

```
可用模板:
  feature
    功能开发任务
    优先级: REQUIRED, 工作量: 3

  bugfix
    Bug修复任务
    优先级: REQUIRED, 工作量: 2

  refactor
    代码重构任务
    优先级: RECOMMENDED, 工作量: 3

  documentation (自定义)
    自定义模板
    优先级: OPTIONAL, 工作量: 1

  api (自定义)
    自定义模板
    优先级: REQUIRED, 工作量: 2

使用方式: harness plan add --template <template_name>
```

**说明**：
- 内置模板：feature, bugfix, refactor
- 自定义模板会标记 `(自定义)` 后缀
- 自定义模板可以覆盖内置模板（同名时优先使用自定义）

#### harness template show

显示模板详细信息。

```bash
harness template show <template_name>
```

**示例**：

```bash
$ harness template show feature

=== 模板: feature ===

标题: 实现 {feature_name} 功能
优先级: REQUIRED
工作量: 3

描述:
### 功能描述
{description}

### 实现要点
- 设计数据模型
- 实现核心逻辑
- 编写单元测试
- 更新文档

### 验收标准
- [ ] 功能正常工作
- [ ] 测试覆盖率 >= 80%
- [ ] 代码审查通过

变量:
  - feature_name (必填): 请输入功能名称
  - description (必填)（多行）: 请输入功能描述
```

```bash
$ harness template show bugfix

=== 模板: bugfix ===

标题: 修复 {bug_description}
优先级: REQUIRED
工作量: 2

描述:
### Bug 描述
{description}

### 复现步骤
{reproduction_steps}

### 修复方案
{fix_plan}

变量:
  - bug_description (必填): 请输入Bug简短描述
  - description (必填)（多行）: 请输入详细Bug描述
  - reproduction_steps (必填)（多行）: 请输入复现步骤
  - fix_plan (可选)（多行）: 请输入修复方案
    默认值: 待分析
```

### 代码审查命令

#### harness review code

审查单个或多个文件的代码质量。

```bash
# 审查单个文件
harness review code <file_path>

# 审查多个文件
harness review code src/**/*.py

# 审查并生成报告
harness review code src/ --report
```

#### harness review incremental

增量代码审查，只审查 Git 变更的文件。

**语法**：
```bash
harness review incremental [--base <ref>]
```

**选项**：
- `--base <ref>` - 指定基准引用（默认: HEAD~1）
  - 提交哈希: `abc1234`
  - 分支名: `main`, `develop`
  - 标签: `v1.0.0`
  - 相对引用: `HEAD~2`, `HEAD^^`

**示例**：

```bash
# 审查相比上一次提交的变更（默认）
harness review incremental

# 审查相比特定提交的变更
harness review incremental --base abc1234

# 审查相比 main 分支的变更
harness review incremental --base main

# 审查相比两次提交前的变更
harness review incremental --base HEAD~2

# 审查相比特定标签的变更
harness review incremental --base v1.0.0
```

**工作原理**：

1. **检测变更**: 使用 `git diff` 识别新增(A)和修改(M)的文件
2. **过滤文件**: 排除已删除的文件
3. **逐个审查**: 对每个变更文件应用 5 观点审查
4. **汇总报告**: 统计问题数量并给出最终判定

**输出格式**：

```
=== 增量代码审查 ===

基准: HEAD~1
检测到 3 个变更文件

审查 src/auth.py...
  发现 1 个问题: 🔴 Critical: 1

审查 src/user.py...
  发现 2 个问题: 🟡 Major: 2

审查 tests/test_auth.py...
  ✅ 无问题

=== 汇总 ===

  🔴 Critical: 1
  🟡 Major: 2
  🟢 Minor: 0
  🔵 Info: 0

判定: REQUEST_CHANGES（需要修改）
```

**错误处理**：

- **无效基准引用**: 如果指定的基准引用不存在，会显示错误信息
- **无变更文件**: 如果没有检测到变更，会提示"无变更文件"
- **非 Git 仓库**: 如果不在 Git 仓库中运行，会提示错误

**优势**：

- ✅ **效率提升**: 只审查变更文件，避免重复审查
- ✅ **灵活对比**: 支持多种基准引用方式
- ✅ **完整审查**: 使用相同的 5 观点审查标准
- ✅ **清晰汇总**: 一目了然的问题统计和判定结果

**适用场景**：

- **Pull Request 审查**: 审查相比目标分支的变更
- **提交前检查**: 审查本次提交的变更
- **增量开发**: 审查相比上次审查的新变更
- **版本对比**: 审查两个版本之间的差异

### 配置命令

```bash
# 查看当前配置
harness config show

# 更新配置
harness config set ai_model claude-opus-4-20250514
harness config set max_workers 8

# 重置为默认配置
harness config reset
```

### 帮助命令

```bash
# 查看总体帮助
harness --help

# 查看子命令帮助
harness plan --help
harness template --help
harness work --help
```

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

## 故障排查

### 模板系统常见错误

#### 错误1: 模板不存在

**错误信息**：
```
❌ 错误: Template 'mytemplate' not found
```

**原因**：
- 模板名称拼写错误
- 自定义模板文件不存在或未正确放置

**解决方法**：
```bash
# 1. 查看可用模板列表
harness template list

# 2. 检查自定义模板目录
ls .harness/templates/

# 3. 确保 JSON 文件名与模板 name 字段匹配
cat .harness/templates/mytemplate.json | grep '"name"'
```

#### 错误2: 模板验证失败

**错误信息**：
```
❌ 错误: Template validation failed: ['缺少必填字段 prompts', '变量 {unknown_var} 未在 prompts 中定义']
```

**原因**：
- 模板 JSON 格式不符合规范
- 模板中的变量未在 prompts 中定义
- 必填字段缺失或类型错误

**解决方法**：

1. **检查必填字段**
```json
{
  "name": "必填 - 模板标识符",
  "title": "必填 - 任务标题",
  "description": "必填 - 任务描述",
  "priority": "必填 - REQUIRED|RECOMMENDED|OPTIONAL",
  "estimated_effort": "必填 - 1到5之间的整数",
  "prompts": "必填 - 至少包含一个 prompt"
}
```

2. **验证变量一致性**
```json
{
  "title": "实现 {feature_name} 功能",
  "description": "详细描述: {description}",
  "prompts": [
    {
      "key": "feature_name",
      "question": "请输入功能名称",
      "required": true
    },
    {
      "key": "description",
      "question": "请输入功能描述",
      "required": true,
      "multiline": true
    }
  ]
}
```

**注意**：所有 `{variable}` 必须在 prompts 中有对应的定义。

3. **检查字段类型**
```json
{
  "name": "必须是字符串，只能包含字母、数字、下划线、连字符",
  "priority": "必须是 REQUIRED, RECOMMENDED, OPTIONAL 之一",
  "estimated_effort": "必须是 1-5 之间的整数（不是字符串）",
  "prompts": [
    {
      "key": "必须是有效的 Python 标识符",
      "question": "必须是非空字符串",
      "required": "必须是布尔值 true/false（不是字符串）",
      "multiline": "必须是布尔值 true/false（不是字符串）"
    }
  ]
}
```

#### 错误3: 缺少必填变量

**错误信息**：
```
❌ 错误: Missing required variables: {'feature_name', 'description'}
```

**原因**：
- 非交互式模式下未通过 `--var` 提供必填变量

**解决方法**：
```bash
# 方案1: 提供所有必填变量
harness plan add --template feature \
  --var feature_name="用户认证" \
  --var description="实现JWT认证"

# 方案2: 使用交互式模式
harness plan add --template feature
# 系统会逐个提示输入
```

#### 错误4: 变量格式错误

**错误信息**：
```
❌ 错误: 无效的变量格式 'invalid_format'，应为 key=value
```

**原因**：
- `--var` 参数格式不正确

**解决方法**：
```bash
# 错误示例
harness plan add --template feature --var "feature_name User Auth"

# 正确示例（使用等号）
harness plan add --template feature --var feature_name="User Auth"

# 包含空格的值需要引号
harness plan add --template feature \
  --var feature_name="User Authentication" \
  --var description="Implement JWT-based authentication system"

# 多行内容可以使用换行符
harness plan add --template feature \
  --var feature_name="User Auth" \
  --var description="Line 1\nLine 2\nLine 3"
```

#### 错误5: JSON 解析错误

**错误信息**：
```
Failed to load template from 'mytemplate.json': Invalid JSON format
```

**原因**：
- JSON 语法错误（缺少逗号、引号、括号等）

**解决方法**：
```bash
# 验证 JSON 格式
python -m json.tool .harness/templates/mytemplate.json

# 如果有错误，会显示具体位置
# Expecting ',' delimiter: line 5 column 3 (char 85)
```

**常见 JSON 语法错误**：
```json
{
  "name": "test",
  "title": "Test"  // ❌ 不允许注释，删除此行
  "description": "..."  // ❌ 缺少逗号
  "prompts": [
    {
      "key": "var1",
      "question": "Q1",
      "required": "true"  // ❌ 应该是布尔值 true，不是字符串 "true"
    },  // ❌ 数组最后一个元素后不应有逗号（某些 JSON 解析器允许，但不推荐）
  ]
}
```

**正确格式**：
```json
{
  "name": "test",
  "title": "Test",
  "description": "...",
  "priority": "REQUIRED",
  "estimated_effort": 3,
  "prompts": [
    {
      "key": "var1",
      "question": "Q1",
      "required": true
    }
  ]
}
```

#### 错误6: 自定义模板未被加载

**症状**：
- `harness template list` 看不到自定义模板
- 使用时提示模板不存在

**可能原因及解决方法**：

1. **模板目录不存在**
```bash
# 创建模板目录
mkdir -p .harness/templates
```

2. **文件扩展名错误**
```bash
# ❌ 错误：mytemplate.txt, mytemplate.yaml
# ✅ 正确：mytemplate.json

# 检查文件扩展名
ls -la .harness/templates/
```

3. **模板验证失败**
```bash
# 查看日志（如果启用了调试模式）
# 系统会跳过无效模板并记录警告
export HARNESS_DEBUG=1
harness template list
```

4. **文件权限问题**
```bash
# 检查文件是否可读
ls -l .harness/templates/mytemplate.json

# 修复权限（Unix/Linux）
chmod 644 .harness/templates/mytemplate.json
```

### 任务执行常见错误

#### 错误7: 任务不存在

**错误信息**：
```
任务 #999 不存在
```

**解决方法**：
```bash
# 查看所有任务
harness plan list

# 确认任务 ID
harness plan show <correct_id>
```

#### 错误8: 任务状态转换错误

**错误信息**：
```
无法将任务状态从 DONE 转换为 WIP
```

**原因**：
- 已完成的任务不能重新设置为进行中

**解决方法**：
```bash
# 创建新任务而不是重新开启旧任务
harness plan add --title "继续开发XXX功能"

# 或者删除旧任务，重新创建
harness plan delete <old_task_id>
```

### 配置相关错误

#### 错误9: 配置文件损坏

**症状**：
- 启动 harness 时崩溃
- 提示 JSON 解析错误

**解决方法**：
```bash
# 1. 备份现有配置
cp .harness/config.json .harness/config.json.backup

# 2. 重置为默认配置
harness config reset

# 3. 手动恢复设置
harness config set ai_model claude-sonnet-4-20250514
harness config set max_workers 4
```

### 调试技巧

#### 启用详细日志

```bash
# 设置环境变量启用调试模式
export HARNESS_DEBUG=1
harness plan add --template feature
```

#### 检查系统状态

```bash
# 查看 .harness 目录结构
tree .harness

# 应该包含：
# .harness/
# ├── config.json        # 配置文件
# ├── state.json         # 任务状态
# ├── events.json        # 历史事件
# ├── history/           # 历史记录
# └── templates/         # 自定义模板
#     ├── api.json
#     └── documentation.json
```

#### 验证模板 JSON

使用在线工具或命令行验证 JSON 格式：

```bash
# Python 验证
python -c "import json; json.load(open('.harness/templates/mytemplate.json'))"

# 如果成功，不会有输出
# 如果失败，会显示错误位置
```

#### 手动测试模板

```python
# test_template.py
from pathlib import Path
from harness.template_loader import TemplateStore

# 加载模板
store = TemplateStore(Path(".harness"))
template = store.get_template("mytemplate")

if template:
    print(f"✅ 模板加载成功: {template.name}")
    
    # 验证模板
    errors = template.validate()
    if errors:
        print(f"❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 验证通过")
        
    # 检查变量
    variables = template.get_variables()
    print(f"📋 模板变量: {variables}")
    
    prompt_keys = {p.key for p in template.prompts}
    print(f"📋 Prompt 键: {prompt_keys}")
else:
    print("❌ 模板不存在")
```

运行测试：
```bash
python test_template.py
```

### 获取帮助

如果问题仍未解决：

1. **查看内置帮助**
```bash
harness --help
harness template --help
harness plan add --help
```

2. **查看示例**
```bash
# 查看内置模板作为参考
harness template show feature
harness template show bugfix
harness template show refactor
```

3. **检查文档**
- API 参考：`docs/api-reference.md`
- 快速开始：`docs/quick-start.md`
- 需求文档：`.kiro/specs/task-template-system/requirements.md`

---

**版本**: 0.6.0
**更新日期**: 2026-06-05
