"""测试执行引擎 - Phase 3"""
import pytest
from harness.models import Task, TaskStatus, Priority
from harness.executor import ExecutionMode, select_execution_mode, ExecutionEngine


class TestExecutionMode:
    """测试执行模式选择"""

    def test_select_solo_mode_single_task(self):
        """RED: 单个任务选择 Solo 模式"""
        tasks = [
            Task(id=1, title="Task 1", description="Single task")
        ]
        mode = select_execution_mode(tasks)
        assert mode == ExecutionMode.SOLO

    def test_select_solo_mode_two_tasks(self):
        """RED: 两个任务选择 Solo 模式"""
        tasks = [
            Task(id=1, title="Task 1", description="First task"),
            Task(id=2, title="Task 2", description="Second task")
        ]
        mode = select_execution_mode(tasks)
        assert mode == ExecutionMode.SOLO

    def test_select_parallel_mode_three_tasks(self):
        """RED: 三个任务选择 Parallel 模式"""
        tasks = [
            Task(id=1, title="Task 1", description="First task"),
            Task(id=2, title="Task 2", description="Second task"),
            Task(id=3, title="Task 3", description="Third task")
        ]
        mode = select_execution_mode(tasks)
        assert mode == ExecutionMode.PARALLEL

    def test_select_parallel_mode_many_tasks(self):
        """RED: 多个任务选择 Parallel 模式"""
        tasks = [
            Task(id=i, title=f"Task {i}", description=f"Task {i} description")
            for i in range(1, 10)
        ]
        mode = select_execution_mode(tasks)
        assert mode == ExecutionMode.PARALLEL


class TestExecutionEngine:
    """测试执行引擎"""

    def test_execution_engine_initializes(self):
        """RED: 测试执行引擎初始化"""
        engine = ExecutionEngine(work_dir="/tmp/test")
        assert engine.work_dir == "/tmp/test"
        assert engine.mode is None
        assert engine.executed_tasks == []

    def test_execution_engine_set_mode(self):
        """RED: 测试设置执行模式"""
        engine = ExecutionEngine(work_dir="/tmp/test")
        engine.set_mode(ExecutionMode.SOLO)
        assert engine.mode == ExecutionMode.SOLO

    def test_execution_engine_prepare_batches_single_task(self):
        """RED: 测试准备执行批次 - 单任务"""
        engine = ExecutionEngine(work_dir="/tmp/test")
        tasks = [Task(id=1, title="Task 1", description="Single task")]
        batches = engine.prepare_batches(tasks)

        # Solo 模式：每个任务一个批次
        assert len(batches) == 1
        assert len(batches[0]) == 1
        assert batches[0][0].id == 1

    def test_execution_engine_prepare_batches_no_dependencies(self):
        """RED: 测试准备执行批次 - 无依赖"""
        engine = ExecutionEngine(work_dir="/tmp/test")
        tasks = [
            Task(id=1, title="Task 1", description="No deps"),
            Task(id=2, title="Task 2", description="No deps"),
            Task(id=3, title="Task 3", description="No deps")
        ]
        batches = engine.prepare_batches(tasks)

        # Parallel 模式：无依赖任务在同一批次
        assert len(batches) == 1
        assert len(batches[0]) == 3

    def test_execution_engine_prepare_batches_with_dependencies(self):
        """RED: 测试准备执行批次 - 有依赖"""
        engine = ExecutionEngine(work_dir="/tmp/test")
        tasks = [
            Task(id=1, title="Task 1", description="Base task", dependencies=[]),
            Task(id=2, title="Task 2", description="Depends on 1", dependencies=[1]),
            Task(id=3, title="Task 3", description="Depends on 2", dependencies=[2])
        ]
        batches = engine.prepare_batches(tasks)

        # 有依赖的任务应该在不同批次
        assert len(batches) == 3
        assert batches[0][0].id == 1
        assert batches[1][0].id == 2
        assert batches[2][0].id == 3


class TestWorkerAgent:
    """测试 Worker Agent"""

    def test_worker_agent_initializes(self):
        """RED: 测试 WorkerAgent 初始化"""
        from harness.executor import WorkerAgent
        worker = WorkerAgent(task=Task(id=1, title="Test Task"))
        assert worker.task.id == 1
        assert worker.status == "idle"

    def test_worker_agent_execute_task(self):
        """RED: 测试 WorkerAgent 执行任务"""
        from harness.executor import WorkerAgent, ExecutionResult
        worker = WorkerAgent(task=Task(id=1, title="Test Task", description="Test"))
        result = worker.execute()

        assert isinstance(result, ExecutionResult)
        assert result.task_id == 1
        assert result.success is True or result.success is False

    def test_worker_agent_capture_output(self):
        """RED: 测试 WorkerAgent 捕获输出"""
        from harness.executor import WorkerAgent
        worker = WorkerAgent(task=Task(id=1, title="Test Task", description="Test"))
        worker.capture_output("Test output line 1")
        worker.capture_output("Test output line 2")

        assert "Test output line 1" in worker.output
        assert "Test output line 2" in worker.output

    def test_worker_agent_update_status(self):
        """RED: 测试 WorkerAgent 状态更新"""
        from harness.executor import WorkerAgent
        worker = WorkerAgent(task=Task(id=1, title="Test Task"))

        worker.update_status("running")
        assert worker.status == "running"

        worker.update_status("completed")
        assert worker.status == "completed"


class TestSoloExecutor:
    """测试 Solo 执行器"""

    def test_solo_executor_initializes(self):
        """RED: 测试 SoloExecutor 初始化"""
        from harness.executor import SoloExecutor
        executor = SoloExecutor(work_dir="/tmp/test")
        assert executor.work_dir == "/tmp/test"

    def test_solo_executor_execute(self):
        """RED: 测试 SoloExecutor 执行单个任务"""
        from harness.executor import SoloExecutor
        executor = SoloExecutor(work_dir="/tmp/test")
        task = Task(id=1, title="Solo Task", description="Execute alone")

        # 执行任务（模拟）
        result = executor.execute(task)

        assert result is not None


class TestParallelExecutor:
    """测试 Parallel 执行器"""

    def test_parallel_executor_initializes(self):
        """RED: 测试 ParallelExecutor 初始化"""
        from harness.executor import ParallelExecutor
        executor = ParallelExecutor(work_dir="/tmp/test")
        assert executor.work_dir == "/tmp/test"

    def test_parallel_executor_execute_batch(self):
        """RED: 测试 ParallelExecutor 执行批次"""
        from harness.executor import ParallelExecutor
        executor = ParallelExecutor(work_dir="/tmp/test")
        tasks = [
            Task(id=1, title="Parallel Task 1"),
            Task(id=2, title="Parallel Task 2"),
        ]

        # 执行批次（模拟）
        results = executor.execute_batch(tasks)

        assert len(results) == 2


class TestGitWorktreeManager:
    """测试 Git 工作区管理器"""

    def test_git_worktree_manager_initializes(self):
        """RED: 测试 GitWorktreeManager 初始化"""
        from harness.git import GitWorktreeManager
        from pathlib import Path
        manager = GitWorktreeManager(repo_path="/tmp/repo")
        assert manager.repo_path == Path("/tmp/repo")
        assert manager.active_worktrees == []

    def test_git_worktree_manager_create_worktree(self):
        """RED: 测试创建工作区"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式（非 git 仓库）
        result = manager.create_worktree("feature-branch", "/tmp/worktree")
        assert result is True
        assert "/tmp/worktree" in manager.active_worktrees

    def test_git_worktree_manager_remove_worktree(self):
        """RED: 测试删除工作区"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")
        manager.active_worktrees.append("/tmp/worktree")

        # 模拟模式
        result = manager.remove_worktree("/tmp/worktree")
        assert result is True
        assert "/tmp/worktree" not in manager.active_worktrees

    def test_git_worktree_manager_detect_changes(self):
        """RED: 测试检测变更"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        changes = manager.detect_changes()
        assert isinstance(changes, list)
        assert len(changes) == 0

    def test_git_worktree_manager_get_current_branch(self):
        """RED: 测试获取当前分支"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        branch = manager.get_current_branch()
        assert branch == "main"

    def test_git_worktree_manager_checkout_branch(self):
        """RED: 测试切换分支"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        result = manager.checkout_branch("feature", create=True)
        assert result is True

    def test_git_worktree_manager_add_files(self):
        """RED: 测试添加文件"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        result = manager.add_files(["file1.py", "file2.py"])
        assert result is True

    def test_git_worktree_manager_commit(self):
        """RED: 测试提交"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        result = manager.commit("Test commit", allow_empty=True)
        assert result is True

    def test_git_worktree_manager_push(self):
        """RED: 测试推送"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        result = manager.push("main", upstream=True)
        assert result is True

    def test_git_worktree_manager_get_diff(self):
        """RED: 测试获取 diff"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")

        # 模拟模式
        diff = manager.get_diff("HEAD~1")
        assert diff == ""

    def test_git_worktree_manager_list_worktrees(self):
        """RED: 测试列出工作区"""
        from harness.git import GitWorktreeManager
        manager = GitWorktreeManager(repo_path="/tmp/repo")
        manager.active_worktrees.append("/tmp/worktree1")
        manager.active_worktrees.append("/tmp/worktree2")

        # 模拟模式
        worktrees = manager.list_worktrees()
        assert len(worktrees) == 2


class TestTaskExecutionService:
    """测试任务执行服务"""

    def test_task_execution_service_initializes(self):
        """RED: 测试 TaskExecutionService 初始化"""
        from harness.executor import TaskExecutionService
        from harness.store import TaskStore
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            store = TaskStore(harness_dir)

            service = TaskExecutionService(harness_dir)
            assert service.harness_dir == harness_dir
            assert service.store is not None

    def test_task_execution_service_execute_tasks_auto_mode(self):
        """RED: 测试自动模式执行任务"""
        from harness.executor import TaskExecutionService
        from harness.store import TaskStore
        from harness.models import Task
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            store = TaskStore(harness_dir)

            # 添加任务
            store.add_task(Task(id=1, title="Task 1", description="Test"))
            store.add_task(Task(id=2, title="Task 2", description="Test"))

            service = TaskExecutionService(harness_dir)
            results = service.execute_tasks(task_ids=[1, 2])

            assert len(results) == 2

    def test_execution_result_to_dict(self):
        """RED: 测试 ExecutionResult 序列化"""
        from harness.executor import ExecutionResult
        from datetime import datetime

        result = ExecutionResult(
            task_id=1,
            task_title="Test",
            success=True,
            output="Test output",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_seconds=1.5
        )

        result_dict = result.to_dict()

        assert result_dict["task_id"] == 1
        assert result_dict["task_title"] == "Test"
        assert result_dict["success"] is True
        assert result_dict["output"] == "Test output"
        assert result_dict["duration_seconds"] == 1.5

    def test_worker_agent_execute_with_acceptance_criteria(self):
        """RED: 测试 WorkerAgent 执行带验收标准的任务"""
        from harness.executor import WorkerAgent
        from harness.models import Task

        task = Task(
            id=1,
            title="Test Task",
            description="Test description",
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        worker = WorkerAgent(task)
        result = worker.execute()

        assert result.success is True
        assert "Criterion 1" in result.output
        assert "Criterion 2" in result.output

    def test_execution_engine_prepare_batches_empty(self):
        """RED: 测试准备执行批次 - 空任务列表"""
        from harness.executor import ExecutionEngine

        engine = ExecutionEngine(work_dir="/tmp/test")
        batches = engine.prepare_batches([])

        assert batches == []

    def test_task_execution_service_execute_task_solo(self):
        """RED: 测试执行单个任务 (Solo)"""
        from harness.executor import TaskExecutionService
        from harness.store import TaskStore
        from harness.models import Task
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            store = TaskStore(harness_dir)
            store.add_task(Task(id=1, title="Solo Task", description="Test"))

            service = TaskExecutionService(harness_dir)
            result = service.execute_task_solo(1)

            assert result is not None
            assert result.task_id == 1

    def test_task_execution_service_execute_task_parallel(self):
        """RED: 测试执行多个任务 (Parallel)"""
        from harness.executor import TaskExecutionService
        from harness.store import TaskStore
        from harness.models import Task
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            store = TaskStore(harness_dir)

            for i in range(1, 4):
                store.add_task(Task(id=i, title=f"Task {i}", description="Test"))

            service = TaskExecutionService(harness_dir)
            results = service.execute_task_parallel([1, 2, 3])

            assert len(results) == 3

    def test_task_execution_service_execute_nonexistent_task(self):
        """RED: 测试执行不存在的任务"""
        from harness.executor import TaskExecutionService
        from harness.store import TaskStore
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            harness_dir = Path(tmpdir) / ".harness"
            harness_dir.mkdir()
            store = TaskStore(harness_dir)

            service = TaskExecutionService(harness_dir)

            with pytest.raises(ValueError):
                service.execute_task_solo(999)
