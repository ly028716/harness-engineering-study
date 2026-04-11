"""测试 CLI 命令 - Phase 2"""
import pytest
from click.testing import CliRunner
from pathlib import Path
from harness.cli import main
from harness.models import Task, TaskStatus, Priority


@pytest.fixture
def runner():
    """创建 Click 测试运行器"""
    return CliRunner()


@pytest.fixture
def harness_dir(tmp_path):
    """创建 .harness 目录"""
    harness = tmp_path / ".harness"
    harness.mkdir()
    return harness


class TestPlanList:
    """测试 plan list 命令"""

    def test_list_empty_tasks(self, runner, tmp_path, monkeypatch):
        """RED: 测试列出空任务列表"""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(main, ['plan', 'list'])
        assert result.exit_code == 0
        assert "没有任务" in result.output or "Task" not in result.output

    def test_list_tasks(self, runner, tmp_path, monkeypatch):
        """RED: 测试列出任务"""
        monkeypatch.chdir(tmp_path)

        # 先添加任务
        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        store.add_task(Task(id=1, title="Task 1", status=TaskStatus.TODO))
        store.add_task(Task(id=2, title="Task 2", status=TaskStatus.WIP))

        result = runner.invoke(main, ['plan', 'list'])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output


class TestPlanShow:
    """测试 plan show 命令"""

    def test_show_task(self, runner, tmp_path, monkeypatch):
        """RED: 测试显示任务详情"""
        monkeypatch.chdir(tmp_path)

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        task = Task(
            id=1,
            title="实现登录功能",
            description="实现用户登录 API",
            acceptance_criteria=["返回 200", "返回 JWT token"]
        )
        store.add_task(task)

        result = runner.invoke(main, ['plan', 'show', '1'])
        assert result.exit_code == 0
        assert "实现登录功能" in result.output
        assert "实现用户登录 API" in result.output

    def test_show_task_not_found(self, runner, tmp_path, monkeypatch):
        """RED: 测试显示不存在的任务"""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(main, ['plan', 'show', '999'])
        assert result.exit_code == 0
        assert "未找到" in result.output or "不存在" in result.output


class TestPlanUpdate:
    """测试 plan update 命令"""

    def test_update_task_status(self, runner, tmp_path, monkeypatch):
        """RED: 测试更新任务状态"""
        monkeypatch.chdir(tmp_path)

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        store.add_task(Task(id=1, title="Task 1", status=TaskStatus.TODO))

        result = runner.invoke(main, ['plan', 'update', '1', '--status', 'WIP'])
        assert result.exit_code == 0

        # 验证状态已更新
        task = store.get_task(1)
        assert task.status == TaskStatus.WIP

    def test_update_task_not_found(self, runner, tmp_path, monkeypatch):
        """RED: 测试更新不存在的任务"""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(main, ['plan', 'update', '999', '--status', 'WIP'])
        assert result.exit_code == 0
        assert "未找到" in result.output or "不存在" in result.output


class TestPlanSync:
    """测试 plan sync 命令"""

    def test_sync_creates_plans_md(self, runner, tmp_path, monkeypatch):
        """RED: 测试同步创建 Plans.md"""
        monkeypatch.chdir(tmp_path)

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        store.add_task(Task(id=1, title="Task 1", status=TaskStatus.TODO))

        result = runner.invoke(main, ['plan', 'sync'])
        assert result.exit_code == 0

        plans_file = tmp_path / "Plans.md"
        assert plans_file.exists()

    def test_sync_updates_plans_md(self, runner, tmp_path, monkeypatch):
        """RED: 测试同步更新 Plans.md"""
        monkeypatch.chdir(tmp_path)

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        task = Task(id=1, title="Task 1", status=TaskStatus.WIP)
        store.add_task(task)

        # 创建初始 Plans.md
        plans_file = tmp_path / "Plans.md"
        plans_file.write_text("# Plans\n\n## Tasks\n\n")

        result = runner.invoke(main, ['plan', 'sync'])
        assert result.exit_code == 0
        assert "Task 1" in plans_file.read_text()


class TestPlanAdd:
    """测试 plan add 命令"""

    def test_add_task_interactive(self, runner, tmp_path, monkeypatch):
        """RED: 测试交互式添加任务"""
        monkeypatch.chdir(tmp_path)

        # 模拟用户输入
        result = runner.invoke(
            main,
            ['plan', 'add'],
            input="新任务\n任务描述\nREQUIRED\n3\n"
        )
        assert result.exit_code == 0

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        tasks = store.load_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "新任务"


class TestPlanStatistics:
    """测试 plan stats 命令"""

    def test_show_statistics(self, runner, tmp_path, monkeypatch):
        """RED: 测试显示统计信息"""
        monkeypatch.chdir(tmp_path)

        from harness.store import TaskStore
        store = TaskStore(tmp_path / ".harness")
        store.add_task(Task(id=1, title="Task 1", status=TaskStatus.TODO))
        store.add_task(Task(id=2, title="Task 2", status=TaskStatus.WIP))
        store.add_task(Task(id=3, title="Task 3", status=TaskStatus.DONE))

        result = runner.invoke(main, ['plan', 'stats'])
        assert result.exit_code == 0
        assert "总数" in result.output or "Total" in result.output
        assert "3" in result.output
