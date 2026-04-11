"""测试状态管理器"""
import json
import pytest
from pathlib import Path
from harness.state import StateManager


class TestStateManager:
    """测试状态管理器"""

    def test_init_creates_state_directory(self, tmp_path):
        """RED: 测试初始化时创建 .harness 目录"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        assert state_dir.exists()
        assert state_dir.is_dir()

    def test_init_creates_state_file(self, tmp_path):
        """RED: 测试初始化时创建 state.json 文件"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        state_file = state_dir / "state.json"
        assert state_file.exists()

    def test_load_empty_state(self, tmp_path):
        """RED: 测试加载空状态返回默认值"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        state = manager.load()
        assert isinstance(state, dict)
        assert "tasks" in state
        assert "metadata" in state

    def test_save_and_load_state(self, tmp_path):
        """RED: 测试保存和加载状态"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        test_state = {
            "tasks": [{"id": 1, "title": "Test Task"}],
            "metadata": {"version": "0.1.0"}
        }

        manager.save(test_state)
        loaded_state = manager.load()

        assert loaded_state == test_state

    def test_update_state(self, tmp_path):
        """RED: 测试更新状态"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        initial_state = {"tasks": [], "metadata": {}}
        manager.save(initial_state)

        manager.update({"tasks": [{"id": 1}]})
        loaded_state = manager.load()

        assert len(loaded_state["tasks"]) == 1
        assert loaded_state["tasks"][0]["id"] == 1

    def test_state_file_format(self, tmp_path):
        """RED: 测试状态文件格式正确"""
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)

        test_state = {"tasks": [], "metadata": {"version": "0.1.0"}}
        manager.save(test_state)

        state_file = state_dir / "state.json"
        with open(state_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        assert content == test_state
