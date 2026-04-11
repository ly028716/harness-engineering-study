"""测试 Markdown 解析器"""
import pytest
from pathlib import Path
from harness.parser import MarkdownParser


class TestMarkdownParser:
    """测试 Markdown 解析器"""

    def test_parse_empty_file(self, tmp_path):
        """RED: 测试解析空文件"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text("", encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert isinstance(tasks, list)
        assert len(tasks) == 0

    def test_parse_single_todo_task(self, tmp_path):
        """RED: 测试解析单个 TODO 任务"""
        content = """# Plans

## Tasks

- [ ] Task 1: Implement feature A
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 1: Implement feature A"
        assert tasks[0]["status"] == "TODO"

    def test_parse_multiple_tasks_with_different_statuses(self, tmp_path):
        """RED: 测试解析多个不同状态的任务"""
        content = """# Plans

## Tasks

- [ ] Task 1: TODO task
- [~] Task 2: WIP task
- [x] Task 3: DONE task
- [!] Task 4: BLOCKED task
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert len(tasks) == 4
        assert tasks[0]["status"] == "TODO"
        assert tasks[1]["status"] == "WIP"
        assert tasks[2]["status"] == "DONE"
        assert tasks[3]["status"] == "BLOCKED"

    def test_parse_task_with_description(self, tmp_path):
        """RED: 测试解析带描述的任务"""
        content = """# Plans

## Tasks

- [ ] Task 1: Main title
  Description line 1
  Description line 2
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert len(tasks) == 1
        assert "Description line 1" in tasks[0]["description"]
        assert "Description line 2" in tasks[0]["description"]

    def test_parse_task_with_acceptance_criteria(self, tmp_path):
        """RED: 测试解析带验收标准的任务"""
        content = """# Plans

## Tasks

- [ ] Task 1: Main title
  - ✅ Criterion 1
  - ✅ Criterion 2
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert len(tasks) == 1
        assert len(tasks[0]["acceptance_criteria"]) == 2
        assert "Criterion 1" in tasks[0]["acceptance_criteria"][0]
        assert "Criterion 2" in tasks[0]["acceptance_criteria"][1]

    def test_parse_assigns_task_ids(self, tmp_path):
        """RED: 测试解析时分配任务 ID"""
        content = """# Plans

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert tasks[0]["id"] == 1
        assert tasks[1]["id"] == 2
        assert tasks[2]["id"] == 3

    def test_parse_ignores_non_task_content(self, tmp_path):
        """RED: 测试忽略非任务内容"""
        content = """# Plans

Some introduction text.

## Tasks

- [ ] Task 1

## Notes

Some notes here.
"""
        md_file = tmp_path / "Plans.md"
        md_file.write_text(content, encoding='utf-8')

        parser = MarkdownParser(md_file)
        tasks = parser.parse()

        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 1"
