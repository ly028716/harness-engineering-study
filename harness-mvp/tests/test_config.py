"""测试配置系统"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from harness.config import (
    Settings,
    ConfigManager,
    ExecutionModePreference,
    DEFAULT_SETTINGS,
    load_config,
)


class TestSettings:
    """测试 Settings 数据类"""

    def test_settings_defaults(self):
        """RED: 测试默认设置"""
        settings = Settings()
        assert settings.ai_model == "claude-sonnet-4-20250514"
        assert settings.execution_mode == ExecutionModePreference.AUTO
        assert settings.max_workers == 4
        assert settings.api_key == ""

    def test_settings_custom_values(self):
        """RED: 测试自定义设置"""
        settings = Settings(
            ai_model="claude-opus-4-20250514",
            execution_mode=ExecutionModePreference.SOLO,
            max_workers=2,
            api_key="sk-test-123",
        )
        assert settings.ai_model == "claude-opus-4-20250514"
        assert settings.execution_mode == ExecutionModePreference.SOLO
        assert settings.max_workers == 2
        assert settings.api_key == "sk-test-123"

    def test_settings_to_dict(self):
        """RED: 测试序列化为字典"""
        settings = Settings(ai_model="test-model", max_workers=8)
        d = settings.to_dict()
        assert d["ai_model"] == "test-model"
        assert d["max_workers"] == 8
        assert d["execution_mode"] == "AUTO"

    def test_settings_from_dict(self):
        """RED: 测试从字典创建设置"""
        d = {
            "ai_model": "claude-haiku-4-20250514",
            "execution_mode": "PARALLEL",
            "max_workers": 6,
            "api_key": "",
        }
        settings = Settings.from_dict(d)
        assert settings.ai_model == "claude-haiku-4-20250514"
        assert settings.execution_mode == ExecutionModePreference.PARALLEL
        assert settings.max_workers == 6

    def test_settings_from_dict_partial(self):
        """RED: 测试从部分字典创建（缺失字段使用默认值）"""
        d = {"ai_model": "custom-model"}
        settings = Settings.from_dict(d)
        assert settings.ai_model == "custom-model"
        assert settings.max_workers == DEFAULT_SETTINGS.max_workers

    def test_settings_validate_max_workers(self):
        """RED: 测试 max_workers 验证（至少为 1）"""
        settings = Settings(max_workers=0)
        assert settings.max_workers >= 1

    def test_settings_merge(self):
        """RED: 测试合并两个设置"""
        base = Settings(ai_model="model-a", max_workers=2)
        override = Settings(ai_model="model-b", api_key="sk-key")
        merged = base.merge(override)
        assert merged.ai_model == "model-b"
        assert merged.max_workers == 2
        assert merged.api_key == "sk-key"


class TestConfigManager:
    """测试 ConfigManager"""

    def test_config_manager_init(self):
        """RED: 测试 ConfigManager 初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            assert manager.config_file == harness_dir / "config.json"

    def test_config_manager_creates_default_config(self):
        """RED: 测试首次初始化时创建默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            assert manager.config_file.exists()
            settings = manager.load()
            assert settings.ai_model == DEFAULT_SETTINGS.ai_model

    def test_config_manager_save_and_load(self):
        """RED: 测试保存和加载配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)

            settings = Settings(ai_model="custom-model", max_workers=8)
            manager.save(settings)

            loaded = manager.load()
            assert loaded.ai_model == "custom-model"
            assert loaded.max_workers == 8

    def test_config_manager_load_nonexistent_returns_defaults(self):
        """RED: 测试加载不存在的配置文件返回默认值"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            # 删除自动创建的配置文件
            manager.config_file.unlink()
            settings = manager.load()
            assert settings == DEFAULT_SETTINGS

    def test_config_manager_load_invalid_json_returns_defaults(self):
        """RED: 测试加载损坏的配置文件返回默认值"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            manager.config_file.write_text("{invalid json", encoding="utf-8")
            settings = manager.load()
            assert settings == DEFAULT_SETTINGS

    def test_config_manager_update(self):
        """RED: 测试更新部分配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)

            manager.update(ai_model="new-model", max_workers=10)
            loaded = manager.load()
            assert loaded.ai_model == "new-model"
            assert loaded.max_workers == 10

    def test_env_var_overrides_api_key(self):
        """RED: 测试环境变量覆盖 API key"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key-456"}, clear=True):
                manager = ConfigManager(harness_dir)
                settings = manager.load_with_env_overrides()
                assert settings.api_key == "env-key-456"

    def test_env_var_overrides_model(self):
        """RED: 测试环境变量覆盖 AI 模型"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            with patch.dict(os.environ, {"HARNESS_AI_MODEL": "env-model"}, clear=True):
                manager = ConfigManager(harness_dir)
                settings = manager.load_with_env_overrides()
                assert settings.ai_model == "env-model"

    def test_env_var_no_override_when_not_set(self):
        """RED: 测试未设置环境变量时不覆盖"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            manager.save(Settings(ai_model="file-model"))
            with patch.dict(os.environ, {}, clear=True):
                settings = manager.load_with_env_overrides()
                assert settings.ai_model == "file-model"

    def test_config_manager_reset(self):
        """RED: 测试重置为默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            manager = ConfigManager(harness_dir)
            manager.save(Settings(ai_model="custom", max_workers=99))
            manager.reset()
            loaded = manager.load()
            assert loaded == DEFAULT_SETTINGS


class TestLoadConfigFunction:
    """测试顶层 load_config 函数"""

    def test_load_config_returns_settings(self):
        """RED: 测试 load_config 返回 Settings"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            settings = load_config(harness_dir)
            assert isinstance(settings, Settings)

    def test_load_config_with_env_overrides(self):
        """RED: 测试 load_config 使用环境变量覆盖"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            with patch.dict(os.environ, {"HARNESS_AI_MODEL": "env-override"}):
                settings = load_config(harness_dir)
                assert settings.ai_model == "env-override"


class TestConfigManagerFindConfig:
    """测试查找配置文件"""

    def test_find_config_in_current_directory(self):
        """RED: 测试在当前目录查找 .harness/config.json"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                harness_dir = Path(tmpdir) / ".harness"
                harness_dir.mkdir()
                config_file = harness_dir / "config.json"
                config_file.write_text(
                    json.dumps({"ai_model": "found-model"}, ensure_ascii=False),
                    encoding="utf-8",
                )

                manager = ConfigManager.find()
                assert manager is not None
                settings = manager.load()
                assert settings.ai_model == "found-model"
            finally:
                os.chdir(orig_cwd)

    def test_find_config_no_directory(self):
        """RED: 测试没有 .harness 目录时返回 None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                manager = ConfigManager.find()
                assert manager is None
            finally:
                os.chdir(orig_cwd)
