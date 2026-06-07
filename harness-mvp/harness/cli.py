"""CLI 入口点 - Phase 2 扩展"""
import click
from pathlib import Path
from harness import __version__
from harness.models import Task, TaskStatus, Priority
from harness.store import TaskStore
from harness.history import HistoryManager
from harness.executor import TaskExecutionService, select_execution_mode, ExecutionMode
from harness.reviewer import ReviewerAgent, ReviewResult
from harness.custom_rules import CustomRuleStore, CustomRuleEngine, RuleNotFoundError, RuleNameConflictError
from harness.dependency_graph import generate_mermaid_graph, generate_graph_report, find_critical_path
from harness.config import ConfigManager, Settings


def _load_custom_rule_engine():
    """加载自定义规则引擎（如果 .harness/custom_rules.json 存在）

    Returns:
        CustomRuleEngine 实例，或 None
    """
    harness_dir = get_harness_dir()
    rules_file = harness_dir / "custom_rules.json"
    if not rules_file.exists():
        return None
    try:
        store = CustomRuleStore(harness_dir)
        return CustomRuleEngine(store)
    except Exception:
        return None


def get_harness_dir() -> Path:
    """获取 .harness 目录"""
    return Path.cwd() / ".harness"


def get_plans_file() -> Path:
    """获取 Plans.md 文件路径"""
    return Path.cwd() / "Plans.md"


@click.group()
@click.version_option(version=__version__)
def main():
    """Harness MVP - Lightweight Agent Harness"""
    pass


@main.group()
def plan():
    """计划管理命令"""
    pass


@plan.command()
def create():
    """创建新计划（对话式）"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)

    click.echo("=== 创建新计划 ===\n")
    click.echo("我来帮你创建计划。请告诉我你想构建什么功能？")

    # 简单版：直接创建空计划
    click.echo("\n计划已创建。使用 'harness plan add' 添加任务。")


@plan.command("list")
def list_tasks():
    """列出所有任务"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)

    tasks = store.load_tasks()
    if not tasks:
        click.echo("没有任务。使用 'harness plan add' 添加任务。")
        return

    click.echo("\n=== 任务列表 ===\n")
    for task in tasks:
        status_icon = {
            TaskStatus.TODO: "[ ]",
            TaskStatus.WIP: "[~]",
            TaskStatus.DONE: "[x]",
            TaskStatus.BLOCKED: "[!]"
        }.get(task.status, "[ ]")

        priority_icon = {
            Priority.REQUIRED: "🔴",
            Priority.RECOMMENDED: "🟡",
            Priority.OPTIONAL: "🟢"
        }.get(task.priority, "")

        click.echo(f"{status_icon} {task.id}. {task.title} {priority_icon}")
        if task.description:
            click.echo(f"    {task.description}")
        click.echo()


@plan.command()
@click.argument('task_id', type=int)
def show(task_id: int):
    """显示任务详情"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)

    task = store.get_task(task_id)
    if not task:
        click.echo(f"未找到任务 #{task_id}")
        return

    click.echo(f"\n=== 任务 #{task_id}: {task.title} ===\n")
    click.echo(f"状态：{task.status.value}")
    click.echo(f"优先级：{task.priority.value}")
    click.echo(f"估算工作量：{task.estimated_effort}")
    if task.actual_effort:
        click.echo(f"实际工作量：{task.actual_effort}")

    click.echo(f"\n描述:\n{task.description or '无'}\n")

    if task.acceptance_criteria:
        click.echo("验收标准:")
        for criterion in task.acceptance_criteria:
            click.echo(f"  - {criterion}")
        click.echo()

    if task.dependencies:
        click.echo(f"依赖：{task.dependencies}")
        click.echo()


@plan.command()
@click.argument('task_id', type=int)
@click.option('--status', '-s', type=click.Choice(['TODO', 'WIP', 'DONE', 'BLOCKED'], case_sensitive=False), required=True)
@click.option('--reason', '-r', help="阻塞原因（当状态为 BLOCKED 时）")
def update(task_id: int, status: str, reason: str):
    """更新任务状态"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)
    history = HistoryManager(harness_dir)

    task = store.get_task(task_id)
    if not task:
        click.echo(f"未找到任务 #{task_id}")
        return

    old_status = task.status
    task.status = TaskStatus.from_string(status)
    task.updated_at = task.updated_at.now()

    if task.status == TaskStatus.BLOCKED and reason:
        task.block(reason)

    if task.status == TaskStatus.DONE:
        task.complete()

    store.update_task(task)
    history.log_task_updated(task, ["status"])

    click.echo(f"任务 #{task_id} 状态已更新：{old_status.value} -> {task.status.value}")


@plan.command()
def sync():
    """同步 Plans.md 和状态"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)
    plans_file = get_plans_file()

    tasks = store.load_tasks()

    # 按优先级分组
    required = [t for t in tasks if t.priority == Priority.REQUIRED]
    recommended = [t for t in tasks if t.priority == Priority.RECOMMENDED]
    optional = [t for t in tasks if t.priority == Priority.OPTIONAL]

    def format_task(task: Task) -> str:
        status_map = {
            TaskStatus.TODO: "[ ]",
            TaskStatus.WIP: "[~]",
            TaskStatus.DONE: "[x]",
            TaskStatus.BLOCKED: "[!]"
        }
        status = status_map.get(task.status, "[ ]")
        lines = [f"- {status} **Task {task.id}**: {task.title}"]
        if task.description:
            lines.append(f"  {task.description}")
        if task.acceptance_criteria:
            for criterion in task.acceptance_criteria:
                lines.append(f"  - ✅ {criterion}")
        lines.append(f"  - 估算：{task.estimated_effort}")
        if task.dependencies:
            lines.append(f"  - 依赖：{task.dependencies}")
        return "\n".join(lines)

    content = ["# 计划", "", "## Tasks", ""]

    if required:
        content.append("### Required（必需）")
        content.append("")
        for task in required:
            content.append(format_task(task))
            content.append("")

    if recommended:
        content.append("### Recommended（推荐）")
        content.append("")
        for task in recommended:
            content.append(format_task(task))
            content.append("")

    if optional:
        content.append("### Optional（可选）")
        content.append("")
        for task in optional:
            content.append(format_task(task))
            content.append("")

    plans_file.write_text("\n".join(content), encoding='utf-8')
    click.echo(f"已同步 {len(tasks)} 个任务到 Plans.md")


@plan.command()
@click.option('--template', '-t', help="模板名称 (feature, bugfix, refactor)")
@click.option('--var', 'variables', multiple=True, help="变量值 (格式: key=value)")
@click.option('--title', help="任务标题")
@click.option('--description', '-d', help="任务描述")
@click.option('--priority', '-p', type=click.Choice(['REQUIRED', 'RECOMMENDED', 'OPTIONAL'], case_sensitive=False), default='REQUIRED')
@click.option('--estimate', '-e', type=int, default=1, help="估算工作量 (1-5)")
def add(template: str, variables, title: str, description: str, priority: str, estimate: int):
    """添加新任务（支持模板或手动输入）"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)
    history = HistoryManager(harness_dir)

    if template:
        # Template mode - Requirements 3.3.1
        from harness.template_loader import TemplateStore
        from harness.templates import (
            TemplateEngine, 
            TemplateNotFoundError, 
            TemplateValidationError, 
            MissingVariableError
        )
        
        # Initialize stores
        template_store = TemplateStore(harness_dir)
        engine = TemplateEngine(template_store, store)
        
        # Parse --var arguments into dict (format: key=value)
        var_dict = {}
        for var in variables:
            if '=' not in var:
                click.echo(f"❌ 错误: 无效的变量格式 '{var}'，应为 key=value")
                return
            key, value = var.split('=', 1)
            var_dict[key.strip()] = value.strip()
        
        # Interactive mode when no --var arguments provided
        # Non-interactive mode when --var arguments are provided
        interactive = len(var_dict) == 0
        
        try:
            # Call engine.create_task_from_template() with interactive mode
            task = engine.create_task_from_template(
                template,
                variables=var_dict,
                interactive=interactive
            )
            store.add_task(task)
            history.log_task_created(task)
            
            # Display success message with task ID, title, priority, and effort
            click.echo(f"\n✅ 任务创建成功! (ID: {task.id})")
            click.echo(f"   标题: {task.title}")
            click.echo(f"   优先级: {task.priority.value}")
            click.echo(f"   工作量: {task.estimated_effort}")
            
        except TemplateNotFoundError as e:
            # Handle TemplateNotFoundError by displaying available templates
            click.echo(f"❌ 错误: {e}")
            click.echo("\n可用模板:")
            for name, tmpl, is_custom in template_store.list_templates():
                suffix = " (自定义)" if is_custom else ""
                click.echo(f"  - {name}{suffix}")
        except (TemplateValidationError, MissingVariableError) as e:
            # Handle TemplateValidationError and MissingVariableError with user-friendly messages
            click.echo(f"❌ 错误: {e}")
    else:
        # Original manual task creation (maintain backward compatibility)
        if not title:
            title = click.prompt("任务标题")
            description = click.prompt("任务描述（可选）", default="")
            priority = click.prompt("优先级", type=click.Choice(['REQUIRED', 'RECOMMENDED', 'OPTIONAL']), default='REQUIRED')
            estimate = click.prompt("估算工作量 (1-5)", type=int, default=1)

        task_id = store.get_next_task_id()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=Priority.from_string(priority),
            estimated_effort=estimate
        )

        store.add_task(task)
        history.log_task_created(task)

        click.echo(f"已添加任务 #{task_id}: {task.title}")


@plan.command()
@click.option('--output', '-o', type=click.Choice(['mermaid', 'report'], case_sensitive=False),
              default='mermaid', help='输出格式：mermaid 图表或文本分析报告')
def graph(output: str):
    """显示任务依赖图

    生成 Mermaid 格式的任务依赖关系图或文本分析报告，
    包含循环依赖检测和关键路径分析。
    """
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    store = TaskStore(harness_dir)
    tasks = store.load_tasks()

    if not tasks:
        click.echo("没有任务。使用 'harness plan add' 添加任务。")
        return

    if output == 'mermaid':
        click.echo("\n=== 任务依赖图 (Mermaid) ===\n")
        click.echo(generate_mermaid_graph(tasks))
        click.echo("\n将以上内容粘贴到支持 Mermaid 的编辑器（如 Notion、GitHub）中查看依赖图。")
    else:
        click.echo(generate_graph_report(tasks))


@plan.command("stats")
def statistics():
    """显示任务统计"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)

    stats = store.get_statistics()

    click.echo("\n=== 任务统计 ===\n")
    click.echo(f"总数：{stats['total']}")
    click.echo(f"待办 (TODO): {stats['todo']}")
    click.echo(f"进行中 (WIP): {stats['wip']}")
    click.echo(f"已完成 (DONE): {stats['done']}")
    click.echo(f"被阻塞 (BLOCKED): {stats['blocked']}")
    click.echo(f"\n进度：{stats['progress_percent']}%")


# ===== Template 命令组 =====

@main.group()
def template():
    """模板管理命令"""
    pass


@template.command('list')
def list_templates():
    """列出所有可用模板
    
    显示所有内置和自定义模板，包括名称、描述预览、优先级和工作量。
    自定义模板会标记 "(自定义)" 后缀。
    
    Requirements: 3.3.2
    """
    harness_dir = get_harness_dir()
    
    # Import here to avoid circular dependencies
    from harness.template_loader import TemplateStore
    
    # Initialize TemplateStore
    template_store = TemplateStore(harness_dir)
    
    # Call template_store.list_templates()
    templates = template_store.list_templates()
    
    if not templates:
        click.echo("没有可用的模板。")
        return
    
    # Display header
    click.echo("\n可用模板:")
    
    # Display each template with name, description preview, priority, effort
    for name, tmpl, is_custom in templates:
        # Mark custom templates with "(自定义)" suffix
        suffix = " (自定义)" if is_custom else ""
        
        # Create a simple description based on template type
        desc_map = {
            "feature": "功能开发任务",
            "bugfix": "Bug修复任务",
            "refactor": "代码重构任务"
        }
        
        # Use mapped description if available, otherwise use a generic description
        if name in desc_map:
            desc_preview = desc_map[name]
        else:
            # For custom templates, use a generic description
            desc_preview = "自定义模板"
        
        # Display template info (multi-line format)
        click.echo(f"  {name}{suffix}")
        click.echo(f"    {desc_preview}")
        click.echo(f"    优先级: {tmpl.priority.value}, 工作量: {tmpl.estimated_effort}")
        click.echo()  # Empty line between templates
    
    # Display usage hint at the end
    click.echo("\n使用方式: harness plan add --template <template_name>")


@template.command('show')
@click.argument('template_name')
def show_template(template_name: str):
    """显示模板详情
    
    显示指定模板的完整定义，包括元数据和所有变量提示。
    
    Args:
        template_name: 要查看的模板名称
        
    Requirements: 3.3.3
    """
    harness_dir = get_harness_dir()
    
    # Import here to avoid circular dependencies
    from harness.template_loader import TemplateStore
    
    # Initialize TemplateStore
    template_store = TemplateStore(harness_dir)
    
    # Call template_store.get_template(template_name)
    template = template_store.get_template(template_name)
    
    # Handle template not found with friendly error message
    if not template:
        click.echo(f"模板 '{template_name}' 不存在。")
        return
    
    # Display template metadata: name, title, priority, effort, description
    click.echo(f"\n=== 模板: {template.name} ===\n")
    click.echo(f"标题: {template.title}")
    click.echo(f"优先级: {template.priority.value}")
    click.echo(f"工作量: {template.estimated_effort}\n")
    click.echo("描述:")
    click.echo(template.description)
    click.echo()
    
    # Display prompt details: key, required/optional, multiline, default value, question
    if template.prompts:
        click.echo("变量:")
        for prompt in template.prompts:
            # Format: key (required/optional) [multiline if applicable]: question [default: value]
            required_text = "必填" if prompt.required else "可选"
            multiline_text = "（多行）" if prompt.multiline else ""
            
            # Build the prompt line
            click.echo(f"  - {prompt.key} ({required_text}){multiline_text}: {prompt.question}")
            
            # Show default value if present
            if prompt.default:
                click.echo(f"    默认值: {prompt.default}")


# ===== Config 命令组 =====

@main.group()
def config():
    """配置管理命令"""
    pass


@config.command()
def show():
    """显示当前配置"""
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    manager = ConfigManager(harness_dir)
    settings = manager.load_with_env_overrides()

    click.echo("\n=== 当前配置 ===\n")
    click.echo(f"AI 模型：{settings.ai_model}")
    click.echo(f"执行模式：{settings.execution_mode.value}")
    click.echo(f"最大 Worker 数：{settings.max_workers}")

    api_status = "已设置" if settings.api_key else "未设置"
    click.echo(f"API 密钥：{api_status}")


@config.command()
@click.argument('key')
@click.argument('value')
def set(key: str, value: str):
    """更新配置项"""
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    manager = ConfigManager(harness_dir)
    manager.update(**{key: value})
    click.echo(f"已更新 {key} = {value}")


@config.command()
def init():
    """初始化默认配置"""
    harness_dir = get_harness_dir()
    manager = ConfigManager(harness_dir)
    manager.reset()
    click.echo("已创建默认配置。")


# ===== Work 命令组 (Phase 3) =====

@main.group()
def work():
    """任务执行命令"""
    pass


@work.command()
@click.argument('task_id', type=int)
def solo(task_id: int):
    """以 Solo 模式执行单个任务"""
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    store = TaskStore(harness_dir)
    task = store.get_task(task_id)

    if not task:
        click.echo(f"错误：未找到任务 #{task_id}")
        return

    click.echo(f"=== 执行任务 #{task_id}: {task.title} (Solo 模式) ===\n")

    service = TaskExecutionService(harness_dir)
    result = service.execute_task_solo(task_id)

    if result.success:
        click.echo(f"✅ 任务执行成功")
        click.echo(f"\n执行输出:\n{result.output}")
    else:
        click.echo(f"❌ 任务执行失败")
        click.echo(f"\n错误：{result.error}")
        click.echo(f"\n执行输出:\n{result.output}")


@work.command()
def parallel():
    """以 Parallel 模式执行所有 TODO 任务"""
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    store = TaskStore(harness_dir)
    tasks = store.get_tasks_by_status(TaskStatus.TODO)

    if not tasks:
        click.echo("没有待执行的任务。")
        return

    click.echo(f"=== 执行 {len(tasks)} 个任务 (Parallel 模式) ===\n")

    service = TaskExecutionService(harness_dir)
    task_ids = [t.id for t in tasks]
    results = service.execute_task_parallel(task_ids)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    click.echo(f"\n执行完成:")
    click.echo(f"  成功：{success_count}")
    click.echo(f"  失败：{fail_count}")


@work.command()
@click.argument('task_spec', nargs=-1)
@click.option('--all', 'execute_all', is_flag=True, help="执行所有 TODO 任务")
def all(task_spec, execute_all: bool):
    """执行任务

    可以指定单个任务 ID、任务范围或 --all 执行所有 TODO 任务
    """
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    store = TaskStore(harness_dir)

    # 解析任务 ID
    task_ids = []

    if execute_all:
        # 执行所有 TODO 任务
        tasks = store.get_tasks_by_status(TaskStatus.TODO)
        task_ids = [t.id for t in tasks]
    elif task_spec:
        # 解析任务规格
        for spec in task_spec:
            if '-' in spec:
                # 范围：如 1-5
                parts = spec.split('-')
                start = int(parts[0])
                end = int(parts[1])
                task_ids.extend(range(start, end + 1))
            else:
                # 单个 ID
                task_ids.append(int(spec))
    else:
        # 默认：执行所有 TODO 任务
        tasks = store.get_tasks_by_status(TaskStatus.TODO)
        task_ids = [t.id for t in tasks]

    if not task_ids:
        click.echo("没有任务可执行。")
        return

    # 自动选择模式
    tasks_to_execute = [store.get_task(tid) for tid in task_ids]
    tasks_to_execute = [t for t in tasks_to_execute if t is not None]

    if not tasks_to_execute:
        click.echo("任务不存在。")
        return

    mode = select_execution_mode(tasks_to_execute)
    mode_name = "Solo" if mode == ExecutionMode.SOLO else "Parallel"

    click.echo(f"=== 执行 {len(tasks_to_execute)} 个任务 ({mode_name} 模式) ===\n")

    service = TaskExecutionService(harness_dir)
    results = service.execute_tasks(task_ids)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    click.echo(f"\n执行完成:")
    click.echo(f"  成功：{success_count}")
    click.echo(f"  失败：{fail_count}")


@work.command()
def status():
    """显示执行状态"""
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。")
        return

    store = TaskStore(harness_dir)
    history = HistoryManager(harness_dir)

    stats = store.get_statistics()
    recent_events = history.get_recent_events(5)

    click.echo("\n=== 执行状态 ===\n")
    click.echo(f"总任务数：{stats['total']}")
    click.echo(f"待执行：{stats['todo']}")
    click.echo(f"进行中：{stats['wip']}")
    click.echo(f"已完成：{stats['done']}")
    click.echo(f"被阻塞：{stats['blocked']}")
    click.echo(f"\n进度：{stats['progress_percent']}%")

    if recent_events:
        click.echo("\n最近事件:")
        for event in recent_events:
            event_type = event.get('event', 'unknown')
            task_id = event.get('task_id', '?')
            task_title = event.get('task_title', 'Unknown')
            timestamp = event.get('timestamp', '')[:19]
            click.echo(f"  [{timestamp}] {event_type}: #{task_id} {task_title}")


# ===== Review 命令组 (Phase 4) =====

@main.group()
def review():
    """代码审查命令"""
    pass


@review.command()
@click.argument('file_path', nargs=-1, required=False)
@click.option('--all', 'review_all', is_flag=True, help="审查所有变更文件")
def code(file_path, review_all: bool):
    """审查代码文件

    可以审查单个或多个文件，或使用 --all 审查所有变更
    """
    if not file_path and not review_all:
        # 默认：审查当前目录下的 Python 文件
        import glob
        files = glob.glob("*.py")
        if not files:
            click.echo("错误：未指定文件，且当前目录没有 .py 文件。")
            click.echo("使用 'harness review code <文件路径>' 指定文件。")
            return
        file_path = files

    if review_all:
        # 审查所有变更文件（简化版：审查当前目录下的所有 Python 文件）
        import glob
        file_path = glob.glob("*.py")
        if not file_path:
            click.echo("没有 Python 文件可审查。")
            return

    # 加载自定义规则
    rule_engine = _load_custom_rule_engine()
    reviewer = ReviewerAgent(rule_engine=rule_engine)
    all_issues = []

    for fp in file_path:
        path = Path(fp)
        if not path.exists():
            click.echo(f"警告：文件不存在 {fp}")
            continue

        code = path.read_text(encoding='utf-8')
        result = reviewer.review_code(code, fp)

        click.echo(f"\n=== 审查：{fp} ===")
        click.echo(f"判定：{result.verdict.value}")

        if result.issues:
            click.echo(f"\n发现 {len(result.issues)} 个问题:")
            for issue in result.issues:
                severity_icon = {
                    "CRITICAL": "🔴",
                    "MAJOR": "🟡",
                    "MINOR": "🟢",
                    "INFO": "ℹ️"
                }.get(issue.severity.value, "")

                click.echo(f"\n  {severity_icon} [{issue.severity.value}] {issue.category.value}")
                click.echo(f"     {issue.message}")
                click.echo(f"     {fp}:{issue.line}")
                if issue.suggestion:
                    click.echo(f"     建议：{issue.suggestion}")
        else:
            click.echo("  没有问题 ✅")

        all_issues.extend(result.issues)

    # 总结
    click.echo("\n=== 审查总结 ===")
    critical = sum(1 for i in all_issues if i.severity.value == "CRITICAL")
    major = sum(1 for i in all_issues if i.severity.value == "MAJOR")
    minor = sum(1 for i in all_issues if i.severity.value == "MINOR")
    info = sum(1 for i in all_issues if i.severity.value == "INFO")

    if critical or major:
        click.echo(f"需要修改：{critical} 个严重，{major} 个主要问题")
    else:
        click.echo(f"批准：{minor} 个次要，{info} 个提示")


@review.command()
@click.argument('plan_id', type=str, required=False)
def plan(plan_id: str):
    """审查计划

    审查指定计划或最近创建的计划的合理性
    """
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先创建计划。")
        return

    store = TaskStore(harness_dir)
    tasks = store.load_tasks()

    if not tasks:
        click.echo("没有任务可审查。")
        return

    click.echo("=== 计划审查 ===\n")

    # 基础检查
    issues = []

    # 检查循环依赖
    task_ids = {t.id for t in tasks}
    for task in tasks:
        for dep_id in task.dependencies:
            if dep_id not in task_ids:
                issues.append(f"任务 {task.id} 依赖不存在的任务 {dep_id}")

    # 检查没有验收标准的任务
    for task in tasks:
        if not task.acceptance_criteria and task.priority == Priority.REQUIRED:
            issues.append(f"任务 {task.id} ({task.title}) 缺少验收标准")

    # 检查依赖关系是否合理
    for task in tasks:
        if task.dependencies and task.priority == Priority.REQUIRED:
            for dep_id in task.dependencies:
                dep_task = store.get_task(dep_id)
                if dep_task and dep_task.priority == Priority.OPTIONAL:
                    issues.append(f"Required 任务 {task.id} 依赖 Optional 任务 {dep_id}")

    if issues:
        click.echo(f"发现 {len(issues)} 个问题:\n")
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("计划审查通过 ✅")
        click.echo(f"总任务数：{len(tasks)}")

        # 统计
        required = sum(1 for t in tasks if t.priority == Priority.REQUIRED)
        recommended = sum(1 for t in tasks if t.priority == Priority.RECOMMENDED)
        optional = sum(1 for t in tasks if t.priority == Priority.OPTIONAL)

        click.echo(f"  Required: {required}")
        click.echo(f"  Recommended: {recommended}")
        click.echo(f"  Optional: {optional}")


@review.command()
def last():
    """显示最近的审查结果

    从历史记录中获取最近的审查结果
    """
    harness_dir = get_harness_dir()

    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。")
        return

    history = HistoryManager(harness_dir)
    recent_events = history.get_recent_events(10)

    if not recent_events:
        click.echo("没有历史记录。")
        return

    click.echo("=== 最近事件 ===\n")
    for event in recent_events:
        event_type = event.get('event', 'unknown')
        task_id = event.get('task_id', '?')
        task_title = event.get('task_title', 'Unknown')
        timestamp = event.get('timestamp', '')[:19]
        click.echo(f"[{timestamp}] {event_type}: #{task_id} {task_title}")


# ===== Custom Review Rules Commands =====


@review.group()
def rule():
    """自定义审查规则管理"""
    pass


@rule.command("add")
@click.argument('name')
@click.option('--pattern', '-p', required=True, help='正则表达式匹配模式')
@click.option('--message', '-m', required=True, help='问题描述')
@click.option('--suggestion', '-s', default='', help='修复建议')
@click.option('--severity', type=click.Choice(['CRITICAL', 'MAJOR', 'MINOR', 'INFO'], case_sensitive=False),
              default='MAJOR', help='问题严重程度')
@click.option('--category', type=click.Choice(['SECURITY', 'PERFORMANCE', 'QUALITY', 'ACCESSIBILITY', 'AI_RESIDUALS'],
                                               case_sensitive=False),
              default='QUALITY', help='问题类别')
@click.option('--file-pattern', default='*.py', help='匹配的文件 glob 模式（默认 *.py）')
@click.option('--description', '-d', default='', help='规则描述')
def add_rule(name: str, pattern: str, message: str, suggestion: str,
             severity: str, category: str, file_pattern: str, description: str):
    """添加自定义审查规则"""
    harness_dir = get_harness_dir()
    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。请先初始化项目。")
        return

    from harness.models import Severity as SevEnum, Category as CatEnum
    store = CustomRuleStore(harness_dir)

    rule_data = dict(
        name=name,
        pattern=pattern,
        message=message,
        suggestion=suggestion,
        severity=SevEnum.from_string(severity),
        category=CatEnum.from_string(category),
        file_pattern=file_pattern,
        enabled=True,
        description=description,
    )
    from harness.models import CustomReviewRule
    rule = CustomReviewRule(**rule_data)

    try:
        store.add_rule(rule)
        click.echo(f"✅ 自定义规则 '{name}' 创建成功")
        click.echo(f"   类别: {category} | 严重程度: {severity}")
        click.echo(f"   文件匹配: {file_pattern}")
        if description:
            click.echo(f"   描述: {description}")
    except RuleNameConflictError as e:
        click.echo(f"❌ 错误: {e}")


@rule.command("list")
@click.option('--category', '-c',
              type=click.Choice(['SECURITY', 'PERFORMANCE', 'QUALITY', 'ACCESSIBILITY', 'AI_RESIDUALS'],
                                case_sensitive=False),
              help='按类别过滤')
def list_rules(category: str):
    """列出自定义审查规则"""
    harness_dir = get_harness_dir()
    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。")
        return

    from harness.models import Category as CatEnum
    store = CustomRuleStore(harness_dir)
    cat = CatEnum.from_string(category) if category else None
    rules = store.list_rules(category=cat)

    if not rules:
        click.echo("没有自定义审查规则。")
        click.echo("使用 'harness review rule add <name> --pattern <regex> --message <msg>' 添加规则。")
        return

    click.echo(f"\n=== 自定义审查规则 ({len(rules)} 条) ===\n")
    for rule in rules:
        status_icon = "✅" if rule.enabled else "⛔"
        click.echo(f"{status_icon} {rule.name}")
        click.echo(f"   模式: {rule.pattern}")
        click.echo(f"   严重程度: {rule.severity.value} | 类别: {rule.category.value}")
        click.echo(f"   文件匹配: {rule.file_pattern}")
        if rule.description:
            click.echo(f"   描述: {rule.description}")
        click.echo()


@rule.command("remove")
@click.argument('name')
def remove_rule(name: str):
    """删除自定义审查规则"""
    harness_dir = get_harness_dir()
    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。")
        return

    store = CustomRuleStore(harness_dir)
    try:
        store.remove_rule(name)
        click.echo(f"✅ 规则 '{name}' 已删除")
    except RuleNotFoundError as e:
        click.echo(f"❌ 错误: {e}")


@rule.command("toggle")
@click.argument('name')
def toggle_rule(name: str):
    """启用/禁用自定义审查规则"""
    harness_dir = get_harness_dir()
    if not harness_dir.exists():
        click.echo("错误：未找到 .harness 目录。")
        return

    store = CustomRuleStore(harness_dir)
    try:
        new_state = store.toggle_rule(name)
        state_str = "启用" if new_state else "禁用"
        click.echo(f"✅ 规则 '{name}' 已{state_str}")
    except RuleNotFoundError as e:
        click.echo(f"❌ 错误: {e}")


@review.command()
@click.option('--base', default='HEAD~1', help='对比基准 (commit/branch/HEAD~N)')
def incremental(base: str):
    """增量代码审查

    只审查相对于基准的变更文件，提高审查效率。

    \b
    使用示例:
      harness review incremental              # 审查最近一次提交
      harness review incremental --base main  # 审查与 main 分支的差异
      harness review incremental --base abc123  # 审查与特定 commit 的差异
    """
    from harness.git import GitWorktreeManager
    
    # 获取仓库路径（当前目录）
    repo_path = Path.cwd()
    
    try:
        git_manager = GitWorktreeManager(str(repo_path))
    except Exception as e:
        click.echo(f"错误：无法初始化 Git 管理器 - {e}")
        return
    
    # 检测变更
    try:
        changes = git_manager.detect_changes_since(base)
    except ValueError as e:
        click.echo(f"错误：{e}")
        return
    except Exception as e:
        click.echo(f"错误：检测变更失败 - {e}")
        return
    
    if not changes:
        click.echo(f"没有相对于 '{base}' 的变更需要审查。")
        return
    
    # 输出报告头部
    click.echo("=== 增量代码审查报告 ===\n")
    click.echo(f"对比基准: {base}")
    click.echo(f"变更文件: {len(changes)} 个\n")
    
    # 逐文件审查
    rule_engine = _load_custom_rule_engine()
    reviewer = ReviewerAgent(rule_engine=rule_engine)
    all_results = {}
    total_issues = []
    
    for change in changes:
        file_path = Path(change.file)
        
        # 检查文件是否存在
        if not file_path.exists():
            click.echo(f"警告：文件不存在 {change.file}")
            continue
        
        # 读取文件内容
        try:
            code = file_path.read_text(encoding='utf-8')
        except Exception as e:
            click.echo(f"警告：无法读取文件 {change.file} - {e}")
            continue
        
        # 审查代码
        result = reviewer.review_code(code, change.file)
        all_results[change.file] = result
        
        # 显示文件审查结果
        click.echo(f"文件: {change.file}")
        click.echo("━" * 60)
        
        if result.issues:
            for issue in result.issues:
                severity_icon = {
                    "CRITICAL": "🔴",
                    "MAJOR": "🟡",
                    "MINOR": "🔵",
                    "INFO": "ℹ️"
                }.get(issue.severity.value, "")
                
                click.echo(f"{severity_icon} {issue.severity.value} - {issue.category.value}")
                click.echo(f"  第 {issue.line} 行: {issue.message}")
                if issue.suggestion:
                    click.echo(f"  建议: {issue.suggestion}")
                click.echo()
            
            total_issues.extend(result.issues)
        else:
            click.echo("✅ 没有问题\n")
    
    # 生成总结
    click.echo("━" * 60)
    click.echo("📊 总结\n")
    click.echo(f"总变更: {len(changes)} 个文件")
    
    if total_issues:
        critical = sum(1 for i in total_issues if i.severity.value == "CRITICAL")
        major = sum(1 for i in total_issues if i.severity.value == "MAJOR")
        minor = sum(1 for i in total_issues if i.severity.value == "MINOR")
        info = sum(1 for i in total_issues if i.severity.value == "INFO")
        
        click.echo("问题统计:")
        if critical > 0:
            click.echo(f"  - 严重问题: {critical} 个")
        if major > 0:
            click.echo(f"  - 主要问题: {major} 个")
        if minor > 0:
            click.echo(f"  - 次要问题: {minor} 个")
        if info > 0:
            click.echo(f"  - 提示信息: {info} 个")
        
        # 判定
        if critical >= 1 or major >= 2:
            click.echo("\n最终判定: ❌ REQUEST_CHANGES (需要修改)")
            if critical > 0:
                click.echo("建议: 优先修复 CRITICAL 级别的问题")
        else:
            click.echo("\n最终判定: ✅ APPROVE (批准)")
    else:
        click.echo("问题统计: 无问题")
        click.echo("\n最终判定: ✅ APPROVE (批准)")


if __name__ == '__main__':
    main()
