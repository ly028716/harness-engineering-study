"""Todo 存储管理"""
import json
from pathlib import Path
from typing import List, Optional
from todo import Todo


class TodoStore:
    """Todo 存储管理器"""

    def __init__(self, data_file: Path):
        """初始化存储

        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, todos: List[Todo]):
        """保存所有 Todo

        Args:
            todos: Todo 列表
        """
        data = [todo.to_dict() for todo in todos]
        self.data_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def load(self) -> List[Todo]:
        """加载所有 Todo

        Returns:
            Todo 列表
        """
        if not self.data_file.exists():
            return []

        data = json.loads(self.data_file.read_text())
        return [Todo.from_dict(item) for item in data]

    def add(self, todo: Todo):
        """添加 Todo

        Args:
            todo: Todo 对象
        """
        todos = self.load()
        todos.append(todo)
        self.save(todos)

    def get(self, todo_id: int) -> Optional[Todo]:
        """获取指定 Todo

        Args:
            todo_id: Todo ID

        Returns:
            Todo 对象或 None
        """
        todos = self.load()
        for todo in todos:
            if todo.id == todo_id:
                return todo
        return None

    def update(self, todo: Todo):
        """更新 Todo

        Args:
            todo: Todo 对象
        """
        todos = self.load()
        for i, t in enumerate(todos):
            if t.id == todo.id:
                todos[i] = todo
                break
        self.save(todos)

    def delete(self, todo_id: int):
        """删除 Todo

        Args:
            todo_id: Todo ID
        """
        todos = self.load()
        todos = [t for t in todos if t.id != todo_id]
        self.save(todos)

    def get_next_id(self) -> int:
        """获取下一个 ID

        Returns:
            下一个可用的 ID
        """
        todos = self.load()
        if not todos:
            return 1
        return max(t.id for t in todos) + 1
