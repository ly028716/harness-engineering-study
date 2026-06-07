"""测试 CLI 配置命令"""
import json
import os
import tempfile
from pathlib import Path

from click.testing import CliRunner
from harness.cli import main


class TestConfigCommands:
    """测试 config 命令组"""

    def test_config_command_exists(self):
        """RED: 测试 config 命令组存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', '--help'])
        assert result.exit_code == 0
        assert 'config' in result.output.lower()

    def test_config_show_command_exists(self):
        """RED: 测试 config show 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'show', '--help'])
        assert result.exit_code == 0

    def test_config_set_command_exists(self):
        """RED: 测试 config set 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'set', '--help'])
        assert result.exit_code == 0

    def test_config_init_command_exists(self):
        """RED: 测试 config init 子命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'init', '--help'])
        assert result.exit_code == 0

    def test_config_show_no_harness_dir(self):
        """RED: 测试 .harness 目录不存在时显示错误"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'show'])
                assert result.exit_code == 0
                assert '未找到' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_show_displays_settings(self):
        """RED: 测试 config show 显示配置"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            config_file = harness_dir / "config.json"
            config_file.write_text(json.dumps({
                "ai_model": "claude-haiku-4-20250514",
                "execution_mode": "PARALLEL",
                "max_workers": 8,
            }), encoding='utf-8')

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'show'])
                assert result.exit_code == 0
                assert 'claude-haiku-4-20250514' in result.output
                assert 'PARALLEL' in result.output
                assert '8' in result.output
                assert '未设置' in result.output  # api_key not set
            finally:
                os.chdir(old_cwd)

    def test_config_set_updates_value(self):
        """RED: 测试 config set 更新配置"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            config_file = harness_dir / "config.json"
            config_file.write_text(json.dumps({
                "ai_model": "old-model",
                "execution_mode": "AUTO",
                "max_workers": 4,
            }), encoding='utf-8')

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'set', 'ai_model', 'new-model'])
                assert result.exit_code == 0
                data = json.loads(config_file.read_text(encoding='utf-8'))
                assert data['ai_model'] == 'new-model'
            finally:
                os.chdir(old_cwd)

    def test_config_set_no_harness_dir(self):
        """RED: 测试 .harness 目录不存在时 config set 显示错误"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'set', 'ai_model', 'test'])
                assert result.exit_code == 0
                assert '未找到' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_init_creates_default_config(self):
        """RED: 测试 config init 创建默认配置"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'init'])
                assert result.exit_code == 0

                config_file = Path(tmpdir) / ".harness" / "config.json"
                assert config_file.exists()
            finally:
                os.chdir(old_cwd)

    def test_config_init_overwrites_existing(self):
        """RED: 测试 config init 覆盖已有配置"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            config_file = harness_dir / "config.json"
            config_file.write_text(json.dumps({
                "ai_model": "custom",
                "max_workers": 99,
            }), encoding='utf-8')

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'init'])
                assert result.exit_code == 0

                data = json.loads(config_file.read_text(encoding='utf-8'))
                assert data['ai_model'] != 'custom'  # 已被重置
            finally:
                os.chdir(old_cwd)

    def test_config_model_list_command_exists(self):
        """RED: 测试 config model list 命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'model', 'list', '--help'])
        assert result.exit_code == 0

    def test_config_model_show_command_exists(self):
        """RED: 测试 config model show 命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'model', 'show', '--help'])
        assert result.exit_code == 0

    def test_config_model_set_command_exists(self):
        """RED: 测试 config model set 命令存在"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'model', 'set', '--help'])
        assert result.exit_code == 0

    def test_config_model_list_shows_models(self):
        """RED: 测试 config model list 显示模型列表"""
        runner = CliRunner()
        result = runner.invoke(main, ['config', 'model', 'list'])
        assert result.exit_code == 0
        assert 'claude-sonnet-4-20250514' in result.output
        assert 'claude-opus-4-20250514' in result.output
        assert 'claude-haiku-4-20250514' in result.output
        assert '$' in result.output  # 成本信息

    def test_config_model_show_no_harness_dir(self):
        """RED: 测试 .harness 不存在时 model show 显示错误"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'model', 'show'])
                assert result.exit_code == 0
                assert '未找到' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_model_show_displays_config(self):
        """RED: 测试 config model show 显示角色模型配置"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            config_file = harness_dir / "config.json"
            config_file.write_text(json.dumps({
                "ai_model": "claude-sonnet-4-20250514",
                "worker_model": "claude-haiku-4-20250514",
            }), encoding='utf-8')

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'model', 'show'])
                assert result.exit_code == 0
                assert 'Worker' in result.output
                assert 'claude-haiku-4-20250514' in result.output
                assert 'claude-sonnet-4-20250514' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_model_set_valid_model(self):
        """RED: 测试 config model set 设置有效模型"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            config_file = harness_dir / "config.json"
            config_file.write_text(json.dumps({
                "ai_model": "claude-sonnet-4-20250514",
            }), encoding='utf-8')

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, [
                    'config', 'model', 'set',
                    'worker', 'claude-haiku-4-20250514',
                ])
                assert result.exit_code == 0
                data = json.loads(config_file.read_text(encoding='utf-8'))
                assert data['worker_model'] == 'claude-haiku-4-20250514'
            finally:
                os.chdir(old_cwd)

    def test_config_model_set_invalid_model(self):
        """RED: 测试 config model set 无效模型显示错误"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, [
                    'config', 'model', 'set',
                    'worker', 'unknown-model',
                ])
                assert result.exit_code == 0
                assert '未知模型' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_model_set_no_harness_dir(self):
        """RED: 测试 .harness 不存在时 model set 显示错误"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, [
                    'config', 'model', 'set',
                    'worker', 'claude-haiku-4-20250514',
                ])
                assert result.exit_code == 0
                assert '未找到' in result.output
            finally:
                os.chdir(old_cwd)

    def test_config_model_set_invalid_role(self):
        """RED: 测试 config model set 无效角色显示错误"""
        runner = CliRunner()
        result = runner.invoke(main, [
            'config', 'model', 'set',
            'invalid', 'claude-haiku-4-20250514',
        ])
        assert result.exit_code != 0
        assert 'invalid' in result.output or 'Error' in result.output or 'Usage' in result.output

    def test_config_model_show_displays_default_indicator(self):
        """RED: 测试使用默认模型的角色显示 (使用默认)"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = runner.invoke(main, ['config', 'model', 'show'])
                assert result.exit_code == 0
                assert '使用默认' in result.output
            finally:
                os.chdir(old_cwd)


    def test_config_show_displays_api_key_status(self):
        """RED: 测试 config show 显示 API 密钥状态"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()

            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                from unittest.mock import patch
                with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-real-key"}):
                    result = runner.invoke(main, ['config', 'show'])
                    assert result.exit_code == 0
                    assert '已设置' in result.output
            finally:
                os.chdir(old_cwd)
