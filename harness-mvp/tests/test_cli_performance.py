"""测试性能监控 CLI 命令 - Phase 7"""
import pytest
from pathlib import Path
from click.testing import CliRunner
from harness.cli import main
from harness.models import Task, TaskStatus
from harness.history import HistoryManager
from harness.store import TaskStore
from harness.config import ConfigManager, Settings


class TestPerformanceCLI:
    """测试 performance CLI 命令组"""

    def _init_harness(self, tmp_path: Path):
        """初始化 .harness 目录并添加数据"""
        harness_dir = tmp_path / ".harness"
        harness_dir.mkdir(parents=True, exist_ok=True)

        config = ConfigManager(harness_dir)
        config.reset()

        store = TaskStore(harness_dir)
        task = Task(id=1, title="Test Task", status=TaskStatus.DONE)
        store.add_task(task)

        history = HistoryManager(harness_dir)
        history.log_task_completed(task, duration_minutes=30,
                                   model_used="claude-sonnet-4-20250514",
                                   success=True)

        return harness_dir

    def test_performance_group_exists(self):
        """RED: performance 命令组存在"""
        runner = CliRunner()
        result = runner.invoke(main, ["performance", "--help"])
        assert result.exit_code == 0
        assert "性能监控" in result.output

    def test_performance_summary_no_harness(self, tmp_path):
        """RED: 无 .harness 目录时提示错误"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            result = runner.invoke(main, ["performance", "summary"])
            assert result.exit_code == 0
            assert "未找到" in result.output

    def test_performance_summary_empty(self, tmp_path):
        """RED: 无数据时显示暂无数据"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            result = runner.invoke(main, ["performance", "summary"])
            assert "暂无数据" in result.output

    def test_performance_summary_with_data(self, tmp_path):
        """RED: 有数据时显示性能摘要"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            self._init_harness(Path(td))
            result = runner.invoke(main, ["performance", "summary"])
            assert result.exit_code == 0
            assert "总任务数" in result.output
            assert "已完成" in result.output

    def test_performance_model_usage_no_harness(self, tmp_path):
        """RED: 无 .harness 时提示错误"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            result = runner.invoke(main, ["performance", "model-usage"])
            assert result.exit_code == 0
            assert "未找到" in result.output

    def test_performance_model_usage_empty(self, tmp_path):
        """RED: 无数据时显示暂无数据"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            result = runner.invoke(main, ["performance", "model-usage"])
            assert "暂无模型使用数据" in result.output

    def test_performance_model_usage_with_data(self, tmp_path):
        """RED: 有数据时显示模型使用统计"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            self._init_harness(Path(td))
            result = runner.invoke(main, ["performance", "model-usage"])
            assert result.exit_code == 0
            assert "claude-sonnet-4-20250514" in result.output

    def test_performance_task_basic(self, tmp_path):
        """RED: 显示任务时序信息"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            self._init_harness(Path(td))
            result = runner.invoke(main, ["performance", "task", "1"])
            assert result.exit_code == 0
            assert "Test Task" in result.output
            assert "30 分钟" in result.output

    def test_performance_task_not_found(self, tmp_path):
        """RED: 任务不存在时提示"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            result = runner.invoke(main, ["performance", "task", "999"])
            assert "未找到" in result.output

    def test_performance_bottlenecks(self, tmp_path):
        """RED: 显示瓶颈任务"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            self._init_harness(Path(td))
            result = runner.invoke(main, ["performance", "bottlenecks"])
            assert result.exit_code == 0
            assert "Test Task" in result.output
            assert "30" in result.output

    def test_performance_bottlenecks_empty(self, tmp_path):
        """RED: 无数据时显示暂无"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            result = runner.invoke(main, ["performance", "bottlenecks"])
            assert "暂无" in result.output

    def test_performance_effort(self, tmp_path):
        """RED: 显示工作量分析"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            store = TaskStore(harness_dir)
            store.add_task(Task(id=1, title="T1", estimated_effort=3,
                                actual_effort=4, status=TaskStatus.DONE))
            history = HistoryManager(harness_dir)
            history.log_task_completed(
                Task(id=1, title="T1"), duration_minutes=20
            )

            result = runner.invoke(main, ["performance", "effort"])
            assert result.exit_code == 0
            assert "工作量" in result.output

    def test_performance_effort_empty(self, tmp_path):
        """RED: 无任务时显示暂无"""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            harness_dir = Path(td) / ".harness"
            harness_dir.mkdir(parents=True, exist_ok=True)
            ConfigManager(harness_dir).reset()

            result = runner.invoke(main, ["performance", "effort"])
            assert "暂无" in result.output
