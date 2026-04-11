"""测试历史记录 - Phase 2"""
import pytest
from pathlib import Path
from harness.models import Task, TaskStatus
from harness.history import HistoryManager


class TestHistoryManager:
    """测试 HistoryManager"""

    def test_init_creates_directory(self, tmp_path):
        """RED: 测试初始化时创建 history 目录"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)
        history_dir = harness_dir / "history"
        assert history_dir.exists()

    def test_log_task_created(self, tmp_path):
        """RED: 测试记录任务创建事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task")
        history.log_task_created(task)

        events = history.get_all_events()
        assert len(events) == 1
        assert events[0]["event"] == "task_created"
        assert events[0]["task_id"] == 1

    def test_log_task_updated(self, tmp_path):
        """RED: 测试记录任务更新事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task")
        history.log_task_updated(task, ["title", "status"])

        events = history.get_all_events()
        assert len(events) == 1
        assert events[0]["event"] == "task_updated"
        assert events[0]["task_id"] == 1
        assert "title" in events[0]["changes"]

    def test_log_task_completed(self, tmp_path):
        """RED: 测试记录任务完成事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task", status=TaskStatus.DONE)
        history.log_task_completed(task, duration_minutes=30)

        events = history.get_all_events()
        assert len(events) == 1
        assert events[0]["event"] == "task_completed"
        assert events[0]["task_id"] == 1
        assert events[0]["duration_minutes"] == 30

    def test_log_task_blocked(self, tmp_path):
        """RED: 测试记录任务阻塞事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task", status=TaskStatus.BLOCKED)
        history.log_task_blocked(task, "等待 API 文档")

        events = history.get_all_events()
        assert len(events) == 1
        assert events[0]["event"] == "task_blocked"
        assert events[0]["task_id"] == 1
        assert events[0]["reason"] == "等待 API 文档"

    def test_get_events_by_task(self, tmp_path):
        """RED: 测试获取指定任务的事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task1 = Task(id=1, title="Task 1")
        task2 = Task(id=2, title="Task 2")

        history.log_task_created(task1)
        history.log_task_created(task2)
        history.log_task_updated(task1, ["status"])

        task1_events = history.get_events_by_task(1)
        assert len(task1_events) == 2

        task2_events = history.get_events_by_task(2)
        assert len(task2_events) == 1

    def test_get_recent_events(self, tmp_path):
        """RED: 测试获取最近事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        for i in range(10):
            task = Task(id=i + 1, title=f"Task {i + 1}")
            history.log_task_created(task)

        recent = history.get_recent_events(limit=5)
        assert len(recent) == 5

    def test_get_events_by_type(self, tmp_path):
        """RED: 测试获取指定类型的事件"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task")
        history.log_task_created(task)
        history.log_task_updated(task, ["status"])
        history.log_task_completed(task, 30)

        completed_events = history.get_events_by_type("task_completed")
        assert len(completed_events) == 1
        assert completed_events[0]["event"] == "task_completed"

    def test_clear_history(self, tmp_path):
        """RED: 测试清空历史记录"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task")
        history.log_task_created(task)

        events = history.get_all_events()
        assert len(events) == 1

        history.clear_history()

        events = history.get_all_events()
        assert len(events) == 0

    def test_get_task_duration(self, tmp_path):
        """RED: 测试获取任务持续时间"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        task = Task(id=1, title="Test Task")
        history.log_task_created(task)
        history.log_task_completed(task, duration_minutes=45)

        duration = history.get_task_duration(1)
        assert duration == 45

    def test_get_task_duration_not_found(self, tmp_path):
        """RED: 测试获取不存在的任务持续时间返回 0"""
        harness_dir = tmp_path / ".harness"
        history = HistoryManager(harness_dir)

        duration = history.get_task_duration(999)
        assert duration == 0
