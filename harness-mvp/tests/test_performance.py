"""测试性能监控 - Phase 7"""
import pytest
from pathlib import Path
from harness.models import Task, TaskStatus
from harness.history import HistoryManager
from harness.performance import PerformanceMonitor, PerformanceMetrics, ModelUsageStats


class TestPerformanceMetrics:
    """测试 PerformanceMetrics"""

    def test_default_values(self):
        """测试默认值"""
        metrics = PerformanceMetrics()
        assert metrics.total_duration_minutes == 0.0
        assert metrics.total_completed == 0
        assert metrics.success_rate == 100.0

    def test_to_dict(self):
        """测试序列化"""
        metrics = PerformanceMetrics(
            total_duration_minutes=60.0,
            avg_duration_minutes=30.0,
            total_completed=2,
            success_rate=100.0,
        )
        d = metrics.to_dict()
        assert d["total_duration_minutes"] == 60.0
        assert d["total_completed"] == 2

    def test_to_dict_contains_all_fields(self):
        """测试序列化包含所有字段"""
        metrics = PerformanceMetrics()
        d = metrics.to_dict()
        expected_keys = [
            "total_duration_minutes", "avg_duration_minutes",
            "min_duration_minutes", "max_duration_minutes",
            "median_duration_minutes", "total_completed", "total_failed",
            "success_rate", "total_tasks", "completed_tasks",
            "effort_accuracy", "bottleneck_tasks",
        ]
        for key in expected_keys:
            assert key in d


class TestModelUsageStats:
    """测试 ModelUsageStats"""

    def test_default_values(self):
        """测试默认值"""
        stats = ModelUsageStats(model_name="test-model")
        assert stats.model_name == "test-model"
        assert stats.task_count == 0
        assert stats.success_rate == 100.0

    def test_to_dict(self):
        """测试序列化"""
        stats = ModelUsageStats(
            model_name="claude-sonnet-4-20250514",
            task_count=10,
            success_count=9,
            failure_count=1,
            success_rate=90.0,
        )
        d = stats.to_dict()
        assert d["model_name"] == "claude-sonnet-4-20250514"
        assert d["task_count"] == 10
        assert d["success_rate"] == 90.0

    def test_to_dict_contains_all_fields(self):
        """测试序列化包含所有字段"""
        stats = ModelUsageStats(model_name="m1")
        d = stats.to_dict()
        expected_keys = [
            "model_name", "task_count", "avg_duration_seconds",
            "total_duration_seconds", "success_count", "failure_count",
            "success_rate",
        ]
        for key in expected_keys:
            assert key in d


class TestPerformanceMonitor:
    """测试 PerformanceMonitor"""

    def test_init(self, tmp_path):
        """RED: 测试初始化"""
        monitor = PerformanceMonitor(tmp_path)
        assert monitor.harness_dir == tmp_path

    def test_get_summary_empty(self, tmp_path):
        """RED: 无数据时返回空摘要"""
        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert metrics.total_tasks == 0
        assert metrics.total_completed == 0

    def test_get_summary_with_data(self, tmp_path):
        """RED: 有数据时返回完整摘要"""
        history = HistoryManager(tmp_path)
        task = Task(id=1, title="Task 1", status=TaskStatus.DONE)
        history.log_task_completed(task, duration_minutes=30,
                                   model_used="claude-sonnet-4-20250514",
                                   success=True)

        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert metrics.total_completed == 1
        assert metrics.total_duration_minutes == 30.0
        assert metrics.success_rate == 100.0

    def test_get_summary_with_failure(self, tmp_path):
        """RED: 有失败任务时正确计算成功率"""
        history = HistoryManager(tmp_path)
        task1 = Task(id=1, title="Task 1", status=TaskStatus.DONE)
        task2 = Task(id=2, title="Task 2", status=TaskStatus.DONE)
        history.log_task_completed(task1, duration_minutes=10, success=True)
        history.log_task_completed(task2, duration_minutes=5, success=False)

        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert metrics.total_completed == 1
        assert metrics.total_failed == 1
        assert metrics.success_rate == 50.0

    def test_get_summary_tasks_from_store(self, tmp_path):
        """RED: 从 TaskStore 加载总任务数和已完成数"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        store.add_task(Task(id=1, title="Task 1"))
        store.add_task(Task(id=2, title="Task 2", status=TaskStatus.DONE))

        history = HistoryManager(tmp_path)
        history.log_task_completed(
            Task(id=2, title="Task 2"), duration_minutes=15
        )

        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert metrics.total_tasks == 2
        assert metrics.completed_tasks == 1

    def test_get_model_usage_empty(self, tmp_path):
        """RED: 无数据时返回空列表"""
        monitor = PerformanceMonitor(tmp_path)
        stats = monitor.get_model_usage()
        assert stats == []

    def test_get_model_usage_single_model(self, tmp_path):
        """RED: 单个模型的正确统计"""
        history = HistoryManager(tmp_path)
        task = Task(id=1, title="Task 1")
        history.log_task_completed(task, duration_minutes=10,
                                   model_used="claude-sonnet-4-20250514",
                                   success=True)

        monitor = PerformanceMonitor(tmp_path)
        stats = monitor.get_model_usage()
        assert len(stats) == 1
        assert stats[0].model_name == "claude-sonnet-4-20250514"
        assert stats[0].task_count == 1
        assert stats[0].success_count == 1

    def test_get_model_usage_multiple_models(self, tmp_path):
        """RED: 多个模型的正确统计"""
        history = HistoryManager(tmp_path)
        history.log_task_completed(
            Task(id=1, title="T1"), duration_minutes=10,
            model_used="model-a", success=True
        )
        history.log_task_completed(
            Task(id=2, title="T2"), duration_minutes=5,
            model_used="model-b", success=True
        )
        history.log_task_completed(
            Task(id=3, title="T3"), duration_minutes=15,
            model_used="model-a", success=False
        )

        monitor = PerformanceMonitor(tmp_path)
        stats = monitor.get_model_usage()
        assert len(stats) == 2
        # model-a 使用 2 次，应排第一
        assert stats[0].model_name == "model-a"
        assert stats[0].task_count == 2
        assert stats[0].success_count == 1
        assert stats[0].failure_count == 1
        assert stats[0].success_rate == 50.0

    def test_get_model_usage_unknown_model(self, tmp_path):
        """RED: model_used 为空时标记为 unknown"""
        history = HistoryManager(tmp_path)
        history.log_task_completed(
            Task(id=1, title="T1"), duration_minutes=10, success=True
        )

        monitor = PerformanceMonitor(tmp_path)
        stats = monitor.get_model_usage()
        assert len(stats) == 1
        assert stats[0].model_name == "unknown"

    def test_get_task_timing_nonexistent(self, tmp_path):
        """RED: 不存在的任务返回 None"""
        monitor = PerformanceMonitor(tmp_path)
        assert monitor.get_task_timing(999) is None

    def test_get_task_timing_basic(self, tmp_path):
        """RED: 获取基本任务时序信息"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        task = Task(id=1, title="Test Task", estimated_effort=3)
        store.add_task(task)
        history = HistoryManager(tmp_path)
        history.log_task_completed(task, duration_minutes=25,
                                   model_used="claude-sonnet-4-20250514")

        monitor = PerformanceMonitor(tmp_path)
        timing = monitor.get_task_timing(1)
        assert timing is not None
        assert timing["task_id"] == 1
        assert timing["title"] == "Test Task"
        assert timing["estimated_effort"] == 3
        assert timing["duration_minutes"] == 25
        assert timing["model_used"] == "claude-sonnet-4-20250514"
        assert timing["event_count"] >= 1

    def test_get_task_timing_no_completed_event(self, tmp_path):
        """RED: 无完成事件时的时序信息"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        store.add_task(Task(id=1, title="Test Task"))

        monitor = PerformanceMonitor(tmp_path)
        timing = monitor.get_task_timing(1)
        assert timing is not None
        assert timing["duration_minutes"] == 0
        assert timing["model_used"] == ""

    def test_get_effort_analysis_empty(self, tmp_path):
        """RED: 无任务时返回空分析"""
        monitor = PerformanceMonitor(tmp_path)
        analysis = monitor.get_effort_analysis()
        assert analysis["total_tasks_completed"] == 0
        assert analysis["accuracy_percent"] == 100.0

    def test_get_effort_analysis_accurate(self, tmp_path):
        """RED: 完全准确的工作量估算"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        store.add_task(Task(id=1, title="T1", estimated_effort=3,
                            actual_effort=3, status=TaskStatus.DONE))
        store.add_task(Task(id=2, title="T2", estimated_effort=5,
                            actual_effort=5, status=TaskStatus.DONE))

        monitor = PerformanceMonitor(tmp_path)
        analysis = monitor.get_effort_analysis()
        assert analysis["total_tasks_completed"] == 2
        assert analysis["estimated_total_hours"] == 8
        assert analysis["actual_total_hours"] == 8
        assert analysis["accuracy_percent"] == 100.0

    def test_get_effort_analysis_over_estimate(self, tmp_path):
        """RED: 超出估算的任务被识别"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        store.add_task(Task(id=1, title="T1", estimated_effort=2,
                            actual_effort=4, status=TaskStatus.DONE))

        monitor = PerformanceMonitor(tmp_path)
        analysis = monitor.get_effort_analysis()
        assert len(analysis["over_estimated_tasks"]) == 1
        over = analysis["over_estimated_tasks"][0]
        assert over["task_id"] == 1
        assert over["ratio"] == 2.0

    def test_get_effort_analysis_no_actual(self, tmp_path):
        """RED: 无实际工作量的任务不影响准确度"""
        from harness.store import TaskStore
        store = TaskStore(tmp_path)
        store.add_task(Task(id=1, title="T1", estimated_effort=3,
                            status=TaskStatus.DONE))

        monitor = PerformanceMonitor(tmp_path)
        analysis = monitor.get_effort_analysis()
        assert analysis["accuracy_percent"] == 100.0

    def test_bottlenecks_empty(self, tmp_path):
        """RED: 无任务时返回空列表"""
        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert metrics.bottleneck_tasks == []

    def test_bottlenecks_sorted_by_duration(self, tmp_path):
        """RED: 瓶颈任务按耗时降序排列"""
        history = HistoryManager(tmp_path)
        history.log_task_completed(Task(id=1, title="Fast"),
                                   duration_minutes=5)
        history.log_task_completed(Task(id=2, title="Medium"),
                                   duration_minutes=15)
        history.log_task_completed(Task(id=3, title="Slow"),
                                   duration_minutes=30)

        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert len(metrics.bottleneck_tasks) == 3
        assert metrics.bottleneck_tasks[0]["task_id"] == 3
        assert metrics.bottleneck_tasks[0]["duration_minutes"] == 30
        assert metrics.bottleneck_tasks[1]["task_id"] == 2
        assert metrics.bottleneck_tasks[2]["task_id"] == 1

    def test_bottlenecks_respects_top_n(self, tmp_path):
        """RED: 瓶颈任务受 top_n 限制"""
        history = HistoryManager(tmp_path)
        for i in range(10):
            history.log_task_completed(
                Task(id=i, title=f"T{i}"), duration_minutes=i * 10
            )

        from harness.performance import PerformanceMetrics
        monitor = PerformanceMonitor(tmp_path)
        metrics = monitor.get_summary()
        assert len(metrics.bottleneck_tasks) == 5  # 默认 top_n=5
