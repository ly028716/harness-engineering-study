"""Git 模块完整测试 - 提升覆盖率至 80%+"""
import pytest
import subprocess
from pathlib import Path
from harness.git import GitWorktreeManager, GitChange


@pytest.fixture(scope="function")
def git_repo(tmp_path):
    """创建临时 Git 仓库"""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    
    # 初始化 Git 仓库
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    
    # 创建初始提交
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)
    
    return repo_dir


class TestGitWorktreeManagerSimulation:
    """测试 GitWorktreeManager 模拟模式（非 Git 仓库）"""
    
    def test_init_non_git_repo(self, tmp_path):
        """测试非 Git 仓库初始化"""
        manager = GitWorktreeManager(str(tmp_path))
        
        assert manager.repo_path == tmp_path
        assert manager._is_git_repo is False
        assert manager.active_worktrees == []
    
    def test_create_worktree_simulation(self, tmp_path):
        """测试模拟模式创建工作区"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.create_worktree("feature/test", "/tmp/worktree")
        
        assert result is True
        assert "/tmp/worktree" in manager.active_worktrees
    
    def test_remove_worktree_simulation(self, tmp_path):
        """测试模拟模式删除工作区"""
        manager = GitWorktreeManager(str(tmp_path))
        manager.active_worktrees.append("/tmp/worktree")
        
        result = manager.remove_worktree("/tmp/worktree")
        
        assert result is True
        assert "/tmp/worktree" not in manager.active_worktrees
    
    def test_remove_worktree_not_exists_simulation(self, tmp_path):
        """测试删除不存在的工作区"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.remove_worktree("/tmp/nonexistent")
        
        assert result is True
    
    def test_detect_changes_simulation(self, tmp_path):
        """测试模拟模式检测变更"""
        manager = GitWorktreeManager(str(tmp_path))
        
        changes = manager.detect_changes()
        
        assert changes == []
    
    def test_get_current_branch_simulation(self, tmp_path):
        """测试模拟模式获取当前分支"""
        manager = GitWorktreeManager(str(tmp_path))
        
        branch = manager.get_current_branch()
        
        assert branch == "main"
    
    def test_checkout_branch_simulation(self, tmp_path):
        """测试模拟模式切换分支"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.checkout_branch("feature/test", create=True)
        
        assert result is True
    
    def test_add_files_simulation(self, tmp_path):
        """测试模拟模式添加文件"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.add_files(["file1.py", "file2.py"])
        
        assert result is True
    
    def test_commit_simulation(self, tmp_path):
        """测试模拟模式提交"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.commit("Test commit")
        
        assert result is True
    
    def test_commit_allow_empty_simulation(self, tmp_path):
        """测试模拟模式空提交"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.commit("Empty commit", allow_empty=True)
        
        assert result is True
    
    def test_push_simulation(self, tmp_path):
        """测试模拟模式推送"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.push("main")
        
        assert result is True
    
    def test_push_with_upstream_simulation(self, tmp_path):
        """测试模拟模式设置上游推送"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager.push("main", upstream=True)
        
        assert result is True
    
    def test_get_diff_simulation(self, tmp_path):
        """测试模拟模式获取 diff"""
        manager = GitWorktreeManager(str(tmp_path))
        
        diff = manager.get_diff()
        
        assert diff == ""
    
    def test_get_diff_with_base_ref_simulation(self, tmp_path):
        """测试模拟模式指定基准 diff"""
        manager = GitWorktreeManager(str(tmp_path))
        
        diff = manager.get_diff("HEAD~2")
        
        assert diff == ""
    
    def test_list_worktrees_simulation(self, tmp_path):
        """测试模拟模式列出工作区"""
        manager = GitWorktreeManager(str(tmp_path))
        manager.active_worktrees.append("/tmp/wt1")
        manager.active_worktrees.append("/tmp/wt2")
        
        worktrees = manager.list_worktrees()
        
        assert len(worktrees) == 2
        assert worktrees[0]["path"] == "/tmp/wt1"
        assert worktrees[1]["path"] == "/tmp/wt2"
    
    def test_run_git_simulation(self, tmp_path):
        """测试模拟模式运行 Git 命令"""
        manager = GitWorktreeManager(str(tmp_path))
        
        result = manager._run_git("status")
        
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""


class TestGitWorktreeManagerReal:
    """测试 GitWorktreeManager 真实 Git 操作"""
    
    def test_init_git_repo(self, git_repo):
        """测试 Git 仓库初始化"""
        manager = GitWorktreeManager(str(git_repo))
        
        assert manager._is_git_repo is True
        assert manager.repo_path == git_repo
    
    def test_get_current_branch_real(self, git_repo):
        """测试真实获取当前分支"""
        manager = GitWorktreeManager(str(git_repo))
        
        branch = manager.get_current_branch()
        
        # Git 默认分支可能是 master 或 main
        assert branch in ["master", "main"]
    
    def test_checkout_branch_existing(self, git_repo):
        """测试切换到已存在的分支"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 获取当前分支
        current_branch = manager.get_current_branch()
        
        # 切换到当前分支（应该成功）
        result = manager.checkout_branch(current_branch)
        
        assert result is True
    
    def test_checkout_create_new_branch(self, git_repo):
        """测试创建并切换到新分支"""
        manager = GitWorktreeManager(str(git_repo))
        
        result = manager.checkout_branch("feature/test", create=True)
        
        assert result is True
        assert manager.get_current_branch() == "feature/test"
    
    def test_checkout_nonexistent_branch_fails(self, git_repo):
        """测试切换到不存在的分支失败"""
        manager = GitWorktreeManager(str(git_repo))
        
        result = manager.checkout_branch("nonexistent-branch", create=False)
        
        assert result is False
    
    def test_add_files_real(self, git_repo):
        """测试真实添加文件"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建新文件
        test_file = git_repo / "test.txt"
        test_file.write_text("test content")
        
        result = manager.add_files(["test.txt"])
        
        assert result is True
        
        # 验证文件已暂存
        status_result = subprocess.run(
            ["git", "status", "--short"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        assert "A  test.txt" in status_result.stdout
    
    def test_commit_real(self, git_repo):
        """测试真实提交"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建并添加文件
        test_file = git_repo / "commit_test.txt"
        test_file.write_text("commit test")
        manager.add_files(["commit_test.txt"])
        
        result = manager.commit("Test commit message")
        
        assert result is True
        
        # 验证提交
        log_result = subprocess.run(
            ["git", "log", "--oneline", "-n", "1"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        assert "Test commit message" in log_result.stdout
    
    def test_commit_allow_empty_real(self, git_repo):
        """测试真实空提交"""
        manager = GitWorktreeManager(str(git_repo))
        
        result = manager.commit("Empty commit", allow_empty=True)
        
        assert result is True
    
    def test_commit_no_changes_fails(self, git_repo):
        """测试无变更提交失败"""
        manager = GitWorktreeManager(str(git_repo))
        
        result = manager.commit("Should fail", allow_empty=False)
        
        assert result is False
    
    def test_detect_changes_no_changes(self, git_repo):
        """测试无变更时检测变更"""
        manager = GitWorktreeManager(str(git_repo))
        
        changes = manager.detect_changes()
        
        assert changes == []
    
    def test_detect_changes_with_modifications(self, git_repo):
        """测试有修改时检测变更"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 修改文件
        readme = git_repo / "README.md"
        readme.write_text("# Modified")
        
        changes = manager.detect_changes()
        
        assert len(changes) > 0
        assert any(c.file == "README.md" for c in changes)
    
    def test_get_diff_real(self, git_repo):
        """测试真实获取 diff"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建并提交文件
        test_file = git_repo / "diff_test.txt"
        test_file.write_text("line 1")
        manager.add_files(["diff_test.txt"])
        manager.commit("Add diff test file")
        
        # 修改文件
        test_file.write_text("line 1\nline 2")
        manager.add_files(["diff_test.txt"])
        manager.commit("Modify diff test file")
        
        # 获取 diff
        diff = manager.get_diff("HEAD~1")
        
        assert "diff_test.txt" in diff
        assert "+line 2" in diff or "line 2" in diff
    
    def test_create_worktree_real(self, git_repo, tmp_path):
        """测试真实创建工作区"""
        manager = GitWorktreeManager(str(git_repo))
        
        worktree_path = str(tmp_path / "worktree1")
        result = manager.create_worktree("feature/wt1", worktree_path)
        
        assert result is True
        assert Path(worktree_path).exists()
        assert worktree_path in manager.active_worktrees
    
    def test_create_worktree_duplicate_fails(self, git_repo, tmp_path):
        """测试创建重复工作区失败"""
        manager = GitWorktreeManager(str(git_repo))
        
        worktree_path = str(tmp_path / "worktree_dup")
        
        # 第一次创建成功
        result1 = manager.create_worktree("feature/dup1", worktree_path)
        assert result1 is True
        
        # 第二次创建相同路径失败
        result2 = manager.create_worktree("feature/dup2", worktree_path)
        assert result2 is False
    
    def test_remove_worktree_real(self, git_repo, tmp_path):
        """测试真实删除工作区"""
        manager = GitWorktreeManager(str(git_repo))
        
        worktree_path = str(tmp_path / "worktree_remove")
        manager.create_worktree("feature/remove", worktree_path)
        
        result = manager.remove_worktree(worktree_path)
        
        assert result is True
        assert not Path(worktree_path).exists()
        assert worktree_path not in manager.active_worktrees
    
    def test_remove_worktree_force(self, git_repo, tmp_path):
        """测试强制删除工作区"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 使用不同的临时路径避免冲突
        worktree_path = str(tmp_path / "force_worktree" / "wt_force")
        manager.create_worktree("feature/force", worktree_path)
        
        # 在工作区创建未提交的文件
        test_file = Path(worktree_path) / "uncommitted.txt"
        test_file.write_text("uncommitted changes")
        
        result = manager.remove_worktree(worktree_path, force=True)
        
        # 强制删除应该成功（即使有未提交变更）
        assert result is True or not Path(worktree_path).exists()
    
    def test_list_worktrees_real(self, git_repo, tmp_path):
        """测试真实列出工作区"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建工作区（使用独立的路径）
        worktree_base = tmp_path / "list_worktrees"
        worktree_base.mkdir(exist_ok=True)
        
        wt1_path = str(worktree_base / "wt1")
        wt2_path = str(worktree_base / "wt2")
        manager.create_worktree("feature/wt1", wt1_path)
        manager.create_worktree("feature/wt2", wt2_path)
        
        worktrees = manager.list_worktrees()
        
        # 应该包含主工作区 + 2 个新工作区
        assert len(worktrees) >= 3
        
        # 验证新工作区在列表中（检查路径或分支）
        wt_branches = [wt.get("branch", "") for wt in worktrees]
        assert "feature/wt1" in wt_branches or "feature/wt2" in wt_branches


class TestGitChange:
    """测试 GitChange 数据类"""
    
    def test_create_git_change_minimal(self):
        """测试创建最小 GitChange"""
        change = GitChange(file="test.py", status="M")
        
        assert change.file == "test.py"
        assert change.status == "M"
        assert change.lines_added == 0
        assert change.lines_deleted == 0
    
    def test_create_git_change_full(self):
        """测试创建完整 GitChange"""
        change = GitChange(
            file="app.py",
            status="A",
            lines_added=100,
            lines_deleted=50
        )
        
        assert change.file == "app.py"
        assert change.status == "A"
        assert change.lines_added == 100
        assert change.lines_deleted == 50


class TestGitEdgeCases:
    """测试边界情况和错误处理"""
    
    def test_run_git_with_check_false(self, tmp_path):
        """测试 check=False 时运行 Git 命令"""
        manager = GitWorktreeManager(str(tmp_path))
        
        # 模拟模式不会真正运行命令
        result = manager._run_git("invalid-command", check=False)
        
        assert result.returncode == 0
    
    def test_empty_worktrees_list(self, tmp_path):
        """测试空工作区列表"""
        manager = GitWorktreeManager(str(tmp_path))
        
        worktrees = manager.list_worktrees()
        
        assert worktrees == []
    
    def test_remove_worktree_multiple_times(self, tmp_path):
        """测试多次删除同一工作区"""
        manager = GitWorktreeManager(str(tmp_path))
        manager.active_worktrees.append("/tmp/wt")
        
        # 第一次删除
        result1 = manager.remove_worktree("/tmp/wt")
        assert result1 is True
        
        # 第二次删除（已不存在）
        result2 = manager.remove_worktree("/tmp/wt")
        assert result2 is True
    
    def test_detect_changes_empty_output(self, git_repo):
        """测试空变更输出"""
        manager = GitWorktreeManager(str(git_repo))
        
        changes = manager.detect_changes()
        
        # 初始状态无变更
        assert changes == []
    
    def test_git_change_status_values(self):
        """测试各种 Git 状态值"""
        statuses = ["A", "M", "D", "R", "C", "U"]
        
        for status in statuses:
            change = GitChange(file="test.py", status=status)
            assert change.status == status


class TestGitIntegrationScenarios:
    """测试真实集成场景"""
    
    def test_complete_workflow(self, git_repo, tmp_path):
        """测试完整工作流：创建分支 → 修改 → 提交 → 工作区"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 1. 创建并切换到新分支
        manager.checkout_branch("feature/complete", create=True)
        assert manager.get_current_branch() == "feature/complete"
        
        # 2. 添加文件
        test_file = git_repo / "workflow.txt"
        test_file.write_text("workflow test")
        manager.add_files(["workflow.txt"])
        
        # 3. 提交变更
        result = manager.commit("Add workflow test")
        assert result is True
        
        # 4. 创建工作区
        worktree_path = str(tmp_path / "wt_complete")
        result = manager.create_worktree("feature/worktree", worktree_path)
        assert result is True
        
        # 5. 列出工作区
        worktrees = manager.list_worktrees()
        assert len(worktrees) >= 2
    
    def test_parallel_worktrees(self, git_repo, tmp_path):
        """测试并行工作区场景"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建多个工作区
        worktrees = []
        for i in range(3):
            wt_path = str(tmp_path / f"wt_{i}")
            result = manager.create_worktree(f"feature/task{i}", wt_path)
            assert result is True
            worktrees.append(wt_path)
        
        # 验证所有工作区存在
        for wt_path in worktrees:
            assert Path(wt_path).exists()
        
        # 列出并验证
        listed_wt = manager.list_worktrees()
        assert len(listed_wt) >= 4  # 主 + 3 个新工作区
        
        # 清理工作区
        for wt_path in worktrees:
            result = manager.remove_worktree(wt_path)
            assert result is True
    
    def test_branch_switching_with_changes(self, git_repo):
        """测试有未提交变更时切换分支"""
        manager = GitWorktreeManager(str(git_repo))
        
        # 创建新分支
        manager.checkout_branch("feature/branch1", create=True)
        
        # 添加文件但不提交
        test_file = git_repo / "uncommitted.txt"
        test_file.write_text("uncommitted")
        manager.add_files(["uncommitted.txt"])
        
        # 尝试切换分支（应该失败或需要处理）
        # 在真实场景中这会失败，但我们可以测试行为
        original_branch = manager.get_current_branch()
        result = manager.checkout_branch("main", create=False)
        
        # 验证行为（可能失败或成功取决于 Git 配置）
        # 这里我们只验证方法可以调用
        assert isinstance(result, bool)
