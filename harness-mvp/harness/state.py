"""状态管理器"""
import json
from pathlib import Path
from typing import Dict, Any


class StateManager:
    """管理 Harness 状态的持久化"""

    def __init__(self, state_dir: Path):
        """初始化状态管理器

        Args:
            state_dir: 状态目录路径（通常是 .harness）
        """
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "state.json"
        self._ensure_state_dir()
        self._ensure_state_file()

    def _ensure_state_dir(self):
        """确保状态目录存在"""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_state_file(self):
        """确保状态文件存在"""
        if not self.state_file.exists():
            self._write_state(self._default_state())

    def _default_state(self) -> Dict[str, Any]:
        """返回默认状态"""
        return {
            "tasks": [],
            "metadata": {}
        }

    def _write_state(self, state: Dict[str, Any]):
        """写入状态到文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load(self) -> Dict[str, Any]:
        """加载状态

        Returns:
            状态字典
        """
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, state: Dict[str, Any]):
        """保存状态

        Args:
            state: 要保存的状态字典
        """
        self._write_state(state)

    def update(self, partial_state: Dict[str, Any]):
        """更新部分状态

        Args:
            partial_state: 要更新的部分状态
        """
        current_state = self.load()
        current_state.update(partial_state)
        self.save(current_state)
