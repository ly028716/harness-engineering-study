"""集成测试"""
import pytest
from pathlib import Path
from harness.state import StateManager
from harness.parser import MarkdownParser


class TestIntegration:
    """测试组件集成"""

    def test_parse_and_save_workflow(self, tmp_path):
        """测试解析 Plans.md 并保存到状态的完整流程"""
        # 创建测试 Plans.md
        plans_content = """# Plans

## Tasks

- [ ] Task 1: Setup project
  Initialize the project structure.
  - ✅ Directory created
  - ✅ Config files added

- [~] Task 2: Implement core
  Working on core functionality.

- [x] Task 3: Write tests
  Tests completed.
"""
        plans_file = tmp_path / "Plans.md"
        plans_file.write_text(plans_content, encoding='utf-8')

        # 解析任务
        parser = MarkdownParser(plans_file)
        tasks = parser.parse()

        # 保存到状态
        state_dir = tmp_path / ".harness"
        manager = StateManager(state_dir)
        manager.update({"tasks": tasks})

        # 验证状态
        loaded_state = manager.load()
        assert len(loaded_state["tasks"]) == 3
        assert loaded_state["tasks"][0]["status"] == "TODO"
        assert loaded_state["tasks"][1]["status"] == "WIP"
        assert loaded_state["tasks"][2]["status"] == "DONE"
        assert len(loaded_state["tasks"][0]["acceptance_criteria"]) == 2

    def test_state_persistence_across_sessions(self, tmp_path):
        """测试状态在多个会话间持久化"""
        state_dir = tmp_path / ".harness"

        # 第一个会话：保存状态
        manager1 = StateManager(state_dir)
        test_tasks = [
            {"id": 1, "title": "Task 1", "status": "TODO"},
            {"id": 2, "title": "Task 2", "status": "WIP"}
        ]
        manager1.update({"tasks": test_tasks})

        # 第二个会话：加载状态
        manager2 = StateManager(state_dir)
        loaded_state = manager2.load()

        assert len(loaded_state["tasks"]) == 2
        assert loaded_state["tasks"][0]["id"] == 1
        assert loaded_state["tasks"][1]["status"] == "WIP"
