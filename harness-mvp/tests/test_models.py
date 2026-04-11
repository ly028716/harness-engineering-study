"""测试数据模型 - Phase 2"""
import pytest
from datetime import datetime
from harness.models import Task, TaskStatus, Priority


class TestTaskStatus:
    """测试 TaskStatus 枚举"""

    def test_task_status_values(self):
        """RED: 测试 TaskStatus 包含所有必需的状态值"""
        assert TaskStatus.TODO.value == "TODO"
        assert TaskStatus.WIP.value == "WIP"
        assert TaskStatus.DONE.value == "DONE"
        assert TaskStatus.BLOCKED.value == "BLOCKED"

    def test_task_status_from_string(self):
        """RED: 测试从字符串创建 TaskStatus"""
        assert TaskStatus.from_string("TODO") == TaskStatus.TODO
        assert TaskStatus.from_string("WIP") == TaskStatus.WIP
        assert TaskStatus.from_string("DONE") == TaskStatus.DONE
        assert TaskStatus.from_string("BLOCKED") == TaskStatus.BLOCKED
        assert TaskStatus.from_string("todo") == TaskStatus.TODO  # 大小写不敏感


class TestPriority:
    """测试 Priority 枚举"""

    def test_priority_values(self):
        """RED: 测试 Priority 包含所有必需的优先级值"""
        assert Priority.REQUIRED.value == "REQUIRED"
        assert Priority.RECOMMENDED.value == "RECOMMENDED"
        assert Priority.OPTIONAL.value == "OPTIONAL"

    def test_priority_from_string(self):
        """RED: 测试从字符串创建 Priority"""
        assert Priority.from_string("REQUIRED") == Priority.REQUIRED
        assert Priority.from_string("RECOMMENDED") == Priority.RECOMMENDED
        assert Priority.from_string("OPTIONAL") == Priority.OPTIONAL
        assert Priority.from_string("required") == Priority.REQUIRED  # 大小写不敏感


class TestTask:
    """测试 Task 数据类"""

    def test_create_minimal_task(self):
        """RED: 测试创建最小任务"""
        task = Task(
            id=1,
            title="实现登录功能",
            description="实现登录接口"
        )
        assert task.id == 1
        assert task.title == "实现登录功能"
        assert task.description == "实现登录接口"
        assert task.status == TaskStatus.TODO
        assert task.priority == Priority.REQUIRED
        assert task.acceptance_criteria == []
        assert task.dependencies == []
        assert task.estimated_effort == 1
        assert task.actual_effort is None
        assert task.created_at is not None
        assert task.updated_at is not None
        assert task.completed_at is None

    def test_create_full_task(self):
        """RED: 测试创建完整任务"""
        now = datetime.now()
        task = Task(
            id=1,
            title="实现注册接口",
            description="实现用户注册 API",
            status=TaskStatus.WIP,
            priority=Priority.REQUIRED,
            acceptance_criteria=[
                "POST /api/auth/register 返回 201",
                "密码使用 bcrypt 加密",
                "邮箱唯一性验证"
            ],
            dependencies=[1, 2],
            estimated_effort=3,
            actual_effort=4,
            created_at=now,
            updated_at=now,
            completed_at=None
        )
        assert task.status == TaskStatus.WIP
        assert task.priority == Priority.REQUIRED
        assert len(task.acceptance_criteria) == 3
        assert task.dependencies == [1, 2]
        assert task.estimated_effort == 3
        assert task.actual_effort == 4

    def test_task_complete(self):
        """RED: 测试完成任务"""
        task = Task(id=1, title="Test Task")
        assert task.completed_at is None

        task.complete()
        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None

    def test_task_start(self):
        """RED: 测试开始任务"""
        task = Task(id=1, title="Test Task", status=TaskStatus.TODO)
        task.start()
        assert task.status == TaskStatus.WIP

    def test_task_block(self):
        """RED: 测试阻塞任务"""
        task = Task(id=1, title="Test Task")
        task.block("等待 API 文档")
        assert task.status == TaskStatus.BLOCKED

    def test_task_add_acceptance_criterion(self):
        """RED: 测试添加验收标准"""
        task = Task(id=1, title="Test Task")
        task.add_acceptance_criterion("测试标准 1")
        assert "测试标准 1" in task.acceptance_criteria

    def test_task_add_dependency(self):
        """RED: 测试添加依赖"""
        task = Task(id=1, title="Test Task")
        task.add_dependency(2)
        assert 2 in task.dependencies

    def test_task_to_dict(self):
        """RED: 测试任务序列化为字典"""
        task = Task(id=1, title="Test Task")
        data = task.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Test Task"
        assert data["status"] == "TODO"
        assert data["priority"] == "REQUIRED"

    def test_task_from_dict(self):
        """RED: 测试从字典创建任务"""
        data = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "status": "WIP",
            "priority": "RECOMMENDED",
            "acceptance_criteria": ["criterion 1"],
            "dependencies": [1],
            "estimated_effort": 3
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.status == TaskStatus.WIP
        assert task.priority == Priority.RECOMMENDED
        assert len(task.acceptance_criteria) == 1
        assert task.dependencies == [1]

    def test_task_str(self):
        """RED: 测试任务字符串表示"""
        task = Task(id=1, title="Test Task")
        result = str(task)
        assert "1" in result
        assert "Test Task" in result
