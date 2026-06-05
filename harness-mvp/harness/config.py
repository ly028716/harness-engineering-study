"""配置系统 - 配置管理和加载"""
import json
import os
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional


class ExecutionModePreference(Enum):
    """执行模式偏好"""
    AUTO = "AUTO"
    SOLO = "SOLO"
    PARALLEL = "PARALLEL"

    @classmethod
    def from_string(cls, value: str) -> "ExecutionModePreference":
        """从字符串创建"""
        return cls[value.upper()]


@dataclass
class Settings:
    """配置设置"""

    ai_model: str = "claude-sonnet-4-20250514"
    execution_mode: ExecutionModePreference = ExecutionModePreference.AUTO
    max_workers: int = 4
    api_key: str = ""

    def __post_init__(self):
        """验证和修正字段"""
        if self.max_workers < 1:
            self.max_workers = 1

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典（排除敏感字段）"""
        return {
            "ai_model": self.ai_model,
            "execution_mode": self.execution_mode.value,
            "max_workers": self.max_workers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """从字典创建设置"""
        kwargs = {}
        if "ai_model" in data:
            kwargs["ai_model"] = data["ai_model"]
        if "execution_mode" in data:
            kwargs["execution_mode"] = ExecutionModePreference.from_string(data["execution_mode"])
        if "max_workers" in data:
            kwargs["max_workers"] = data["max_workers"]
        if "api_key" in data:
            kwargs["api_key"] = data["api_key"]
        return cls(**kwargs)

    def merge(self, other: "Settings") -> "Settings":
        """合并两个设置，other 的非默认值覆盖当前值"""
        merged = deepcopy(self)
        if other.ai_model != DEFAULT_SETTINGS.ai_model:
            merged.ai_model = other.ai_model
        if other.execution_mode != DEFAULT_SETTINGS.execution_mode:
            merged.execution_mode = other.execution_mode
        if other.max_workers != DEFAULT_SETTINGS.max_workers:
            merged.max_workers = other.max_workers
        if other.api_key:
            merged.api_key = other.api_key
        return merged


DEFAULT_SETTINGS = Settings()


class ConfigManager:
    """配置管理器"""

    def __init__(self, harness_dir: Path):
        """初始化配置管理器

        Args:
            harness_dir: .harness 目录路径
        """
        self.config_file = Path(harness_dir) / "config.json"
        self._ensure_default()

    def _ensure_default(self):
        """确保默认配置文件存在"""
        if not self.config_file.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.save(DEFAULT_SETTINGS)

    def load(self) -> Settings:
        """从文件加载配置

        Returns:
            配置设置对象
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Settings.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return deepcopy(DEFAULT_SETTINGS)

    def save(self, settings: Settings):
        """保存配置到文件

        Args:
            settings: 配置设置对象
        """
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)

    def update(self, **kwargs) -> Settings:
        """更新部分配置

        Args:
            **kwargs: 要更新的配置字段

        Returns:
            更新后的配置设置对象
        """
        settings = self.load()
        for key, value in kwargs.items():
            if hasattr(settings, key):
                if key == "execution_mode" and isinstance(value, str):
                    value = ExecutionModePreference.from_string(value)
                setattr(settings, key, value)
        self.save(settings)
        return settings

    def reset(self):
        """重置为默认配置"""
        self.save(DEFAULT_SETTINGS)

    def load_with_env_overrides(self) -> Settings:
        """加载配置并应用环境变量覆盖

        环境变量:
        - ANTHROPIC_API_KEY: API 密钥
        - HARNESS_AI_MODEL: AI 模型名称

        Returns:
            覆盖后的配置设置对象
        """
        settings = self.load()

        env_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if env_api_key:
            settings.api_key = env_api_key

        env_model = os.environ.get("HARNESS_AI_MODEL")
        if env_model:
            settings.ai_model = env_model

        return settings

    @classmethod
    def find(cls) -> Optional["ConfigManager"]:
        """在当前目录查找 .harness 配置

        Returns:
            ConfigManager 实例，未找到时返回 None
        """
        harness_dir = Path.cwd() / ".harness"
        if harness_dir.exists():
            return cls(harness_dir)
        return None


def load_config(harness_dir: Path) -> Settings:
    """加载配置（便捷函数）

    从配置文件加载并应用环境变量覆盖。

    Args:
        harness_dir: .harness 目录路径

    Returns:
        配置设置对象
    """
    manager = ConfigManager(harness_dir)
    return manager.load_with_env_overrides()
