"""Todo 单元测试"""
import pytest
from pathlib import Path
from todo import Todo
from api import TodoStore


@pytest.fixture
def temp_store(tmp_path):
    """创建临时存储"""
    return TodoStore(tmp_path / "todos.json")


class TestTodo:
    """测试 Todo 类"""

    def test_create_todo(self):
        """测试创建 Todo"""
        todo = Todo(id=1, title="学习 Python")
        assert todo.id == 1
        assert todo.title == "学习 Python"
        assert todo.completed is False

    def test_complete_todo(self):
        """测试完成 Todo"""
        todo = Todo(id=1, title="学习 Python")
        todo.complete()
        assert todo.completed is True

    def test_to_dict(self):
        """测试序列化"""
        todo = Todo(id=1, title="学习 Python")
        data = todo.to_dict()
        assert data["id"] == 1
        assert data["title"] == "学习 Python"
        assert data["completed"] is False

    def test_from_dict(self):
        """测试反序列化"""
        data = {
            "id": 1,
            "title": "学习 Python",
            "completed": False,
            "created_at": "2026-04-11T10:00:00"
        }
        todo = Todo.from_dict(data)
        assert todo.id == 1
        assert todo.title == "学习 Python"
        assert todo.completed is False


class TestTodoStore:
    """测试 TodoStore 类"""

    def test_add_todo(self, temp_store):
        """测试添加 Todo"""
        todo = Todo(id=1, title="学习 Python")
        temp_store.add(todo)

        todos = temp_store.load()
        assert len(todos) == 1
        assert todos[0].title == "学习 Python"

    def test_get_todo(self, temp_store):
        """测试获取 Todo"""
        todo = Todo(id=1, title="学习 Python")
        temp_store.add(todo)

        found = temp_store.get(1)
        assert found is not None
        assert found.title == "学习 Python"

    def test_update_todo(self, temp_store):
        """测试更新 Todo"""
        todo = Todo(id=1, title="学习 Python")
        temp_store.add(todo)

        todo.complete()
        temp_store.update(todo)

        found = temp_store.get(1)
        assert found.completed is True

    def test_delete_todo(self, temp_store):
        """测试删除 Todo"""
        todo = Todo(id=1, title="学习 Python")
        temp_store.add(todo)

        temp_store.delete(1)

        found = temp_store.get(1)
        assert found is None

    def test_get_next_id(self, temp_store):
        """测试获取下一个 ID"""
        assert temp_store.get_next_id() == 1

        todo = Todo(id=1, title="学习 Python")
        temp_store.add(todo)

        assert temp_store.get_next_id() == 2
