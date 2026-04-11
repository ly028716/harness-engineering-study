"""任务存储 - Phase 2"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from harness.models import Task, TaskStatus, Priority


class TaskStore:
    """任务存储管理器"""

    def __init__(self, harness_dir: Path):
        """初始化任务存储

        Args:
            harness_dir: .harness 目录路径
        """
        self.harness_dir = Path(harness_dir)
        self.state_file = self.harness_dir / "state.json"
        self._ensure_directory()
        self._ensure_state_file()

    def _ensure_directory(self):
        """确保目录存在"""
        self.harness_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_state_file(self):
        """确保状态文件存在"""
        if not self.state_file.exists():
            self._write_state({"tasks": []})

    def _write_state(self, state: Dict[str, Any]):
        """写入状态到文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def _read_state(self) -> Dict[str, Any]:
        """读取状态文件"""
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_tasks(self, tasks: List[Task]):
        """保存任务列表

        Args:
            tasks: 任务列表
        """
        from datetime import datetime
        state = {
            "tasks": [task.to_dict() for task in tasks],
            "updated_at": datetime.now().isoformat()
        }
        self._write_state(state)

    def load_tasks(self) -> List[Task]:
        """加载任务列表

        Returns:
            任务列表
        """
        state = self._read_state()
        return [Task.from_dict(task_data) for task_data in state.get("tasks", [])]

    def get_task(self, task_id: int) -> Optional[Task]:
        """根据 ID 获取任务

        Args:
            task_id: 任务 ID

        Returns:
            任务或 None
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, task: Task):
        """添加新任务

        Args:
            task: 要添加的任务
        """
        tasks = self.load_tasks()
        tasks.append(task)
        self.save_tasks(tasks)

    def update_task(self, task: Task):
        """更新任务

        Args:
            task: 要更新的任务
        """
        tasks = self.load_tasks()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break
        self.save_tasks(tasks)

    def delete_task(self, task_id: int):
        """删除任务

        Args:
            task_id: 任务 ID
        """
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t.id != task_id]
        self.save_tasks(tasks)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """根据状态获取任务

        Args:
            status: 任务状态

        Returns:
            任务列表
        """
        tasks = self.load_tasks()
        return [t for t in tasks if t.status == status]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """根据优先级获取任务

        Args:
            priority: 优先级

        Returns:
            任务列表
        """
        tasks = self.load_tasks()
        return [t for t in tasks if t.priority == priority]

    def get_next_task_id(self) -> int:
        """获取下一个任务 ID

        Returns:
            下一个任务 ID
        """
        tasks = self.load_tasks()
        if not tasks:
            return 1
        return max(t.id for t in tasks) + 1

    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计

        Returns:
            统计字典
        """
        tasks = self.load_tasks()
        total = len(tasks)

        if total == 0:
            return {
                "total": 0,
                "todo": 0,
                "wip": 0,
                "done": 0,
                "blocked": 0,
                "progress_percent": 0
            }

        todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)
        wip = sum(1 for t in tasks if t.status == TaskStatus.WIP)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        blocked = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)

        progress_percent = int((done / total) * 100)

        return {
            "total": total,
            "todo": todo,
            "wip": wip,
            "done": done,
            "blocked": blocked,
            "progress_percent": progress_percent
        }
