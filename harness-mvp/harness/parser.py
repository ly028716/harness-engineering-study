"""Markdown 解析器"""
import re
from pathlib import Path
from typing import List, Dict, Any


class MarkdownParser:
    """解析 Plans.md 格式的 Markdown 文件"""

    # 任务状态映射
    STATUS_MAP = {
        '[ ]': 'TODO',
        '[~]': 'WIP',
        '[x]': 'DONE',
        '[!]': 'BLOCKED'
    }

    def __init__(self, md_file: Path):
        """初始化解析器

        Args:
            md_file: Markdown 文件路径
        """
        self.md_file = Path(md_file)

    def parse(self) -> List[Dict[str, Any]]:
        """解析 Markdown 文件

        Returns:
            任务列表
        """
        if not self.md_file.exists():
            return []

        content = self.md_file.read_text(encoding='utf-8')
        if not content.strip():
            return []

        return self._parse_tasks(content)

    def _parse_tasks(self, content: str) -> List[Dict[str, Any]]:
        """解析任务列表

        Args:
            content: Markdown 内容

        Returns:
            任务列表
        """
        tasks = []
        lines = content.split('\n')
        task_id = 1
        current_task = None
        in_tasks_section = False

        for i, line in enumerate(lines):
            # 检查是否进入 Tasks 部分
            if line.strip().startswith('## Tasks'):
                in_tasks_section = True
                continue

            # 检查是否离开 Tasks 部分
            if in_tasks_section and line.strip().startswith('##'):
                in_tasks_section = False
                continue

            if not in_tasks_section:
                continue

            # 检查是否是任务行
            task_match = self._match_task_line(line)
            if task_match:
                # 保存上一个任务
                if current_task:
                    tasks.append(current_task)

                # 创建新任务
                status, title = task_match
                current_task = {
                    'id': task_id,
                    'title': title,
                    'status': status,
                    'description': '',
                    'acceptance_criteria': []
                }
                task_id += 1
            elif current_task:
                # 处理任务的附加内容
                self._process_task_content(line, current_task)

        # 保存最后一个任务
        if current_task:
            tasks.append(current_task)

        return tasks

    def _match_task_line(self, line: str) -> tuple:
        """匹配任务行

        Args:
            line: 行内容

        Returns:
            (status, title) 或 None
        """
        for marker, status in self.STATUS_MAP.items():
            pattern = rf'^-\s+{re.escape(marker)}\s+(.+)$'
            match = re.match(pattern, line.strip())
            if match:
                return (status, match.group(1))
        return None

    def _process_task_content(self, line: str, task: Dict[str, Any]):
        """处理任务的附加内容

        Args:
            line: 行内容
            task: 当前任务字典
        """
        stripped = line.strip()

        # 检查是否是验收标准
        if stripped.startswith('- ✅'):
            criterion = stripped[4:].strip()
            task['acceptance_criteria'].append(criterion)
        elif stripped and not stripped.startswith('-'):
            # 普通描述文本
            if task['description']:
                task['description'] += '\n'
            task['description'] += stripped
