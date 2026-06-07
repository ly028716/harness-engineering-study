"""测试多 AI 模型配置"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from harness.config import (
    ModelName,
    Settings,
    DEFAULT_SETTINGS,
    get_model_for_role,
)


class TestModelName:
    """测试 ModelName 枚举"""

    def test_from_string_valid(self):
        """从字符串创建有效模型"""
        model = ModelName.from_string("claude-sonnet-4-20250514")
        assert model == ModelName.CLAUDE_SONNET_4_20250514

    def test_from_string_invalid_raises(self):
        """从字符串创建无效模型抛出 ValueError"""
        with pytest.raises(ValueError, match="未知模型"):
            ModelName.from_string("unknown-model")

    def test_list_all(self):
        """list_all 返回所有模型"""
        models = ModelName.list_all()
        assert len(models) == 3
        assert ModelName.CLAUDE_SONNET_4_20250514 in models
        assert ModelName.CLAUDE_OPUS_4_20250514 in models
        assert ModelName.CLAUDE_HAIKU_4_20250514 in models

    def test_display_name(self):
        """display_name 返回人类可读名称"""
        model = ModelName.CLAUDE_SONNET_4_20250514
        assert "Sonnet" in model.display_name

    def test_cost_per_1k_input(self):
        """cost_per_1k_input 返回输入成本"""
        assert ModelName.CLAUDE_HAIKU_4_20250514.cost_per_1k_input < \
               ModelName.CLAUDE_OPUS_4_20250514.cost_per_1k_input

    def test_cost_per_1k_output(self):
        """cost_per_1k_output 返回输出成本"""
        assert ModelName.CLAUDE_HAIKU_4_20250514.cost_per_1k_output < \
               ModelName.CLAUDE_SONNET_4_20250514.cost_per_1k_output

    def test_is_powerful(self):
        """is_powerful 仅对 Opus 返回 True"""
        assert ModelName.CLAUDE_OPUS_4_20250514.is_powerful is True
        assert ModelName.CLAUDE_SONNET_4_20250514.is_powerful is False
        assert ModelName.CLAUDE_HAIKU_4_20250514.is_powerful is False


class TestSettingsRoleModels:
    """测试 Settings 按角色模型字段"""

    def test_default_role_fields_are_none(self):
        """角色模型字段默认为 None"""
        settings = Settings()
        assert settings.worker_model is None
        assert settings.reviewer_model is None
        assert settings.planner_model is None

    def test_custom_role_fields(self):
        """设置角色模型"""
        settings = Settings(
            worker_model="claude-haiku-4-20250514",
            reviewer_model="claude-sonnet-4-20250514",
            planner_model="claude-opus-4-20250514",
        )
        assert settings.worker_model == "claude-haiku-4-20250514"
        assert settings.reviewer_model == "claude-sonnet-4-20250514"
        assert settings.planner_model == "claude-opus-4-20250514"

    def test_to_dict_skips_none_role_fields(self):
        """to_dict 跳过 None 的角色模型字段"""
        settings = Settings(worker_model="claude-haiku-4-20250514")
        d = settings.to_dict()
        assert "worker_model" in d
        assert "reviewer_model" not in d
        assert "planner_model" not in d

    def test_from_dict_with_role_fields(self):
        """from_dict 加载角色模型字段"""
        d = {
            "worker_model": "claude-haiku-4-20250514",
            "reviewer_model": "claude-sonnet-4-20250514",
        }
        settings = Settings.from_dict(d)
        assert settings.worker_model == "claude-haiku-4-20250514"
        assert settings.reviewer_model == "claude-sonnet-4-20250514"
        assert settings.planner_model is None

    def test_from_dict_without_role_fields_backward_compat(self):
        """from_dict 向后兼容（缺失角色字段返回 None）"""
        d = {"ai_model": "claude-sonnet-4-20250514"}
        settings = Settings.from_dict(d)
        assert settings.worker_model is None
        assert settings.reviewer_model is None
        assert settings.planner_model is None

    def test_post_init_invalid_role_model_resets_to_none(self):
        """__post_init__ 将无效角色模型置 None"""
        settings = Settings(worker_model="invalid-model")
        assert settings.worker_model is None

    def test_merge_keeps_defaults(self):
        """merge 不覆盖默认值"""
        base = Settings()
        override = Settings(worker_model="claude-haiku-4-20250514")
        merged = base.merge(override)
        assert merged.worker_model == "claude-haiku-4-20250514"
        assert merged.reviewer_model is None

    def test_merge_overrides_role_model(self):
        """merge 覆盖角色模型"""
        base = Settings(worker_model="claude-haiku-4-20250514")
        override = Settings(worker_model="claude-sonnet-4-20250514")
        merged = base.merge(override)
        assert merged.worker_model == "claude-sonnet-4-20250514"


class TestGetModelForRole:
    """测试 get_model_for_role 函数"""

    def test_returns_global_model_when_no_role_model(self):
        """角色模型未设置时返回全局模型"""
        settings = Settings(ai_model="claude-sonnet-4-20250514")
        model = get_model_for_role(settings, "worker")
        assert model == "claude-sonnet-4-20250514"

    def test_returns_role_specific_model(self):
        """返回按角色设置的模型"""
        settings = Settings(
            ai_model="claude-sonnet-4-20250514",
            worker_model="claude-haiku-4-20250514",
        )
        model = get_model_for_role(settings, "worker")
        assert model == "claude-haiku-4-20250514"

    def test_reviewer_role(self):
        """reviewer 角色返回正确模型"""
        settings = Settings(
            reviewer_model="claude-opus-4-20250514",
        )
        model = get_model_for_role(settings, "reviewer")
        assert model == "claude-opus-4-20250514"

    def test_planner_role(self):
        """planner 角色返回正确模型"""
        settings = Settings(
            planner_model="claude-opus-4-20250514",
        )
        model = get_model_for_role(settings, "planner")
        assert model == "claude-opus-4-20250514"

    def test_invalid_role_uses_global(self):
        """未知角色使用全局模型"""
        settings = Settings(ai_model="claude-sonnet-4-20250514")
        model = get_model_for_role(settings, "unknown_role")
        assert model == "claude-sonnet-4-20250514"


class TestEnvVarRoleOverrides:
    """测试环境变量覆盖按角色模型"""

    def test_worker_model_env_var(self):
        """HARNESS_WORKER_MODEL 环境变量生效"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            from harness.config import ConfigManager
            manager = ConfigManager(harness_dir)
            with patch.dict(os.environ, {"HARNESS_WORKER_MODEL": "claude-haiku-4-20250514"}, clear=True):
                settings = manager.load_with_env_overrides()
                assert settings.worker_model == "claude-haiku-4-20250514"

    def test_reviewer_model_env_var(self):
        """HARNESS_REVIEWER_MODEL 环境变量生效"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            from harness.config import ConfigManager
            manager = ConfigManager(harness_dir)
            with patch.dict(os.environ, {"HARNESS_REVIEWER_MODEL": "claude-opus-4-20250514"}, clear=True):
                settings = manager.load_with_env_overrides()
                assert settings.reviewer_model == "claude-opus-4-20250514"

    def test_planner_model_env_var(self):
        """HARNESS_PLANNER_MODEL 环境变量生效"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            from harness.config import ConfigManager
            manager = ConfigManager(harness_dir)
            with patch.dict(os.environ, {"HARNESS_PLANNER_MODEL": "claude-opus-4-20250514"}, clear=True):
                settings = manager.load_with_env_overrides()
                assert settings.planner_model == "claude-opus-4-20250514"

    def test_role_env_vars_not_set(self):
        """角色环境变量未设置时不覆盖"""
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            from harness.config import ConfigManager
            manager = ConfigManager(harness_dir)
            with patch.dict(os.environ, {}, clear=True):
                settings = manager.load_with_env_overrides()
                assert settings.worker_model is None
                assert settings.reviewer_model is None
                assert settings.planner_model is None
