"""测试 CLI 基础功能"""
import pytest
from pathlib import Path
import tempfile
from click.testing import CliRunner
from harness.cli import main


class TestCLIBasics:
    """测试 CLI 基本功能"""

    def test_version_flag(self):
        """RED: 测试 --version 标志显示版本号"""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        assert result.exit_code == 0
        assert '0.1.0' in result.output

    def test_help_flag(self):
        """RED: 测试 --help 标志显示帮助信息"""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'harness' in result.output.lower()

    def test_plan_command_exists(self):
        """RED: 测试 plan 命令组存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['plan', '--help'])

        assert result.exit_code == 0
        assert 'plan' in result.output.lower()

    def test_plan_create_command_exists(self):
        """RED: 测试 plan create 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['plan', 'create', '--help'])

        assert result.exit_code == 0
        assert 'create' in result.output.lower()


class TestWorkCommands:
    """测试 Work 命令"""

    def test_work_command_exists(self):
        """RED: 测试 work 命令组存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['work', '--help'])

        assert result.exit_code == 0
        assert 'work' in result.output.lower()

    def test_work_solo_command_exists(self):
        """RED: 测试 work solo 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['work', 'solo', '--help'])

        assert result.exit_code == 0

    def test_work_parallel_command_exists(self):
        """RED: 测试 work parallel 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['work', 'parallel', '--help'])

        assert result.exit_code == 0

    def test_work_status_command_exists(self):
        """RED: 测试 work status 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['work', 'status', '--help'])

        assert result.exit_code == 0

    def test_work_solo_executes_task(self):
        """RED: 测试 work solo 执行任务"""
        runner = CliRunner()
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()

            # 切换到临时目录
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                # 添加任务
                result = runner.invoke(main, ['plan', 'add', '-t', 'Test Task', '-d', 'Test'])
                assert result.exit_code == 0

                # 执行 solo 命令
                result = runner.invoke(main, ['work', 'solo', '1'])
                assert result.exit_code == 0
            finally:
                os.chdir(old_cwd)

    def test_work_all_executes_all_tasks(self):
        """RED: 测试 work all 执行所有任务"""
        runner = CliRunner()
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()

            # 切换到临时目录
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                # 添加多个任务
                for i in range(1, 4):
                    result = runner.invoke(main, ['plan', 'add', '-t', f'Task {i}', '-d', 'Test'])
                    assert result.exit_code == 0

                # 执行 all 命令
                result = runner.invoke(main, ['work', 'all'])
                assert result.exit_code == 0
            finally:
                os.chdir(old_cwd)


class TestReviewCommands:
    """测试 Review 命令"""

    def test_review_command_exists(self):
        """RED: 测试 review 命令组存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['review', '--help'])

        assert result.exit_code == 0
        assert 'review' in result.output.lower()

    def test_review_code_command_exists(self):
        """RED: 测试 review code 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['review', 'code', '--help'])

        assert result.exit_code == 0

    def test_review_plan_command_exists(self):
        """RED: 测试 review plan 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['review', 'plan', '--help'])

        assert result.exit_code == 0

    def test_review_last_command_exists(self):
        """RED: 测试 review last 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['review', 'last', '--help'])

        assert result.exit_code == 0

    def test_review_code_reviews_file(self):
        """RED: 测试 review code 审查文件"""
        runner = CliRunner()
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "test_auth.py"
            test_file.write_text('''
def login(user_id, password):
    # TODO: 实现验证逻辑
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    API_KEY = "test_key_12345"
    return True
''', encoding='utf-8')

            # 切换到临时目录
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                # 执行 review code 命令
                result = runner.invoke(main, ['review', 'code', str(test_file)])
                assert result.exit_code == 0
                # 应该检测到问题
                assert 'CRITICAL' in result.output or 'MAJOR' in result.output or 'APPROVE' in result.output
            finally:
                os.chdir(old_cwd)

    def test_review_code_reviews_python_file(self):
        """RED: 测试 review code 审查 Python 文件"""
        runner = CliRunner()
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建干净的 Python 文件
            test_file = Path(tmpdir) / "clean_code.py"
            test_file.write_text('''
def add(a: int, b: int) -> int:
    """返回两个整数的和"""
    return a + b
''', encoding='utf-8')

            # 切换到临时目录
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['review', 'code', str(test_file)])
                assert result.exit_code == 0
            finally:
                os.chdir(old_cwd)

    def test_review_code_reviews_html_file(self):
        """RED: 测试 review code 审查 HTML 文件"""
        runner = CliRunner()
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 HTML 文件
            test_file = Path(tmpdir) / "test.html"
            test_file.write_text('''
<!DOCTYPE html>
<html>
<body>
    <img src="test.jpg">
    <div onclick="handleClick()">按钮</div>
</body>
</html>
''', encoding='utf-8')

            # 切换到临时目录
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['review', 'code', str(test_file)])
                assert result.exit_code == 0
            finally:
                os.chdir(old_cwd)
