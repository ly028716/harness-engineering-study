"""Performance Monitor - Phase 7"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from statistics import median

from harness.history import HistoryManager
from harness.store import TaskStore
from harness.models import TaskStatus


@dataclass
class PerformanceMetrics:
    """性能指标摘要"""
    total_duration_minutes: float = 0.0
    avg_duration_minutes: float = 0.0
    min_duration_minutes: float = 0.0
    max_duration_minutes: float = 0.0
    median_duration_minutes: float = 0.0
    total_completed: int = 0
    total_failed: int = 0
    success_rate: float = 100.0
    total_tasks: int = 0
    completed_tasks: int = 0
    effort_accuracy: float = 0.0
    bottleneck_tasks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "total_duration_minutes": self.total_duration_minutes,
            "avg_duration_minutes": self.avg_duration_minutes,
            "min_duration_minutes": self.min_duration_minutes,
            "max_duration_minutes": self.max_duration_minutes,
            "median_duration_minutes": self.median_duration_minutes,
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "success_rate": self.success_rate,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "effort_accuracy": self.effort_accuracy,
            "bottleneck_tasks": self.bottleneck_tasks,
        }


@dataclass
class ModelUsageStats:
    """模型使用统计"""
    model_name: str
    task_count: int = 0
    avg_duration_seconds: float = 0.0
    total_duration_seconds: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "model_name": self.model_name,
            "task_count": self.task_count,
            "avg_duration_seconds": self.avg_duration_seconds,
            "total_duration_seconds": self.total_duration_seconds,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
        }


class PerformanceMonitor:
    """性能监控器 - 基于历史记录和任务存储的只读分析"""

    def __init__(self, harness_dir: Path):
        """初始化性能监控器

        Args:
            harness_dir: .harness 目录路径
        """
        self.harness_dir = Path(harness_dir)
        self.history = HistoryManager(self.harness_dir)
        self.store = TaskStore(self.harness_dir)

    def get_summary(self, top_n: int = 5) -> PerformanceMetrics:
        """获取性能摘要

        Args:
            top_n: 瓶颈任务数量

        Returns:
            性能指标
        """
        completed_events = self.history.get_completed_events()
        tasks = self.store.load_tasks()

        if not completed_events:
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
            return PerformanceMetrics(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
            )

        durations = [e.get("duration_minutes", 0) for e in completed_events]
        total_duration = sum(durations)
        avg_duration = total_duration / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        med_duration = median(durations) if durations else 0

        total_completed = sum(1 for e in completed_events if e.get("success", True))
        total_failed = sum(1 for e in completed_events if not e.get("success", True))
        total_events = len(completed_events)
        success_rate = (total_completed / total_events * 100) if total_events else 100.0

        # 工作量准确度
        total_tasks = len(tasks)
        done_tasks = [t for t in tasks if t.status == TaskStatus.DONE]
        effort_accuracy = self._calc_effort_accuracy(done_tasks)

        bottlenecks = self._find_bottlenecks(top_n)

        return PerformanceMetrics(
            total_duration_minutes=total_duration,
            avg_duration_minutes=round(avg_duration, 1),
            min_duration_minutes=min_duration,
            max_duration_minutes=max_duration,
            median_duration_minutes=round(med_duration, 1),
            total_completed=total_completed,
            total_failed=total_failed,
            success_rate=round(success_rate, 1),
            total_tasks=total_tasks,
            completed_tasks=len(done_tasks),
            effort_accuracy=round(effort_accuracy, 1),
            bottleneck_tasks=bottlenecks,
        )

    def get_model_usage(self) -> List[ModelUsageStats]:
        """获取模型使用统计

        Returns:
            各模型使用统计列表，按使用次数降序排列
        """
        completed_events = self.history.get_completed_events()
        model_map: Dict[str, List[Dict[str, Any]]] = {}

        for event in completed_events:
            model = event.get("model_used", "") or "unknown"
            if model not in model_map:
                model_map[model] = []
            model_map[model].append(event)

        result = []
        for model_name, events in model_map.items():
            count = len(events)
            total_duration = sum(
                e.get("duration_minutes", 0) * 60 for e in events
            )
            success_count = sum(1 for e in events if e.get("success", True))
            failure_count = count - success_count
            rate = (success_count / count * 100) if count else 100.0
            avg_duration = total_duration / count if count else 0

            result.append(ModelUsageStats(
                model_name=model_name,
                task_count=count,
                avg_duration_seconds=round(avg_duration, 1),
                total_duration_seconds=round(total_duration, 1),
                success_count=success_count,
                failure_count=failure_count,
                success_rate=round(rate, 1),
            ))

        result.sort(key=lambda s: s.task_count, reverse=True)
        return result

    def get_task_timing(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取单个任务的时序信息

        Args:
            task_id: 任务 ID

        Returns:
            时序信息字典，如果任务不存在则返回 None
        """
        task = self.store.get_task(task_id)
        if not task:
            return None

        task_events = self.history.get_events_by_task(task_id)
        completed_event = None
        for e in task_events:
            if e.get("event") == "task_completed":
                completed_event = e
                break

        result: Dict[str, Any] = {
            "task_id": task.id,
            "title": task.title,
            "status": task.status.value,
            "estimated_effort": task.estimated_effort,
            "actual_effort": task.actual_effort,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "duration_minutes": 0,
            "model_used": "",
            "event_count": len(task_events),
        }

        if completed_event:
            result["duration_minutes"] = completed_event.get("duration_minutes", 0)
            result["model_used"] = completed_event.get("model_used", "")

        return result

    def get_effort_analysis(self) -> Dict[str, Any]:
        """获取工作量分析（估算 vs 实际）

        Returns:
            工作量分析字典
        """
        tasks = self.store.load_tasks()
        done_tasks = [t for t in tasks if t.status == TaskStatus.DONE]

        estimated_total = sum(t.estimated_effort for t in done_tasks)
        actual_total = sum(t.actual_effort or 0 for t in done_tasks)

        accuracy = self._calc_effort_accuracy(done_tasks)

        # 按超出估算百分比排序的任务列表
        over_estimates = []
        for t in done_tasks:
            if t.actual_effort and t.estimated_effort:
                ratio = t.actual_effort / t.estimated_effort
                if ratio > 1.2:
                    over_estimates.append({
                        "task_id": t.id,
                        "title": t.title,
                        "estimated": t.estimated_effort,
                        "actual": t.actual_effort,
                        "ratio": round(ratio, 1),
                    })

        over_estimates.sort(key=lambda x: x["ratio"], reverse=True)

        return {
            "total_tasks_completed": len(done_tasks),
            "estimated_total_hours": estimated_total,
            "actual_total_hours": actual_total,
            "accuracy_percent": round(accuracy, 1),
            "over_estimated_tasks": over_estimates[:10],
        }

    def _find_bottlenecks(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """找出最耗时的任务（瓶颈）

        Args:
            top_n: 返回前 N 个瓶颈任务

        Returns:
            瓶颈任务列表
        """
        completed_events = self.history.get_completed_events()
        bottlenecks = []

        for event in completed_events:
            duration = event.get("duration_minutes", 0)
            if duration > 0:
                bottlenecks.append({
                    "task_id": event.get("task_id"),
                    "task_title": event.get("task_title", "Unknown"),
                    "duration_minutes": duration,
                    "model_used": event.get("model_used", ""),
                })

        bottlenecks.sort(key=lambda x: x["duration_minutes"], reverse=True)
        return bottlenecks[:top_n]

    def _calc_effort_accuracy(self, done_tasks) -> float:
        """计算工作量准确度

        比较估算工作量和实际工作量的偏差百分比。
        100% 表示完全准确，0% 表示完全偏离。

        Args:
            done_tasks: 已完成的任务列表

        Returns:
            准确度百分比
        """
        if not done_tasks:
            return 100.0

        valid_tasks = [t for t in done_tasks if t.actual_effort is not None]
        if not valid_tasks:
            return 100.0

        deviations = []
        for t in valid_tasks:
            if t.estimated_effort > 0:
                ratio = (t.actual_effort or 0) / t.estimated_effort
                deviation = abs(1 - ratio)
                deviations.append(deviation)

        if not deviations:
            return 100.0

        avg_deviation = sum(deviations) / len(deviations)
        accuracy = max(0, (1 - avg_deviation) * 100)
        return accuracy
