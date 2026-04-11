"""Todo 数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class Todo:
    """待办事项数据类"""

    id: int
    title: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def complete(self):
        """标记为完成"""
        self.completed = True

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Todo":
        """从字典创建 Todo"""
        return cls(
            id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )
