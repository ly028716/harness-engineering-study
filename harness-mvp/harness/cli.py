"""CLI 入口点 - Phase 2 扩展"""
import click
from pathlib import Path
from harness import __version__
from harness.models import Task, TaskStatus, Priority
from harness.store import TaskStore
from harness.history import HistoryManager
from harness.executor import TaskExecutionService, select_execution_mode, ExecutionMode
from harness.reviewer import ReviewerAgent, ReviewResult


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
@click.option('--title', '-t', help="任务标题")
@click.option('--description', '-d', help="任务描述")
@click.option('--priority', '-p', type=click.Choice(['REQUIRED', 'RECOMMENDED', 'OPTIONAL'], case_sensitive=False), default='REQUIRED')
@click.option('--estimate', '-e', type=int, default=1, help="估算工作量 (1-5)")
def add(title: str, description: str, priority: str, estimate: int):
    """添加新任务（交互式或参数式）"""
    harness_dir = get_harness_dir()
    store = TaskStore(harness_dir)
    history = HistoryManager(harness_dir)

    # 如果没有提供参数，使用交互模式
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

    reviewer = ReviewerAgent()
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


if __name__ == '__main__':
    main()
