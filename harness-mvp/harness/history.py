"""历史记录管理器 - Phase 2"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from harness.models import Task


class HistoryManager:
    """管理任务历史记录"""

    def __init__(self, harness_dir: Path):
        """初始化历史记录管理器

        Args:
            harness_dir: .harness 目录路径
        """
        self.harness_dir = Path(harness_dir)
        self.history_dir = self.harness_dir / "history"
        self.events_file = self.harness_dir / "events.json"
        self._ensure_directories()
        self._ensure_events_file()

    def _ensure_directories(self):
        """确保目录存在"""
        self.harness_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_events_file(self):
        """确件事件文件存在"""
        if not self.events_file.exists():
            self._write_events([])

    def _write_events(self, events: List[Dict[str, Any]]):
        """写入事件列表"""
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

    def _read_events(self) -> List[Dict[str, Any]]:
        """读取事件列表"""
        with open(self.events_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _add_event(self, event: Dict[str, Any]):
        """添加事件"""
        events = self._read_events()
        events.append(event)
        self._write_events(events)

    def log_task_created(self, task: Task):
        """记录任务创建事件

        Args:
            task: 任务对象
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": "task_created",
            "task_id": task.id,
            "task_title": task.title,
        }
        self._add_event(event)

    def log_task_updated(self, task: Task, changes: List[str]):
        """记录任务更新事件

        Args:
            task: 任务对象
            changes: 变更的字段列表
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": "task_updated",
            "task_id": task.id,
            "task_title": task.title,
            "changes": changes,
        }
        self._add_event(event)

    def log_task_completed(self, task: Task, duration_minutes: int = 0):
        """记录任务完成事件

        Args:
            task: 任务对象
            duration_minutes: 持续时间（分钟）
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": "task_completed",
            "task_id": task.id,
            "task_title": task.title,
            "duration_minutes": duration_minutes,
        }
        self._add_event(event)

    def log_task_blocked(self, task: Task, reason: str):
        """记录任务阻塞事件

        Args:
            task: 任务对象
            reason: 阻塞原因
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": "task_blocked",
            "task_id": task.id,
            "task_title": task.title,
            "reason": reason,
        }
        self._add_event(event)

    def log_task_deleted(self, task_id: int, task_title: str):
        """记录任务删除事件

        Args:
            task_id: 任务 ID
            task_title: 任务标题
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": "task_deleted",
            "task_id": task_id,
            "task_title": task_title,
        }
        self._add_event(event)

    def get_all_events(self) -> List[Dict[str, Any]]:
        """获取所有事件

        Returns:
            事件列表
        """
        return self._read_events()

    def get_events_by_task(self, task_id: int) -> List[Dict[str, Any]]:
        """获取指定任务的事件

        Args:
            task_id: 任务 ID

        Returns:
            事件列表
        """
        events = self._read_events()
        return [e for e in events if e.get("task_id") == task_id]

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的事件

        Args:
            event_type: 事件类型

        Returns:
            事件列表
        """
        events = self._read_events()
        return [e for e in events if e.get("event") == event_type]

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近事件

        Args:
            limit: 数量限制

        Returns:
            事件列表
        """
        events = self._read_events()
        return events[-limit:]

    def clear_history(self):
        """清空历史记录"""
        self._write_events([])

    def get_task_duration(self, task_id: int) -> int:
        """获取任务持续时间

        Args:
            task_id: 任务 ID

        Returns:
            持续时间（分钟）
        """
        events = self.get_events_by_task(task_id)
        for event in events:
            if event.get("event") == "task_completed":
                return event.get("duration_minutes", 0)
        return 0
