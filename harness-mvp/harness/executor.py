"""执行引擎 - Phase 3 + AI 集成"""
import asyncio
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from harness.models import Task, TaskStatus
from harness.ai_client import AIClient
from harness.prompts import WORKER_SYSTEM_PROMPT, build_work_prompt


class ExecutionMode(Enum):
    """执行模式枚举"""
    SOLO = "SOLO"
    PARALLEL = "PARALLEL"


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: int
    task_title: str
    success: bool
    output: str = ""
    error: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


class WorkerAgent:
    """工作 Agent - 使用 AI 生成代码执行单个任务"""

    def __init__(self, task: Task, ai_client: Optional[AIClient] = None):
        """初始化 Worker Agent

        Args:
            task: 要执行的任务
            ai_client: AI 客户端，默认从环境变量自动创建
        """
        self.task = task
        self.ai_client = ai_client
        self.status = "idle"
        self.output: List[str] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def capture_output(self, line: str):
        """捕获输出行

        Args:
            line: 输出行
        """
        self.output.append(line)

    def update_status(self, status: str):
        """更新状态

        Args:
            status: 新状态
        """
        self.status = status

    def execute(self, work_dir: str = "") -> ExecutionResult:
        """执行任务

        Args:
            work_dir: 工作目录，用于写入生成的文件

        Returns:
            执行结果
        """
        self.started_at = datetime.now()
        self.update_status("running")
        self.capture_output(f"开始执行任务：{self.task.title}")

        success = False
        try:
            self._execute_task(work_dir)
            success = True
        except Exception as e:
            self.capture_output(f"执行错误：{str(e)}")

        self.completed_at = datetime.now()
        self.update_status("completed")

        duration = (self.completed_at - self.started_at).total_seconds()

        return ExecutionResult(
            task_id=self.task.id,
            task_title=self.task.title,
            success=success,
            output="\n".join(self.output),
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_seconds=duration
        )

    def _execute_task(self, work_dir: str = ""):
        """执行任务逻辑 — 调用 AI 生成代码

        Args:
            work_dir: 工作目录
        """
        self.capture_output(f"任务描述：{self.task.description or '无'}")

        # 创建 AI 客户端
        if self.ai_client is None:
            try:
                self.ai_client = AIClient()
            except ValueError as e:
                self.capture_output(str(e))
                self.capture_output("回退到模拟模式（仅输出任务信息）")
                self._fallback_execute()
                return

        # 构建提示词
        user_prompt = build_work_prompt(
            task_title=self.task.title,
            task_description=self.task.description,
            acceptance_criteria=self.task.acceptance_criteria,
            dependencies=self.task.dependencies,
        )

        self.capture_output("正在调用 AI 生成代码...")
        response = self.ai_client.generate_code(WORKER_SYSTEM_PROMPT, user_prompt)

        # 解析并写入生成的文件
        files_written = self._parse_and_write_files(response, work_dir)
        if files_written:
            self.capture_output(f"已生成 {len(files_written)} 个文件:")
            for f in files_written:
                self.capture_output(f"  ✅ {f}")
        else:
            self.capture_output("AI 返回内容（未检测到代码文件）:")
            # 截断过长响应
            display = response[:500] + "..." if len(response) > 500 else response
            self.capture_output(display)

    def _fallback_execute(self):
        """模拟执行（无 API key 时的回退）"""
        self.capture_output(f"任务描述：{self.task.description or '无'}")
        if self.task.acceptance_criteria:
            self.capture_output("验收标准:")
            for criterion in self.task.acceptance_criteria:
                self.capture_output(f"  - {criterion}")

    def _parse_and_write_files(self, response: str, work_dir: str) -> List[str]:
        """解析 AI 响应中的代码块并写入文件

        Args:
            response: AI 响应文本
            work_dir: 工作目录

        Returns:
            写入的文件路径列表
        """
        # 匹配 ```python:<path> 或 ```python 代码块
        pattern = r'```python(?::(\S+))?\s*\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)

        written = []
        for file_path, code in matches:
            file_path = file_path or "generated.py"
            file_path = file_path.strip("'\"` ")

            # 写入文件
            full_path = Path(work_dir) / file_path if work_dir else Path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code.strip(), encoding='utf-8')
            written.append(str(full_path))

        return written


def select_execution_mode(tasks: List[Task]) -> ExecutionMode:
    """根据任务数量选择执行模式

    规则:
    - 1-2 个任务 → Solo (最小开销)
    - 3+ 个任务 → Parallel (Worker 分离)

    Args:
        tasks: 任务列表

    Returns:
        执行模式
    """
    if len(tasks) <= 2:
        return ExecutionMode.SOLO
    else:
        return ExecutionMode.PARALLEL


class ExecutionEngine:
    """执行引擎 - 协调任务执行"""

    def __init__(self, work_dir: str):
        """初始化执行引擎

        Args:
            work_dir: 工作目录
        """
        self.work_dir = work_dir
        self.mode: Optional[ExecutionMode] = None
        self.executed_tasks: List[ExecutionResult] = []

    def set_mode(self, mode: ExecutionMode):
        """设置执行模式

        Args:
            mode: 执行模式
        """
        self.mode = mode

    def prepare_batches(self, tasks: List[Task]) -> List[List[Task]]:
        """准备执行批次

        根据依赖关系将任务分组到批次中。
        无依赖的任务在同一批次，有依赖的任务在后续批次。

        Args:
            tasks: 任务列表

        Returns:
            批次列表
        """
        if not tasks:
            return []

        # 根据模式决定批次策略
        if self.mode == ExecutionMode.SOLO or len(tasks) <= 2:
            # Solo 模式：每个任务独立批次
            return [[task] for task in tasks]

        # Parallel 模式：按依赖关系分组
        batches = []
        remaining = tasks.copy()
        completed_ids = set()

        while remaining:
            # 找出所有依赖已满足的任务
            ready = [
                t for t in remaining
                if all(dep in completed_ids for dep in t.dependencies)
            ]

            if not ready:
                # 剩余的都有未满足的依赖，可能是循环依赖
                # 将它们放入最后的批次
                batches.append(remaining)
                break

            batches.append(ready)
            completed_ids.update(t.id for t in ready)
            remaining = [t for t in remaining if t not in ready]

        return batches


class SoloExecutor:
    """Solo 执行器 - 顺序执行任务"""

    def __init__(self, work_dir: str):
        """初始化 Solo 执行器

        Args:
            work_dir: 工作目录
        """
        self.work_dir = work_dir

    def execute(self, task: Task) -> ExecutionResult:
        """执行单个任务

        Args:
            task: 任务

        Returns:
            执行结果
        """
        worker = WorkerAgent(task)
        return worker.execute(work_dir=self.work_dir)


class ParallelExecutor:
    """Parallel 执行器 - 并行执行任务"""

    def __init__(self, work_dir: str):
        """初始化 Parallel 执行器

        Args:
            work_dir: 工作目录
        """
        self.work_dir = work_dir

    def execute_batch(self, tasks: List[Task]) -> List[ExecutionResult]:
        """并行执行一批任务

        Args:
            tasks: 任务列表

        Returns:
            执行结果列表
        """
        results = []

        # 为每个任务创建 worker
        workers = [WorkerAgent(task) for task in tasks]

        # 顺序执行（基础实现，后续可改为异步并行）
        for worker in workers:
            result = worker.execute(work_dir=self.work_dir)
            results.append(result)

        return results


class TaskExecutionService:
    """任务执行服务 - 高层 API"""

    def __init__(self, harness_dir: Path):
        """初始化任务执行服务

        Args:
            harness_dir: .harness 目录路径
        """
        self.harness_dir = harness_dir
        self.work_dir = str(harness_dir.parent)

        # 延迟导入避免循环依赖
        from harness.store import TaskStore
        from harness.history import HistoryManager
        self.store = TaskStore(harness_dir)
        self.history = HistoryManager(harness_dir)

    def execute_tasks(self, task_ids: Optional[List[int]] = None) -> List[ExecutionResult]:
        """执行任务

        Args:
            task_ids: 任务 ID 列表，None 表示执行所有 TODO 状态的任务

        Returns:
            执行结果列表
        """
        # 如果没有指定任务 ID，获取所有 TODO 状态的任务
        if task_ids is None:
            tasks = self.store.get_tasks_by_status(TaskStatus.TODO)
        else:
            tasks = [self.store.get_task(tid) for tid in task_ids]
            tasks = [t for t in tasks if t is not None]

        if not tasks:
            return []

        # 自动选择执行模式
        mode = select_execution_mode(tasks)

        # 创建执行引擎
        engine = ExecutionEngine(self.work_dir)
        engine.set_mode(mode)

        # 准备批次
        batches = engine.prepare_batches(tasks)

        # 执行任务
        all_results = []

        if mode == ExecutionMode.SOLO:
            executor = SoloExecutor(self.work_dir)
            for batch in batches:
                for task in batch:
                    # 更新任务状态为进行中
                    task.start()
                    self.store.update_task(task)

                    # 执行任务
                    result = executor.execute(task)
                    all_results.append(result)

                    # 根据执行结果更新任务状态
                    if result.success:
                        task.complete()
                        self.store.update_task(task)
                        self.history.log_task_completed(task, int(result.duration_seconds / 60))
        else:
            executor = ParallelExecutor(self.work_dir)
            for batch in batches:
                # 更新任务状态为进行中
                for task in batch:
                    task.start()
                    self.store.update_task(task)

                # 执行批次
                results = executor.execute_batch(batch)
                all_results.extend(results)

                # 根据执行结果更新任务状态
                for task, result in zip(batch, results):
                    if result.success:
                        task.complete()
                    self.store.update_task(task)
                    if result.success:
                        self.history.log_task_completed(task, int(result.duration_seconds / 60))

        return all_results

    def execute_task_solo(self, task_id: int) -> ExecutionResult:
        """以 Solo 模式执行单个任务

        Args:
            task_id: 任务 ID

        Returns:
            执行结果
        """
        task = self.store.get_task(task_id)
        if not task:
            raise ValueError(f"任务 #{task_id} 不存在")

        # 更新任务状态为进行中
        task.start()
        self.store.update_task(task)

        # 执行任务
        executor = SoloExecutor(self.work_dir)
        result = executor.execute(task)

        # 根据执行结果更新任务状态
        if result.success:
            task.complete()
            self.store.update_task(task)
            self.history.log_task_completed(task, int(result.duration_seconds / 60))

        return result

    def execute_task_parallel(self, task_ids: List[int]) -> List[ExecutionResult]:
        """以 Parallel 模式执行多个任务

        Args:
            task_ids: 任务 ID 列表

        Returns:
            执行结果列表
        """
        tasks = [self.store.get_task(tid) for tid in task_ids]
        tasks = [t for t in tasks if t is not None]

        if not tasks:
            return []

        # 更新任务状态为进行中
        for task in tasks:
            task.start()
            self.store.update_task(task)

        # 执行任务
        executor = ParallelExecutor(self.work_dir)
        results = executor.execute_batch(tasks)

        # 根据执行结果更新任务状态
        for task, result in zip(tasks, results):
            if result.success:
                task.complete()
                self.store.update_task(task)
                self.history.log_task_completed(task, int(result.duration_seconds / 60))

        return results
