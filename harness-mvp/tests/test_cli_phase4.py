"""测试 Review CLI 命令 - Phase 4"""
import pytest
from pathlib import Path
from click.testing import CliRunner
from harness.cli import main
from harness.models import Task, TaskStatus, Priority
from harness.store import TaskStore


@pytest.fixture
def runner():
    """创建 CLI runner"""
    return CliRunner()


@pytest.fixture
def temp_harness_dir(tmp_path):
    """创建临时 .harness 目录"""
    harness_dir = tmp_path / ".harness"
    harness_dir.mkdir()
    return harness_dir


@pytest.fixture
def temp_project(tmp_path, temp_harness_dir):
    """创建临时项目环境"""
    # 创建测试文件
    test_file = tmp_path / "test_code.py"
    test_file.write_text('''
def add(a, b):
    """返回两个数的和"""
    return a + b
''')

    # 创建有问题的文件
    bad_file = tmp_path / "bad_code.py"
    bad_file.write_text('''
# TODO: 实现这个功能
def login(user_id):
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    API_KEY = "test_key_12345"
    return True
''')

    return tmp_path


class TestReviewCodeCommand:
    """测试 harness review code 命令"""

    def test_review_code_single_file(self, runner, temp_project):
        """RED: 测试审查单个文件"""
        test_file = temp_project / "test_code.py"
        result = runner.invoke(main, ['review', 'code', str(test_file)])
        assert result.exit_code == 0
        assert '审查' in result.output
        assert '判定：' in result.output

    def test_review_code_with_issues(self, runner, temp_project):
        """RED: 测试审查有问题的文件"""
        bad_file = temp_project / "bad_code.py"
        result = runner.invoke(main, ['review', 'code', str(bad_file)])
        assert result.exit_code == 0
        assert '审查' in result.output
        # 应该检测到问题
        assert '发现' in result.output or '问题' in result.output or 'CRITICAL' in result.output

    def test_review_code_nonexistent_file(self, runner, temp_project):
        """RED: 测试审查不存在的文件"""
        result = runner.invoke(main, ['review', 'code', str(temp_project / 'nonexistent.py')])
        assert result.exit_code == 0
        assert '警告' in result.output or '不存在' in result.output

    def test_review_code_multiple_files(self, runner, temp_project):
        """RED: 测试审查多个文件"""
        test_file = str(temp_project / "test_code.py")
        bad_file = str(temp_project / "bad_code.py")
        result = runner.invoke(main, ['review', 'code', test_file, bad_file])
        assert result.exit_code == 0
        assert '审查' in result.output
        assert '审查总结' in result.output

    def test_review_code_all_flag(self, runner, temp_project):
        """RED: 测试使用 --all 标志"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'code', '--all'])
            assert result.exit_code == 0
            # 应该审查所有 Python 文件
            assert '审查' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_code_no_files(self, runner, tmp_path):
        """RED: 测试没有文件时的行为"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(main, ['review', 'code'])
            assert result.exit_code == 0
            assert '错误' in result.output or '没有' in result.output
        finally:
            os.chdir(old_cwd)


class TestReviewPlanCommand:
    """测试 harness review plan 命令"""

    def test_review_plan_no_harness_dir(self, runner, tmp_path):
        """RED: 测试没有 .harness 目录时的行为"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '错误' in result.output or '未找到' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_plan_empty(self, runner, temp_project, temp_harness_dir):
        """RED: 测试审查空计划"""
        import os
        store = TaskStore(temp_harness_dir)
        store.save_tasks([])

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '没有任务' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_plan_valid(self, runner, temp_project, temp_harness_dir):
        """RED: 测试审查有效计划"""
        import os
        store = TaskStore(temp_harness_dir)
        tasks = [
            Task(
                id=1,
                title="实现登录功能",
                description="支持邮箱和密码验证",
                priority=Priority.REQUIRED,
                acceptance_criteria=["返回 200", "返回 JWT token"]
            ),
            Task(
                id=2,
                title="添加测试",
                description="单元测试",
                priority=Priority.RECOMMENDED,
                acceptance_criteria=["覆盖率 80%+"]
            )
        ]
        store.save_tasks(tasks)

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '计划审查' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_plan_missing_acceptance_criteria(self, runner, temp_project, temp_harness_dir):
        """RED: 测试检测缺少验收标准的任务"""
        import os
        store = TaskStore(temp_harness_dir)
        tasks = [
            Task(
                id=1,
                title="实现功能",
                description="描述",
                priority=Priority.REQUIRED,
                acceptance_criteria=[]  # 缺少验收标准
            )
        ]
        store.save_tasks(tasks)

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '缺少验收标准' in result.output or '问题' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_plan_invalid_dependency(self, runner, temp_project, temp_harness_dir):
        """RED: 测试检测无效依赖"""
        import os
        store = TaskStore(temp_harness_dir)
        tasks = [
            Task(
                id=1,
                title="任务 1",
                priority=Priority.REQUIRED,
                dependencies=[999]  # 不存在的依赖
            )
        ]
        store.save_tasks(tasks)

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '依赖' in result.output or '问题' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_plan_priority_mismatch(self, runner, temp_project, temp_harness_dir):
        """RED: 测试检测优先级不匹配的依赖"""
        import os
        store = TaskStore(temp_harness_dir)
        tasks = [
            Task(
                id=1,
                title="可选任务",
                priority=Priority.OPTIONAL
            ),
            Task(
                id=2,
                title="必需任务",
                priority=Priority.REQUIRED,
                dependencies=[1]  # Required 依赖 Optional
            )
        ]
        store.save_tasks(tasks)

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            # 应该检测到优先级不匹配
            assert 'Optional' in result.output or '问题' in result.output
        finally:
            os.chdir(old_cwd)


class TestReviewLastCommand:
    """测试 harness review last 命令"""

    def test_review_last_no_harness_dir(self, runner, tmp_path):
        """RED: 测试没有 .harness 目录时的行为"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(main, ['review', 'last'])
            assert result.exit_code == 0
            assert '错误' in result.output or '未找到' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_last_no_history(self, runner, temp_project, temp_harness_dir):
        """RED: 测试没有历史记录时的行为"""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'last'])
            assert result.exit_code == 0
            assert '没有历史记录' in result.output or '没有' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_last_with_history(self, runner, temp_project, temp_harness_dir):
        """RED: 测试显示历史记录"""
        import os
        from harness.history import HistoryManager

        history = HistoryManager(temp_harness_dir)
        task = Task(
            id=1,
            title="测试任务",
            priority=Priority.REQUIRED
        )
        history.log_task_created(task)

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'last'])
            assert result.exit_code == 0
            assert '最近事件' in result.output
        finally:
            os.chdir(old_cwd)


class TestReviewIntegration:
    """测试 Review 功能集成"""

    def test_review_workflow(self, runner, temp_project, temp_harness_dir):
        """RED: 测试完整的审查工作流"""
        import os

        # 1. 审查代码
        test_file = str(temp_project / "test_code.py")
        result = runner.invoke(main, ['review', 'code', test_file])
        assert result.exit_code == 0

        # 2. 创建计划
        store = TaskStore(temp_harness_dir)
        tasks = [
            Task(
                id=1,
                title="修复问题",
                priority=Priority.REQUIRED,
                acceptance_criteria=["通过审查"]
            )
        ]
        store.save_tasks(tasks)

        # 3. 审查计划
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(main, ['review', 'plan'])
            assert result.exit_code == 0
            assert '计划审查' in result.output
        finally:
            os.chdir(old_cwd)

    def test_review_detects_critical_issues(self, runner, temp_project):
        """RED: 测试检测严重问题"""
        bad_file = str(temp_project / "bad_code.py")
        result = runner.invoke(main, ['review', 'code', bad_file])
        assert result.exit_code == 0
        # 应该检测到 SQL 注入或硬编码密钥
        assert 'CRITICAL' in result.output or '严重' in result.output or '需要修改' in result.output
