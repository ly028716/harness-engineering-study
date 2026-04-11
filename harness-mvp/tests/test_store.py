"""测试 TaskStore - Phase 2"""
import pytest
from pathlib import Path
from harness.models import Task, TaskStatus, Priority
from harness.store import TaskStore


class TestTaskStore:
    """测试 TaskStore"""

    def test_init_creates_directory(self, tmp_path):
        """RED: 测试初始化时创建 .harness 目录"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)
        assert harness_dir.exists()

    def test_init_creates_state_file(self, tmp_path):
        """RED: 测试初始化时创建 state.json 文件"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)
        state_file = harness_dir / "state.json"
        assert state_file.exists()

    def test_save_and_load_tasks(self, tmp_path):
        """RED: 测试保存和加载任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
        ]
        store.save_tasks(tasks)

        loaded_tasks = store.load_tasks()
        assert len(loaded_tasks) == 2
        assert loaded_tasks[0].title == "Task 1"
        assert loaded_tasks[1].title == "Task 2"

    def test_get_task_by_id(self, tmp_path):
        """RED: 测试根据 ID 获取任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
        ]
        store.save_tasks(tasks)

        task = store.get_task(1)
        assert task is not None
        assert task.title == "Task 1"

    def test_get_task_not_found(self, tmp_path):
        """RED: 测试获取不存在的任务返回 None"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [Task(id=1, title="Task 1")]
        store.save_tasks(tasks)

        task = store.get_task(999)
        assert task is None

    def test_add_task(self, tmp_path):
        """RED: 测试添加新任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        task = Task(id=1, title="New Task")
        store.add_task(task)

        loaded_tasks = store.load_tasks()
        assert len(loaded_tasks) == 1
        assert loaded_tasks[0].title == "New Task"

    def test_update_task(self, tmp_path):
        """RED: 测试更新任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        task = Task(id=1, title="Task 1")
        store.add_task(task)

        task.title = "Updated Task"
        task.status = TaskStatus.WIP
        store.update_task(task)

        loaded_task = store.get_task(1)
        assert loaded_task.title == "Updated Task"
        assert loaded_task.status == TaskStatus.WIP

    def test_delete_task(self, tmp_path):
        """RED: 测试删除任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
        ]
        for task in tasks:
            store.add_task(task)

        store.delete_task(1)

        loaded_tasks = store.load_tasks()
        assert len(loaded_tasks) == 1
        assert loaded_tasks[0].id == 2

    def test_get_tasks_by_status(self, tmp_path):
        """RED: 测试根据状态获取任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1", status=TaskStatus.TODO),
            Task(id=2, title="Task 2", status=TaskStatus.WIP),
            Task(id=3, title="Task 3", status=TaskStatus.DONE),
        ]
        for task in tasks:
            store.add_task(task)

        wip_tasks = store.get_tasks_by_status(TaskStatus.WIP)
        assert len(wip_tasks) == 1
        assert wip_tasks[0].title == "Task 2"

    def test_get_tasks_by_priority(self, tmp_path):
        """RED: 测试根据优先级获取任务"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1", priority=Priority.REQUIRED),
            Task(id=2, title="Task 2", priority=Priority.RECOMMENDED),
            Task(id=3, title="Task 3", priority=Priority.OPTIONAL),
        ]
        for task in tasks:
            store.add_task(task)

        required_tasks = store.get_tasks_by_priority(Priority.REQUIRED)
        assert len(required_tasks) == 1
        assert required_tasks[0].title == "Task 1"

    def test_get_next_task_id(self, tmp_path):
        """RED: 测试获取下一个任务 ID"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
        ]
        for task in tasks:
            store.add_task(task)

        next_id = store.get_next_task_id()
        assert next_id == 3

    def test_get_next_task_id_empty(self, tmp_path):
        """RED: 测试空任务列表时下一个 ID 为 1"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        next_id = store.get_next_task_id()
        assert next_id == 1

    def test_get_statistics(self, tmp_path):
        """RED: 测试获取任务统计"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        tasks = [
            Task(id=1, title="Task 1", status=TaskStatus.TODO),
            Task(id=2, title="Task 2", status=TaskStatus.WIP),
            Task(id=3, title="Task 3", status=TaskStatus.DONE),
            Task(id=4, title="Task 4", status=TaskStatus.DONE),
        ]
        for task in tasks:
            store.add_task(task)

        stats = store.get_statistics()
        assert stats["total"] == 4
        assert stats["todo"] == 1
        assert stats["wip"] == 1
        assert stats["done"] == 2
        assert stats["blocked"] == 0
        assert stats["progress_percent"] == 50  # 2/4 = 50%

    def test_get_statistics_empty(self, tmp_path):
        """RED: 测试空任务列表的统计"""
        harness_dir = tmp_path / ".harness"
        store = TaskStore(harness_dir)

        stats = store.get_statistics()
        assert stats["total"] == 0
        assert stats["todo"] == 0
        assert stats["wip"] == 0
        assert stats["done"] == 0
        assert stats["blocked"] == 0
        assert stats["progress_percent"] == 0
