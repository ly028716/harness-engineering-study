"""Git 操作工具 - Phase 3"""
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GitChange:
    """Git 变更"""
    file: str
    status: str  # A, M, D, R, etc.
    lines_added: int = 0
    lines_deleted: int = 0


class GitWorktreeManager:
    """Git 工作区管理器"""

    def __init__(self, repo_path: str):
        """初始化 Git 工作区管理器

        Args:
            repo_path: Git 仓库路径
        """
        self.repo_path = Path(repo_path)
        self.active_worktrees: List[str] = []
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        """确保是 Git 仓库"""
        if not (self.repo_path / ".git").exists():
            # 不是 Git 仓库，模拟模式
            self._is_git_repo = False
        else:
            self._is_git_repo = True

    def _run_git(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """运行 Git 命令

        Args:
            args: Git 命令参数
            check: 是否检查错误

        Returns:
            CompletedProcess 对象
        """
        if not self._is_git_repo:
            # 模拟模式
            return subprocess.CompletedProcess(args, 0, "", "")

        cmd = ["git", "-C", str(self.repo_path), *args]
        return subprocess.run(cmd, capture_output=True, text=check)

    def create_worktree(self, branch: str, path: str) -> bool:
        """创建工作区

        Args:
            branch: 分支名
            path: 工作区路径

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            # 模拟模式
            self.active_worktrees.append(path)
            return True

        result = self._run_git("worktree", "add", path, "-b", branch)
        if result.returncode == 0:
            self.active_worktrees.append(path)
            return True
        return False

    def remove_worktree(self, path: str, force: bool = False) -> bool:
        """删除工作区

        Args:
            path: 工作区路径
            force: 是否强制删除

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            # 模拟模式
            if path in self.active_worktrees:
                self.active_worktrees.remove(path)
            return True

        args = ["worktree", "remove"]
        if force:
            args.insert(1, "--force")
        args.append(path)

        result = self._run_git(*args)
        if result.returncode == 0:
            if path in self.active_worktrees:
                self.active_worktrees.remove(path)
            return True
        return False

    def detect_changes(self) -> List[GitChange]:
        """检测变更

        Returns:
            变更列表
        """
        if not self._is_git_repo:
            # 模拟模式
            return []

        changes = []

        # 获取变更文件列表
        result = self._run_git("diff", "--name-status", "HEAD")
        if result.returncode != 0:
            return changes

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[0]
                file = parts[1]
                changes.append(GitChange(file=file, status=status))

        return changes

    def get_current_branch(self) -> Optional[str]:
        """获取当前分支

        Returns:
            分支名
        """
        if not self._is_git_repo:
            return "main"

        result = self._run_git("branch", "--show-current")
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    def checkout_branch(self, branch: str, create: bool = False) -> bool:
        """切换分支

        Args:
            branch: 分支名
            create: 是否创建新分支

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            return True

        args = ["checkout"]
        if create:
            args.append("-b")
        args.append(branch)

        result = self._run_git(*args)
        return result.returncode == 0

    def add_files(self, files: List[str]) -> bool:
        """添加文件到暂存区

        Args:
            files: 文件列表

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            return True

        result = self._run_git("add", *files)
        return result.returncode == 0

    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """提交变更

        Args:
            message: 提交信息
            allow_empty: 是否允许空提交

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            return True

        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        result = self._run_git(*args)
        return result.returncode == 0

    def push(self, branch: str, upstream: bool = False) -> bool:
        """推送分支

        Args:
            branch: 分支名
            upstream: 是否设置上游

        Returns:
            是否成功
        """
        if not self._is_git_repo:
            return True

        args = ["push"]
        if upstream:
            args.append("-u")
        args.append("origin")
        args.append(branch)

        result = self._run_git(*args)
        return result.returncode == 0

    def get_diff(self, base_ref: str = "HEAD~1") -> str:
        """获取变更 diff

        Args:
            base_ref: 基准引用

        Returns:
            Diff 字符串
        """
        if not self._is_git_repo:
            return ""

        result = self._run_git("diff", base_ref)
        if result.returncode == 0:
            return result.stdout
        return ""

    def list_worktrees(self) -> List[Dict[str, Any]]:
        """列出工作区

        Returns:
            工作区信息列表
        """
        if not self._is_git_repo:
            return [{"path": p, "branch": "unknown"} for p in self.active_worktrees]

        result = self._run_git("worktree", "list", "--porcelain")
        if result.returncode != 0:
            return []

        worktrees = []
        current = {}

        for line in result.stdout.strip().split("\n"):
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue

            if line.startswith("worktree "):
                current["path"] = line[9:]
            elif line.startswith("branch "):
                current["branch"] = line[7:]

        if current:
            worktrees.append(current)

        return worktrees
