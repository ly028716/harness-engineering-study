"""数据模型 - Phase 2"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class TaskStatus(Enum):
    """任务状态枚举"""
    TODO = "TODO"
    WIP = "WIP"
    DONE = "DONE"
    BLOCKED = "BLOCKED"

    @classmethod
    def from_string(cls, value: str) -> "TaskStatus":
        """从字符串创建 TaskStatus"""
        return cls[value.upper()]


class Priority(Enum):
    """优先级枚举"""
    REQUIRED = "REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    OPTIONAL = "OPTIONAL"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """从字符串创建 Priority"""
        return cls[value.upper()]


@dataclass
class Task:
    """任务数据类"""

    id: int
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.REQUIRED
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)
    estimated_effort: int = 1
    actual_effort: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    block_reason: Optional[str] = None

    def complete(self):
        """标记任务为完成"""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def start(self):
        """标记任务为进行中"""
        self.status = TaskStatus.WIP
        self.updated_at = datetime.now()

    def block(self, reason: str):
        """标记任务为被阻塞"""
        self.status = TaskStatus.BLOCKED
        self.block_reason = reason
        self.updated_at = datetime.now()

    def add_acceptance_criterion(self, criterion: str):
        """添加验收标准"""
        self.acceptance_criteria.append(criterion)
        self.updated_at = datetime.now()

    def add_dependency(self, task_id: int):
        """添加依赖"""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "estimated_effort": self.estimated_effort,
            "actual_effort": self.actual_effort,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "block_reason": self.block_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus.from_string(data.get("status", "TODO")),
            priority=Priority.from_string(data.get("priority", "REQUIRED")),
            acceptance_criteria=data.get("acceptance_criteria", []),
            dependencies=data.get("dependencies", []),
            estimated_effort=data.get("estimated_effort", 1),
            actual_effort=data.get("actual_effort"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            block_reason=data.get("block_reason"),
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"Task {self.id}: {self.title} [{self.status.value}]"


# ===== Phase 4: Review 功能数据模型 =====

class Severity(Enum):
    """问题严重程度枚举"""
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """从字符串创建 Severity"""
        return cls[value.upper()]


class Category(Enum):
    """问题类别枚举"""
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    QUALITY = "QUALITY"
    ACCESSIBILITY = "ACCESSIBILITY"
    AI_RESIDUALS = "AI_RESIDUALS"

    @classmethod
    def from_string(cls, value: str) -> "Category":
        """从字符串创建 Category"""
        return cls[value.upper()]


class Verdict(Enum):
    """审查判定结果枚举"""
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"

    @classmethod
    def from_string(cls, value: str) -> "Verdict":
        """从字符串创建 Verdict"""
        return cls[value.upper()]


@dataclass
class Issue:
    """代码审查问题数据类"""

    severity: Severity
    category: Category
    message: str
    file: str
    line: int
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """从字典创建 Issue"""
        return cls(
            severity=Severity.from_string(data["severity"]),
            category=Category.from_string(data["category"]),
            message=data["message"],
            file=data["file"],
            line=data["line"],
            suggestion=data.get("suggestion"),
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.severity.value}] {self.category.value}: {self.message} ({self.file}:{self.line})"


@dataclass
class ReviewResult:
    """代码审查结果数据类"""

    verdict: Verdict
    issues: List[Issue]
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "verdict": self.verdict.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
        }
